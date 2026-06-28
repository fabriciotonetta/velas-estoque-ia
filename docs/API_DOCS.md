\# 📡 Documentação da API — Velas Estoque IA



Base URL: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`



\## Endpoints



\### Sistema

| Método | Rota | Descrição |

|--------|------|-----------|

| GET | `/` | Status da API |

| GET | `/health` | Saúde do sistema |



\### Insumos

| Método | Rota | Descrição |

|--------|------|-----------|

| GET | `/insumos` | Lista todos os insumos |

| GET | `/insumos/alertas` | Insumos abaixo do mínimo |

| GET | `/insumos/{id}` | Detalhe com previsão |

| POST | `/insumos/entrada` | Registra entrada |

| POST | `/insumos/saida` | Registra saída |

| GET | `/insumos/{id}/historico` | Histórico de movimentações |



\### Velas

| Método | Rota | Descrição |

|--------|------|-----------|

| GET | `/velas` | Lista com filtros |

| GET | `/velas/alertas` | Velas com estoque baixo |

| GET | `/velas/top-vendidas` | Ranking de vendas |

| POST | `/velas/venda` | Registra venda |

| POST | `/velas/producao` | Registra produção |



\### Dashboard

| Método | Rota | Descrição |

|--------|------|-----------|

| GET | `/dashboard/resumo` | Resumo geral |

| GET | `/dashboard/vendas` | Análise de vendas |



\## Exemplo de Uso



```bash

\# Listar insumos em alerta

curl http://localhost:8000/insumos/alertas



\# Registrar entrada de insumo

curl -X POST http://localhost:8000/insumos/entrada \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"insumo\_id": 1, "quantidade": 10.0, "observacao": "Compra NF 001"}'

```

