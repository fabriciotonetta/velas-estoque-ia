# ================================================================
# app.py — Dashboard interativo com Streamlit
# Para rodar: streamlit run dashboard/app.py
# ================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from src.database import SessionLocal
from src.estoque import EstoqueInsumos, EstoqueVelas
from src.models import Insumo, VelaPronta
from src.ia_assistente import AssistenteEstoque
from ml.prever_estoque import PrevisaoEstoque

# ================================================================
# CONFIGURAÇÃO DA PÁGINA
# ================================================================

st.set_page_config(
    page_title="🕯️ Velas Estoque IA",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para deixar o dashboard mais bonito
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem; border-radius: 10px; color: white;
        text-align: center; margin: 0.5rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem; border-radius: 10px; color: white;
    }
    .ok-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem; border-radius: 10px; color: white;
    }
    h1 { color: #4a4a4a; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; border: none; border-radius: 8px;
        padding: 0.5rem; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ================================================================
# FUNÇÕES AUXILIARES
# ================================================================

@st.cache_resource
def get_previsor():
    """Carrega o modelo ML uma única vez (cache)"""
    return PrevisaoEstoque()

def get_db():
    """Retorna sessão do banco"""
    return SessionLocal()


# ================================================================
# SIDEBAR — Menu de navegação
# ================================================================

st.sidebar.image("https://img.icons8.com/emoji/96/candle-emoji.png", width=80)
st.sidebar.title("🕯️ Velas Estoque IA")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "📌 Navegação",
    [
        "🏠 Início",
        "📦 Insumos",
        "🕯️ Velas",
        "📊 Vendas",
        "🤖 Previsões ML",
        "🧠 Assistente IA",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.sidebar.markdown("⚙️ Modo Simulado IA")


# ================================================================
# PÁGINA 1 — INÍCIO (Dashboard principal)
# ================================================================

if pagina == "🏠 Início":
    st.title("🕯️ Velas Estoque IA — Dashboard")
    st.markdown("Sistema inteligente de controle de estoque para velas artesanais")
    st.markdown("---")

    db = get_db()
    try:
        est_ins   = EstoqueInsumos(db)
        est_velas = EstoqueVelas(db)

        resumo_ins   = est_ins.resumo_estoque()
        resumo_velas = est_velas.resumo_estoque()

        # Cards de resumo
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📦 Total Insumos",
                resumo_ins["total_insumos"],
                help="Total de insumos cadastrados"
            )
        with col2:
            st.metric(
                "🚨 Insumos em Alerta",
                resumo_ins["em_alerta"],
                delta=f"-{resumo_ins['em_alerta']} críticos",
                delta_color="inverse"
            )
        with col3:
            st.metric(
                "🕯️ SKUs de Velas",
                resumo_velas["total_skus"],
                help="Combinações únicas de velas"
            )
        with col4:
            st.metric(
                "💰 Valor em Estoque",
                f"R$ {resumo_velas['valor_estoque']:,.2f}",
                help="Valor total das velas prontas"
            )

        st.markdown("---")

        # Gráfico de insumos por categoria
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("📦 Insumos por Categoria")
            todos = est_ins.listar_todos()
            df_cat = pd.DataFrame([{
                "Categoria": i.categoria,
                "Quantidade": i.quantidade_atual,
                "Nome": i.nome
            } for i in todos])

            if not df_cat.empty:
                fig = px.bar(
                    df_cat.groupby("Categoria")["Quantidade"].sum().reset_index(),
                    x="Categoria", y="Quantidade",
                    color="Categoria",
                    title="Estoque por Categoria",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("🚨 Insumos em Alerta")
            alertas = est_ins.insumos_em_alerta()
            if alertas:
                df_alert = pd.DataFrame([{
                    "Insumo": i.nome,
                    "Atual":  round(i.quantidade_atual, 2),
                    "Mínimo": i.quantidade_minima,
                    "Déficit": round(i.quantidade_minima - i.quantidade_atual, 2)
                } for i in alertas])
                st.dataframe(
                    df_alert.style.highlight_max(
                        subset=["Déficit"], color="#ffcccc"
                    ),
                    use_container_width=True, height=350
                )
            else:
                st.success("✅ Todos os insumos estão dentro do limite!")

        # Vendas recentes
        st.markdown("---")
        st.subheader("📈 Vendas dos Últimos 30 Dias")
        df_vendas = est_velas.vendas_por_periodo(30)

        if not df_vendas.empty:
            vendas_dia = df_vendas.groupby("data").agg(
                Vendas=("quantidade", "sum"),
                Receita=("receita", "sum")
            ).reset_index()

            fig2 = px.line(
                vendas_dia, x="data", y="Vendas",
                title="Unidades vendidas por dia",
                color_discrete_sequence=["#764ba2"]
            )
            fig2.update_traces(fill="tozeroy", fillcolor="rgba(118,75,162,0.1)")
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)

    finally:
        db.close()


# ================================================================
# PÁGINA 2 — INSUMOS
# ================================================================

elif pagina == "📦 Insumos":
    st.title("📦 Gestão de Insumos")
    st.markdown("---")

    db = get_db()
    try:
        est = EstoqueInsumos(db)

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            categorias = ["Todas", "Cera", "Essência", "Pavio",
                         "Corante", "Recipiente", "Embalagem"]
            cat_sel = st.selectbox("Filtrar por categoria:", categorias)
        with col2:
            apenas_alerta = st.checkbox("Mostrar apenas em alerta 🚨")

        # Lista de insumos
        if cat_sel == "Todas":
            insumos = est.listar_todos()
        else:
            insumos = est.buscar_por_categoria(cat_sel)

        if apenas_alerta:
            insumos = [i for i in insumos
                      if i.quantidade_atual <= i.quantidade_minima]

        df_ins = pd.DataFrame([{
            "ID":        i.id,
            "Nome":      i.nome,
            "Categoria": i.categoria,
            "Unidade":   i.unidade_medida,
            "Atual":     round(i.quantidade_atual, 2),
            "Mínimo":    i.quantidade_minima,
            "Ideal":     i.quantidade_ideal,
            "Preço R$":  i.preco_unitario,
            "Fornecedor":i.fornecedor,
            "Status":    "🚨" if i.quantidade_atual <= i.quantidade_minima else "✅"
        } for i in insumos])

        st.dataframe(df_ins, use_container_width=True, height=400)
        st.caption(f"Total: {len(df_ins)} insumos")

        st.markdown("---")

        # Formulários de entrada/saída
        col_e, col_s = st.columns(2)

        with col_e:
            st.subheader("➕ Registrar Entrada")
            todos_ins = est.listar_todos()
            nomes     = {i.nome: i.id for i in todos_ins}
            sel_e     = st.selectbox("Insumo:", list(nomes.keys()), key="ent")
            qtd_e     = st.number_input("Quantidade:", min_value=0.1, step=0.1, key="qtd_e")
            obs_e     = st.text_input("Observação:", "Compra/Recebimento", key="obs_e")

            if st.button("✅ Registrar Entrada"):
                try:
                    est.registrar_entrada(nomes[sel_e], qtd_e, obs_e)
                    st.success(f"✅ Entrada de {qtd_e} registrada!")
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))

        with col_s:
            st.subheader("➖ Registrar Saída")
            sel_s = st.selectbox("Insumo:", list(nomes.keys()), key="sai")
            qtd_s = st.number_input("Quantidade:", min_value=0.1, step=0.1, key="qtd_s")
            obs_s = st.text_input("Observação:", "Uso na produção", key="obs_s")

            if st.button("✅ Registrar Saída"):
                try:
                    est.registrar_saida(nomes[sel_s], qtd_s, obs_s)
                    st.success(f"✅ Saída de {qtd_s} registrada!")
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))

    finally:
        db.close()


