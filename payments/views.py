import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from orders.models import Order

from .forms import PaymentForm
from .models import Payment
from .services import MercadoPagoService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# View legada — mantida para compatibilidade com URLs existentes
# ---------------------------------------------------------------------------

class PaymentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'payments/payment_form.html'
    form_class = PaymentForm

    def _get_order(self):
        return get_object_or_404(Order, pk=self.kwargs['order_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self._get_order()
        return context

    def form_valid(self, form):
        order = self._get_order()

        if order.buyer != self.request.user:
            raise PermissionDenied

        form.instance.order = order
        form.instance.status = Payment.STATUS_CONFIRMED
        form.instance.paid_at = timezone.now()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('payments:payment_success', kwargs={'pk': self.object.pk})


# ---------------------------------------------------------------------------
# Checkout Pro — view principal
# ---------------------------------------------------------------------------

class CheckoutProView(LoginRequiredMixin, View):
    """
    GET: Cria (ou reutiliza) a preferência MP para o pedido e renderiza
         o template com o botão de Wallet do Checkout Pro.

    Fluxo:
      1. Valida que o pedido pertence ao usuário e está pendente.
      2. Cria ou recupera o Payment pendente vinculado ao pedido.
      3. Chama MercadoPagoService.create_preference() → obtém preference_id.
      4. Salva mp_preference_id no Payment.
      5. Renderiza checkout_pro.html com public_key e preference_id.
    """

    template_name = 'payments/checkout_pro.html'

    def get(self, request, order_pk):
        order = get_object_or_404(Order, pk=order_pk)

        # Segurança: apenas o dono do pedido pode pagar
        if order.buyer != request.user:
            raise PermissionDenied

        # Não permite pagar pedido já confirmado ou cancelado
        if not order.is_pending:
            messages.warning(
                request,
                'Este pedido não está mais disponível para pagamento.',
            )
            return redirect('orders:detail', pk=order.pk)

        # Cria ou recupera o Payment pendente vinculado ao pedido
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'method': Payment.METHOD_MERCADOPAGO,
                'amount': order.total_amount,
                'status': Payment.STATUS_PENDING,
            },
        )

        try:
            preference = MercadoPagoService.create_preference(order, request)
        except Exception as exc:
            logger.exception('Falha ao criar preferência MP para pedido #%s', order.pk)
            messages.error(
                request,
                'Não foi possível iniciar o pagamento. Tente novamente em instantes.',
            )
            return redirect('orders:detail', pk=order.pk)

        # Persiste o preference_id para referência futura
        payment.mp_preference_id = preference['id']
        payment.save(update_fields=['mp_preference_id', 'updated_at'])

        from django.shortcuts import render
        return render(request, self.template_name, {
            'order': order,
            'payment': payment,
            'preference_id': preference['id'],
            # sandbox_init_point para testes; em prod use init_point
            'init_point': preference.get('sandbox_init_point') or preference.get('init_point'),
            'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
        })


