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

### Sprint 2 — Site Público e Dashboard Base ✅

**Objetivo:** Página inicial pública com eventos e dashboard interno pós-login.

#### Tarefa 2.1 — Página inicial pública
- [x] 2.1.1 — Criar `HomeView(ListView)` em `events/views.py` com `queryset` filtrando eventos ativos, ordenados por `start_date`, limitados a 8
- [x] 2.1.2 — Criar `templates/public/home.html` extendendo `base.html`
- [x] 2.1.3 — Implementar seção hero com gradiente violet→fuchsia→pink, logo, tagline e dois botões CTA: "Cadastre-se" e "Ver Eventos"
- [x] 2.1.4 — Implementar seção de eventos: grid responsivo com cards de evento
- [x] 2.1.5 — Garantir responsividade: 1 coluna mobile, 2 tablet, 3-4 desktop

#### Tarefa 2.2 — Dashboard base (pós-login)
- [x] 2.2.1 — Criar `DashboardView(LoginRequiredMixin, TemplateView)` que agrega contadores no contexto
- [x] 2.2.2 — Contadores no contexto: total de eventos ativos, total de pedidos do usuário, total de ingressos emitidos, total de ingressos já validados (utilizados)
- [x] 2.2.3 — Criar `templates/dashboard/index.html` extendendo `base_dashboard.html`
- [x] 2.2.4 — Exibir quatro cards de resumo com ícone, número e label para cada contador
- [x] 2.2.5 — Sidebar com links funcionais para todas as seções do dashboard

---

### Sprint 3 — App `events` ✅

**Objetivo:** CRUD de eventos completo com interface consistente.

#### Tarefa 3.1 — Model `Event`
- [x] 3.1.1 — Criar `events/models.py` com model `Event`
- [x] 3.1.2 — Campos: `name` (CharField 200), `description` (TextField), `location` (CharField 200), `start_date` (DateTimeField), `end_date` (DateTimeField), `is_active` (BooleanField, default=False), `organizer` (FK settings.AUTH_USER_MODEL), `created_at` (auto_now_add), `updated_at` (auto_now)
- [x] 3.1.3 — Adicionar `history = HistoricalRecords()`
- [x] 3.1.4 — Implementar `__str__` retornando `self.name`
- [x] 3.1.5 — Implementar property `is_upcoming` retornando `self.start_date > timezone.now()`
- [x] 3.1.6 — Implementar `get_absolute_url()` usando `reverse('events:detail', kwargs={'pk': self.pk})`
- [x] 3.1.7 — Definir `class Meta` com `ordering = ['-start_date']`
- [x] 3.1.8 — Gerar migration com `makemigrations events`
- [x] 3.1.9 — Aplicar migration com `migrate`

#### Tarefa 3.2 — Admin de `Event`
- [x] 3.2.1 — Registrar `Event` em `events/admin.py` com `@admin.register`
- [x] 3.2.2 — Configurar `list_display = ['name', 'organizer', 'start_date', 'is_active']`
- [x] 3.2.3 — Configurar `list_filter = ['is_active', 'start_date']`
- [x] 3.2.4 — Configurar `search_fields = ['name', 'location']`
- [x] 3.2.5 — Configurar `list_editable = ['is_active']`

#### Tarefa 3.3 — Formulário de `Event`
- [x] 3.3.1 — Criar `events/forms.py` com `EventForm(ModelForm)`
- [x] 3.3.2 — Incluir campos: `name`, `description`, `location`, `start_date`, `end_date`
- [x] 3.3.3 — Usar `DateTimeInput` com `type='datetime-local'` para campos de data
- [x] 3.3.4 — Implementar `clean()` validando que `end_date >= start_date`
- [x] 3.3.5 — Aplicar classes TailwindCSS nos widgets via `attrs`

#### Tarefa 3.4 — Views de `Event`
- [x] 3.4.1 — Criar `EventListView(ListView)` pública com `queryset = Event.objects.filter(is_active=True)`
- [x] 3.4.2 — Criar `EventDetailView(DetailView)` pública; passar tipos de ingresso do evento no contexto
- [x] 3.4.3 — Criar `EventCreateView(LoginRequiredMixin, CreateView)` com `form_class = EventForm`
- [x] 3.4.4 — Sobrescrever `form_valid` em `EventCreateView` para setar `form.instance.organizer = self.request.user`
- [x] 3.4.5 — Criar `EventUpdateView(LoginRequiredMixin, UpdateView)` verificando que `request.user == event.organizer`
- [x] 3.4.6 — Criar `EventToggleActiveView(LoginRequiredMixin, View)` recebendo POST e invertendo `is_active`