# ================================================================
# PÁGINA 3 — VELAS
# ================================================================

elif pagina == "🕯️ Velas":
    st.title("🕯️ Catálogo de Velas")
    st.markdown("---")

    db = get_db()
    try:
        est = EstoqueVelas(db)

        # Filtros
        col1, col2, col3, col4 = st.columns(4)
        cores = ["Todas","Branco Clássico","Marfim","Rosa Quartzo",
                 "Lavanda","Azul Serenidade","Verde Sage","Terracota",
                 "Preto Obsidiana","Dourado","Vermelho Bordeaux"]
        formatos = ["Todos","Cilíndrica","Cônica","Quadrada","Esférica",
                    "Pilar","Votiva","Flutuante","Container","Escultural","Tealight"]
        tamanhos = ["Todos","P","M","G"]

        with col1:
            cor_f = st.selectbox("Cor:", cores)
        with col2:
            fmt_f = st.selectbox("Formato:", formatos)
        with col3:
            tam_f = st.selectbox("Tamanho:", tamanhos)
        with col4:
            alert_v = st.checkbox("Só em alerta 🚨")

        velas = est.listar_todas(
            cor=None if cor_f=="Todas" else cor_f,
            formato=None if fmt_f=="Todos" else fmt_f,
            tamanho=None if tam_f=="Todos" else tam_f
        )

        if alert_v:
            velas = [v for v in velas
                    if v.quantidade_estoque <= v.estoque_minimo]

        df_vel = pd.DataFrame([{
            "Código":    v.codigo_produto,
            "Cor":       v.cor,
            "Formato":   v.formato,
            "Perfume":   v.perfume,
            "Tamanho":   v.tamanho,
            "Estoque":   v.quantidade_estoque,
            "Mínimo":    v.estoque_minimo,
            "Preço R$":  v.preco_venda,
            "Status":    "🚨" if v.quantidade_estoque <= v.estoque_minimo else "✅"
        } for v in velas])

        st.dataframe(df_vel, use_container_width=True, height=400)
        st.caption(f"Total: {len(df_vel)} SKUs")

        st.markdown("---")
        st.subheader("🏆 Top 10 Mais Vendidas")
        top = est.top_mais_vendidas(10)
        if top:
            df_top = pd.DataFrame(top)
            fig = px.bar(
                df_top, x="codigo", y="total_vendido",
                color="total_vendido",
                color_continuous_scale="purples",
                title="Velas mais vendidas (histórico total)"
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    finally:
        db.close()


# ================================================================
# PÁGINA 4 — VENDAS
# ================================================================

elif pagina == "📊 Vendas":
    st.title("📊 Análise de Vendas")
    st.markdown("---")

    db = get_db()
    try:
        est   = EstoqueVelas(db)
        dias  = st.slider("Período (dias):", 7, 365, 30)
        df    = est.vendas_por_periodo(dias)

        if df.empty:
            st.warning("Nenhuma venda encontrada no período.")
        else:
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Unidades", int(df["quantidade"].sum()))
            col2.metric("💰 Receita", f"R$ {df['receita'].sum():,.2f}")
            col3.metric("🎯 Ticket Médio", f"R$ {df['receita'].mean():.2f}")
            col4.metric("📅 Dias analisados", dias)

            st.markdown("---")

            # Gráfico de vendas por dia
            vendas_dia = df.groupby("data").agg(
                Vendas=("quantidade","sum"),
                Receita=("receita","sum")
            ).reset_index()

            fig1 = px.area(
                vendas_dia, x="data", y="Receita",
                title=f"Receita diária — últimos {dias} dias",
                color_discrete_sequence=["#764ba2"]
            )
            st.plotly_chart(fig1, use_container_width=True)

            col_a, col_b = st.columns(2)

            with col_a:
                # Vendas por canal
                canal_data = df.groupby("canal")["quantidade"].sum().reset_index()
                fig2 = px.pie(
                    canal_data, values="quantidade", names="canal",
                    title="Vendas por Canal",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig2, use_container_width=True)

            with col_b:
                # Vendas por tamanho
                tam_data = df.groupby("tamanho")["quantidade"].sum().reset_index()
                fig3 = px.pie(
                    tam_data, values="quantidade", names="tamanho",
                    title="Vendas por Tamanho",
                    color_discrete_sequence=["#667eea","#764ba2","#f5576c"]
                )
                st.plotly_chart(fig3, use_container_width=True)

            # Vendas por cor
            cor_data = df.groupby("cor")["quantidade"].sum().reset_index()
            fig4 = px.bar(
                cor_data.sort_values("quantidade", ascending=True),
                x="quantidade", y="cor", orientation="h",
                title="Vendas por Cor de Vela",
                color="quantidade",
                color_continuous_scale="purples"
            )
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)

    finally:
        db.close()


