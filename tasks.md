## 13. Lista de Tarefas por Sprint

> **Legenda:** `[ ]` = pendente · `[X]` = concluído

---

### Sprint 0 — Configuração do Projeto

**Objetivo:** Projeto Django funcionando com TailwindCSS, estrutura de apps e templates base.

#### Tarefa 0.1 — Ambiente e dependências
- [x] 0.1.1 — Criar e ativar virtualenv Python 3.12+
- [x] 0.1.2 — Instalar Django 6.x via pip
- [x] 0.1.3 — Instalar `django-simple-history`
- [x] 0.1.4 — Instalar `qrcode[pil]` para geração de QR Codes server-side
- [x] 0.1.5 — Instalar `Pillow` (dependência do qrcode para salvar PNG)
- [x] 0.1.6 — Criar `requirements.txt` com todas as dependências iniciais
- [x] 0.1.7 — Criar o projeto Django com o nome `core` (`django-admin startproject core .`)
- [x] 0.1.8 — Verificar que `python manage.py runserver` sobe sem erros

#### Tarefa 0.2 — Configuração do `settings.py`
- [x] 0.2.1 — Configurar `INSTALLED_APPS` com: `accounts`, `events`, `tickets`, `orders`, `payments`, `simple_history`
- [x] 0.2.2 — Configurar `DATABASES` com SQLite padrão
- [x] 0.2.3 — Configurar `LANGUAGE_CODE = 'pt-br'` e `TIME_ZONE = 'America/Sao_Paulo'`
- [x] 0.2.4 — Configurar `USE_I18N = True` e `USE_TZ = True`
- [x] 0.2.5 — Configurar `LOGIN_URL = '/login/'`, `LOGIN_REDIRECT_URL = '/dashboard/'`, `LOGOUT_REDIRECT_URL = '/'`
- [x] 0.2.6 — Adicionar `AUTHENTICATION_BACKENDS` com o backend customizado de e-mail (a ser criado na Sprint 1)
- [x] 0.2.7 — Configurar `TEMPLATES['DIRS']` apontando para o diretório `templates/` na raiz
- [x] 0.2.8 — Configurar `STATIC_URL` e `STATICFILES_DIRS`

#### Tarefa 0.3 — Estrutura de templates base
- [x] 0.3.1 — Criar diretório `templates/` na raiz do projeto
- [x] 0.3.2 — Criar `templates/base.html` com HTML5, TailwindCSS via CDN, fonte Inter, bloco `title`, bloco `content` e bloco `extra_scripts`
- [x] 0.3.3 — Criar `templates/base_dashboard.html` extendendo `base.html`, com sidebar e área de conteúdo principal
- [x] 0.3.4 — Criar `templates/components/navbar.html` com logo, links e botões de auth
- [x] 0.3.5 — Criar `templates/components/footer.html` com texto simples
- [x] 0.3.6 — Criar `templates/components/sidebar.html` com links de navegação do dashboard
- [x] 0.3.7 — Criar `templates/components/messages.html` para exibir flash messages do Django com estilos do design system

#### Tarefa 0.4 — URLs base
- [x] 0.4.1 — Configurar `core/urls.py` com `include()` para cada app
- [x] 0.4.2 — Criar `urls.py` em cada app com `app_name` definido para namespace
- [x] 0.4.3 — Criar uma view de teste (`TemplateView`) apontando para `base.html` para validar o setup visual

---

### Sprint 1 — Autenticação com E-mail ✅

**Objetivo:** Login, cadastro e logout funcionando com e-mail no lugar de username.

#### Tarefa 1.1 — Backend de autenticação customizado
- [x] 1.1.1 — Criar `accounts/backends.py`
- [x] 1.1.2 — Implementar classe `EmailBackend(ModelBackend)` que recebe `username` como e-mail e busca via `User.objects.get(email=username)`
- [x] 1.1.3 — Tratar `User.DoesNotExist` retornando `None`
- [x] 1.1.4 — Verificar `user.check_password(password)` e `user.is_active` antes de retornar o usuário
- [x] 1.1.5 — Registrar `'accounts.backends.EmailBackend'` em `settings.AUTHENTICATION_BACKENDS`

