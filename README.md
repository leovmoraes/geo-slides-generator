# Geoambiente & Google Cloud - Slide Master Generator (ADK Multi-Agent Workflow)

Solução corporativa oficial baseada em **Workflow Multi-Agente com Google Agent Development Kit (ADK / Python)** e **Vertex AI Agent Runtime (Reasoning Engine)**, utilizando o modelo **Gemini 3.7 Flash**. Especialista na criação e formatação automatizada de apresentações corporativas no Google Slides diretamente pelo **Gemini Enterprise**, seguindo rigorosamente a identidade visual da **Geoambiente** e a apresentação matriz homologada.

---

## 🏛️ Arquitetura da Solução

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   GEMINI ENTERPRISE                                    │
│                    (Interface de Usuário Final / Agent Space)                          │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP POST (Stream / Eventos)
                                            │ + Token OAuth Delegado (slides-agent-auth)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                 VERTEX AI AGENT RUNTIME (REASONING ENGINE ADK)                         │
│                                                                                        │
│  ┌────────────────────────────────────────┐    ┌────────────────────────────────────┐  │
│  │ 🧠 AGENTE 1: CONTENT & DESIGN PLANNER  │    │ 🔨 AGENTE 2: SLIDE MASTER BUILDER  │  │
│  │ (LLM: Gemini 3.7 Flash)                │    │ (Motor Determinístico de Slides)   │  │
│  │                                        │    │                                    │  │
│  │ • Briefing livre do usuário final      │───▶│ • Clona a matriz oficial homologada│  │
│  │ • Cria narrativa, títulos e pilares    │    │   (ID: 19F33ff11h0p2NF6...)        │  │
│  │ • Estrutura conteúdo em cartões        │    │ • Autentica via OAuth do usuário   │  │
│  │ • Gera JSON validado (Pydantic Schema) │    │ • Aplica Paleta (#F58120, #1A73E8) │  │
│  └────────────────────────────────────────┘    │ • Insere Cards, Sumário e Rodapé   │  │
│                                                │ • Salva no "Meu Drive" do usuário  │  │
│                                                └─────────────────┬──────────────────┘  │
│                                                                  │                     │
│                                                                  ▼                     │
│                                                   📊 Google Slides Editável no Drive   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Identidade Visual e Regras Inquebráveis

| Elemento | Especificação | Aplicação |
| :--- | :--- | :--- |
| **Modelo LLM Padrão** | **Gemini 3.7 Flash** (`gemini-3.7-flash`) | Raciocínio, estruturação e planejamento dos slides |
| **Apresentação Matriz** | `19F33ff11h0p2NF6GEcYAPj3se0eGzWKwzir3szAZpiI` | Template oficial homologado Geoambiente clonado a cada execução |
| **Destino do Arquivo** | `Meu Drive (root)` do Usuário Final | Criado com a credencial OAuth do próprio usuário do Gemini Enterprise |
| **Fundo dos Slides** | `#F5F7FA` ou `#FFFFFF` | **Fundo escuro estritamente proibido** |
| **Laranja Geoambiente** | `#F58120` | Pílulas/Tags de numeração, ênfases e destaques |
| **Azul Google Cloud** | `#1A73E8` | Títulos dos cartões de conteúdo e ícones |
| **Texto Primário** | `#202124` | Título principal e cabeçalhos |
| **Texto Secundário** | `#5F6368` | Corpo dos tópicos e descrições |
| **Tipografia** | **Poppins** (Títulos) / **Inter** (Corpo) | Padronização em todas as caixas de texto |
| **Cards Pattern** | 2 a 4 cartões brancos com cantos arredondados | Estruturação visual modular de todos os slides de conteúdo |

---

## 📁 Estrutura do Projeto

```
slides-agent/
├── app/                           # Entrypoint Oficial ADK / Reasoning Engine
│   ├── agent.py                   # Definição do root_agent ADK e tool de slides
│   ├── fast_api_app.py            # Servidor FastAPI com endpoints REST e healthcheck
│   └── app_utils/
│       ├── reasoning_engine_adapter.py # Adaptador de rotas e extração do OAuth do Gemini Enterprise
│       ├── services.py            # Serviços de sessão e telemetria
│       └── a2a.py                 # Protocolo Agent-to-Agent (A2A)
├── src/
│   ├── config.py                  # Tokens de Design System e Modelo
│   ├── models/
│   │   └── presentation_spec.py   # Contrato Pydantic (CardSpec, SlideSpec, PresentationSpec)
│   ├── agents/
│   │   ├── planner_agent.py       # Agente 1: Content & Design Planner (Gemini 3.7 Flash)
│   │   └── builder_agent.py       # Agente 2: Slide Master Builder (Automação de Slides)
│   ├── services/
│   │   ├── auth_service.py        # Autenticação (OAuth delegado do usuário, ADC e token local)
│   │   ├── drive_service.py       # Operações no Google Drive (Clonagem e compartilhamento)
│   │   └── slides_service.py      # Motor de batchUpdate para o Google Slides API
│   ├── workflow/
│   │   └── orchestrator.py        # Orquestrador do Workflow Sequencial Multi-Agente
│   └── main.py                    # Entrypoint CLI interativo para testes locais
├── tests/
│   ├── unit/                      # Testes unitários (auth extraction, builder agent, etc.)
│   ├── integration/               # Testes de integração e server E2E
│   └── eval/                      # Datasets e avaliações de qualidade do agente
├── pyproject.toml                 # Gerenciamento de dependências e empacotamento com uv
├── Dockerfile                     # Imagem de container para deploy no Vertex AI Agent Runtime
├── deploy_agent.py                # Script de deploy programático
└── README.md                      # Documentação oficial
```

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos:
* Python 3.12+ ou 3.14+ com [`uv`](https://docs.astral.sh/uv/) instalado.

### 2. Instalação:
```bash
uv sync
```

### 3. Executar Suíte de Testes:
```bash
.venv/bin/pytest tests/unit tests/test_schema.py tests/test_workflow.py
```

### 4. Testar CLI Local:
```bash
.venv/bin/python -m src.main "Gerar proposta comercial de Modernização de Dados e IA Generativa para o cliente Corporativo"
```

---

## ☁️ Deploy no Vertex AI Agent Runtime

O deploy em nuvem para integração com o Gemini Enterprise é gerenciado via `google-agents-cli`:

```bash
# Atualização in-place do container existente
agents-cli deploy --update-only --service-name "Gerador de Apresentações Geoambiente" --project geo-gemini-enterprise --region us-central1 --no-confirm-project
```

### 🔐 Autenticação no Gemini Enterprise:
Para que o agente crie apresentações diretamente no Drive do usuário sem violar compliance corporativo:
* O Gemini Enterprise solicita autorização via fluxo OAuth Web (`slides-agent-auth`).
* Escopos requeridos: `https://www.googleapis.com/auth/presentations`, `https://www.googleapis.com/auth/drive`, `openid`, `email`.
* O token é repassado automaticamente pelo Gemini Enterprise a cada invocação e consumido pelo `DriveService` e `SlidesService`.