# ================================================================
# PÁGINA 5 — PREVISÕES ML
# ================================================================

elif pagina == "🤖 Previsões ML":
    st.title("🤖 Previsões de Machine Learning")
    st.markdown("Previsões geradas por modelo Random Forest treinado com 12 meses de histórico")
    st.markdown("---")

    db = get_db()
    try:
        previsor = get_previsor()

        if not previsor.modelo_carregado:
            st.error("❌ Modelo não encontrado! Rode: python ml/treinar_modelo.py")
        else:
            metricas = previsor.metricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🎯 R² Insumos",
                       f"{metricas['insumos']['r2']*100:.1f}%")
            col2.metric("📉 MAE Insumos",
                       f"{metricas['insumos']['mae']:.3f}")
            col3.metric("🎯 R² Velas",
                       f"{metricas['velas']['r2']*100:.1f}%")
            col4.metric("📉 MAE Velas",
                       f"{metricas['velas']['mae']:.3f}")

            st.markdown("---")
            st.subheader("📦 Previsão de Consumo de Insumos")

            with st.spinner("Gerando previsões..."):
                previsoes = previsor.prever_todos_insumos(db)

            df_prev = pd.DataFrame([{
                "Insumo":          p["insumo_nome"],
                "Estoque Atual":   p["estoque_atual"],
                "Consumo/Dia":     p["consumo_diario_previsto"],
                "Dias Restantes":  p["dias_para_acabar"],
                "Qtd Repor":       p["quantidade_repor"],
                "Custo R$":        p["custo_reposicao"],
                "Urgência":        p["nivel_urgencia"]
            } for p in previsoes])

            st.dataframe(df_prev, use_container_width=True, height=450)

            # Gráfico de dias restantes
            fig = px.bar(
                df_prev.head(15),
                x="Insumo", y="Dias Restantes",
                color="Urgência",
                title="Dias até acabar o estoque (Top 15 mais críticos)",
                color_discrete_map={
                    "🔴 CRÍTICO": "#f5576c",
                    "🟠 URGENTE": "#f093fb",
                    "🟡 ATENÇÃO": "#ffd700",
                    "🟢 NORMAL":  "#00f2fe"
                }
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    finally:
        db.close()


# ================================================================
# PÁGINA 6 — ASSISTENTE IA
# ================================================================

elif pagina == "🧠 Assistente IA":
    st.title("🧠 Assistente Inteligente")
    st.markdown("Análises e recomendações geradas por IA com base nos dados reais do estoque")
    st.markdown("---")

    db = get_db()
    try:
        assistente = AssistenteEstoque()

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋 Gerar Relatório Completo"):
                with st.spinner("Analisando estoque..."):
                    relatorio = assistente.gerar_relatorio_estoque(db)
                st.text_area("Relatório:", relatorio, height=500)

        with col2:
            if st.button("📈 Análise de Sazonalidade"):
                with st.spinner("Analisando sazonalidade..."):
                    sazonal = assistente.analisar_sazonalidade(db)
                st.text_area("Sazonalidade:", sazonal, height=500)

        with col3:
            if st.button("🚨 Ver Insumos Urgentes"):
                with st.spinner("Verificando alertas..."):
                    urgentes = assistente.chat(
                        "Quais insumos estão urgentes ou críticos?", db
                    )
                st.text_area("Alertas:", urgentes, height=500)

        st.markdown("---")
        st.subheader("💬 Chat com o Assistente")

        if "historico" not in st.session_state:
            st.session_state.historico = []

        for msg in st.session_state.historico:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        pergunta = st.chat_input("Pergunte sobre o estoque...")
        if pergunta:
            st.session_state.historico.append(
                {"role": "user", "content": pergunta}
            )
            with st.chat_message("user"):
                st.write(pergunta)

            with st.spinner("Pensando..."):
                resposta = assistente.chat(pergunta, db)

            st.session_state.historico.append(
                {"role": "assistant", "content": resposta}
            )
            with st.chat_message("assistant"):
                st.write(resposta)

    finally:
        db.close()