#### Tarefa 1.2 — Formulários de autenticação
- [x] 1.2.1 — Criar `accounts/forms.py`
- [x] 1.2.2 — Implementar `CustomUserCreationForm(UserCreationForm)` com campo `email` obrigatório
- [x] 1.2.3 — Adicionar validação de e-mail único no método `clean_email()`
- [x] 1.2.4 — Implementar `CustomAuthenticationForm(AuthenticationForm)` alterando o label do campo `username` para "E-mail"
- [x] 1.2.5 — Aplicar classes TailwindCSS nos widgets de todos os campos via `attrs`

#### Tarefa 1.3 — Views de autenticação
- [x] 1.3.1 — Criar `accounts/views.py` com `RegisterView(CreateView)` usando `CustomUserCreationForm`
- [x] 1.3.2 — Em `RegisterView.form_valid`: salvar o formulário e redirecionar para `/login/`
- [x] 1.3.3 — Configurar `LoginView` nativo com `authentication_form = CustomAuthenticationForm`
- [x] 1.3.4 — Configurar `LogoutView` nativo com `next_page = '/'`
- [x] 1.3.5 — Criar `ProfileView(LoginRequiredMixin, TemplateView)` exibindo dados do usuário autenticado

#### Tarefa 1.4 — Templates de autenticação
- [x] 1.4.1 — Criar `templates/accounts/register.html` com layout centralizado, card branco e gradiente decorativo
- [x] 1.4.2 — Criar `templates/accounts/login.html` com layout centralizado, card branco e link para cadastro
- [x] 1.4.3 — Criar `templates/accounts/profile.html` exibindo nome, e-mail e data de cadastro
- [x] 1.4.4 — Em ambos os formulários, exibir erros de campo inline abaixo de cada input (usar `{{ form.field.errors }}`)
- [x] 1.4.5 — Em ambos os formulários, exibir erros globais do formulário (usar `{{ form.non_field_errors }}`)

#### Tarefa 1.5 — URLs de autenticação
- [x] 1.5.1 — Criar `accounts/urls.py` com `app_name = 'accounts'`
- [x] 1.5.2 — Definir rotas: `cadastro/` → `RegisterView`, `login/` → `LoginView`, `logout/` → `LogoutView`, `perfil/` → `ProfileView`
- [x] 1.5.3 — Incluir `accounts.urls` no `core/urls.py`
- [x] 1.5.4 — Testar manualmente o fluxo completo: cadastro → login → perfil → logout

---

### Sprint 2 — Site Público e Dashboard Base

**Objetivo:** Página inicial pública com eventos e dashboard interno pós-login.

#### Tarefa 2.1 — Página inicial pública
- [ ] 2.1.1 — Criar `HomeView(ListView)` em `events/views.py` com `queryset` filtrando eventos ativos, ordenados por `start_date`, limitados a 8
- [ ] 2.1.2 — Criar `templates/public/home.html` extendendo `base.html`
- [ ] 2.1.3 — Implementar seção hero com gradiente violet→fuchsia→pink, logo, tagline e dois botões CTA: "Cadastre-se" e "Ver Eventos"
- [ ] 2.1.4 — Implementar seção de eventos: grid responsivo com cards de evento
- [ ] 2.1.5 — Garantir responsividade: 1 coluna mobile, 2 tablet, 3-4 desktop

#### Tarefa 2.2 — Dashboard base (pós-login)
- [ ] 2.2.1 — Criar `DashboardView(LoginRequiredMixin, TemplateView)` que agrega contadores no contexto
- [ ] 2.2.2 — Contadores no contexto: total de eventos ativos, total de pedidos do usuário, total de ingressos emitidos, total de ingressos já validados (utilizados)
- [ ] 2.2.3 — Criar `templates/dashboard/index.html` extendendo `base_dashboard.html`
- [ ] 2.2.4 — Exibir quatro cards de resumo com ícone, número e label para cada contador
- [ ] 2.2.5 — Sidebar com links funcionais para todas as seções do dashboard

---

### Sprint 3 — App `events`

**Objetivo:** CRUD de eventos completo com interface consistente.

