# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos comuns

```bash
# Ativar virtualenv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt

# Migrations
python manage.py makemigrations
python manage.py migrate

# Rodar servidor
python manage.py runserver

# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell
```

## Arquitetura

Aplicação Django full stack com 5 apps:

- **`accounts`** — autenticação por e-mail (não username), cadastro e perfil. Backend customizado em `accounts/backends.py`.
- **`events`** — CRUD de eventos. Cada evento tem um organizador (FK para User) e múltiplos `TicketType`s.
- **`tickets`** — dois models centrais: `TicketType` (categorias de ingresso por evento, ex: Pista/VIP) e `Ticket` (ingresso individual emitido, com UUID, código `VNL-XXXXX` e QR Code).
- **`orders`** — `Order` (pedido do comprador) e `OrderItem` (tipo + quantidade). Race condition evitada com `select_for_update()` ao decrementar `sold_quantity`.
- **`payments`** — `Payment` (OneToOne com Order). Signal `post_save` em `payments/signals.py` emite os `Ticket`s individuais ao confirmar o pagamento.

Configurações do projeto em `core/` (settings, urls, wsgi, asgi).

## Padrões obrigatórios

**Código:** PEP8, aspas simples, inglês no código, português na interface.

**Views:** sempre Class Based Views (`LoginRequiredMixin` para views autenticadas).

**Models:** ricos — lógica de negócio fica no model (properties, métodos). Views simples, só orquestram.

**Todo model deve ter:**
```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
history = HistoricalRecords()  # django-simple-history
```

**URLs:** cada app tem `urls.py` com namespace próprio, incluído em `core/urls.py`.

**Signals:** definidos em `<app>/signals.py`, registrados no `ready()` do `<app>/apps.py`.

**Templates:** componentes reutilizáveis em `templates/components/`. Layout público herda de `base.html`. Dashboard herda de `base_dashboard.html` (inclui sidebar).

**Frontend:** TailwindCSS via CDN. Sem build step. Gradiente padrão: `from-violet-600 via-fuchsia-500 to-pink-400`.

## QR Code e validação de ingressos

O QR Code é gerado server-side com `qrcode[pil]` a partir do código alfanumérico (`VNL-XXXXX`) e retornado como base64 para renderização direta no template. A leitura na portaria usa `jsQR` (JS via CDN) para decodificar frames da câmera em tempo real e submeter o código via POST. O servidor valida, inutiliza o ingresso (`is_used=True`) e retorna o resultado.

## Documentação

- `PRD.md` — requisitos completos, user stories, fluxos de UX e design system
- `docs/` — guidelines de setup, arquitetura, design system e convenções