#### Tarefa 3.5 — Templates de `Event`
- [x] 3.5.1 — Criar `templates/events/event_list.html` com grid de cards e botão para criar evento
- [x] 3.5.2 — Criar `templates/events/event_detail.html` com info do evento, seção de tipos de ingresso e botão de compra
- [x] 3.5.3 — Criar `templates/events/event_form.html` reutilizável para criação e edição

#### Tarefa 3.6 — URLs de `Event`
- [x] 3.6.1 — Criar `events/urls.py` com `app_name = 'events'`
- [x] 3.6.2 — Definir rotas: `''` → lista, `<pk>/` → detalhe, `criar/` → criar, `<pk>/editar/` → editar, `<pk>/toggle/` → toggle ativo
- [x] 3.6.3 — Incluir em `core/urls.py` com prefixo `eventos/`

---

### Sprint 4 — App `tickets` — Parte 1: Tipos de Ingresso ✅

**Objetivo:** Múltiplos tipos de ingresso por evento, com controle de disponibilidade.

#### Tarefa 4.1 — Model `TicketType`
- [x] 4.1.1 — Criar `tickets/models.py` com model `TicketType`
- [x] 4.1.2 — Campos: `event` (FK Event, related_name='ticket_types'), `name` (CharField 100), `description` (TextField, blank=True), `price` (DecimalField, max_digits=10, decimal_places=2), `total_quantity` (PositiveIntegerField), `sold_quantity` (PositiveIntegerField, default=0), `created_at` (auto_now_add), `updated_at` (auto_now)
- [x] 4.1.3 — Adicionar `history = HistoricalRecords()`
- [x] 4.1.4 — Implementar property `available_quantity` retornando `self.total_quantity - self.sold_quantity`
- [x] 4.1.5 — Implementar property `is_available` retornando `self.available_quantity > 0`
- [x] 4.1.6 — Implementar `__str__` retornando `f'{self.event.name} — {self.name}'`
- [x] 4.1.7 — Definir `class Meta` com `ordering = ['price']`
- [x] 4.1.8 — Gerar e aplicar migration

#### Tarefa 4.2 — Admin de `TicketType`
- [x] 4.2.1 — Criar `TicketTypeInline(TabularInline)` em `tickets/admin.py` com `model = TicketType` e `extra = 1`
- [x] 4.2.2 — Adicionar `TicketTypeInline` ao admin de `Event` em `events/admin.py`
- [x] 4.2.3 — Registrar `TicketType` separadamente com `list_display = ['event', 'name', 'price', 'total_quantity', 'sold_quantity']`

#### Tarefa 4.3 — Formulário e Views de `TicketType`
- [x] 4.3.1 — Criar `tickets/forms.py` com `TicketTypeForm(ModelForm)` com campos: `name`, `description`, `price`, `total_quantity`
- [x] 4.3.2 — Aplicar classes TailwindCSS nos widgets
- [x] 4.3.3 — Criar `TicketTypeCreateView(LoginRequiredMixin, CreateView)`
- [x] 4.3.4 — Em `form_valid`: buscar `Event` pelo `event_pk` da URL; validar que `event.organizer == request.user`; setar `form.instance.event = event`
- [x] 4.3.5 — Criar `TicketTypeUpdateView(LoginRequiredMixin, UpdateView)`
- [x] 4.3.6 — Em `TicketTypeForm.clean_total_quantity()`: validar que o novo valor não é menor que `sold_quantity`

#### Tarefa 4.4 — Templates de `TicketType`
- [x] 4.4.1 — Criar `templates/tickets/ticket_type_form.html`
- [x] 4.4.2 — Na `event_detail.html`, listar todos os tipos do evento em cards com nome, descrição, preço e disponibilidade
- [x] 4.4.3 — Exibir badge "Esgotado" e botão desabilitado para tipos com `available_quantity == 0`
- [x] 4.4.4 — Exibir link "Adicionar tipo de ingresso" na página do evento apenas para o organizador autenticado

#### Tarefa 4.5 — URLs de `TicketType`
- [x] 4.5.1 — Criar `tickets/urls.py` com `app_name = 'tickets'`
- [x] 4.5.2 — Definir rotas: `eventos/<int:event_pk>/ingressos/criar/` → criar tipo, `ingressos/<int:pk>/editar/` → editar tipo
