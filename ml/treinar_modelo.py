# ================================================================
# treinar_modelo.py — Treina o modelo de Machine Learning
# Usa Random Forest Regressor para prever consumo de insumos
# e demanda de velas com base no histórico de movimentações
# ================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd               # Manipulação de dados em tabela
import numpy as np                # Operações matemáticas
import joblib                     # Salvar e carregar o modelo treinado
from datetime import datetime, timedelta

from sklearn.ensemble import RandomForestRegressor
# RandomForest = conjunto de várias árvores de decisão trabalhando juntas
# É robusto, preciso e funciona bem com poucos dados

from sklearn.model_selection import train_test_split
# Divide os dados em treino e teste para avaliar o modelo

from sklearn.metrics import mean_absolute_error, r2_score
# Métricas para avaliar a qualidade do modelo
# MAE = Erro Médio Absoluto (quanto o modelo erra em média)
# R² = Coeficiente de determinação (0 a 1, quanto maior melhor)

from sklearn.preprocessing import LabelEncoder
# Transforma texto em número (ML só trabalha com números)

from src.database import SessionLocal
from src.models import Insumo, VelaPronta, MovimentacaoInsumo, MovimentacaoVela


# ================================================================
# ETAPA 1 — Extrair e preparar os dados do banco
# ================================================================

def extrair_dados_insumos(db) -> pd.DataFrame:
    """
    Extrai o histórico de movimentações de insumos e transforma
    em um DataFrame com features (características) para o modelo.
    Features são as variáveis que o modelo usa para aprender.
    """
    print("  📥 Extraindo dados de insumos...")

    movimentacoes = db.query(MovimentacaoInsumo).all()

    if not movimentacoes:
        print("  ⚠️  Nenhuma movimentação encontrada!")
        return pd.DataFrame()

    dados = []
    for m in movimentacoes:
        insumo = db.query(Insumo).filter(Insumo.id == m.insumo_id).first()
        if not insumo:
            continue

        dados.append({
            # Features de tempo (o modelo aprende sazonalidade com isso)
            "dia_semana":     m.data_movimentacao.weekday(),  # 0=Seg, 6=Dom
            "mes":            m.data_movimentacao.month,       # 1 a 12
            "dia_mes":        m.data_movimentacao.day,         # 1 a 31
            "trimestre":      (m.data_movimentacao.month - 1) // 3 + 1,

            # Features do insumo
            "categoria":      insumo.categoria,
            "preco_unitario": insumo.preco_unitario,
            "estoque_atual":  m.estoque_anterior,  # Estoque ANTES da movim.
            "estoque_minimo": insumo.quantidade_minima,
            "estoque_ideal":  insumo.quantidade_ideal,

            # Proporção do estoque (0 = vazio, 1 = no ideal)
            "proporcao_estoque": (
                m.estoque_anterior / insumo.quantidade_ideal
                if insumo.quantidade_ideal > 0 else 0
            ),

            # Tipo da movimentação (entrada=1, saída=0)
            "tipo":           1 if m.tipo == "entrada" else 0,

            # TARGET — o que o modelo vai aprender a prever
            "quantidade_movimentada": m.quantidade
        })

    df = pd.DataFrame(dados)
    print(f"  ✅ {len(df)} registros extraídos de insumos")
    return df


def extrair_dados_velas(db) -> pd.DataFrame:
    """
    Extrai o histórico de vendas de velas e prepara para o modelo.
    O modelo vai prever a demanda diária de cada tipo de vela.
    """
    print("  📥 Extraindo dados de velas...")

    movimentacoes = db.query(MovimentacaoVela).filter(
        MovimentacaoVela.tipo == "saida"  # Só as vendas
    ).all()

    if not movimentacoes:
        return pd.DataFrame()

    dados = []
    for m in movimentacoes:
        vela = db.query(VelaPronta).filter(VelaPronta.id == m.vela_id).first()
        if not vela:
            continue

        # Fator de sazonalidade real por mês
        sazonalidade = {
            1: 0.7, 2: 0.8, 3: 0.9, 4: 1.0,
            5: 1.8, 6: 0.8, 7: 0.9, 8: 1.0,
            9: 1.1, 10: 1.2, 11: 1.4, 12: 2.0
        }

        mes = m.data_movimentacao.month
        dados.append({
            # Features de tempo
            "dia_semana":      m.data_movimentacao.weekday(),
            "mes":             mes,
            "trimestre":       (mes - 1) // 3 + 1,
            "fator_sazonalidade": sazonalidade.get(mes, 1.0),

            # Features da vela
            "tamanho_cod":     {"P": 1, "M": 2, "G": 3}.get(vela.tamanho, 1),
            "preco_venda":     vela.preco_venda,
            "peso_gramas":     vela.peso_gramas,
            "estoque_atual":   m.estoque_anterior,

            # TARGET
            "quantidade_vendida": m.quantidade
        })

    df = pd.DataFrame(dados)
    print(f"  ✅ {len(df)} registros extraídos de vendas")
    return df


