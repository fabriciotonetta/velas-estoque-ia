\# 🕯️ Velas Estoque IA — Apresentação do Projeto



\## O que é este projeto?



Este sistema foi desenvolvido como projeto de portfólio para demonstrar

habilidades reais de desenvolvimento de software aplicadas a um problema

de negócio concreto: o controle de estoque de uma fabricante artesanal

de velas.



O problema real que ele resolve: pequenas fabricantes de velas perdem

dinheiro por falta de controle — compram insumos em excesso, ficam sem

estoque na hora errada, e não sabem quais produtos vendem mais. Este

sistema resolve tudo isso com tecnologia.



\---



\## O que foi desenvolvido?



\### 🗄️ Banco de Dados (SQLite + SQLAlchemy)

Modelei 5 tabelas relacionais para controlar insumos, produtos acabados

e todo o histórico de movimentações. O catálogo gerencia até 3.000

combinações de velas (10 cores × 10 formatos × 10 perfumes × 3 tamanhos).

Gerei 12 meses de dados históricos realistas com sazonalidade simulada,

incluindo picos de vendas no Dia das Mães e no Natal.



\### 🔌 API REST (FastAPI)

Desenvolvi 12 endpoints RESTful seguindo boas práticas, com validação

automática de dados via Pydantic, tratamento de erros com códigos HTTP

corretos e documentação interativa gerada automaticamente pelo Swagger UI

(acessível em /docs).



\### 🤖 Machine Learning (scikit-learn)

Treinei dois modelos Random Forest Regressor — um para prever o consumo

de insumos e outro para prever a demanda de velas. Os modelos aprendem

com o histórico de 12 meses e classificam cada insumo em 4 níveis de

urgência: Crítico, Urgente, Atenção e Normal. O pipeline completo inclui

extração de features, encoding de variáveis categóricas, divisão

treino/teste e avaliação com métricas MAE e R².



\### 🧠 Inteligência Artificial (Anthropic Claude API)

Integrei a arquitetura completa para uso da Claude API, que gera

relatórios executivos em linguagem natural, sugestões de reposição

personalizadas e responde perguntas livres sobre o estoque via chat.

O sistema foi desenvolvido com modo simulado funcional, mantendo toda

a estrutura profissional pronta para ativação com créditos de API.



\### 📊 Dashboard (Streamlit + Plotly)

Criei uma interface visual completa com 6 páginas interativas:

página inicial com KPIs e gráficos em tempo real, gestão de insumos

com formulários de entrada e saída, catálogo de velas com filtros,

análise de vendas com gráficos de área e pizza, previsões do modelo

ML com gráfico de urgência, e chat com o assistente de IA.



\### ✅ Testes Automatizados (Pytest)

Escrevi 7 testes unitários cobrindo as regras de negócio críticas:

listagem, entrada, saída, estoque insuficiente, alertas, validações

e resumo do estoque.



\---



\## Tecnologias utilizadas



| Categoria        | Tecnologia              |

|------------------|------------------------|

| Linguagem        | Python 3.13            |

| Banco de Dados   | SQLite + SQLAlchemy    |

| API REST         | FastAPI + Uvicorn      |

| Machine Learning | scikit-learn (RF)      |

| Dados            | pandas + numpy         |

| IA Generativa    | Anthropic Claude API   |

| Dashboard        | Streamlit + Plotly     |

| Testes           | Pytest                 |

| Versionamento    | Git + GitHub           |



\---



\## O que demonstra tecnicamente?



\- Modelagem de banco de dados relacional com ORM

\- Desenvolvimento de API REST com boas práticas

\- Pipeline completo de Machine Learning (coleta → treino → previsão)

\- Integração com API de IA generativa

\- Desenvolvimento de interface visual interativa

\- Testes automatizados e qualidade de código

\- Versionamento semântico com commits organizados

\- Documentação técnica completa



\---



\## Como rodar o projeto



```bash

git clone https://github.com/fabriciotonetta/velas-estoque-ia.git

cd velas-estoque-ia

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

python -m data.gerar\_dados

python ml/treinar\_modelo.py

streamlit run dashboard/app.py

```



\---



\## Próximos passos planejados



\- Ativar Claude API para relatórios com IA real

\- Deploy na nuvem (Railway ou Render)

\- Autenticação de usuários com JWT

\- Notificações por email quando estoque crítico

\- App mobile com React Native



\---



\*Desenvolvido por Fabricio Tonetta — 2026\*

\*GitHub: github.com/fabriciotonetta/velas-estoque-ia\*