#### Tarefa 3.1 — Model `Event`
- [ ] 3.1.1 — Criar `events/models.py` com model `Event`
- [ ] 3.1.2 — Campos: `name` (CharField 200), `description` (TextField), `location` (CharField 200), `start_date` (DateTimeField), `end_date` (DateTimeField), `is_active` (BooleanField, default=False), `organizer` (FK settings.AUTH_USER_MODEL), `created_at` (auto_now_add), `updated_at` (auto_now)
- [ ] 3.1.3 — Adicionar `history = HistoricalRecords()`
- [ ] 3.1.4 — Implementar `__str__` retornando `self.name`
- [ ] 3.1.5 — Implementar property `is_upcoming` retornando `self.start_date > timezone.now()`
- [ ] 3.1.6 — Implementar `get_absolute_url()` usando `reverse('events:detail', kwargs={'pk': self.pk})`
- [ ] 3.1.7 — Definir `class Meta` com `ordering = ['-start_date']`
- [ ] 3.1.8 — Gerar migration com `makemigrations events`
- [ ] 3.1.9 — Aplicar migration com `migrate`

#### Tarefa 3.2 — Admin de `Event`
- [ ] 3.2.1 — Registrar `Event` em `events/admin.py` com `@admin.register`
- [ ] 3.2.2 — Configurar `list_display = ['name', 'organizer', 'start_date', 'is_active']`
- [ ] 3.2.3 — Configurar `list_filter = ['is_active', 'start_date']`
- [ ] 3.2.4 — Configurar `search_fields = ['name', 'location']`
- [ ] 3.2.5 — Configurar `list_editable = ['is_active']`

#### Tarefa 3.3 — Formulário de `Event`
- [ ] 3.3.1 — Criar `events/forms.py` com `EventForm(ModelForm)`
- [ ] 3.3.2 — Incluir campos: `name`, `description`, `location`, `start_date`, `end_date`
- [ ] 3.3.3 — Usar `DateTimeInput` com `type='datetime-local'` para campos de data
- [ ] 3.3.4 — Implementar `clean()` validando que `end_date >= start_date`
- [ ] 3.3.5 — Aplicar classes TailwindCSS nos widgets via `attrs`

#### Tarefa 3.4 — Views de `Event`
- [ ] 3.4.1 — Criar `EventListView(ListView)` pública com `queryset = Event.objects.filter(is_active=True)`
- [ ] 3.4.2 — Criar `EventDetailView(DetailView)` pública; passar tipos de ingresso do evento no contexto
- [ ] 3.4.3 — Criar `EventCreateView(LoginRequiredMixin, CreateView)` com `form_class = EventForm`
- [ ] 3.4.4 — Sobrescrever `form_valid` em `EventCreateView` para setar `form.instance.organizer = self.request.user`
- [ ] 3.4.5 — Criar `EventUpdateView(LoginRequiredMixin, UpdateView)` verificando que `request.user == event.organizer`
- [ ] 3.4.6 — Criar `EventToggleActiveView(LoginRequiredMixin, View)` recebendo POST e invertendo `is_active`

#### Tarefa 3.5 — Templates de `Event`
- [ ] 3.5.1 — Criar `templates/events/event_list.html` com grid de cards e botão para criar evento
- [ ] 3.5.2 — Criar `templates/events/event_detail.html` com info do evento, seção de tipos de ingresso e botão de compra
- [ ] 3.5.3 — Criar `templates/events/event_form.html` reutilizável para criação e edição

#### Tarefa 3.6 — URLs de `Event`
- [ ] 3.6.1 — Criar `events/urls.py` com `app_name = 'events'`
- [ ] 3.6.2 — Definir rotas: `''` → lista, `<pk>/` → detalhe, `criar/` → criar, `<pk>/editar/` → editar, `<pk>/toggle/` → toggle ativo
- [ ] 3.6.3 — Incluir em `core/urls.py` com prefixo `eventos/`

---

### Sprint 4 — App `tickets` — Parte 1: Tipos de Ingresso

**Objetivo:** Múltiplos tipos de ingresso por evento, com controle de disponibilidade.

#### Tarefa 4.1 — Model `TicketType`
- [ ] 4.1.1 — Criar `tickets/models.py` com model `TicketType`
- [ ] 4.1.2 — Campos: `event` (FK Event, related_name='ticket_types'), `name` (CharField 100), `description` (TextField, blank=True), `price` (DecimalField, max_digits=10, decimal_places=2), `total_quantity` (PositiveIntegerField), `sold_quantity` (PositiveIntegerField, default=0), `created_at` (auto_now_add), `updated_at` (auto_now)
- [ ] 4.1.3 — Adicionar `history = HistoricalRecords()`
- [ ] 4.1.4 — Implementar property `available_quantity` retornando `self.total_quantity - self.sold_quantity`
- [ ] 4.1.5 — Implementar property `is_available` retornando `self.available_quantity > 0`
- [ ] 4.1.6 — Implementar `__str__` retornando `f'{self.event.name} — {self.name}'`
- [ ] 4.1.7 — Definir `class Meta` com `ordering = ['price']`
- [ ] 4.1.8 — Gerar e aplicar migration