# ================================================================
# ETAPA 2 — Preparar as features para o modelo
# ================================================================

def preparar_features_insumos(df: pd.DataFrame):
    """
    Transforma o DataFrame de insumos em arrays numéricos.
    O ML só trabalha com números, então precisamos converter texto.
    """
    if df.empty:
        return None, None, None

    # Converte a coluna 'categoria' de texto para número
    le = LabelEncoder()
    df["categoria_cod"] = le.fit_transform(df["categoria"])
    # Exemplo: "Cera"=0, "Corante"=1, "Embalagem"=2...

    # Define quais colunas são as FEATURES (entradas do modelo)
    features = [
        "dia_semana", "mes", "dia_mes", "trimestre",
        "categoria_cod", "preco_unitario",
        "estoque_atual", "estoque_minimo", "estoque_ideal",
        "proporcao_estoque", "tipo"
    ]

    # X = features (o que o modelo recebe)
    X = df[features].values

    # y = target (o que o modelo deve prever)
    y = df["quantidade_movimentada"].values

    return X, y, le


def preparar_features_velas(df: pd.DataFrame):
    """
    Transforma o DataFrame de velas em arrays numéricos.
    """
    if df.empty:
        return None, None

    features = [
        "dia_semana", "mes", "trimestre",
        "fator_sazonalidade", "tamanho_cod",
        "preco_venda", "peso_gramas", "estoque_atual"
    ]

    X = df[features].values
    y = df["quantidade_vendida"].values

    return X, y


# ================================================================
# ETAPA 3 — Treinar os modelos
# ================================================================

def treinar_modelo_insumos(X, y, le):
    """
    Treina o modelo Random Forest para prever consumo de insumos.
    Retorna o modelo treinado e as métricas de avaliação.
    """
    print("\n  🌲 Treinando modelo de insumos...")

    # Divide os dados: 80% para treinar, 20% para avaliar
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,      # 20% para teste
        random_state=42     # Garante reprodutibilidade
    )

    # Cria o modelo Random Forest
    modelo = RandomForestRegressor(
        n_estimators=100,   # 100 árvores de decisão trabalhando juntas
        max_depth=10,       # Cada árvore pode ter no máximo 10 níveis
        min_samples_split=5,# Mínimo de amostras para dividir um nó
        random_state=42,    # Reprodutibilidade
        n_jobs=-1           # Usa todos os núcleos do processador
    )

    # TREINA o modelo com os dados de treino
    modelo.fit(X_train, y_train)
    # .fit() = "aprenda com esses dados"

    # AVALIA o modelo com os dados de teste (que ele nunca viu)
    y_pred = modelo.predict(X_test)
    # .predict() = "agora use o que aprendeu para prever"

    mae = mean_absolute_error(y_test, y_pred)
    r2  = r2_score(y_test, y_pred)
    # R² próximo de 1.0 = modelo excelente

    print(f"  📊 Modelo de Insumos:")
    print(f"     MAE (Erro Médio): {mae:.4f} unidades")
    print(f"     R² (Precisão):    {r2:.4f} ({r2*100:.1f}%)")

    # Importância de cada feature — mostra o que o modelo mais usa
    features_names = [
        "dia_semana", "mes", "dia_mes", "trimestre",
        "categoria", "preco_unit", "estoque_atual",
        "estoque_min", "estoque_ideal", "proporcao", "tipo"
    ]
    importancias = modelo.feature_importances_
    print(f"\n  🔍 Features mais importantes:")
    for nome, imp in sorted(
        zip(features_names, importancias),
        key=lambda x: x[1], reverse=True
    )[:5]:
        print(f"     {nome}: {imp*100:.1f}%")

    return modelo, {"mae": mae, "r2": r2}


