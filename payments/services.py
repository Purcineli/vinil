import binascii
import hashlib
import hmac
import json
import logging

import mercadopago
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def _get_sdk():
    """Retorna uma instância do SDK autenticada com o ACCESS_TOKEN do settings."""
    return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


class MercadoPagoService:
    """
    Camada de serviço para operações com a API do MercadoPago.

    Centraliza criação de preferências, consulta de pagamentos e
    validação de webhooks. Não contém lógica de modelo — apenas
    chamadas de API e mapeamento de dados.
    """

    # Mapeamento: status MP → status interno do Payment
    # approved  → confirmado (emite tickets via signal)
    # rejected/cancelled → cancelado
    # pending/in_process → permanece pending (aguarda próxima notificação)
    MP_TO_INTERNAL_STATUS = {
        'approved': 'confirmed',
        'rejected': 'cancelled',
        'cancelled': 'cancelled',
        'charged_back': 'cancelled',
        'refunded': 'cancelled',
        'pending': 'pending',
        'in_process': 'pending',
        'authorized': 'pending',
    }

    @staticmethod
    def create_preference(order, request):
        """
        Cria uma preferência de pagamento no Checkout Pro para o pedido dado.

        Retorna o dict de resposta da API do MP, que inclui:
          - 'id': o preference_id a ser passado ao SDK JS no frontend
          - 'init_point': URL de redirect para o checkout (sandbox: sandbox_init_point)

        Lança uma exceção se a API retornar erro.
        """
        sdk = _get_sdk()

        # Monta a lista de items a partir dos OrderItems do pedido
        items = []
        for item in order.items.select_related('ticket_type__event').all():
            items.append({
                'id': str(item.ticket_type.pk),
                'title': f'{item.ticket_type.name} — {item.ticket_type.event.name}',
                'description': f'Ingresso para {item.ticket_type.event.name}',
                'category_id': 'entertainment',
                'quantity': item.quantity,
                # unit_price precisa ser float — MP não aceita Decimal
                'unit_price': float(item.unit_price),
                'currency_id': 'BRL',
            })

        # URLs absolutas de retorno (back_urls)
        # Em produção, use request.build_absolute_uri com HTTPS
        base = request.build_absolute_uri('/')[:-1]  # ex: http://localhost:8000
        BASE_URL = "https://trustee-bodies-que-letting.trycloudflare.com"

        base = BASE_URL
        preference_data = {
            # Identificador do pedido no nosso sistema — usado no webhook
            # para localizar o Payment correto
            'external_reference': str(order.pk),

            'items': items,

            'payer': {
                'email': order.buyer.email,
                'name': order.buyer.get_full_name() or order.buyer.email,
            },

            # URLs para onde o MP redireciona o comprador após o pagamento
            'back_urls': {
                'success': base + reverse('payments:payment_success_pending'),
                'failure': base + reverse('payments:payment_failure'),
                'pending': base + reverse('payments:payment_success_pending'),
            },

            # Redireciona automaticamente após pagamento aprovado
            'auto_return': 'approved',

            # URL do webhook — o MP envia POST aqui após qualquer mudança de status
            'notification_url': base + reverse('payments:webhook'),

            # statement_descriptor aparece na fatura do cartão do comprador
            'statement_descriptor': 'VINIL INGRESSOS',
        }

        logger.info(
            'Criando preferência MP para pedido #%s (total: R$ %s)',
            order.pk,
            order.total_amount,
        )

        result = sdk.preference().create(preference_data)
        response = result.get('response', {})
        status_code = result.get('status', 0)

        if status_code not in (200, 201):
            logger.error(
                'Erro ao criar preferência MP para pedido #%s: status=%s response=%s',
                order.pk,
                status_code,
                response,
            )
            raise ValueError(
                f'MercadoPago retornou status {status_code}: {response}'
            )

        logger.info(
            'Preferência MP criada: preference_id=%s pedido=#%s',
            response.get('id'),
            order.pk,
        )
        return response

    @staticmethod
    def create_transparent_payment(order, token, installments, payment_method_id,
                                   payment_type_id, payer_email, payer_cpf,
                                   issuer_id=None):
        """
        Creates a direct (transparent) card payment via the MercadoPago Payments API.

        Card data never touches our server — only the opaque token generated
        by MercadoPago.js in the browser.

        Args:
            order: Order instance being paid.
            token: Card token generated by MercadoPago.js on the frontend.
            installments: Number of installments chosen by the buyer.
            payment_method_id: MP payment method ID (e.g. 'visa', 'master').
            payment_type_id: MP payment type (e.g. 'credit_card', 'debit_card').
            payer_email: Buyer e-mail (required by MP for fraud prevention).
            payer_cpf: Buyer CPF digits only (required for Brazilian payments).
            issuer_id: Card issuer ID returned by MP getPaymentMethods().

        Returns:
            dict: Full payment response from MP API.

        Raises:
            ValueError: If the MP API returns an error status.
        """
        sdk = _get_sdk()

        # Build items list for approval rate optimisation (quality checklist)
        # Note: currency_id is NOT accepted inside additional_info.items (only in preferences)
        items = []
        for item in order.items.select_related('ticket_type__event').all():
            items.append({
                'id': str(item.ticket_type.pk),
                'title': f'{item.ticket_type.name} — {item.ticket_type.event.name}',
                'description': f'Ingresso para {item.ticket_type.event.name}',
                'category_id': 'entertainment',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
            })

        payment_data = {
            'transaction_amount': float(order.total_amount),
            'token': token,
            'installments': int(installments),
            'payment_method_id': payment_method_id,
            'payment_type_id': payment_type_id,
            'external_reference': str(order.pk),
            'statement_descriptor': 'VINIL INGRESSOS',
            'payer': {
                'email': payer_email,
                'identification': {
                    'type': 'CPF',
                    'number': payer_cpf,
                },
            },
            'additional_info': {
                'items': items,
                # additional_info.payer does NOT accept email — only name/phone/address
                'payer': {
                    'first_name': order.buyer.first_name or '',
                    'last_name': order.buyer.last_name or '',
                    'registration_date': order.buyer.date_joined.isoformat(),
                },
            },
        }

        if issuer_id:
            payment_data['issuer_id'] = issuer_id

        logger.info(
            'Creating transparent card payment for order #%s (amount: R$ %s, '
            'installments: %s, method: %s)',
            order.pk,
            order.total_amount,
            installments,
            payment_method_id,
        )

        print('='*60)
        print(f'MP PAYMENT DATA SENT: {json.dumps(payment_data, indent=2, default=str)}')
        print('='*60)

        result = sdk.payment().create(payment_data)
        response = result.get('response', {})
        status_code = result.get('status', 0)

        print('='*60)
        print(f'MP RAW RESULT status_code={status_code}')
        print(f'MP RAW RESULT response={json.dumps(response, indent=2, default=str)}')
        print('='*60)

        if status_code not in (200, 201):
            logger.error(
                'Error creating transparent card payment for order #%s: '
                'status=%s response=%s',
                order.pk,
                status_code,
                response,
            )
            raise ValueError(
                f'MercadoPago returned status {status_code}: {response}'
            )

        logger.info(
            'Transparent card payment created: mp_payment_id=%s mp_status=%s '
            'mp_status_detail=%s order=#%s',
            response.get('id'),
            response.get('status'),
            response.get('status_detail'),
            order.pk,
        )
        return response

    @staticmethod
    def create_pix_payment(order, payer_email, payer_cpf, payer_first_name='',
                           payer_last_name=''):
        """
        Creates a Pix payment via the MercadoPago Payments API.

        Returns a response with point_of_interaction.transaction_data containing:
          - qr_code_base64: base64-encoded QR code image
          - qr_code: Pix Copia e Cola string
          - ticket_url: link to a hosted page with QR and instructions

        Pix payments always start as 'pending' and are confirmed async via webhook.

        Args:
            order: Order instance being paid.
            payer_email: Buyer e-mail.
            payer_cpf: Buyer CPF digits only (11 digits, no punctuation).
            payer_first_name: Buyer first name (optional, improves approval).
            payer_last_name: Buyer last name (optional, improves approval).

        Returns:
            dict: Full payment response from MP API.

        Raises:
            ValueError: If the MP API returns an error status.
        """
        sdk = _get_sdk()

        items = []
        for item in order.items.select_related('ticket_type__event').all():
            items.append({
                'id': str(item.ticket_type.pk),
                'title': f'{item.ticket_type.name} — {item.ticket_type.event.name}',
                'description': f'Ingresso para {item.ticket_type.event.name}',
                'category_id': 'entertainment',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
            })

        payment_data = {
            'transaction_amount': float(order.total_amount),
            'payment_method_id': 'pix',
            'external_reference': str(order.pk),
            'description': 'Ingressos Vinil',
            'payer': {
                'email': payer_email,
                'first_name': payer_first_name,
                'last_name': payer_last_name,
                'identification': {
                    'type': 'CPF',
                    'number': payer_cpf,
                },
            },
            'additional_info': {
                'items': items,
            },
        }

        logger.info(
            'Creating Pix payment for order #%s (amount: R$ %s)',
            order.pk,
            order.total_amount,
        )

        result = sdk.payment().create(payment_data)
        response = result.get('response', {})
        status_code = result.get('status', 0)

        if status_code not in (200, 201):
            logger.error(
                'Error creating Pix payment for order #%s: status=%s response=%s',
                order.pk,
                status_code,
                response,
            )
            raise ValueError(
                f'MercadoPago returned status {status_code}: {response}'
            )

        logger.info(
            'Pix payment created: mp_payment_id=%s mp_status=%s order=#%s',
            response.get('id'),
            response.get('status'),
            order.pk,
        )
        return response

    @staticmethod
    def create_boleto_payment(order, payer_email, payer_cpf, payment_method_id='bolbradesco',
                              payer_first_name='', payer_last_name='', zip_code='',
                              street_name='', street_number='', neighborhood='',
                              city='', federal_unit=''):
        """
        Creates a boleto bancário payment via the MercadoPago Payments API.

        Boleto requires payer address fields (zip_code, street_name, etc.) as
        mandated by the MP API for Brazilian boleto processing.

        Returns a response with transaction_details.external_resource_url
        (the boleto PDF URL) and point_of_interaction with barcode data.

        Args:
            order: Order instance being paid.
            payer_email: Buyer e-mail.
            payer_cpf: Buyer CPF digits only (11 digits).
            payer_first_name: Buyer first name.
            payer_last_name: Buyer last name.
            zip_code: Buyer postal code.
            street_name: Buyer street name.
            street_number: Buyer street number.
            neighborhood: Buyer neighborhood.
            city: Buyer city.
            federal_unit: Brazilian state abbreviation (e.g. 'SP').

        Returns:
            dict: Full payment response from MP API.

        Raises:
            ValueError: If the MP API returns an error status.
        """
        sdk = _get_sdk()

        items = []
        for item in order.items.select_related('ticket_type__event').all():
            items.append({
                'id': str(item.ticket_type.pk),
                'title': f'{item.ticket_type.name} — {item.ticket_type.event.name}',
                'description': f'Ingresso para {item.ticket_type.event.name}',
                'category_id': 'entertainment',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
            })

        payment_data = {
            'transaction_amount': float(order.total_amount),
            'payment_method_id': payment_method_id,
            'external_reference': str(order.pk),
            'description': 'Ingressos Vinil',
            'payer': {
                'email': payer_email,
                'first_name': payer_first_name,
                'last_name': payer_last_name,
                'identification': {
                    'type': 'CPF',
                    'number': payer_cpf,
                },
                'address': {
                    'zip_code': zip_code,
                    'street_name': street_name,
                    'street_number': street_number,
                    'neighborhood': neighborhood,
                    'city': city,
                    'federal_unit': federal_unit,
                },
            },
            'additional_info': {
                'items': items,
            },
        }

        logger.info(
            'Creating boleto payment for order #%s (amount: R$ %s, method: %s)',
            order.pk, order.total_amount, payment_method_id,
        )

        result = sdk.payment().create(payment_data)
        response = result.get('response', {})
        status_code = result.get('status', 0)

        if status_code not in (200, 201):
            logger.error(
                'Error creating boleto payment for order #%s: status=%s response=%s',
                order.pk,
                status_code,
                response,
            )
            raise ValueError(
                f'MercadoPago returned status {status_code}: {response}'
            )

        logger.info(
            'Boleto payment created: mp_payment_id=%s mp_status=%s order=#%s',
            response.get('id'),
            response.get('status'),
            order.pk,
        )
        return response

    @staticmethod
    def get_payment(mp_payment_id):
        """
        Consulta um pagamento na API do MP pelo ID.
        Retorna o dict do pagamento ou None em caso de erro.
        """
        sdk = _get_sdk()
        result = sdk.payment().get(mp_payment_id)
        status_code = result.get('status', 0)

        if status_code != 200:
            logger.error(
                'Erro ao consultar pagamento MP id=%s: status=%s',
                mp_payment_id,
                status_code,
            )
            return None

        return result.get('response')

    @staticmethod
    def validate_webhook_signature(request):
        """
        Valida a assinatura HMAC-SHA256 do webhook recebido do MercadoPago.

        O MP envia no header 'x-signature' o valor no formato:
            ts=<timestamp>,v1=<hash_hex>

        O template da mensagem assinada é:
            id:<data.id>;request-id:<x-request-id>;ts:<ts>;

        Retorna True se a assinatura for válida, False caso contrário.
        Se MERCADOPAGO_WEBHOOK_SECRET estiver vazio, pula a validação
        (útil apenas em desenvolvimento local sem ngrok).
        """
        secret = settings.MERCADOPAGO_WEBHOOK_SECRET
        if not secret:
            logger.warning(
                'MERCADOPAGO_WEBHOOK_SECRET não configurado — '
                'validação de assinatura desativada'
            )
            return True

        x_signature = request.headers.get('x-signature', '')
        x_request_id = request.headers.get('x-request-id', '')
        # data.id vem como query param na URL da notificação
        data_id = request.GET.get('data.id', '')

        if not x_signature:
            logger.warning('Webhook recebido sem header x-signature')
            return False

        # Extrai ts e v1 do header x-signature
        ts = None
        received_hash = None
        for part in x_signature.split(','):
            try:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key == 'ts':
                    ts = value
                elif key == 'v1':
                    received_hash = value
            except ValueError:
                continue

        if not ts or not received_hash:
            logger.warning('Header x-signature malformado: %s', x_signature)
            return False

        # Monta a string a ser assinada conforme documentação oficial do MP
        signed_template = f'id:{data_id};request-id:{x_request_id};ts:{ts};'

        # Calcula o HMAC-SHA256
        expected_bytes = hmac.new(
            secret.encode('utf-8'),
            signed_template.encode('utf-8'),
            hashlib.sha256,
        ).digest()
        expected_hash = binascii.hexlify(expected_bytes).decode()

        # Comparação segura contra timing attacks
        is_valid = hmac.compare_digest(received_hash, expected_hash)

        if not is_valid:
            logger.warning(
                'Assinatura de webhook inválida. '
                'template=%s expected=%s received=%s',
                signed_template,
                expected_hash,
                received_hash,
            )

        return is_valid

    @classmethod
    def map_mp_status(cls, mp_status):
        """
        Converte o status bruto do MercadoPago para o status interno do Payment.
        Retorna None se o status não deve gerar mudança (ex: desconhecido).
        """
        return cls.MP_TO_INTERNAL_STATUS.get(mp_status)