# ---------------------------------------------------------------------------
# Webhook — recebe notificações assíncronas do MercadoPago
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """
    Recebe notificações POST do MercadoPago após mudanças de status de pagamento.

    Segurança:
      - csrf_exempt: MP não envia CSRF token.
      - Valida assinatura HMAC-SHA256 (x-signature header).
      - Idempotente: ignora notificações já processadas.

    Responde 200 imediatamente — MP considera qualquer outra resposta como falha
    e reenvia a notificação (até 5 vezes com backoff exponencial).
    """

    def post(self, request):
        # Valida assinatura antes de qualquer processamento
        if not MercadoPagoService.validate_webhook_signature(request):
            logger.warning('Webhook com assinatura inválida rejeitado')
            return HttpResponse(status=400)

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            logger.warning('Webhook com corpo JSON inválido')
            return HttpResponse(status=200)  # 200 para evitar reenvio

        topic = body.get('type') or body.get('topic', '')
        logger.info('Webhook MP recebido: type=%s', topic)

        # Só processa notificações de pagamento
        if topic not in ('payment', 'payment.updated'):
            return HttpResponse(status=200)

        mp_payment_id = str(body.get('data', {}).get('id', ''))
        if not mp_payment_id:
            logger.warning('Webhook sem data.id no corpo')
            return HttpResponse(status=200)

        # Consulta o pagamento completo na API do MP
        mp_payment_data = MercadoPagoService.get_payment(mp_payment_id)
        if not mp_payment_data:
            logger.error('Não foi possível consultar pagamento MP id=%s', mp_payment_id)
            return HttpResponse(status=200)

        mp_status = mp_payment_data.get('status', '')
        # external_reference = pk do nosso Order, definido em create_preference()
        order_pk = mp_payment_data.get('external_reference', '')

        if not order_pk:
            logger.warning('Pagamento MP %s sem external_reference', mp_payment_id)
            return HttpResponse(status=200)

        try:
            self._process_payment_notification(mp_payment_id, mp_status, order_pk)
        except Exception:
            logger.exception(
                'Erro ao processar notificação MP: payment_id=%s order_pk=%s',
                mp_payment_id,
                order_pk,
            )
            # Retorna 200 mesmo em erro interno — evita reenvio em loop
            # Em produção, considere enfileirar para retry via Celery

        return HttpResponse(status=200)

    @staticmethod
    def _process_payment_notification(mp_payment_id, mp_status, order_pk):
        """
        Atualiza o Payment interno com base no status recebido do MP.

        Usa select_for_update() para evitar race conditions quando o MP
        reenvia notificações em paralelo (padrão do projeto, ver orders/views.py).
        O signal post_save em payments/signals.py emite os Tickets automaticamente
        quando o status transita para 'confirmed'.
        """
        new_internal_status = MercadoPagoService.map_mp_status(mp_status)

        with transaction.atomic():
            try:
                # select_for_update bloqueia a linha durante a transação
                payment = Payment.objects.select_for_update().get(order__pk=order_pk)
            except Payment.DoesNotExist:
                logger.warning(
                    'Payment não encontrado para order_pk=%s (mp_payment_id=%s)',
                    order_pk,
                    mp_payment_id,
                )
                return

            # Idempotência: se o status não mudou, não faz nada
            if payment.mp_payment_id == mp_payment_id and payment.mp_status == mp_status:
                logger.info(
                    'Notificação duplicada ignorada: mp_payment_id=%s status=%s',
                    mp_payment_id,
                    mp_status,
                )
                return

            # Atualiza campos MP sempre (para auditoria)
            payment.mp_payment_id = mp_payment_id
            payment.mp_status = mp_status

            # Atualiza status interno apenas se houver mapeamento definido
            # e se o status ainda não foi confirmado (evita reverter tickets emitidos)
            if new_internal_status and payment.status != Payment.STATUS_CONFIRMED:
                payment.status = new_internal_status
                if new_internal_status == Payment.STATUS_CONFIRMED:
                    payment.paid_at = timezone.now()

            payment.save()

            logger.info(
                'Payment #%s atualizado: mp_status=%s internal_status=%s',
                payment.pk,
                mp_status,
                payment.status,
            )


# ---------------------------------------------------------------------------
# Views de retorno (back_urls do Checkout Pro)
# ---------------------------------------------------------------------------

class PaymentSuccessPendingView(LoginRequiredMixin, View):
    """
    Página de retorno após pagamento aprovado ou pendente.

    O MP redireciona para cá com query params:
      ?payment_id=<id>&status=<status>&external_reference=<order_pk>

    O status real vem do webhook — aqui apenas mostramos o estado atual do Payment.
    """

    def get(self, request):
        order_pk = request.GET.get('external_reference')
        mp_payment_id = request.GET.get('payment_id')
        mp_status = request.GET.get('status', '')

        if not order_pk:
            return redirect('dashboard')

        order = get_object_or_404(Order, pk=order_pk)

        if order.buyer != request.user:
            raise PermissionDenied

        # Tenta obter o payment já existente
        payment = getattr(order, 'payment', None)

        # Atualiza mp_payment_id no redirect de sucesso (o webhook pode chegar depois)
        if payment and mp_payment_id and not payment.mp_payment_id:
            Payment.objects.filter(pk=payment.pk).update(
                mp_payment_id=mp_payment_id,
                mp_status=mp_status,
            )
            payment.refresh_from_db()

        from django.shortcuts import render

        # Se já foi confirmado, redireciona para a tela de sucesso com tickets
        if payment and payment.status == Payment.STATUS_CONFIRMED:
            return redirect('payments:payment_success', pk=payment.pk)

        # Caso ainda esteja pending (ex: boleto, Pix aguardando)
        return render(request, 'payments/payment_pending.html', {
            'order': order,
            'payment': payment,
        })


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'payments/payment_success.html'
    context_object_name = 'payment'

    def get_object(self, queryset=None):
        payment = super().get_object(queryset)

        if payment.order.buyer != self.request.user:
            raise PermissionDenied

        return payment


