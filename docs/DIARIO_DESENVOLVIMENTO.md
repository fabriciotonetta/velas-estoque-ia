\# 📔 Diário de Desenvolvimento — Velas Estoque IA



> Registro cronológico de todas as decisões técnicas, desafios e aprendizados durante o desenvolvimento.



\---



\## 📅 Dia 1 — Configuração do Ambiente e Estrutura do Projeto



\*\*Data:\*\* (coloque a data de hoje)

\*\*Duração:\*\* \~2 horas

\*\*Status:\*\* ✅ Concluído



\### O que foi feito

\- Verificação e documentação do ambiente de desenvolvimento (Python 3.13.2, Git 2.54.0)

\- Criação do repositório no GitHub com licença MIT

\- Configuração do ambiente virtual Python isolado

\- Definição da arquitetura completa do projeto

\- Definição do catálogo de produtos: 10 cores × 10 formatos × 10 perfumes × 3 tamanhos

\- Criação da estrutura de pastas seguindo boas práticas

\- Configuração do sistema de variáveis de ambiente (.env)

\- Escrita do README profissional com badges e arquitetura



\### Decisões técnicas tomadas

\- \*\*SQLite\*\* escolhido por ser leve e não precisar de servidor separado (ideal para portfólio)

\- \*\*Streamlit\*\* escolhido por permitir dashboards bonitos sem HTML/CSS

\- \*\*Random Forest\*\* escolhido por ser robusto para séries temporais simples



\### Desafios encontrados

\- (Preencha com dificuldades que você teve)



\### Aprendizados do dia

\- (Preencha com o que você aprendeu)



\### Próximo passo

\- Criar o banco de dados e gerar dados realistas de velas



\---

---

## 📅 Sessão 2 — Backend, ML, IA e Dashboard

**Status:** ✅ Concluído

### O que foi feito
- Criados modelos do banco de dados com SQLAlchemy (5 tabelas)
- Gerados 12 meses de dados históricos realistas com sazonalidade
- Implementada API REST com FastAPI (12 endpoints)
- Criados 7 testes automatizados com Pytest
- Treinado modelo Random Forest para previsão de demanda
- Implementado assistente de IA (modo simulado, pronto para Claude API)
- Criado dashboard completo com Streamlit e Plotly (6 páginas)

### Decisões técnicas
- Modo simulado para IA mantém estrutura profissional sem custo de API
- Cache do modelo ML com `@st.cache_resource` para performance
- Dashboard organizado em 6 páginas para melhor UX

### Aprendizados
- SQLAlchemy ORM facilita muito a manipulação do banco em Python
- Random Forest é robusto mesmo com dados sintéticos
- Streamlit permite dashboards profissionais sem HTML/CSS

