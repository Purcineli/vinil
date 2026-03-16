# Convenções

## Código

| Regra | Detalhe |
|---|---|
| Estilo | PEP8 |
| Aspas | Simples (`'valor'`) |
| Idioma do código | Inglês (variáveis, funções, classes, comentários) |
| Idioma da interface | Português (labels, mensagens, textos ao usuário) |
| Views | Class Based Views (CBV) sempre que possível |
| Models | Ricos — lógica de negócio vai no model (properties, métodos) |
| Views | Simples — apenas orquestram, sem lógica de negócio |

## Models

Todo model deve ter:

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
history = HistoricalRecords()  # django-simple-history
```

## Autenticação

O login é feito por **e-mail**, não por username. Um `EmailBackend` customizado em `accounts/backends.py` sobrescreve o comportamento padrão do Django.

## Segurança

- CSRF habilitado em todos os formulários (`{% csrf_token %}`)
- Views que exigem login usam `LoginRequiredMixin`
- Race condition na compra de ingressos tratada com `select_for_update()`
- Ingressos (`Ticket`) só são criados após `Payment.status == 'confirmado'` via signal

## Nomenclatura

| Tipo | Convenção | Exemplo |
|---|---|---|
| Model | PascalCase | `TicketType`, `OrderItem` |
| View | PascalCase + sufixo | `EventCreateView`, `OrderListView` |
| Form | PascalCase + `Form` | `EventForm`, `PaymentForm` |
| Template | snake_case | `event_detail.html`, `order_list.html` |
| URL name | snake_case com namespace | `events:event_detail` |

## URLs

Cada app tem seu próprio `urls.py` com namespace definido, incluído no `core/urls.py`:

```python
# core/urls.py
path('eventos/', include('events.urls', namespace='events')),
path('pedidos/', include('orders.urls', namespace='orders')),
# ...
```

## Templates

- Templates de componentes reutilizáveis ficam em `templates/components/`
- O layout público herda de `base.html`
- O layout do dashboard herda de `base_dashboard.html`, que inclui a sidebar
- Mensagens flash do Django são exibidas via `templates/components/messages.html`

## Signals

Signals ficam em `<app>/signals.py` e são registrados no `ready()` do `<app>/apps.py`:

```python
# payments/apps.py
class PaymentsConfig(AppConfig):
    name = 'payments'

    def ready(self):
        import payments.signals  # noqa
```