#### Tarefa 4.2 — Admin de `TicketType`
- [ ] 4.2.1 — Criar `TicketTypeInline(TabularInline)` em `tickets/admin.py` com `model = TicketType` e `extra = 1`
- [ ] 4.2.2 — Adicionar `TicketTypeInline` ao admin de `Event` em `events/admin.py`
- [ ] 4.2.3 — Registrar `TicketType` separadamente com `list_display = ['event', 'name', 'price', 'total_quantity', 'sold_quantity']`

#### Tarefa 4.3 — Formulário e Views de `TicketType`
- [ ] 4.3.1 — Criar `tickets/forms.py` com `TicketTypeForm(ModelForm)` com campos: `name`, `description`, `price`, `total_quantity`
- [ ] 4.3.2 — Aplicar classes TailwindCSS nos widgets
- [ ] 4.3.3 — Criar `TicketTypeCreateView(LoginRequiredMixin, CreateView)`
- [ ] 4.3.4 — Em `form_valid`: buscar `Event` pelo `event_pk` da URL; validar que `event.organizer == request.user`; setar `form.instance.event = event`
- [ ] 4.3.5 — Criar `TicketTypeUpdateView(LoginRequiredMixin, UpdateView)`
- [ ] 4.3.6 — Em `TicketTypeForm.clean_total_quantity()`: validar que o novo valor não é menor que `sold_quantity`

#### Tarefa 4.4 — Templates de `TicketType`
- [ ] 4.4.1 — Criar `templates/tickets/ticket_type_form.html`
- [ ] 4.4.2 — Na `event_detail.html`, listar todos os tipos do evento em cards com nome, descrição, preço e disponibilidade
- [ ] 4.4.3 — Exibir badge "Esgotado" e botão desabilitado para tipos com `available_quantity == 0`
- [ ] 4.4.4 — Exibir link "Adicionar tipo de ingresso" na página do evento apenas para o organizador autenticado

#### Tarefa 4.5 — URLs de `TicketType`
- [ ] 4.5.1 — Criar `tickets/urls.py` com `app_name = 'tickets'`
- [ ] 4.5.2 — Definir rotas: `eventos/<int:event_pk>/ingressos/criar/` → criar tipo, `ingressos/<int:pk>/editar/` → editar tipo

---

### Sprint 5 — App `tickets` — Parte 2: Ingresso Individual e QR Code

**Objetivo:** Emissão de `Ticket` individual por unidade comprada, com código único e QR Code.

#### Tarefa 5.1 — Model `Ticket`
- [ ] 5.1.1 — Adicionar model `Ticket` em `tickets/models.py`
- [ ] 5.1.2 — Campos: `order_item` (FK 'orders.OrderItem', related_name='tickets'), `uuid` (UUIDField, default=uuid.uuid4, unique=True, editable=False), `code` (CharField, max_length=10, unique=True, blank=True), `is_used` (BooleanField, default=False), `used_at` (DateTimeField, null=True, blank=True), `created_at` (auto_now_add), `updated_at` (auto_now)
- [ ] 5.1.3 — Adicionar `history = HistoricalRecords()`
- [ ] 5.1.4 — Implementar `__str__` retornando `f'Ingresso {self.code}'`
- [ ] 5.1.5 — Implementar método estático `generate_code()` retornando string no formato `VNL-XXXXX` com `random.choices` de `string.ascii_uppercase + string.digits` com k=5
- [ ] 5.1.6 — Sobrescrever `save()`: se `self.code` está vazio, chamar `generate_code()` em loop com try/except `IntegrityError` até sucesso
- [ ] 5.1.7 — Implementar método `get_qrcode_base64()` que instancia `qrcode.make(self.code)`, salva em `BytesIO`, retorna `base64.b64encode(buffer.getvalue()).decode('utf-8')`
- [ ] 5.1.8 — Implementar método `mark_as_used()` que seta `self.is_used = True`, `self.used_at = timezone.now()`, e chama `self.save()`
- [ ] 5.1.9 — Gerar e aplicar migration

