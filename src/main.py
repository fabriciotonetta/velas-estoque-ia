# ================================================================
# main.py — API REST do sistema Velas Estoque IA
# FastAPI cria automaticamente documentação interativa em /docs
# Para rodar: uvicorn src.main:app --reload
# ================================================================

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware permite que o dashboard acesse a API

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
# Pydantic valida os dados que chegam na API automaticamente

from src.database import get_db, criar_tabelas
from src.estoque import EstoqueInsumos, EstoqueVelas
from src.models import Insumo, VelaPronta


# ================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ================================================================

# Cria a aplicação FastAPI com metadados para a documentação
app = FastAPI(
    title="🕯️ Velas Estoque IA — API",
    description="""
    API REST para gerenciamento inteligente de estoque de velas artesanais.

    ## Funcionalidades
    * 📦 **Insumos** — CRUD completo de materiais de fabricação
    * 🕯️ **Velas** — Gestão de produtos acabados
    * 📊 **Relatórios** — Análises e métricas de estoque
    * 🤖 **ML** — Previsões de demanda e alertas inteligentes
    """,
    version="1.0.0",
    contact={"name": "Velas Estoque IA", "url": "https://github.com"},
)

# Configura o CORS para permitir acesso do dashboard Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],       # Permite GET, POST, PUT, DELETE
    allow_headers=["*"],
)

# Cria as tabelas quando a API inicia (se não existirem)
@app.on_event("startup")
def startup():
    criar_tabelas()


# ================================================================
# SCHEMAS PYDANTIC — Definem o formato dos dados da API
# São como "formulários" que validam o que entra e sai da API
# ================================================================

class EntradaInsumoSchema(BaseModel):
    """Dados necessários para registrar entrada de insumo"""
    insumo_id:  int
    quantidade: float
    observacao: str = "Compra/Recebimento"

class SaidaInsumoSchema(BaseModel):
    """Dados necessários para registrar saída de insumo"""
    insumo_id:  int
    quantidade: float
    observacao: str = "Uso na produção"

class VendaVelaSchema(BaseModel):
    """Dados necessários para registrar uma venda"""
    codigo_produto: str
    quantidade:     int
    canal_venda:    str = "Direto"

class ProducaoVelaSchema(BaseModel):
    """Dados necessários para registrar produção de velas"""
    codigo_produto: str
    quantidade:     int


# ================================================================
# ROTAS — RAIZ E SAÚDE DA API
# ================================================================

