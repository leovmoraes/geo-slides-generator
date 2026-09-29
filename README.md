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
| **Slide 1 (Capa)** | Nome do Lead + Data de Envio | Conteúdo dinâmico mantendo Poppins Bold 36pt e formato institucional |
| **Slides 2 a 5** | Preservados na sequência oficial | Agenda, Responsáveis pelo Projeto, Sumário Executivo e Divisor de Solução |
| **Slide 6 em diante** | Início do conteúdo dinâmico | Cards estruturados gerados a partir do briefing do usuário |
| **Último Slide** | Consultor & E-mail Corporativo | Personalizado para o apresentador (`nome.sobrenome@geoambiente.com.br`) |
| **Fundo dos Slides** | `#F5F7FA` ou `#FFFFFF` | **Fundo escuro estritamente proibido** |
| **Laranja Geoambiente** | `#F58120` | Pílulas/Tags de numeração, ênfases e destaques |
| **Azul Google Cloud** | `#1A73E8` | Títulos dos cartões de conteúdo e ícones |
| **Texto Primário** | `#202124` | Título principal e cabeçalhos |
| **Texto Secundário** | `#5F6368` | Corpo dos tópicos e descrições |
| **Tipografia** | **Poppins** (Títulos) / **Inter** (Corpo) | Padronização em todas as caixas de texto |
| **Cards Pattern** | 2 a 4 cartões brancos com cantos arredondados | Estruturação visual modular de todos os slides de conteúdo |

---

## 📋 Pré-Requisitos e Fluxo de Geração

Antes de criar a apresentação, o agente valida com o usuário três pré-requisitos essenciais:
1. **Nome do Lead (Cliente / Empresa):** Obrigatório. Se não informado no briefing inicial, o agente solicita antes de chamar a ferramenta.
2. **Consultor / Apresentador Responsável:** Obrigatório. O agente permite informar o nome de outro colega (executivo de contas) ou confirmar se a proposta será assinada pelo próprio usuário (resolvido automaticamente via Google Workspace OAuth). O e-mail corporativo é formatado automaticamente no padrão `nome.sobrenome@geoambiente.com.br`.
3. **Data de Envio:** Opcional. Se omitida, assume a data atual.

---

## 💰 Estimativa de Investimento por Slide e Apresentação (Gemini 3.7 Flash)

O custo de geração é baseado na tabela de consumo de tokens da API **Gemini 3.7 Flash Standard** no Vertex AI:

### 1. Tabela de Precificação do Modelo (Google Cloud)
* **Input (Tokens de Entrada):** `\$0.75` por 1 milhão de tokens
* **Output (Tokens de Saída):** `\$3.75` por 1 milhão de tokens
* ⚠️ **Vigência:** Tarifa promocional introdutória válida até **31 de dezembro de 2026** *(a partir de 1º de janeiro de 2027, os preços dobram para `\$1.50` input / `\$7.50` output por 1 milhão de tokens)*.

### 2. Média de Consumo de Tokens por Execução
* **Entrada (Input):** ~1.000 a 1.500 tokens (Briefing do usuário, contexto do lead, persona e validação do schema Pydantic).
* **Saída (Output):** ~1.500 a 2.500 tokens (Estruturação completa em JSON de 4 a 6 slides de conteúdo com cards, tópicos e pilares).

### 3. Custo por Apresentação e Escala de Produção

| Período | Custo por Apresentação (~18 slides) | Custo por Slide Dinâmico | **Estimativa para 1.000 Slides Dinâmicos (~200 decks)** | Estimativa para 100 Apresentações Completas (~1.800 slides) |
| :--- | :--- | :--- | :--- | :--- |
| **Até 31/12/2026** *(Tarifa Vigente)* | **~\$0.0084** | **~\$0.0017** | **~\$1.70** | **~\$0.84** |
| **A partir de 01/01/2027** *(Tabela Regular)* | **~\$0.0168** | **~\$0.0034** | **~\$3.40** | **~\$1.68** |

> [!TIP]
> **APIs do Google Workspace Gratuitas:** Todas as chamadas de clonagem, estruturação e compartilhamento via Google Slides API e Google Drive API não possuem custo por chamada (inclusas nas cotas do Google Workspace). O container no Agent Runtime escala para zero quando inativo, sendo tarifado apenas pelos segundos de execução do request (~15-20s).

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