#### Tarefa 5.2 — Admin de `Ticket`
- [ ] 5.2.1 — Registrar `Ticket` em `tickets/admin.py`
- [ ] 5.2.2 — Configurar `list_display = ['code', 'uuid', 'order_item', 'is_used', 'used_at', 'created_at']`
- [ ] 5.2.3 — Configurar `list_filter = ['is_used']`
- [ ] 5.2.4 — Configurar `search_fields = ['code', 'uuid']`
- [ ] 5.2.5 — Tornar `uuid`, `code`, `is_used`, `used_at` como `readonly_fields` no admin

#### Tarefa 5.3 — Views de `Ticket`
- [ ] 5.3.1 — Criar `TicketDetailView(LoginRequiredMixin, DetailView)` buscando por `uuid`
- [ ] 5.3.2 — Em `get_queryset()`: retornar apenas ingressos cujo comprador é `request.user`
- [ ] 5.3.3 — Criar `MyTicketsListView(LoginRequiredMixin, ListView)` listando todos os ingressos do usuário autenticado via `order_item__order__buyer = request.user`

#### Tarefa 5.4 — Templates de `Ticket`
- [ ] 5.4.1 — Criar `templates/tickets/ticket_detail.html` com card de ingresso completo (gradiente no header, QR Code, código, dados do evento e tipo)
- [ ] 5.4.2 — Renderizar QR Code via `<img src="data:image/png;base64,{{ ticket.get_qrcode_base64 }}">`
- [ ] 5.4.3 — Exibir código alfanumérico em fonte mono grande e legível
- [ ] 5.4.4 — Exibir badge de status: "Válido" em verde ou "Utilizado em [data/hora]" em vermelho
- [ ] 5.4.5 — Criar `templates/tickets/my_tickets.html` com lista de todos os ingressos do usuário, agrupados por evento

#### Tarefa 5.5 — URLs de `Ticket`
- [ ] 5.5.1 — Adicionar rotas em `tickets/urls.py`: `meus-ingressos/` → lista, `ingressos/<uuid:uuid>/` → detalhe
- [ ] 5.5.2 — Incluir em `core/urls.py`

---

### Sprint 6 — App `orders`

**Objetivo:** Fluxo de criação e listagem de pedidos com proteção de concorrência.

#### Tarefa 6.1 — Models `Order` e `OrderItem`
- [ ] 6.1.1 — Criar `orders/models.py`
- [ ] 6.1.2 — Implementar model `Order` com campos: `buyer` (FK settings.AUTH_USER_MODEL), `status` (CharField, choices: `pending`, `confirmed`, `cancelled`, default=`pending`), `total_amount` (DecimalField, max_digits=10, decimal_places=2), `created_at`, `updated_at`
- [ ] 6.1.3 — Adicionar `history = HistoricalRecords()` em `Order`
- [ ] 6.1.4 — Implementar `__str__` de `Order` retornando `f'Pedido #{self.pk}'`
- [ ] 6.1.5 — Implementar model `OrderItem` com campos: `order` (FK Order, related_name='items'), `ticket_type` (FK tickets.TicketType), `quantity` (PositiveIntegerField), `unit_price` (DecimalField, max_digits=10, decimal_places=2), `created_at`, `updated_at`
- [ ] 6.1.6 — Implementar property `subtotal` em `OrderItem` retornando `self.quantity * self.unit_price`
- [ ] 6.1.7 — Adicionar `history = HistoricalRecords()` em `OrderItem`
- [ ] 6.1.8 — Gerar e aplicar migration

#### Tarefa 6.2 — Admin de `Order`
- [ ] 6.2.1 — Criar `OrderItemInline(TabularInline)` em `orders/admin.py`
- [ ] 6.2.2 — Registrar `Order` com `inlines = [OrderItemInline]`
- [ ] 6.2.3 — Configurar `list_display = ['pk', 'buyer', 'status', 'total_amount', 'created_at']`
- [ ] 6.2.4 — Configurar `list_filter = ['status']`