# ---------------------------------------------------------------------------
# Transparent Checkout (Card Payment Brick) — views
# ---------------------------------------------------------------------------

class TransparentCheckoutView(LoginRequiredMixin, View):
    """
    GET: Renders the transparent checkout form using MercadoPago Card Payment
    Brick.  No preference is created here — the Brick tokenises the card in
    the browser and POSTs the token + metadata directly to
    TransparentCheckoutProcessView.

    Flow:
      1. Validate the order belongs to the authenticated user and is pending.
      2. Get or create a pending Payment record linked to the order.
      3. Render the template with public_key, order, and payment context.
    """

    template_name = 'payments/transparent_checkout.html'

    def get(self, request, order_pk):
        order = get_object_or_404(Order, pk=order_pk)

        if order.buyer != request.user:
            raise PermissionDenied

        if not order.is_pending:
            messages.warning(
                request,
                'Este pedido não está mais disponível para pagamento.',
            )
            return redirect('orders:detail', pk=order.pk)

        # Method is set to MERCADOPAGO as placeholder — it will be updated to
        # credit_card, pix, or mercadopago (boleto) when the Brick submits.
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'method': Payment.METHOD_MERCADOPAGO,
                'amount': order.total_amount,
                'status': Payment.STATUS_PENDING,
            },
        )

        from django.shortcuts import render
        return render(request, self.template_name, {
            'order': order,
            'payment': payment,
            'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
        })


