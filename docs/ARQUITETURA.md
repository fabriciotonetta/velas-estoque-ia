\# 🏗️ Arquitetura do Sistema — Velas Estoque IA



\## Visão Geral

┌─────────────────────────────────────────┐



│         DASHBOARD (Streamlit)           │



│  6 páginas interativas com Plotly       │



└──────────────┬──────────────────────────┘



│



┌──────────────▼──────────────────────────┐



│           API REST (FastAPI)            │



│  12 endpoints documentados em /docs     │



└──────┬───────────┬──────────┬───────────┘



│           │          │



┌──────▼───┐ ┌─────▼────┐ ┌──▼──────────┐



│ SQLite   │ │ Random   │ │ Assistente  │



│ SQLAlch. │ │ Forest   │ │ IA (Claude) │



│ 5 tabelas│ │ 2 modelos│ │ 4 métodos   │



└──────────┘ └──────────┘ └─────────────┘

## Tabelas do Banco de Dados



| Tabela | Descrição | Registros aprox. |

|--------|-----------|-----------------|

| insumos | Materiais de fabricação | 20 |

| velas\_prontas | SKUs do catálogo | 3.000 |

| movimentacoes\_insumos | Histórico de insumos | 2.000+ |

| movimentacoes\_velas | Histórico de vendas | 5.000+ |

| previsoes\_ml | Histórico de previsões | dinâmico |



\## Modelo de Machine Learning



\- \*\*Algoritmo:\*\* Random Forest Regressor

\- \*\*Features:\*\* 11 (insumos) e 8 (velas)

\- \*\*Dados de treino:\*\* 12 meses de histórico

\- \*\*Sazonalidade:\*\* modelada via features de mês e trimestre

\- \*\*Persistência:\*\* joblib (.pkl)



\## Fluxo de uma Previsão



1\. Dashboard chama `PrevisaoEstoque.prever\_todos\_insumos()`

2\. Modelo carrega features do insumo atual

3\. Random Forest retorna consumo diário previsto

4\. Sistema calcula dias restantes e quantidade a repor

5\. Resultado classificado em 4 níveis de urgência

6\. Salvo em `previsoes\_ml` para histórico



\## Stack Tecnológica Completa



| Camada | Tecnologia | Versão |

|--------|-----------|--------|

| Linguagem | Python | 3.13 |

| ORM | SQLAlchemy | 2.0 |

| Banco | SQLite | 3.x |

| API | FastAPI | 0.115 |

| Servidor | Uvicorn | 0.32 |

| ML | scikit-learn | 1.5 |

| Dados | pandas + numpy | 2.x |

| Dashboard | Streamlit | 1.40 |

| Gráficos | Plotly | 5.24 |

| IA | Anthropic Claude | API |

| Testes | Pytest | 8.3 |