@app.get("/", tags=["Sistema"])
def raiz():
    """Rota raiz — confirma que a API está funcionando"""
    return {
        "sistema":  "🕯️ Velas Estoque IA",
        "versao":   "1.0.0",
        "status":   "online",
        "docs":     "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    """Verifica se a API e o banco estão funcionando"""
    try:
        # Tenta fazer uma query simples para testar o banco
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "healthy", "banco": "conectado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================================================================
# ROTAS — INSUMOS
# ================================================================

@app.get("/insumos", tags=["Insumos"])
def listar_insumos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os insumos cadastrados.
    Parâmetro opcional: ?categoria=Cera
    """
    estoque = EstoqueInsumos(db)

    if categoria:
        insumos = estoque.buscar_por_categoria(categoria)
    else:
        insumos = estoque.listar_todos()

    # Transforma os objetos em dicionários para retornar como JSON
    return [{
        "id":               i.id,
        "nome":             i.nome,
        "categoria":        i.categoria,
        "unidade_medida":   i.unidade_medida,
        "quantidade_atual": i.quantidade_atual,
        "quantidade_minima":i.quantidade_minima,
        "quantidade_ideal": i.quantidade_ideal,
        "preco_unitario":   i.preco_unitario,
        "fornecedor":       i.fornecedor,
        "em_alerta":        i.quantidade_atual <= i.quantidade_minima
    } for i in insumos]


@app.get("/insumos/alertas", tags=["Insumos"])
def insumos_em_alerta(db: Session = Depends(get_db)):
    """Retorna apenas insumos com estoque abaixo do mínimo"""
    estoque = EstoqueInsumos(db)
    insumos = estoque.insumos_em_alerta()
    return {
        "total_alertas": len(insumos),
        "insumos": [{
            "id":               i.id,
            "nome":             i.nome,
            "quantidade_atual": i.quantidade_atual,
            "quantidade_minima":i.quantidade_minima,
            "deficit":          round(i.quantidade_minima - i.quantidade_atual, 2),
            "fornecedor":       i.fornecedor
        } for i in insumos]
    }


@app.get("/insumos/{insumo_id}", tags=["Insumos"])
def detalhe_insumo(insumo_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes completos de um insumo, incluindo previsão de dias"""
    estoque = EstoqueInsumos(db)
    insumo = estoque.buscar_por_id(insumo_id)

    if not insumo:
        # Retorna erro 404 se não encontrar
        raise HTTPException(status_code=404, detail="Insumo não encontrado")

    consumo_diario = estoque.consumo_medio_diario(insumo_id)
    dias_restantes = estoque.dias_ate_acabar(insumo_id)

    return {
        "id":                insumo.id,
        "nome":              insumo.nome,
        "categoria":         insumo.categoria,
        "unidade_medida":    insumo.unidade_medida,
        "quantidade_atual":  insumo.quantidade_atual,
        "quantidade_minima": insumo.quantidade_minima,
        "quantidade_ideal":  insumo.quantidade_ideal,
        "preco_unitario":    insumo.preco_unitario,
        "fornecedor":        insumo.fornecedor,
        "consumo_diario":    consumo_diario,
        "dias_para_acabar":  dias_restantes,
        "em_alerta":         insumo.quantidade_atual <= insumo.quantidade_minima,
        "valor_em_estoque":  round(insumo.quantidade_atual * insumo.preco_unitario, 2)
    }


@app.post("/insumos/entrada", tags=["Insumos"])
def registrar_entrada(dados: EntradaInsumoSchema, db: Session = Depends(get_db)):
    """Registra a entrada (compra/recebimento) de um insumo"""
    estoque = EstoqueInsumos(db)
    try:
        movim = estoque.registrar_entrada(
            dados.insumo_id, dados.quantidade, dados.observacao
        )
        return {
            "sucesso":   True,
            "mensagem":  "Entrada registrada com sucesso",
            "movimentacao_id": movim.id,
            "novo_estoque":    movim.estoque_posterior
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/insumos/saida", tags=["Insumos"])
def registrar_saida(dados: SaidaInsumoSchema, db: Session = Depends(get_db)):
    """Registra a saída (uso na produção) de um insumo"""
    estoque = EstoqueInsumos(db)
    try:
        movim = estoque.registrar_saida(
            dados.insumo_id, dados.quantidade, dados.observacao
        )
        return {
            "sucesso":         True,
            "mensagem":        "Saída registrada com sucesso",
            "movimentacao_id": movim.id,
            "novo_estoque":    movim.estoque_posterior
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/insumos/{insumo_id}/historico", tags=["Insumos"])
def historico_insumo(
    insumo_id: int,
    limite: int = Query(30, description="Número de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Retorna o histórico de movimentações de um insumo"""
    estoque = EstoqueInsumos(db)
    historico = estoque.historico_movimentacoes(insumo_id, limite)

    return [{
        "id":                m.id,
        "tipo":              m.tipo,
        "quantidade":        m.quantidade,
        "estoque_anterior":  m.estoque_anterior,
        "estoque_posterior": m.estoque_posterior,
        "observacao":        m.observacao,
        "data":              m.data_movimentacao.isoformat()
    } for m in historico]


# ================================================================
# ROTAS — VELAS PRONTAS
# ================================================================

@app.get("/velas", tags=["Velas"])
def listar_velas(
    cor:     Optional[str] = Query(None),
    formato: Optional[str] = Query(None),
    perfume: Optional[str] = Query(None),
    tamanho: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lista velas com filtros opcionais por cor, formato, perfume e tamanho"""
    estoque = EstoqueVelas(db)
    velas = estoque.listar_todas(cor, formato, perfume, tamanho)

    return [{
        "codigo_produto":     v.codigo_produto,
        "cor":                v.cor,
        "formato":            v.formato,
        "perfume":            v.perfume,
        "tamanho":            v.tamanho,
        "peso_gramas":        v.peso_gramas,
        "tempo_queima_horas": v.tempo_queima_horas,
        "preco_venda":        v.preco_venda,
        "custo_producao":     v.custo_producao,
        "margem_percent":     round((v.preco_venda - v.custo_producao) / v.preco_venda * 100, 1),
        "quantidade_estoque": v.quantidade_estoque,
        "estoque_minimo":     v.estoque_minimo,
        "em_alerta":          v.quantidade_estoque <= v.estoque_minimo
    } for v in velas]


@app.get("/velas/alertas", tags=["Velas"])
def velas_em_alerta(db: Session = Depends(get_db)):
    """Retorna velas com estoque abaixo do mínimo"""
    estoque = EstoqueVelas(db)
    velas = estoque.velas_em_alerta()
    return {
        "total_alertas": len(velas),
        "velas": [{
            "codigo":    v.codigo_produto,
            "cor":       v.cor,
            "formato":   v.formato,
            "tamanho":   v.tamanho,
            "estoque":   v.quantidade_estoque,
            "minimo":    v.estoque_minimo
        } for v in velas]
    }


@app.get("/velas/top-vendidas", tags=["Velas"])
def top_velas(
    limite: int = Query(10, description="Quantas velas retornar"),
    db: Session = Depends(get_db)
):
    """Retorna as velas mais vendidas"""
    estoque = EstoqueVelas(db)
    return estoque.top_mais_vendidas(limite)


@app.post("/velas/venda", tags=["Velas"])
def registrar_venda(dados: VendaVelaSchema, db: Session = Depends(get_db)):
    """Registra a venda de velas prontas"""
    estoque = EstoqueVelas(db)
    try:
        movim = estoque.registrar_venda(
            dados.codigo_produto, dados.quantidade, dados.canal_venda
        )
        return {
            "sucesso":         True,
            "mensagem":        "Venda registrada com sucesso",
            "movimentacao_id": movim.id,
            "novo_estoque":    movim.estoque_posterior
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/velas/producao", tags=["Velas"])
def registrar_producao(dados: ProducaoVelaSchema, db: Session = Depends(get_db)):
    """Registra a fabricação de novas velas"""
    estoque = EstoqueVelas(db)
    try:
        movim = estoque.registrar_producao(
            dados.codigo_produto, dados.quantidade
        )
        return {
            "sucesso":         True,
            "mensagem":        "Produção registrada com sucesso",
            "movimentacao_id": movim.id,
            "novo_estoque":    movim.estoque_posterior
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ================================================================
# ROTAS — DASHBOARD E RELATÓRIOS
# ================================================================

@app.get("/dashboard/resumo", tags=["Dashboard"])
def resumo_dashboard(db: Session = Depends(get_db)):
    """
    Retorna todos os dados necessários para os cards do dashboard.
    Uma única chamada traz tudo para a tela inicial.
    """
    est_insumos = EstoqueInsumos(db)
    est_velas   = EstoqueVelas(db)

    return {
        "insumos": est_insumos.resumo_estoque(),
        "velas":   est_velas.resumo_estoque(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/dashboard/vendas", tags=["Dashboard"])
def vendas_periodo(
    dias: int = Query(30, description="Período em dias"),
    db: Session = Depends(get_db)
):
    """Retorna análise de vendas do período para os gráficos"""
    est_velas = EstoqueVelas(db)
    df = est_velas.vendas_por_periodo(dias)

    if df.empty:
        return {"periodo_dias": dias, "total_vendas": 0, "dados": []}

    # Agrupa vendas por dia para o gráfico de linha
    vendas_dia = df.groupby("data").agg(
        quantidade=("quantidade", "sum"),
        receita=("receita", "sum")
    ).reset_index()

    return {
        "periodo_dias":   dias,
        "total_vendas":   int(df["quantidade"].sum()),
        "receita_total":  round(df["receita"].sum(), 2),
        "ticket_medio":   round(df["receita"].mean(), 2),
        "canal_top":      df["canal"].value_counts().index[0] if not df.empty else "N/A",
        "dados_por_dia":  vendas_dia.to_dict("records")
    }