@method_decorator(csrf_exempt, name='dispatch')
class TransparentCheckoutProcessView(LoginRequiredMixin, View):
    """
    POST: Unified endpoint for the Payment Brick onSubmit callback.

    Handles three payment types depending on the 'payment_type' field in the
    JSON body sent by the Brick:

      - 'credit_card' / 'debit_card': card flow — receives opaque token
      - 'bank_transfer': Pix — creates payment and returns QR code inline
      - 'ticket': boleto — creates payment and returns ticket_url inline

    For cards, returns a redirect_url so the browser navigates to the result
    page.  For Pix/boleto, returns the payment data so the template can render
    the QR code or barcode without leaving the page.

    Security:
        - Protected by LoginRequiredMixin.
        - Order ownership validated before any API call.
        - Card data never reaches the server — only the opaque MP token.
        - select_for_update() prevents race conditions on parallel webhooks.
    """

    def post(self, request, order_pk):
        order = get_object_or_404(Order, pk=order_pk)

        if order.buyer != request.user:
            return JsonResponse({'error': 'Acesso negado.'}, status=403)

        if not order.is_pending:
            return JsonResponse(
                {'error': 'Este pedido não está mais disponível para pagamento.'},
                status=400,
            )

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Requisição inválida.'}, status=400)

        print('='*60)
        print(f'BRICK BODY: {json.dumps(body, indent=2, default=str)}')
        print('='*60)
        logger.info('TransparentCheckout body: %s', json.dumps(body, default=str))

        payer = body.get('payer', {}) or {}
        # Brick may not include email in formData when pre-filled — fall back to logged-in user
        payer_email = payer.get('email', '').strip() or request.user.email

        # The Brick sends identification in different structures depending on
        # payment type. Try nested payer.identification first, then top-level.
        identification = payer.get('identification', {}) or {}
        payer_cpf_raw = identification.get('number', '')
        if not payer_cpf_raw:
            # Some Brick versions send it at body level
            top_identification = body.get('identification', {}) or {}
            payer_cpf_raw = top_identification.get('number', '')
        payer_cpf_raw = str(payer_cpf_raw).strip()
        payer_cpf = ''.join(c for c in payer_cpf_raw if c.isdigit())
        payment_type = body.get('payment_type', '').strip()

        if not payer_email:
            return JsonResponse({'error': 'E-mail é obrigatório.'}, status=400)

        # CPF is required for cards, optional for Pix/boleto
        if payment_type in ('credit_card', 'debit_card'):
            if not payer_cpf:
                return JsonResponse({'error': 'E-mail e CPF são obrigatórios.'}, status=400)
            if len(payer_cpf) != 11:
                return JsonResponse({'error': 'CPF inválido.'}, status=400)
        else:
            # For Pix/boleto, use CPF from form or fallback to buyer's CPF
            # If not available, use a placeholder (MP will still process)
            if not payer_cpf:
                # Try to get from order buyer profile
                buyer_cpf = getattr(order.buyer, 'cpf', None)
                payer_cpf = buyer_cpf or '00000000000'

        # Route to the correct payment method handler
        if payment_type in ('credit_card', 'debit_card'):
            return self._process_card(request, order, body, payer_email, payer_cpf)
        elif payment_type == 'bank_transfer':
            # Pix
            return self._process_pix(request, order, body, payer_email, payer_cpf)
        elif payment_type == 'ticket':
            # Boleto
            return self._process_boleto(request, order, body, payer_email, payer_cpf)
        else:
            return JsonResponse(
                {'error': f'Tipo de pagamento não suportado: {payment_type}'},
                status=400,
            )

    def _process_card(self, request, order, body, payer_email, payer_cpf):
        """Handles card (credit/debit) payment flow."""
        token = body.get('token', '').strip()
        installments = body.get('installments', 1)
        payment_method_id = body.get('payment_method_id', '').strip()
        payment_type_id = body.get('payment_type', '').strip()
        issuer_id = body.get('issuer_id')

        if not all([token, payment_method_id]):
            return JsonResponse({'error': 'Dados do cartão incompletos.'}, status=400)

        try:
            mp_response = MercadoPagoService.create_transparent_payment(
                order=order,
                token=token,
                installments=installments,
                payment_method_id=payment_method_id,
                payment_type_id=payment_type_id,
                payer_email=payer_email,
                payer_cpf=payer_cpf,
                issuer_id=issuer_id,
            )
            print('='*60)
            print(f'MP CARD RESPONSE: {json.dumps(mp_response, indent=2, default=str)}')
            print('='*60)
        except Exception as exc:
            print('='*60)
            print(f'MP CARD EXCEPTION: {exc}')
            print('='*60)
            logger.exception('Falha ao criar pagamento de cartão para pedido #%s', order.pk)
            return JsonResponse(
                {'error': 'Não foi possível processar o pagamento. Tente novamente.'},
                status=500,
            )

        mp_status = mp_response.get('status', '')
        mp_status_detail = mp_response.get('status_detail', '')
        mp_payment_id = str(mp_response.get('id', ''))

        self._save_payment(order, mp_payment_id, mp_status, mp_status_detail,
                           method=Payment.METHOD_CREDIT_CARD,
                           installments=int(installments))

        # Cards: navigate the user to a result page
        if mp_status == Payment.MP_STATUS_APPROVED:
            payment = Payment.objects.get(order=order)
            redirect_url = reverse('payments:payment_success', kwargs={'pk': payment.pk})
        elif mp_status in (Payment.MP_STATUS_PENDING, Payment.MP_STATUS_IN_PROCESS):
            redirect_url = (
                reverse('payments:payment_success_pending')
                + f'?external_reference={order.pk}&payment_id={mp_payment_id}&status={mp_status}'
            )
        else:
            redirect_url = reverse('payments:payment_failure') + f'?external_reference={order.pk}'

        logger.info(
            'Card payment processed: order=#%s mp_payment_id=%s mp_status=%s',
            order.pk, mp_payment_id, mp_status,
        )
        return JsonResponse({
            'payment_type': 'card',
            'status': mp_status,
            'status_detail': mp_status_detail,
            'redirect_url': redirect_url,
        })

    def _process_pix(self, request, order, body, payer_email, payer_cpf):
        """Handles Pix payment flow — returns QR code data for inline display."""
        payer = body.get('payer', {})
        first_name = payer.get('first_name', order.buyer.first_name or '')
        last_name = payer.get('last_name', order.buyer.last_name or '')

        try:
            mp_response = MercadoPagoService.create_pix_payment(
                order=order,
                payer_email=payer_email,
                payer_cpf=payer_cpf,
                payer_first_name=first_name,
                payer_last_name=last_name,
            )
        except Exception:
            logger.exception('Falha ao criar pagamento Pix para pedido #%s', order.pk)
            return JsonResponse(
                {'error': 'Não foi possível gerar o Pix. Tente novamente.'},
                status=500,
            )

        mp_status = mp_response.get('status', '')
        mp_status_detail = mp_response.get('status_detail', '')
        mp_payment_id = str(mp_response.get('id', ''))

        self._save_payment(order, mp_payment_id, mp_status, mp_status_detail,
                           method=Payment.METHOD_PIX)

        # Extract QR code data from the MP response
        poi = mp_response.get('point_of_interaction', {})
        transaction_data = poi.get('transaction_data', {})
        qr_code_base64 = transaction_data.get('qr_code_base64', '')
        qr_code = transaction_data.get('qr_code', '')
        ticket_url = transaction_data.get('ticket_url', '')

        logger.info(
            'Pix payment created: order=#%s mp_payment_id=%s mp_status=%s',
            order.pk, mp_payment_id, mp_status,
        )
        return JsonResponse({
            'payment_type': 'pix',
            'status': mp_status,
            'status_detail': mp_status_detail,
            'qr_code_base64': qr_code_base64,
            'qr_code': qr_code,
            'ticket_url': ticket_url,
            'mp_payment_id': mp_payment_id,
        })

    # Maps full Brazilian state names (as sent by the Payment Brick) to 2-letter UF codes
    _BR_STATE_TO_UF = {
        'ACRE': 'AC', 'ALAGOAS': 'AL', 'AMAPÁ': 'AP', 'AMAPA': 'AP',
        'AMAZONAS': 'AM', 'BAHIA': 'BA', 'CEARÁ': 'CE', 'CEARA': 'CE',
        'DISTRITO FEDERAL': 'DF', 'ESPÍRITO SANTO': 'ES', 'ESPIRITO SANTO': 'ES',
        'GOIÁS': 'GO', 'GOIAS': 'GO', 'MARANHÃO': 'MA', 'MARANHAO': 'MA',
        'MATO GROSSO DO SUL': 'MS', 'MATO GROSSO': 'MT',
        'MINAS GERAIS': 'MG', 'PARÁ': 'PA', 'PARA': 'PA',
        'PARAÍBA': 'PB', 'PARAIBA': 'PB', 'PARANÁ': 'PR', 'PARANA': 'PR',
        'PERNAMBUCO': 'PE', 'PIAUÍ': 'PI', 'PIAUI': 'PI',
        'RIO DE JANEIRO': 'RJ', 'RIO GRANDE DO NORTE': 'RN',
        'RIO GRANDE DO SUL': 'RS', 'RONDÔNIA': 'RO', 'RONDONIA': 'RO',
        'RORAIMA': 'RR', 'SANTA CATARINA': 'SC',
        'SÃO PAULO': 'SP', 'SAO PAULO': 'SP',
        'SERGIPE': 'SE', 'TOCANTINS': 'TO',
    }

    def _normalize_federal_unit(self, value):
        """Convert full state name or mixed input to the 2-letter UF code MP requires."""
        v = value.strip().upper()
        if len(v) <= 2:
            return v
        return self._BR_STATE_TO_UF.get(v, v[:2])

    def _process_boleto(self, request, order, body, payer_email, payer_cpf):
        """Handles boleto payment flow — returns ticket_url for inline display."""
        payer = body.get('payer', {}) or {}
        first_name = payer.get('first_name', '') or order.buyer.first_name or ''
        last_name = payer.get('last_name', '') or order.buyer.last_name or ''
        address = payer.get('address', {}) or {}
        zip_code = ''.join(c for c in address.get('zip_code', '') if c.isdigit())
        street_name = address.get('street_name', '').strip()
        street_number = str(address.get('street_number', '')).strip()
        neighborhood = address.get('neighborhood', '').strip()
        city = address.get('city', '').strip()
        federal_unit = self._normalize_federal_unit(address.get('federal_unit', ''))
        # Use the payment_method_id sent by the Brick (e.g. 'bolbradesco', 'pagofacil')
        payment_method_id = body.get('payment_method_id', 'bolbradesco').strip()

        logger.info(
            'Boleto extracted — email=%s cpf=%s zip=%s method=%s street=%s num=%s '
            'neighborhood=%s city=%s state=%s raw_address=%s',
            payer_email, payer_cpf, zip_code, payment_method_id,
            street_name, street_number, neighborhood, city, federal_unit, address,
        )

        # MP requires these address fields for boleto
        if not all([zip_code, street_name, street_number, neighborhood, city, federal_unit]):
            return JsonResponse(
                {'error': 'Endereço completo é obrigatório para pagamento com boleto.'},
                status=400,
            )

        if len(zip_code) != 8:
            return JsonResponse({'error': 'CEP inválido.'}, status=400)

        try:
            mp_response = MercadoPagoService.create_boleto_payment(
                order=order,
                payment_method_id=payment_method_id,
                payer_email=payer_email,
                payer_cpf=payer_cpf,
                payer_first_name=first_name,
                payer_last_name=last_name,
                zip_code=zip_code,
                street_name=street_name,
                street_number=street_number,
                neighborhood=neighborhood,
                city=city,
                federal_unit=federal_unit,
            )
        except Exception:
            logger.exception('Falha ao criar boleto para pedido #%s', order.pk)
            return JsonResponse(
                {'error': 'Não foi possível gerar o boleto. Tente novamente.'},
                status=500,
            )

        mp_status = mp_response.get('status', '')
        mp_status_detail = mp_response.get('status_detail', '')
        mp_payment_id = str(mp_response.get('id', ''))

        self._save_payment(order, mp_payment_id, mp_status, mp_status_detail,
                           method=Payment.METHOD_MERCADOPAGO)

        # ticket_url is the boleto PDF hosted on MP; digitable line for banks
        transaction_details = mp_response.get('transaction_details', {})
        ticket_url = transaction_details.get('external_resource_url', '')
        poi = mp_response.get('point_of_interaction', {})
        transaction_data = poi.get('transaction_data', {})
        digitable_line = transaction_data.get('digitable_line', '')
        barcode = transaction_data.get('barcode_content', '')

        logger.info(
            'Boleto payment created: order=#%s mp_payment_id=%s mp_status=%s',
            order.pk, mp_payment_id, mp_status,
        )
        return JsonResponse({
            'payment_type': 'boleto',
            'status': mp_status,
            'status_detail': mp_status_detail,
            'ticket_url': ticket_url,
            'digitable_line': digitable_line,
            'barcode': barcode,
            'mp_payment_id': mp_payment_id,
        })

    @staticmethod
    def _save_payment(order, mp_payment_id, mp_status, mp_status_detail,
                      method, installments=None):
        """
        Atomically updates the Payment record with MP response data.
        Uses select_for_update() to prevent race conditions with webhooks.
        """
        new_internal_status = MercadoPagoService.map_mp_status(mp_status)

        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(order=order)

            payment.mp_payment_id = mp_payment_id
            payment.mp_status = mp_status
            payment.mp_status_detail = mp_status_detail
            payment.method = method

            if installments is not None:
                payment.mp_installments = installments

            if new_internal_status and payment.status != Payment.STATUS_CONFIRMED:
                payment.status = new_internal_status
                if new_internal_status == Payment.STATUS_CONFIRMED:
                    payment.paid_at = timezone.now()

            payment.save()

        logger.info(
            'Payment #%s saved: mp_payment_id=%s mp_status=%s internal_status=%s',
            payment.pk, mp_payment_id, mp_status, payment.status,
        )


class PaymentFailureView(LoginRequiredMixin, View):
    """
    Página de retorno após pagamento recusado ou cancelado.

    O MP redireciona para cá com query params:
      ?payment_id=<id>&status=rejected&external_reference=<order_pk>
    """

    def get(self, request):
        order_pk = request.GET.get('external_reference')

        order = None
        payment = None

        if order_pk:
            order = get_object_or_404(Order, pk=order_pk)
            if order.buyer != request.user:
                raise PermissionDenied
            payment = getattr(order, 'payment', None)

        from django.shortcuts import render
        return render(request, 'payments/payment_failure.html', {
            'order': order,
            'payment': payment,
        })