#### Tarefa 6.3 — Formulário e Views de `Order`
- [ ] 6.3.1 — Criar `orders/forms.py` com `OrderCreateForm(Form)` com campos: `ticket_type_id` (HiddenInput) e `quantity` (IntegerField, min_value=1)
- [ ] 6.3.2 — Criar `OrderCreateView(LoginRequiredMixin, View)` com métodos `get` e `post`
- [ ] 6.3.3 — No `post`: dentro de `transaction.atomic()`, buscar `TicketType` com `select_for_update()` pelo `ticket_type_id`
- [ ] 6.3.4 — Verificar se `ticket_type.available_quantity >= quantity`; se não, adicionar mensagem de erro e redirecionar
- [ ] 6.3.5 — Incrementar `ticket_type.sold_quantity += quantity` e salvar
- [ ] 6.3.6 — Criar `Order` com `buyer=request.user`, `status='pending'`, `total_amount = quantity * ticket_type.price`
- [ ] 6.3.7 — Criar `OrderItem` vinculando `order`, `ticket_type`, `quantity` e `unit_price = ticket_type.price`
- [ ] 6.3.8 — Redirecionar para detalhe do pedido criado
- [ ] 6.3.9 — Criar `OrderListView(LoginRequiredMixin, ListView)` filtrando `buyer=request.user`
- [ ] 6.3.10 — Criar `OrderDetailView(LoginRequiredMixin, DetailView)` verificando `order.buyer == request.user`

#### Tarefa 6.4 — Templates de `Order`
- [ ] 6.4.1 — Criar `templates/orders/order_list.html` com tabela de pedidos, badges de status e link para detalhe
- [ ] 6.4.2 — Criar `templates/orders/order_detail.html` com itens, valores subtotais, total e status
- [ ] 6.4.3 — No `order_detail.html`, listar os `Ticket`s emitidos com link para cada um (se pedido confirmado)
- [ ] 6.4.4 — No `event_detail.html`, adicionar formulário de criação de pedido com seleção de quantidade para cada tipo de ingresso

#### Tarefa 6.5 — URLs de `Order`
- [ ] 6.5.1 — Criar `orders/urls.py` com `app_name = 'orders'`
- [ ] 6.5.2 — Definir rotas: `pedidos/` → lista, `pedidos/<int:pk>/` → detalhe, `pedidos/criar/` → criar
- [ ] 6.5.3 — Incluir em `core/urls.py`

---

### Sprint 7 — App `payments` e Emissão Automática de Ingressos

**Objetivo:** Registro de pagamento e emissão automática de `Ticket`s individuais via signal.

#### Tarefa 7.1 — Model `Payment`
- [ ] 7.1.1 — Criar `payments/models.py` com model `Payment`
- [ ] 7.1.2 — Campos: `order` (OneToOneField orders.Order, related_name='payment'), `method` (CharField, choices: `cash`, `pix`, `credit_card`, `debit_card`), `status` (CharField, choices: `pending`, `confirmed`, `cancelled`, default=`pending`), `amount` (DecimalField), `paid_at` (DateTimeField, null=True, blank=True), `created_at`, `updated_at`
- [ ] 7.1.3 — Adicionar `history = HistoricalRecords()`
- [ ] 7.1.4 — Implementar `__str__` retornando `f'Pagamento #{self.pk} — Pedido #{self.order.pk}'`
- [ ] 7.1.5 — Gerar e aplicar migration

#### Tarefa 7.2 — Signal de emissão de ingressos
- [ ] 7.2.1 — Criar `payments/signals.py`
- [ ] 7.2.2 — Implementar função `emit_tickets_on_payment_confirmed(sender, instance, created, **kwargs)`
- [ ] 7.2.3 — Condição de disparo: `not created` (atualização) e `instance.status == 'confirmed'`
- [ ] 7.2.4 — Dentro de `transaction.atomic()`: atualizar `instance.order.status = 'confirmed'` e `instance.order.save()`
- [ ] 7.2.5 — Para cada `OrderItem` do pedido, criar `item.quantity` instâncias de `Ticket` com `order_item=item` (código e UUID gerados automaticamente pelo `save()` do model)
- [ ] 7.2.6 — Verificar antes de criar tickets se eles ainda não existem (para idempotência do signal)
- [ ] 7.2.7 — Conectar o signal: `post_save.connect(emit_tickets_on_payment_confirmed, sender=Payment)`
- [ ] 7.2.8 — Criar `payments/apps.py` com `PaymentsConfig` importando os signals em `ready()`

