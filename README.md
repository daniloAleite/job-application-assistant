# Tutorial Completo: Assistente de Candidatura de Emprego com LangChain, LangGraph e FastAPI

Este tutorial orienta, passo a passo, a construção de uma Prova de Conceito (POC) chamada **"Job Application Assistant"**, utilizando uma arquitetura sólida com LangChain, LangGraph e FastAPI.

## Sumário
1. [Visão Geral do Projeto](#visao)
2. [Estrutura de Diretórios Profissional](#estrutura)
3. [Configuração do Ambiente no Windows 11 + VS Code](#ambiente)
4. [Gerenciamento de Dependências e Variáveis de Ambiente](#dependencias)
5. [Modelagem de Dados com Pydantic](#modelagem)
6. [Configuração e Organização FastAPI](#fastapi)
7. [Implementando o Serviço com LangGraph (Workflow)](#langgraph)
8. [Conexão entre FastAPI e Workflow](#conexao)
9. [Executando e Testando a Aplicação](#executando)
10. [README.md Profissional](#readme)

***

<a name="visao"></a>
## 1. Visão Geral do Projeto

**O quê:**
Um assistente baseado em linguagem natural capaz de analisar um currículo e uma descrição de vaga para gerar feedback personalizado, incluindo sugestões para a carta de apresentação e recomendações de melhorias no currículo.

**Por quê:**
Muitos candidatos não sabem alinhar seus currículos e cartas de apresentação às exigências das vagas. Vamos demonstrar como orquestrar agentes com LangChain/LangGraph para gerar sugestões automáticas e personalizadas. O foco é em arquitetura escalável, modular e fácil de manter.

***
<a name="estrutura"></a>
## 2. Estrutura de Diretórios Profissional

**O quê:**
Estrutura separando responsabilidades de API, core/config, serviços, modelos e organização main, alinhada a aplicações empresariais em Python.

```plaintext
job-application-assistant/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── application.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── agent_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── main.py
├── venv/
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

**Por quê:**
Arquiteturas limpas e modulares facilitam manutenção e testabilidade. Cada camada tem responsabilidade única:
- **api/**: definição de endpoints.
- **core/**: configurações globais.
- **services/**: regras de negócio (LangGraph workflow).
- **models/**: schemas de dados.

***
<a name="ambiente"></a>
## 3. Configuração do Ambiente no Windows 11 + VS Code

**O quê:**
Preparar o ambiente e ferramentas para desenvolvimento.

**Como:**
1. **Abra o VS Code.**
2. **Clone/crie o diretório do projeto:**
   ```sh
   mkdir job-application-assistant && cd job-application-assistant
   ```
3. **Crie ambiente virtual:**
   ```sh
   python -m venv venv
   ```
   > Motivo: Isola as dependências do projeto.

4. **Ative o venv no Windows:**
   ```sh
   .\venv\Scripts\activate
   ```
   Se usar Git Bash:
   ```sh
   source venv/Scripts/activate
   ```
5. **Abra a pasta no VS Code:**
   Menu > File > Open Folder > selecione `job-application-assistant`.

6. **Assegure que o VS Code usará o interpretador do venv.** No VS Code: Ctrl+Shift+P > Python: Select Interpreter > escolha o da pasta `venv`.

***
<a name="dependencias"></a>
## 4. Gerenciamento de Dependências e Variáveis de Ambiente

**O quê:**
Instale as bibliotecas essenciais no `requirements.txt`:
- fastapi
- uvicorn
- pydantic
- langchain
- langgraph
- openai
- python-dotenv

**Como:**
1. Crie um arquivo `requirements.txt` no root e adicione:
   ```txt
   fastapi
   uvicorn
   pydantic
   langchain
   langgraph
   openai
   python-dotenv
   ```
2. Instale:
   ```sh
   pip install -r requirements.txt
   ```
3. Monte o arquivo `.env.example` para as chaves:
   ```env
   OPENAI_API_KEY=your-openai-key-here
   ```
4. Para uso real, copie `.env.example` para `.env` e preencha com sua chave.

**Por quê:**
Gerenciar chaves de API e manter dependências seguras e explícitas são partes fundamentais de aplicações de produção.

***
<a name="modelagem"></a>
## 5. Modelagem de Dados com Pydantic

**O quê:**
Defina schemas de entrada e saída para as rotas API.

**Como:**
Crie `src/models/schemas.py`:
```python
from pydantic import BaseModel, Field

class ApplicationRequest(BaseModel):
    resume: str = Field(..., description="User resume (plain text)")
    job_description: str = Field(..., description="Job description (plain text)")

class FeedbackResponse(BaseModel):
    feedback: str
    cover_letter_suggestion: str
    resume_improvements: str
```

**Por quê:**
Usar Pydantic garante validação, documentação automática (Swagger), e tipos fortes, tornando a aplicação segura para entrada/saída.

***
<a name="fastapi"></a>
## 6. Configuração e Organização FastAPI

### A. Configuração Global

**src/core/config.py:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY")

settings = Settings()
```
**Por quê:** Centralizar configs facilita troca de ambiente ou extensão futura.

***
### B. Dependências de Injeção

**src/api/dependencies.py:**
```python
from src.core.config import settings

def get_settings():
    return settings
```
**Por quê:** Permite centralizar e alterar dependências facilmente para testes/mocks.

***
### C. Endpoints FastAPI

**src/api/endpoints/application.py:**
```python
from fastapi import APIRouter, Depends, HTTPException
from src.models.schemas import ApplicationRequest, FeedbackResponse
from src.api.dependencies import get_settings
from src.services.agent_service import process_application

router = APIRouter()

@router.post("/analyze", response_model=FeedbackResponse)
def analyze_application(
    request: ApplicationRequest,
    settings = Depends(get_settings)
):
    try:
        response = process_application(request.resume, request.job_description, settings)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**src/api/endpoints/__init__.py:**
```python
# Can be empty, just to mark as package
```

**src/api/__init__.py:**
```python
# Can be empty
```

***
### D. Arquivo Principal

**src/main.py:**
```python
from fastapi import FastAPI
from src.api.endpoints import application

app = FastAPI(title="Job Application Assistant API")
app.include_router(application.router, prefix="/application", tags=["Application Analysis"])
```

**Por quê:** Cada camada está bem separada. O endpoint aceita uma requisição, injeta dependências, chama o serviço e retorna a resposta.

***
<a name="langgraph"></a>
## 7. Implementando o Serviço LangGraph (Workflow)

**O quê:**
Workflow multipassos usando LangGraph para:
1. Extrair requisitos da vaga
2. Extrair habilidades do currículo
3. Gerar o feedback final comparando os dois

**Como:**

**src/services/agent_service.py:**
```python
from langchain_openai import OpenAI
from langgraph.graph import StateGraph, State, Node
from src.models.schemas import FeedbackResponse

# Definição de estado (pode ser um dict ou classe, aqui simplificado)
class ApplicationState(State):
    resume: str
    job_description: str
    job_requirements: str = ""
    resume_skills: str = ""
    feedback: str = ""
    cover_letter_suggestion: str = ""
    resume_improvements: str = ""

# Cada nó do workflow:
def analyze_job_description_node(state: ApplicationState, llm):
    prompt = (
        f"""
        Given the following job description, extract a concise list (bullet points) of the main requirements and skills requested.\n
        Job Description:\n{state.job_description}
        """
    )
    response = llm.invoke(prompt)
    state.job_requirements = response
    return state


def analyze_resume_node(state: ApplicationState, llm):
    prompt = (
        f"""
        Given the following resume, extract a concise list (bullet points) of the candidate's main skills and experiences.\n
        Resume:\n{state.resume}
        """
    )
    response = llm.invoke(prompt)
    state.resume_skills = response
    return state


def generate_feedback_node(state: ApplicationState, llm):
    prompt = (
        f"""
        Compare the job requirements below with the resume skills. Write a personalized feedback for the candidate, suggest a custom cover letter draft, and point out specific improvements for the resume.\n
        Job Requirements:\n{state.job_requirements}\n
        Resume Skills:\n{state.resume_skills}
        """
    )
    response = llm.invoke(prompt)
    # LLM response must be structured, you can use prompts to delimit sections.
    # Here, we suppose the LLM outputs markdown with three sections.
    try:
        feedback, cover_letter, improvements = response.split("---")
    except Exception:
        # fallback: everything as feedback
        feedback, cover_letter, improvements = response, "", ""
    state.feedback = feedback.strip()
    state.cover_letter_suggestion = cover_letter.strip()
    state.resume_improvements = improvements.strip()
    return state

# Construção do graph

def process_application(resume, job_description, settings):
    llm = OpenAI(api_key=settings.openai_api_key)  # Configure temperature/drafts se quiser
    state = ApplicationState(resume=resume, job_description=job_description)
    graph = StateGraph()
    graph.add_node(Node("analyze_job_description", lambda s: analyze_job_description_node(s, llm)))
    graph.add_node(Node("analyze_resume", lambda s: analyze_resume_node(s, llm)))
    graph.add_node(Node("generate_feedback", lambda s: generate_feedback_node(s, llm)))
    graph.add_edge("analyze_job_description", "analyze_resume")
    graph.add_edge("analyze_resume", "generate_feedback")
    graph.set_start("analyze_job_description")
    graph.set_end("generate_feedback")

    result_state = graph.run(state)
    # Construa o schema Pydantic da resposta
    return FeedbackResponse(
        feedback=result_state.feedback,
        cover_letter_suggestion=result_state.cover_letter_suggestion,
        resume_improvements=result_state.resume_improvements,
    )
```

**Por quê:**
- **Workflow step-by-step** permite depuração, manutenção e melhora de cada estágio separadamente.
- **Gerenciamento de estado**: a cada nó, o estado é atualizado com os dados extraídos/analisados, garantindo passagem de contexto clara e transparente ao longo da execução.
- **Separação dos prompts**: facilita tuning e ajustes para o LLM.

***
<a name="conexao"></a>
## 8. Conexão FastAPI ↔ Workflow

**O quê:**
Endpoint FastAPI apenas orquestra entrada/saída e delega ao serviço o que for de processamento.

**Como:**
- O endpoint `/application/analyze` recebe `resume` e `job_description`, valida, injeta settings, e chama `process_application`.
- Toda lógica, prompts e manipulação do LLM se concentram em `agent_service.py`.

**Por quê:**
Esse design facilita testes unitários, evolução do agente e rastreio de eventuais incidentes.

***
<a name="executando"></a>
## 9. Executando e Testando a Aplicação

**Como executar:**
1. Garanta que você está com o venv ativado e dependências instaladas.
2. Assegure que seu `.env` está preenchido com sua chave OpenAI.
3. Execute a API:
   ```sh
   uvicorn src.main:app --reload
   ```
4. Acesse a documentação interativa Swagger UI:
   http://localhost:8000/docs
5. Para testar por linha de comando, exemplo com `curl`:
   ```sh
   curl -X POST "http://localhost:8000/application/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "resume": "John Doe, B.Sc. Computer Science, Python, REST APIs, 5 years experience in SaaS products...",
       "job_description": "Seeking Python developer with strong background in API design, OpenAI knowledge, experience with cloud deployments..."
     }'
   ```

**Por quê:**
Proporciona desenvolvimento rápido, feedback imediato e fácil integração futura.

***
<a name="readme"></a>
## 10. README.md Profissional

Veja a seguir um exemplo a ser colocado no arquivo `README.md`:

***

# Job Application Assistant

**Job Application Assistant** é uma POC que utiliza IA Generativa via LangChain (LangGraph) e FastAPI para analisar currículos e vagas de emprego, gerando feedback personalizado, carta de apresentação sugerida e recomendações de melhoria.

## 🚀 Tecnologias Utilizadas
- Python 3.10+
- FastAPI
- LangChain / LangGraph
- OpenAI API
- Pydantic
- Uvicorn

## 📦 Como configurar e rodar

1. **Clone o repositório e entre no diretório:**
   ```sh
   git clone https://github.com/seu-usuario/job-application-assistant.git
   cd job-application-assistant
   ```

2. **Crie e ative um ambiente virtual (Windows):**
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure suas variáveis de ambiente:**
   - Copie `.env.example` para `.env` e preencha `OPENAI_API_KEY` com sua chave.

5. **Rode a API:**
   ```sh
   uvicorn src.main:app --reload
   ```

6. **Acesse a API:**
   - Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧑‍💻 Exemplo de uso (via cURL):

```sh
curl -X POST "http://localhost:8000/application/analyze" \
  -H "Content-Type: application/json" \
  -d '{
        "resume": "John Doe, B.Sc. Computer Science, Python, REST APIs, 5 years experience in SaaS products...",
        "job_description": "Seeking Python developer with strong background in API design, OpenAI knowledge, experience with cloud deployments..."
      }'
```

**Retorno esperado:**
```json
{
  "feedback": "Your resume matches most of the technical requirements...",
  "cover_letter_suggestion": "Dear Hiring Manager, I am excited to apply...",
  "resume_improvements": "Add more details about your OpenAI experience..."
}
```

***
