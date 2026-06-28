\# 🕯️ Velas Estoque IA



> Sistema inteligente de controle de estoque para fabricação de velas artesanais com previsão de demanda via Machine Learning e sugestões automatizadas por IA generativa.



!\[Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge\&logo=python)

!\[FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=for-the-badge\&logo=fastapi)

!\[scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange?style=for-the-badge\&logo=scikit-learn)

!\[Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?style=for-the-badge\&logo=streamlit)

!\[Claude AI](https://img.shields.io/badge/Claude\_AI-Anthropic-purple?style=for-the-badge)



\---



\## 📋 Sobre o Projeto



Este sistema foi desenvolvido para resolver um problema real enfrentado por fabricantes de velas artesanais: \*\*o controle manual de estoque é ineficiente e sujeito a erros\*\*, causando falta de insumos no momento de produção ou compras desnecessárias.



A solução combina:

\- 📦 \*\*Gestão de estoque\*\* com histórico completo de movimentações

\- 🤖 \*\*Machine Learning\*\* para prever quando insumos vão acabar

\- 🧠 \*\*IA Generativa (Claude)\*\* para sugestões em linguagem natural

\- 📊 \*\*Dashboard interativo\*\* para visualização em tempo real



\### Catálogo de Produtos

O sistema gerencia \*\*3.000 combinações\*\* de velas:

\- 🎨 \*\*10 cores\*\* — Do Branco Clássico ao Vermelho Bordeaux

\- 🕯️ \*\*10 formatos\*\* — Da Cilíndrica à Tealight

\- 🌸 \*\*10 perfumes\*\* — Da Lavanda \& Baunilha ao Sândalo \& Âmbar

\- 📏 \*\*3 tamanhos\*\* — Pequeno (80g), Médio (180g), Grande (350g)



\---



\## 🏗️ Arquitetura do Sistema

┌─────────────────────────────────────────────────────┐



│                   DASHBOARD (Streamlit)              │



│              Interface visual do usuário             │



└──────────────────────┬──────────────────────────────┘



│



┌──────────────────────▼──────────────────────────────┐



│                  API REST (FastAPI)                  │



│           Endpoints para todas as operações          │



└────────┬─────────────┬──────────────┬───────────────┘



│             │              │



┌────────▼───┐  ┌──────▼──────┐  ┌───▼────────────────┐



│  BANCO DE  │  │  MODELO ML  │  │   IA GENERATIVA    │



│    DADOS   │  │(Random Forest│  │  (Claude API)      │



│  (SQLite)  │  │  Regressor) │  │  Relatórios e      │



│            │  │  Previsão   │  │  sugestões em      │



│ Produtos   │  │  de demanda │  │  linguagem natural │



│ Insumos    │  └─────────────┘  └────────────────────┘



│ Moviment.  │



└────────────┘


---



\## 🚀 Como Executar



\### Pré-requisitos

\- Python 3.10 ou superior

\- Conta na Anthropic (para a chave da API Claude)



\### Instalação



\*\*1. Clone o repositório\*\*

```bash

git clone https://github.com/SEU\_USUARIO/velas-estoque-ia.git

cd velas-estoque-ia

```



\*\*2. Crie e ative o ambiente virtual\*\*

```bash

python -m venv venv

venv\\Scripts\\activate  # Windows

source venv/bin/activate  # Linux/Mac

```



\*\*3. Instale as dependências\*\*

```bash

pip install -r requirements.txt

```



\*\*4. Configure as variáveis de ambiente\*\*

```bash

copy .env.example .env

\# Edite o .env e adicione sua chave da API Anthropic

```



\*\*5. Gere os dados iniciais\*\*

```bash

python data/gerar\_dados.py

```



\*\*6. Treine o modelo de ML\*\*

```bash

python ml/treinar\_modelo.py

```



\*\*7. Inicie o dashboard\*\*

```bash

streamlit run dashboard/app.py

```



\---



\## 📁 Estrutura do Projeto

velas-estoque-ia/



├── data/               # Dados e scripts de geração



├── src/                # Código fonte principal



├── ml/                 # Modelos de Machine Learning



├── dashboard/          # Interface Streamlit



├── docs/               # Documentação completa



└── tests/              # Testes automatizados

---



\## 🛠️ Tecnologias Utilizadas



| Categoria | Tecnologia | Uso |

|-----------|-----------|-----|

| Linguagem | Python 3.13 | Base do projeto |

| API REST | FastAPI | Endpoints do sistema |

| Banco de Dados | SQLite + SQLAlchemy | Persistência dos dados |

| Machine Learning | scikit-learn | Previsão de demanda |

| IA Generativa | Anthropic Claude | Relatórios inteligentes |

| Dashboard | Streamlit + Plotly | Visualização |

| Testes | Pytest | Qualidade do código |



\---



\## 📊 Funcionalidades



\- \[x] Cadastro de insumos e produtos

\- \[x] Registro de entradas e saídas de estoque

\- \[x] Alertas de estoque mínimo

\- \[x] Previsão de demanda com ML

\- \[x] Sugestões de reposição com IA

\- \[x] Dashboard interativo

\- \[x] API REST documentada

\- \[x] Testes automatizados



\---



\## 📖 Documentação



\- \[Diário de Desenvolvimento](docs/DIARIO\_DESENVOLVIMENTO.md)

\- \[Arquitetura do Sistema](docs/ARQUITETURA.md)

\- \[Documentação da API](docs/API\_DOCS.md)



\---



\## 👨‍💻 Autor



Desenvolvido com 💛 como projeto de portfólio para demonstrar habilidades em desenvolvimento Python, Machine Learning e IA Generativa.



\---



\## 📄 Licença



Este projeto está sob a licença MIT. Veja o arquivo \[LICENSE](LICENSE) para detalhes.