#### Tarefa 7.3 — Admin de `Payment`
- [ ] 7.3.1 — Registrar `Payment` em `payments/admin.py`
- [ ] 7.3.2 — Configurar `list_display = ['pk', 'order', 'method', 'status', 'amount', 'paid_at']`
- [ ] 7.3.3 — Configurar `list_filter = ['status', 'method']`

#### Tarefa 7.4 — Formulário e Views de `Payment`
- [ ] 7.4.1 — Criar `payments/forms.py` com `PaymentForm(ModelForm)` com campos: `method`, `amount`
- [ ] 7.4.2 — Aplicar classes TailwindCSS nos widgets
- [ ] 7.4.3 — Criar `PaymentCreateView(LoginRequiredMixin, CreateView)`
- [ ] 7.4.4 — Em `form_valid`: buscar `Order` pelo `order_pk` da URL; validar que `order.buyer == request.user`; setar `form.instance.order = order`; redirecionar para sucesso
- [ ] 7.4.5 — Criar `PaymentUpdateStatusView(LoginRequiredMixin, UpdateView)` apenas com campo `status` para atualização manual

#### Tarefa 7.5 — Templates de `Payment`
- [ ] 7.5.1 — Criar `templates/payments/payment_form.html` exibindo resumo do pedido (evento, itens, total) e formulário de pagamento
- [ ] 7.5.2 — Criar `templates/payments/payment_success.html` com confirmação, valor pago e links para cada ingresso emitido

#### Tarefa 7.6 — URLs de `Payment`
- [ ] 7.6.1 — Criar `payments/urls.py` com `app_name = 'payments'`
- [ ] 7.6.2 — Definir rotas: `pedidos/<int:order_pk>/pagar/` → criar pagamento, `pagamento/<int:pk>/sucesso/` → sucesso, `pagamento/<int:pk>/status/` → atualizar status
- [ ] 7.6.3 — Incluir em `core/urls.py`

---

### Sprint 8 — Validação de Portaria (QR Code + Código Manual)

**Objetivo:** Tela de validação com leitura de QR Code via câmera e digitação manual de código.

#### Tarefa 8.1 — View de Validação
- [ ] 8.1.1 — Criar `TicketValidateView(LoginRequiredMixin, View)` em `tickets/views.py`
- [ ] 8.1.2 — Método `GET`: renderizar `templates/tickets/validate.html` sem contexto de resultado
- [ ] 8.1.3 — Método `POST`: obter `code` do `request.POST`, fazer strip e uppercase
- [ ] 8.1.4 — Buscar `Ticket.objects.filter(code=code).first()`
- [ ] 8.1.5 — Se `ticket` é `None`: retornar contexto com `result = 'invalid'`
- [ ] 8.1.6 — Se `ticket.is_used` é `True`: retornar contexto com `result = 'already_used'`, `ticket` e `ticket.used_at`
- [ ] 8.1.7 — Se ingresso válido e não usado: chamar `ticket.mark_as_used()` e retornar contexto com `result = 'success'` e `ticket`
- [ ] 8.1.8 — Em todos os casos de POST, renderizar o mesmo template com o contexto de resultado (sem redirect, para manter foco no campo)

#### Tarefa 8.2 — Template de Validação
- [ ] 8.2.1 — Criar `templates/tickets/validate.html` extendendo `base_dashboard.html`
- [ ] 8.2.2 — Seção de câmera: elemento `<video id="video">` e `<canvas id="canvas">` para captura de frames
- [ ] 8.2.3 — Botão "Ativar câmera" que chama `getUserMedia` via JavaScript
- [ ] 8.2.4 — Incluir `jsQR` via CDN: `<script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"></script>`
- [ ] 8.2.5 — Implementar loop JS com `requestAnimationFrame` que captura frame do vídeo no canvas, chama `jsQR(imageData, ...)` e, ao detectar código, preenche o campo `<input name="code">` e submete o formulário via `form.submit()`
- [ ] 8.2.6 — Seção de digitação manual: `<form method="POST">` com `{% csrf_token %}`, campo `<input name="code" type="text">` com `autofocus`, `oninput="this.value = this.value.toUpperCase()"` e botão "Validar"
- [ ] 8.2.7 — Seção de resultado: exibir bloco condicional baseado em `{{ result }}`
- [ ] 8.2.8 — Bloco `result == 'success'`: card verde com ✅, nome do evento, tipo de ingresso, nome do titular, mensagem de inutilização
- [ ] 8.2.9 — Bloco `result == 'already_used'`: card vermelho com ❌, data e hora da utilização anterior formatada em pt-BR
- [ ] 8.2.10 — Bloco `result == 'invalid'`: card amarelo com ⚠️ e mensagem de código não encontrado
- [ ] 8.2.11 — Após renderizar qualquer resultado, usar JS para limpar o campo de código e aplicar `autofocus` para nova leitura

