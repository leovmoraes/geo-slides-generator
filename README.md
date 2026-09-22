# Geoambiente & Google Cloud - Slide Master Generator (ADK Multi-Agent Workflow)

Solução corporativa oficial baseada em **Workflow Multi-Agente com Google ADK / Python**, utilizando o modelo **Gemini 3.7 Flash**, especialista na criação e formatação automatizada de apresentações corporativas no Google Slides, seguindo rigorosamente a identidade visual da **Geoambiente** e a apresentação matriz homologada.

---

## 🏛️ Arquitetura do Workflow Multi-Agente

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MULTI-AGENT WORKFLOW (ADK)                               │
│                                                                                        │
│  ┌────────────────────────────────────────┐    ┌────────────────────────────────────┐  │
│  │ 🧠 AGENTE 1: CONTENT & DESIGN PLANNER  │    │ 🔨 AGENTE 2: SLIDE MASTER BUILDER  │  │
│  │ (LLM: Gemini 3.7 Flash)                │    │ (Motor Determinístico de Slides)   │  │
│  │                                        │    │                                    │  │
│  │ • Recebe o briefing livre do usuário   │───▶│ • Clona a matriz oficial           │  │
│  │ • Cria a narrativa e títulos           │    │   (ID: 19F33ff11h0p2NF6...)        │  │
│  │ • Estrutura os slides em cartões       │    │ • Aplica Capa, Boas-vindas e Fim   │  │
│  │ • Gera JSON validado (Pydantic Schema) │    │ • Insere Cartões (#FFFFFF, #F58120)│  │
│  └────────────────────────────────────────┘    │ • Retorna URL do Google Slides     │  │
│                                                └─────────────────┬──────────────────┘  │
│                                                                  │                     │
│                                                                  ▼                     │
│                                                   📊 Google Slides Pronto no Drive     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Identidade Visual e Regras Inquebráveis

| Elemento | Especificação | Aplicação |
| :--- | :--- | :--- |
| **Modelo LLM Padrão** | **Gemini 3.7 Flash** (`gemini-3.7-flash`) | Geração de conteúdo inteligente e estruturação |
| **Apresentação Base** | `19F33ff11h0p2NF6GEcYAPj3se0eGzWKwzir3szAZpiI` | Template matrix oficial clonado para cada apresentação |
| **Fundo dos Slides** | `#F5F7FA` ou `#FFFFFF` | **Fundo escuro estritamente proibido** |
| **Laranja Geoambiente** | `#F58120` | Pílulas/Tags de numeração, ênfases e destaques |
| **Azul Google Cloud** | `#1A73E8` | Títulos dos cartões de conteúdo e ícones |
| **Texto Primário** | `#202124` | Título principal e cabeçalhos |
| **Texto Secundário** | `#5F6368` | Corpo dos tópicos e descrições |
| **Tipografia** | **Poppins** (Títulos) / **Inter** (Corpo) | Padronização em todas as caixas de texto |
| **Cards Pattern** | 2 a 4 cartões brancos com cantos arredondados | Estruturação visual de todos os slides de conteúdo |

---

## 📁 Estrutura do Projeto

```
slides-agent/
├── src/
│   ├── config.py                  # Tokens de Design System e Modelo (gemini-3.7-flash)
│   ├── models/
│   │   ├── __init__.py
│   │   └── presentation_spec.py   # Contrato Pydantic (CardSpec, SlideSpec, PresentationSpec)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner_agent.py       # Agente 1: Content & Design Planner (Gemini 3.7 Flash)
│   │   └── builder_agent.py       # Agente 2: Slide Master Builder (Automação de Slides)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Autenticação Google Workspace (ADC / Service Account)
│   │   ├── drive_service.py       # Operações no Google Drive (Clonagem para root)
│   │   └── slides_service.py      # Motor de batchUpdate para o Google Slides API
│   ├── workflow/
│   │   ├── __init__.py
│   │   └── orchestrator.py        # Orquestrador do Workflow Sequencial
│   └── main.py                    # Entrypoint CLI interativo
├── tests/
│   ├── __init__.py
│   ├── test_schema.py             # Testes de validação dos schemas Pydantic
│   └── test_workflow.py           # Testes unitários do orquestrador
├── requirements.txt               # Dependências Python
├── .env.example                   # Configurações de ambiente
└── README.md                      # Documentação
```

---

## 🚀 Como Executar

### 1. Instalar Dependências:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Rodar a Suíte de Testes:
```bash
pytest -v
```

### 3. Gerar Apresentação via Linha de Comando:
```bash
python -m src.main "Gerar proposta comercial de Modernização de Dados e IA Generativa para a AgroTech Brasil com 3 pilares"
```