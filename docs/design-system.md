# Design System

Todo o frontend usa **TailwindCSS via CDN** dentro do **Django Template Language**. Componentes são implementados como partials reutilizáveis em `templates/components/`.

## Paleta de cores

| Token | Classe Tailwind | Hex | Uso |
|---|---|---|---|
| Primary | `violet-600` | `#7c3aed` | Botões primários, links ativos |
| Primary Dark | `violet-800` | `#5b21b6` | Hover de primário |
| Secondary | `fuchsia-500` | `#d946ef` | Gradiente, destaques |
| Accent | `pink-400` | `#f472b6` | Badges, tags |
| Background | `slate-50` | `#f8fafc` | Fundo geral das páginas |
| Surface | `white` | `#ffffff` | Cards, formulários |
| Border | `slate-200` | `#e2e8f0` | Bordas suaves |
| Text Primary | `slate-800` | `#1e293b` | Texto principal |
| Text Muted | `slate-400` | `#94a3b8` | Labels, placeholders |
| Success | `emerald-500` | `#10b981` | Ingresso válido, confirmações |
| Warning | `amber-400` | `#fbbf24` | Alertas, status pendente |
| Danger | `rose-500` | `#f43f5e` | Ingresso já usado, erros |

**Gradiente padrão:**
```html
class="bg-gradient-to-br from-violet-600 via-fuchsia-500 to-pink-400"
```

## Tipografia

Fonte base: **Inter** via Google Fonts.

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style> body { font-family: 'Inter', system-ui, sans-serif; } </style>
```

| Elemento | Classes Tailwind |
|---|---|
| Título de página | `text-3xl font-bold text-slate-800 tracking-tight` |
| Subtítulo | `text-xl font-semibold text-slate-700` |
| Corpo | `text-base text-slate-600 leading-relaxed` |
| Label de campo | `text-sm font-medium text-slate-700` |
| Texto muted | `text-sm text-slate-400` |
| Código de ingresso | `font-mono text-2xl font-bold tracking-widest text-violet-700` |
| Link | `text-violet-600 hover:text-violet-800 underline-offset-2 hover:underline` |

## Botões

```html
<!-- Primário -->
<button class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl
               bg-gradient-to-r from-violet-600 to-fuchsia-500
               text-white font-semibold text-sm shadow-md
               hover:from-violet-700 hover:to-fuchsia-600
               transition-all duration-200 active:scale-95">
  Ação Principal
</button>

<!-- Secundário (outline) -->
<button class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl
               border border-violet-300 text-violet-700 font-semibold text-sm
               bg-white hover:bg-violet-50 transition-all duration-200 active:scale-95">
  Ação Secundária
</button>

<!-- Danger -->
<button class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl
               bg-rose-500 text-white font-semibold text-sm
               hover:bg-rose-600 transition-all duration-200 active:scale-95">
  Cancelar
</button>

<!-- Success (validação de portaria) -->
<button class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl
               bg-emerald-500 text-white font-semibold text-sm
               hover:bg-emerald-600 transition-all duration-200 active:scale-95">
  Validar Ingresso
</button>
```

## Inputs e formulários

```html
<div class="flex flex-col gap-1">
  <label class="text-sm font-medium text-slate-700">Nome do campo</label>
  <input type="text"
         class="w-full px-4 py-2.5 rounded-xl border border-slate-200
                bg-white text-slate-800 placeholder-slate-400
                focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent
                transition-all duration-150"
         placeholder="Placeholder...">
  <span class="text-xs text-rose-500">Mensagem de erro.</span>
</div>

<!-- Container de formulário -->
<form class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col gap-5">
  <!-- campos aqui -->
</form>
```

Campo de código de ingresso (portaria):
```html
<input type="text"
       class="w-full px-4 py-2.5 rounded-xl border border-slate-200
              bg-white text-slate-800 font-mono uppercase placeholder-slate-400
              focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent
              transition-all duration-150"
       placeholder="VNL-XXXXX">
```

## Badges de status

```html
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">Confirmado</span>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-700">Pendente</span>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-700">Cancelado</span>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-100 text-violet-700">Utilizado</span>
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">Não utilizado</span>
```

## Feedbacks de validação de portaria

```html
<!-- Válido -->
<div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 flex flex-col gap-2">
  <p class="text-emerald-700 font-bold text-lg">✅ Ingresso válido!</p>
  <p class="text-emerald-600 text-sm">Evento: Nome do Evento · Tipo: VIP</p>
  <p class="text-emerald-600 text-sm">Titular: Nome do Comprador</p>