### 🔐 Guia Detalhado de Configuração do OAuth no Gemini Enterprise

Para que o agente clone a matriz oficial diretamente para o Google Drive do usuário final sem depender de contas de serviço externas (atendendo às regras de compliance corporativo), a integração exige uma configuração precisa de **OAuth 2.0**.

#### 1. Criação da Credencial no Google Cloud Console:
* Acesse **APIs e Serviços** > **Credenciais** no projeto GCP (`geo-gemini-enterprise`).
* Clique em **Criar Credenciais** > **ID do cliente OAuth**.
* ⚠️ **OBRIGATÓRIO:** Selecione o tipo de aplicativo **Aplicativo da Web (Web Application)**.  
  *(Credenciais do tipo "Desktop Application" **não funcionam** no Gemini Enterprise e disparam erro 400 `invalid_request / GeneralOAuthFlow`).*
* No campo **URIs de redirecionamento autorizados**, adicione a URL de callback fornecida pelo Gemini Enterprise durante a criação da autorização.

#### 2. Campos de Configuração no Gemini Enterprise:
Na interface do Gemini Enterprise (ao vincular o Custom Agent / Reasoning Engine):

| Campo | Valor Exato / Homologado |
| :--- | :--- |
| **Nome da Autorização** | `slides-agent-auth` |
| **Grant Type** | `Authorization Code` |
| **Client ID** | ID do cliente gerado no GCP (`...apps.googleusercontent.com`) |
| **Client Secret** | Chave secreta correspondente ao cliente Web |
| **Token URI** | `https://oauth2.googleapis.com/token` |
| **Authorization URI** | *(Ver formato completo abaixo com query params obrigatórios)* |

##### 📌 URL Completa da Authorization URI:
O servidor de autorização do Google e a validação do Gemini Enterprise exigem explicitamente os parâmetros de offline access, consentimento e escopos embutidos na URL:

```text
https://accounts.google.com/o/oauth2/v2/auth?response_type=code&access_type=offline&prompt=consent&scope=https://www.googleapis.com/auth/presentations+https://www.googleapis.com/auth/drive+openid+email+profile
```

#### 3. Escopos Solicitados (Scopes):
* `https://www.googleapis.com/auth/presentations` (Criação, leitura e edição de slides)
* `https://www.googleapis.com/auth/drive` (Clonagem e compartilhamento do arquivo matriz)
* `openid`
* `email`
* `profile`

#### 4. Erros Comuns e Como Foram Resolvidos:
* **Erro:** `The authorization URI must contain 'access_type=offline'`  
  👉 **Solução:** Adicionar `&access_type=offline` na Authorization URI para permitir refresh tokens seguros.
* **Erro:** `Required parameter is missing: response_type (Error 400: invalid_request)`  
  👉 **Solução:** Incluir explicitamente `?response_type=code` na URL base de autorização.
* **Erro:** `Missing required parameter: scope`  
  👉 **Solução:** Encadear todos os escopos diretamente na query string da Authorization URI concatenados com `+`.
* **Erro:** `404: File not found` na clonagem  
  👉 **Solução:** Garantir que o token repassado pelo Gemini Enterprise no payload JSON seja capturado e injetado no `ContextVar` do runtime, chamando a API do Drive com a identidade do usuário e nunca como a Service Account.

---

## 🎨 Como Atualizar o Template Matriz da Apresentação (Novo Padrão Visual do Marketing)

Quando a equipe de Marketing atualizar a identidade visual ou homologar uma nova apresentação matriz, você pode trocar o template de **duas formas**: sem alterar código (via variável de ambiente) ou atualizando o padrão no repositório.

### 1. Onde Obter o ID da Nova Apresentação:
Na URL da apresentação aberta no Google Slides pelo Marketing:
```text
https://docs.google.com/presentation/d/19F33ff11h0p2NF6GEcYAPj3se0eGzWKwzir3szAZpiI/edit
                                       ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
                                                 TEMPLATE_PRESENTATION_ID
```
Copie a sequência alfanumérica entre `/d/` e `/edit`.