def treinar_modelo_velas(X, y):
    """
    Treina o modelo para prever demanda de velas.
    """
    print("\n  🕯️  Treinando modelo de velas...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modelo = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )

    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2  = r2_score(y_test, y_pred)

    print(f"  📊 Modelo de Velas:")
    print(f"     MAE (Erro Médio): {mae:.4f} unidades")
    print(f"     R² (Precisão):    {r2:.4f} ({r2*100:.1f}%)")

    return modelo, {"mae": mae, "r2": r2}


# ================================================================
# ETAPA 4 — Salvar os modelos treinados
# ================================================================

def salvar_modelos(modelo_insumos, le_insumos, modelo_velas, metricas):
    """
    Salva os modelos treinados em disco.
    joblib é mais eficiente que pickle para modelos scikit-learn.
    """
    print("\n  💾 Salvando modelos...")

    # Cria a pasta se não existir
    os.makedirs("ml/modelo_salvo", exist_ok=True)

    # Salva cada artefato em um arquivo separado
    joblib.dump(modelo_insumos, "ml/modelo_salvo/modelo_insumos.pkl")
    joblib.dump(le_insumos,     "ml/modelo_salvo/encoder_insumos.pkl")
    joblib.dump(modelo_velas,   "ml/modelo_salvo/modelo_velas.pkl")
    joblib.dump(metricas,       "ml/modelo_salvo/metricas.pkl")

    print("  ✅ Modelos salvos em ml/modelo_salvo/")

    # Salva as métricas em texto legível também
    with open("ml/modelo_salvo/metricas.txt", "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("MÉTRICAS DO MODELO — VELAS ESTOQUE IA\n")
        f.write("=" * 50 + "\n")
        f.write(f"Data de treinamento: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        f.write("MODELO DE INSUMOS:\n")
        f.write(f"  MAE: {metricas['insumos']['mae']:.4f}\n")
        f.write(f"  R²:  {metricas['insumos']['r2']:.4f}\n\n")
        f.write("MODELO DE VELAS:\n")
        f.write(f"  MAE: {metricas['velas']['mae']:.4f}\n")
        f.write(f"  R²:  {metricas['velas']['r2']:.4f}\n")

    print("  ✅ Métricas salvas em ml/modelo_salvo/metricas.txt")


# ================================================================
# FUNÇÃO PRINCIPAL
# ================================================================

def main():
    print("\n" + "="*60)
    print("  🤖 TREINAMENTO DO MODELO DE MACHINE LEARNING")
    print("="*60 + "\n")

    db = SessionLocal()

    try:
        # PASSO 1 — Extrai os dados
        print("📊 ETAPA 1 — Extração de dados")
        df_insumos = extrair_dados_insumos(db)
        df_velas   = extrair_dados_velas(db)

        if df_insumos.empty or df_velas.empty:
            print("❌ Dados insuficientes. Rode gerar_dados.py primeiro!")
            return

        # PASSO 2 — Prepara as features
        print("\n🔧 ETAPA 2 — Preparação das features")
        X_ins, y_ins, le_ins = preparar_features_insumos(df_insumos)
        X_vel, y_vel         = preparar_features_velas(df_velas)
        print(f"  ✅ Insumos: {X_ins.shape[0]} amostras, {X_ins.shape[1]} features")
        print(f"  ✅ Velas:   {X_vel.shape[0]} amostras, {X_vel.shape[1]} features")

        # PASSO 3 — Treina os modelos
        print("\n🌲 ETAPA 3 — Treinamento")
        modelo_ins, metricas_ins = treinar_modelo_insumos(X_ins, y_ins, le_ins)
        modelo_vel, metricas_vel = treinar_modelo_velas(X_vel, y_vel)

        # PASSO 4 — Salva tudo
        print("\n💾 ETAPA 4 — Salvando modelos")
        metricas = {
            "insumos": metricas_ins,
            "velas":   metricas_vel
        }
        salvar_modelos(modelo_ins, le_ins, modelo_vel, metricas)

        print("\n" + "="*60)
        print("  ✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("="*60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()