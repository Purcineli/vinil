# Arquitetura

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+ / Django 6.0.3 |
| Frontend | Django Template Language + TailwindCSS (via CDN) |
| Banco de dados | SQLite (padrão Django) |
| Histórico de models | `django-simple-history` |
| Geração de QR Code | `qrcode[pil]` — server-side, retornado como base64 |
| Leitura de QR Code | `jsQR` — biblioteca JavaScript via CDN, roda no browser |
| Admin | Django Admin nativo |
| Autenticação | Django Auth nativo com backend customizado (login por e-mail) |

## Estrutura de apps

```
vinil/
├── core/           # Configurações do projeto (settings, urls, wsgi, asgi)
├── accounts/       # Autenticação, cadastro e perfil de usuário
├── events/         # Criação e gestão de eventos
├── tickets/        # Tipos de ingresso (TicketType) e ingressos emitidos (Ticket)
├── orders/         # Pedidos e itens de pedido
├── payments/       # Pagamentos associados a pedidos
├── templates/      # Templates HTML (a criar)
└── manage.py
```

Cada app tem responsabilidade única. O app `tickets` é o mais central: gerencia tanto as categorias de ingresso (`TicketType`) quanto os ingressos individuais emitidos (`Ticket`), incluindo QR Code e validação de portaria.

## Modelo de dados

```
USER ──────────── organizes ──────────── EVENT
  │                                        │
  └── places ──── ORDER                   └── has many ── TICKET_TYPE
                    │                                          │
                    ├── contains ── ORDER_ITEM ── references ─┘
                    │                   │
                    │                   └── emits N ── TICKET
                    │                                   (uuid, code VNL-XXXXX,
                    │                                    is_used, used_at)
                    └── paid via ── PAYMENT
```

### Entidades principais

**Event**
Campos: `name`, `description`, `location`, `start_date`, `end_date`, `is_active`, `organizer` (FK User), `created_at`, `updated_at`.

**TicketType**
Múltiplos por evento (ex: Pista, VIP, Camarote).
Campos: `event` (FK), `name`, `description`, `price`, `total_quantity`, `sold_quantity`, `created_at`, `updated_at`.
Property: `available_quantity = total_quantity - sold_quantity`.

**Order**
Campos: `buyer` (FK User), `status` (pendente / confirmado / cancelado), `total_amount`, `created_at`, `updated_at`.

**OrderItem**
Campos: `order` (FK), `ticket_type` (FK), `quantity`, `unit_price`, `created_at`, `updated_at`.
Property: `subtotal = quantity * unit_price`.

**Ticket**
Um registro por ingresso físico emitido. Criado via signal após pagamento confirmado.
Campos: `order_item` (FK), `uuid` (UUID único), `code` (alfanumérico único, formato `VNL-XXXXX`), `is_used`, `used_at`, `created_at`, `updated_at`.

**Payment**
Campos: `order` (OneToOne), `method` (dinheiro / pix / cartão), `status` (pendente / confirmado / cancelado), `amount`, `paid_at`, `created_at`, `updated_at`.

## Fluxos técnicos importantes

### Emissão de ingressos (signal)

Ao confirmar um pagamento (`Payment.status = 'confirmado'`), um signal `post_save` em `payments` percorre os `OrderItem`s do pedido e cria N `Ticket`s individuais — um por unidade comprada. Os `Ticket`s só são criados uma vez (verificação de `created` no signal).

### Geração do código alfanumérico

Formato: `VNL-XXXXX` (5 caracteres aleatórios, maiúsculos + dígitos).
Gerado no `save()` do model `Ticket`, com retry automático em caso de colisão de `unique=True`.

```python
def generate_ticket_code():
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=5))
    return f'VNL-{suffix}'
```

### Geração do QR Code

Gerado server-side a partir do código alfanumérico do ingresso. Retornado como base64 e renderizado diretamente no template.

```python
def get_qrcode_base64(self) -> str:
    qr = qrcode.make(self.code)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
```

Template: `<img src="data:image/png;base64,{{ ticket.get_qrcode_base64 }}">`

### Validação de portaria

```
[Browser] jsQR decodifica frame da câmera → extrai código → preenche input → POST
[Server]  busca Ticket pelo code
          → não existe: result = 'invalid'
          → is_used == True: result = 'already_used' + used_at
          → is_used == False: ticket.mark_as_used() → result = 'success'
[Browser] renderiza bloco de resultado → limpa campo para nova leitura
```

### Controle de race condition na compra

Ao criar um pedido, o `sold_quantity` do `TicketType` é decrementado dentro de uma transação com `select_for_update()`, evitando que dois compradores simultâneos adquiram o mesmo ingresso.

## Templates

Estrutura esperada em `templates/`:

```
templates/
├── base.html                  # Layout público (navbar + footer)
├── base_dashboard.html        # Layout interno (sidebar)
├── components/
│   ├── navbar.html
│   ├── footer.html
│   ├── sidebar.html
│   └── messages.html          # Mensagens flash do Django
├── public/
│   └── home.html
├── accounts/
│   ├── register.html
│   ├── login.html
│   └── profile.html
├── events/
│   ├── event_list.html
│   ├── event_detail.html
│   └── event_form.html
├── tickets/
│   └── ticket_type_form.html
├── orders/
│   ├── order_form.html
│   ├── order_list.html
│   └── order_detail.html
├── payments/
│   ├── payment_form.html
│   └── payment_success.html
├── dashboard/
│   └── index.html
├── 404.html
└── 500.html
```