### 2. Requisitos de Acesso da Nova Matriz:
* O arquivo deve estar salvo no Google Drive da organização Geoambiente (ex: em um Drive Compartilhado ou compartilhado com o domínio `@geoambiente.com.br` com permissão de Leitor/Comentador).
* **Não é necessário** compartilhar com contas de serviço externas, pois a clonagem é feita diretamente com o token do usuário final autenticado no Gemini Enterprise.

### 3. Atualizando em Produção no Vertex AI Reasoning Engine:

#### Opção A: Atualização Imediata via `--update-env-vars` (Recomendado)
Você pode atualizar a variável de ambiente diretamente no container em nuvem sem alterar código:

```bash
agents-cli deploy --update-only \
  --service-name "Gerador de Apresentações Geoambiente" \
  --project geo-gemini-enterprise \
  --region us-central1 \
  --no-confirm-project \
  --update-env-vars TEMPLATE_PRESENTATION_ID="NOVO_ID_AQUI"
```

#### Opção B: Atualização no Código (`src/config.py`)
Para manter a nova matriz como o valor padrão fixo no repositório:
1. Altere o ID padrão em [src/config.py](file:///home/leovmoraes/projetos/slides-agent/src/config.py#L18):
   ```python
   TEMPLATE_PRESENTATION_ID = os.getenv(
       "TEMPLATE_PRESENTATION_ID", 
       "NOVO_ID_AQUI"
   )
   ```
2. Atualize o `.env` local e `.env.example`.
3. Faça o commit e reexecute o deploy:
   ```bash
   agents-cli deploy --update-only --service-name "Gerador de Apresentações Geoambiente" --project geo-gemini-enterprise --region us-central1 --no-confirm-project
   ```

### 4. Atualizando em Ambiente Local:
Basta alterar a variável no seu arquivo `.env`:
```bash
TEMPLATE_PRESENTATION_ID="NOVO_ID_AQUI"
```

---

## 🤖 Como Atualizar a Versão do Modelo Gemini (ex: Gemini 4.0, 4.5 Flash)

Os modelos de IA do ecossistema Google Cloud evoluem periodicamente. O agente foi arquitetado para permitir a troca do modelo (ex: de `gemini-3.7-flash` para `gemini-4.0-flash` ou `gemini-4.5-flash`) de forma desacoplada através da variável de ambiente `GEMINI_MODEL`.

### 1. Atualização Imediata em Produção (Sem mexer em código):
Execute o deploy com o parâmetro `--update-env-vars`:

```bash
agents-cli deploy --update-only \
  --service-name "Gerador de Apresentações Geoambiente" \
  --project geo-gemini-enterprise \
  --region us-central1 \
  --no-confirm-project \
  --update-env-vars GEMINI_MODEL="gemini-4.0-flash"
```
*(O Vertex AI Agent Runtime atualiza a variável em segundos e passa a invocar o novo modelo tanto no Agente Conversacional quanto no Planejador de Conteúdo).*

### 2. Atualização Definitiva no Repositório:
1. Altere o valor padrão em `src/config.py`:
   ```python
   DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-4.0-flash")
   ```
2. Atualize o arquivo `.env` e `.env.example`:
   ```bash
   GEMINI_MODEL=gemini-4.0-flash
   ```
3. Execute a suíte de testes locais para homologação:
   ```bash
   .venv/bin/pytest tests/unit tests/test_schema.py tests/test_workflow.py
   ```
4. Faça o commit e publique o novo contêiner:
   ```bash
   agents-cli deploy --update-only --service-name "Gerador de Apresentações Geoambiente" --project geo-gemini-enterprise --region us-central1 --no-confirm-project
   ```

> [!NOTE]
> **Compatibilidade de Região:** Lembre-se que alguns modelos novos são lançados inicialmente com endpoint global (`GOOGLE_CLOUD_LOCATION=global`) ou regional (`us-central1`). O projeto já está configurado com fallback automático de localização.

---

## 🎨 Ícone Oficial no Gemini Enterprise

O agente possui o logotipo oficial da Geoambiente configurado diretamente no registro do **Discovery Engine**:
* **Arquivo Fonte:** [`logo.png`](logo.png) na raiz do projeto (PNG 300x300 institucional).
* **Backup no Cloud Storage:** `gs://geo-gemini-artifacts-presales/logo.png`.
* O ícone é renderizado nativamente no card do agente e nas conversas do Gemini Enterprise em substituição à inicial genérica.