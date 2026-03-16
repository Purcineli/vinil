# Agentes de IA — Projeto Vinil

Agentes especializados para o desenvolvimento do **Vinil**, plataforma Django de gestão e venda de ingressos para eventos.

Cada agente é um arquivo `.md` nesta pasta e pode ser carregado com o comando `/agents` no Claude Code.

---

## Índice

| Agente | Arquivo | Especialidade |
|---|---|---|
| [backend](#backend) | `backend.md` | Django: models, views, URLs, signals, admin |
| [frontend](#frontend) | `frontend.md` | Django Templates + TailwindCSS |
| [qa](#qa) | `qa.md` | Testes via browser com Playwright |
| [payments](#payments) | `payments.md` | Integração Mercado Pago |

---

## Agentes

### backend

**Arquivo:** `backend.md`

Engenheiro backend sênior especializado em Django 6.x. Responsável por toda a camada Python do projeto: models, views (CBV), URLs, forms, signals, admin e migrations.

**Quando usar:**
- Criar ou editar um model (ex: adicionar campo ao `Ticket`, criar novo model)
- Criar ou editar uma view Django (CBV)
- Configurar URLs e namespaces de app
- Escrever signals (`post_save`, `pre_save`)
- Registrar apps e configurar `AppConfig.ready()`
- Escrever lógica de negócio (properties, métodos de model)
- Configurar autenticação, permissões e mixins
- Gerar e executar migrations

**MCP usado:** Context7 — consulta docs atualizados de Django, django-simple-history e qrcode[pil].

---

### frontend

**Arquivo:** `frontend.md`

Engenheiro frontend sênior especializado em Django Template Language e TailwindCSS. Responsável por todos os templates HTML do projeto.

**Quando usar:**
- Criar ou editar páginas HTML (templates de app)
- Criar ou editar componentes reutilizáveis (`templates/components/`)
- Implementar o design system (paleta, tipografia, botões, cards, badges)
- Adicionar interações JavaScript puro (sem frameworks)
- Implementar a tela de validação de portaria com jsQR (câmera + decodificação QR Code)
- Garantir responsividade mobile/desktop
- Criar ou editar os layouts base (`base.html`, `base_dashboard.html`)

**MCP usado:** Context7 — consulta tags/filters do Django Template Language.

---

### qa

**Arquivo:** `qa.md`

Engenheiro de QA que acessa o sistema em execução via browser usando Playwright. Verifica se as funcionalidades implementadas estão corretas e se o design está de acordo com o design system.

**Quando usar:**
- Verificar se uma funcionalidade recém-implementada funciona como esperado
- Validar os critérios de aceite das User Stories do PRD
- Checar se o design visual está de acordo com o design system (cores, tipografia, layout)
- Testar fluxos completos (cadastro → compra → pagamento → ingresso → validação na portaria)
- Verificar responsividade em mobile e desktop
- Detectar erros JavaScript no console
- Gerar relatório de testes antes de encerrar uma sprint

**Pré-condição:** o servidor Django deve estar rodando em `http://127.0.0.1:8000`.

**MCP usado:** Playwright — navegação, cliques, preenchimento de formulários, screenshots, console logs, network requests.

---

### payments

**Arquivo:** `payments.md`

Engenheiro backend especializado em integração com Mercado Pago. Responsável por evoluir o app `payments` do Vinil para suportar checkout real, webhooks e notificações de pagamento.

**Quando usar:**
- Integrar o checkout com Mercado Pago (Checkout Pro)
- Configurar e processar webhooks de notificação de pagamento
- Criar usuários de teste no Mercado Pago para desenvolvimento
- Verificar boas práticas e checklist de qualidade da integração
- Adicionar campos de integração ao model `Payment` (IDs do MP, status detalhado)
- Depurar notificações recebidas no histórico do MP
- Implementar validação de assinatura de webhook

**MCP usado:**
- Mercado Pago — documentação, checklist de qualidade, criação de usuários de teste, webhook, histórico de notificações
- Context7 — Django (signals, views, variáveis de ambiente)

---

## Fluxo de trabalho sugerido

```
1. backend  → Cria/edita models e views
2. frontend → Cria/edita templates correspondentes
3. qa       → Verifica a funcionalidade no browser
4. backend  → Corrige bugs reportados pelo qa
5. frontend → Corrige problemas visuais reportados pelo qa
```

Para a integração de pagamentos:
```
1. payments → Implementa checkout + webhook
2. backend  → Ajusta signal se necessário
3. frontend → Cria templates de sucesso/pendente/falha
4. qa       → Testa fluxo completo de compra
```