</div>

<!-- Já utilizado -->
<div class="bg-rose-50 border border-rose-200 rounded-2xl p-6 flex flex-col gap-2">
  <p class="text-rose-700 font-bold text-lg">❌ Ingresso já utilizado</p>
  <p class="text-rose-600 text-sm">Utilizado em: 25/04/2026 às 19:42</p>
</div>

<!-- Código inválido -->
<div class="bg-amber-50 border border-amber-200 rounded-2xl p-6 flex flex-col gap-2">
  <p class="text-amber-700 font-bold text-lg">⚠️ Código inválido</p>
  <p class="text-amber-600 text-sm">Nenhum ingresso encontrado com este código.</p>
</div>
```

## Card de ingresso

```html
<div class="bg-white rounded-2xl shadow-lg border border-slate-100 overflow-hidden max-w-sm mx-auto">
  <div class="bg-gradient-to-r from-violet-600 to-fuchsia-500 p-5 text-white">
    <p class="text-xs font-semibold uppercase tracking-widest opacity-80">🎵 Vinil</p>
    <h2 class="text-xl font-bold mt-1">Nome do Evento</h2>
    <p class="text-sm opacity-90 mt-0.5">São Paulo · 25 de Abril de 2026</p>
  </div>
  <div class="p-5 flex flex-col items-center gap-4">
    <img src="data:image/png;base64,{{ ticket.get_qrcode_base64 }}"
         alt="QR Code"
         class="w-40 h-40 rounded-xl border border-slate-100 shadow-sm">
    <span class="font-mono text-2xl font-bold tracking-widest text-violet-700">
      {{ ticket.code }}
    </span>
    <div class="w-full border-t border-slate-100 pt-4 flex flex-col gap-1 text-sm text-slate-600">
      <div class="flex justify-between">
        <span class="text-slate-400">Tipo</span>
        <span class="font-semibold text-slate-800">{{ ticket.order_item.ticket_type.name }}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-slate-400">Titular</span>
        <span class="font-semibold text-slate-800">{{ ticket.order_item.order.buyer.get_full_name }}</span>
      </div>
    </div>
  </div>
  <div class="{% if ticket.is_used %}bg-rose-50 border-t border-rose-100{% else %}bg-emerald-50 border-t border-emerald-100{% endif %} px-5 py-3 text-center">
    {% if ticket.is_used %}
      <span class="text-rose-700 font-semibold text-sm">❌ Utilizado em {{ ticket.used_at|date:'d/m/Y \às H:i' }}</span>
    {% else %}
      <span class="text-emerald-700 font-semibold text-sm">✅ Válido</span>
    {% endif %}
  </div>
</div>
```

## Navbar pública

```html
<nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100 shadow-sm">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
    <a href="/" class="text-xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-500
                       bg-clip-text text-transparent">🎵 Vinil</a>
    <div class="flex items-center gap-3">
      <a href="/login/" class="text-sm text-slate-600 hover:text-violet-600 font-medium transition-colors">Entrar</a>
      <a href="/cadastro/" class="px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-500
                                  text-white text-sm font-semibold hover:opacity-90 transition-opacity">
        Cadastre-se
      </a>
    </div>
  </div>
</nav>
```

## Sidebar (dashboard interno)

```html
<aside class="w-64 min-h-screen bg-gradient-to-b from-slate-900 to-violet-950
              text-white flex flex-col py-6 px-4 gap-1 shadow-xl">
  <div class="mb-6 px-2">
    <span class="text-xl font-bold bg-gradient-to-r from-violet-300 to-fuchsia-300
                 bg-clip-text text-transparent">🎵 Vinil</span>
  </div>
  <!-- item ativo -->
  <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-xl
                     bg-violet-600/30 text-violet-200 font-medium text-sm">
    📊 Dashboard
  </a>
  <!-- item padrão -->
  <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-xl
                     text-slate-400 hover:text-white hover:bg-white/10
                     font-medium text-sm transition-all">
    🎪 Meus Eventos
  </a>
</aside>
```

## Layout base (`base.html`)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Vinil{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style> body { font-family: 'Inter', system-ui, sans-serif; } </style>
  {% block extra_head %}{% endblock %}
</head>
<body class="bg-slate-50 text-slate-800 antialiased">
  {% include 'components/navbar.html' %}
  <main class="min-h-screen">
    {% include 'components/messages.html' %}
    {% block content %}{% endblock %}
  </main>
  {% include 'components/footer.html' %}
  {% block extra_scripts %}{% endblock %}
</body>
</html>
```