#### Tarefa 8.3 — URLs de Validação
- [ ] 8.3.1 — Adicionar rota `portaria/validar/` em `tickets/urls.py` apontando para `TicketValidateView`
- [ ] 8.3.2 — Incluir link "🚪 Validar Ingresso" na sidebar do dashboard

---

### Sprint 9 — Polimento e Refinamento de UI

**Objetivo:** Consistência visual em todas as telas, mensagens e UX.

#### Tarefa 9.1 — Mensagens flash do sistema
- [ ] 9.1.1 — Estilizar `templates/components/messages.html` com classes TailwindCSS por tag (`success`, `error`, `warning`, `info`)
- [ ] 9.1.2 — Adicionar botão de fechar em cada mensagem via `onclick="this.parentElement.remove()"`
- [ ] 9.1.3 — Confirmar que o partial está incluído em `base.html` logo abaixo da navbar

#### Tarefa 9.2 — Páginas de erro
- [ ] 9.2.1 — Criar `templates/404.html` extendendo `base.html` com mensagem amigável e link para o início
- [ ] 9.2.2 — Criar `templates/500.html` extendendo `base.html` com mensagem de erro interno
- [ ] 9.2.3 — Configurar `handler404` e `handler500` em `core/urls.py`
- [ ] 9.2.4 — Definir `DEBUG = False` em ambiente de teste para validar as páginas de erro

#### Tarefa 9.3 — Responsividade mobile
- [ ] 9.3.1 — Implementar menu hambúrguer na navbar para mobile usando JavaScript vanilla e classes `hidden/block`
- [ ] 9.3.2 — Tornar sidebar collapsible em telas < `md` com botão de toggle
- [ ] 9.3.3 — Testar tela de validação de portaria em dispositivo mobile (câmera, campo de código, botões grandes)
- [ ] 9.3.4 — Adicionar `@media print` no card de ingresso para ocultar navbar/sidebar e otimizar impressão

#### Tarefa 9.4 — Acessibilidade básica
- [ ] 9.4.1 — Adicionar `aria-label` em botões sem texto descritivo (ex: botão de fechar mensagem)
- [ ] 9.4.2 — Garantir contraste mínimo WCAG AA em todos os textos sobre fundos coloridos
- [ ] 9.4.3 — Adicionar `autofocus` no campo de código após cada validação na portaria via JS

---

### Sprint 10 (Futura) — Docker

- [ ] 10.1.1 — Criar `Dockerfile` para o projeto Django com Python 3.12
- [ ] 10.1.2 — Criar `docker-compose.yml` com serviço web e volume persistente para SQLite
- [ ] 10.1.3 — Configurar variáveis de ambiente sensíveis via arquivo `.env` e `python-decouple`
- [ ] 10.1.4 — Documentar processo de build e execução no `README.md`

---

### Sprint 11 (Futura) — Testes Automatizados

- [ ] 11.1.1 — Configurar `pytest-django` e `pytest-cov`
- [ ] 11.1.2 — Escrever testes para o backend de autenticação por e-mail (login com e-mail válido, inválido, senha errada)
- [ ] 11.1.3 — Escrever testes para criação de evento e validação de datas
- [ ] 11.1.4 — Escrever testes de unicidade de código alfanumérico (geração, colisão e retry)
- [ ] 11.1.5 — Escrever testes de criação de pedido com `select_for_update` e controle de race condition
- [ ] 11.1.6 — Escrever testes para o signal de emissão de ingressos após confirmação do pagamento
- [ ] 11.1.7 — Escrever testes para a view de validação de portaria: código válido, já usado e inválido
- [ ] 11.1.8 — Escrever testes para o método `get_qrcode_base64()` verificando que retorna string base64 válida
- [ ] 11.1.9 — Configurar GitHub Actions para rodar os testes em cada push

---