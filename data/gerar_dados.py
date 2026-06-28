# ================================================================
# gerar_dados.py — Gera dados falsos mas realistas para o projeto
# Simula 12 meses de operação de uma fábrica de velas artesanais
# Isso é fundamental para treinar o modelo de Machine Learning
# ================================================================

import sys
import os

# Adiciona a pasta raiz do projeto ao caminho de busca do Python
# Isso permite importar módulos de outras pastas do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker          # Gera dados falsos realistas
import random                    # Gera números aleatórios
from datetime import datetime, timedelta  # Manipula datas
import pandas as pd              # Manipula dados em tabela

from src.database import SessionLocal, criar_tabelas, engine
from src.models import (
    Insumo, VelaPronta, MovimentacaoInsumo,
    MovimentacaoVela, CategoriaInsumo
)

# Configura o Faker para gerar dados em português do Brasil
fake = Faker("pt_BR")

# Semente aleatória — garante que os dados gerados sejam sempre iguais
# Isso é importante para reprodutibilidade do projeto
random.seed(42)

# ================================================================
# DEFINIÇÃO DO CATÁLOGO COMPLETO
# ================================================================

CORES = [
    "Branco Clássico", "Marfim", "Rosa Quartzo", "Lavanda",
    "Azul Serenidade", "Verde Sage", "Terracota",
    "Preto Obsidiana", "Dourado", "Vermelho Bordeaux"
]

FORMATOS = [
    "Cilíndrica", "Cônica", "Quadrada", "Esférica", "Pilar",
    "Votiva", "Flutuante", "Container", "Escultural", "Tealight"
]

PERFUMES = [
    "Lavanda & Baunilha", "Rosa Búlgara", "Sândalo & Âmbar",
    "Cedro & Bergamota", "Jasmim Noturno", "Baunilha & Canela",
    "Eucalipto & Hortelã", "Patchouli & Vetiver",
    "Figo & Madeira", "Sem Perfume"
]

TAMANHOS = {
    "P": {"peso": 80,  "queima": 20, "fator_preco": 1.0},
    "M": {"peso": 180, "queima": 45, "fator_preco": 2.2},
    "G": {"peso": 350, "queima": 80, "fator_preco": 3.8},
}

# Preço base por formato (velas mais elaboradas custam mais)
PRECO_BASE_FORMATO = {
    "Cilíndrica": 25.0,  "Cônica": 28.0,    "Quadrada": 30.0,
    "Esférica": 35.0,    "Pilar": 32.0,      "Votiva": 18.0,
    "Flutuante": 22.0,   "Container": 38.0,  "Escultural": 45.0,
    "Tealight": 12.0
}

# Popularidade de cada combinação (afeta a demanda simulada)
# Cores mais vendidas têm peso maior
POPULARIDADE_COR = {
    "Branco Clássico": 3, "Marfim": 2, "Rosa Quartzo": 3,
    "Lavanda": 2, "Azul Serenidade": 1, "Verde Sage": 1,
    "Terracota": 2, "Preto Obsidiana": 1, "Dourado": 2,
    "Vermelho Bordeaux": 1
}

# Fornecedores dos insumos
FORNECEDORES = [
    "Aromas Brasil Ltda", "Ceras & Cia", "Embalagens Premium",
    "NaturaCera Fornecimentos", "Essências do Vale",
    "Pavios & Moldes ME", "Corantes Naturais Brasil"
]


# ================================================================
# FUNÇÃO 1 — Criar os Insumos
# ================================================================

def criar_insumos(db):
    """
    Cria os 20 insumos principais de fabricação de velas.
    Cada insumo tem estoque inicial realista.
    """
    print("📦 Criando insumos...")

    # Lista completa de insumos com seus dados
    insumos_data = [
        # CERAS (base de todas as velas)
        {"nome": "Cera de Parafina", "categoria": "Cera",
         "unidade": "kg", "qtd": 85.0, "minimo": 20.0,
         "ideal": 100.0, "preco": 12.50, "fornecedor": "Ceras & Cia"},

        {"nome": "Cera de Soja", "categoria": "Cera",
         "unidade": "kg", "qtd": 60.0, "minimo": 15.0,
         "ideal": 80.0, "preco": 18.90, "fornecedor": "Ceras & Cia"},

        {"nome": "Cera de Carnaúba", "categoria": "Cera",
         "unidade": "kg", "qtd": 30.0, "minimo": 8.0,
         "ideal": 40.0, "preco": 32.00, "fornecedor": "NaturaCera Fornecimentos"},

        {"nome": "Cera de Abelha", "categoria": "Cera",
         "unidade": "kg", "qtd": 15.0, "minimo": 5.0,
         "ideal": 25.0, "preco": 45.00, "fornecedor": "NaturaCera Fornecimentos"},

        # ESSÊNCIAS (perfumes — 10 tipos)
        {"nome": "Essência Lavanda & Baunilha", "categoria": "Essência",
         "unidade": "litro", "qtd": 4.5, "minimo": 1.0,
         "ideal": 6.0, "preco": 89.00, "fornecedor": "Aromas Brasil Ltda"},

        {"nome": "Essência Rosa Búlgara", "categoria": "Essência",
         "unidade": "litro", "qtd": 3.2, "minimo": 0.8,
         "ideal": 5.0, "preco": 125.00, "fornecedor": "Essências do Vale"},

        {"nome": "Essência Sândalo & Âmbar", "categoria": "Essência",
         "unidade": "litro", "qtd": 2.8, "minimo": 0.8,
         "ideal": 4.0, "preco": 98.00, "fornecedor": "Aromas Brasil Ltda"},

        {"nome": "Essência Cedro & Bergamota", "categoria": "Essência",
         "unidade": "litro", "qtd": 2.0, "minimo": 0.5,
         "ideal": 3.5, "preco": 112.00, "fornecedor": "Essências do Vale"},

        {"nome": "Essência Baunilha & Canela", "categoria": "Essência",
         "unidade": "litro", "qtd": 5.0, "minimo": 1.2,
         "ideal": 7.0, "preco": 76.00, "fornecedor": "Aromas Brasil Ltda"},

        # PAVIOS
        {"nome": "Pavio Algodão 15cm", "categoria": "Pavio",
         "unidade": "unidade", "qtd": 800, "minimo": 200,
         "ideal": 1000, "preco": 0.45, "fornecedor": "Pavios & Moldes ME"},

        {"nome": "Pavio Algodão 20cm", "categoria": "Pavio",
         "unidade": "unidade", "qtd": 500, "minimo": 150,
         "ideal": 700, "preco": 0.60, "fornecedor": "Pavios & Moldes ME"},

        # CORANTES (10 cores)
        {"nome": "Corante Branco/Marfim", "categoria": "Corante",
         "unidade": "kg", "qtd": 2.5, "minimo": 0.5,
         "ideal": 3.0, "preco": 55.00, "fornecedor": "Corantes Naturais Brasil"},

        {"nome": "Corante Rosa/Vermelho", "categoria": "Corante",
         "unidade": "kg", "qtd": 1.8, "minimo": 0.4,
         "ideal": 2.5, "preco": 62.00, "fornecedor": "Corantes Naturais Brasil"},

        {"nome": "Corante Azul/Lavanda", "categoria": "Corante",
         "unidade": "kg", "qtd": 1.5, "minimo": 0.3,
         "ideal": 2.0, "preco": 58.00, "fornecedor": "Corantes Naturais Brasil"},

        {"nome": "Corante Verde/Terracota/Dourado", "categoria": "Corante",
         "unidade": "kg", "qtd": 1.2, "minimo": 0.3,
         "ideal": 2.0, "preco": 65.00, "fornecedor": "Corantes Naturais Brasil"},

        # RECIPIENTES/POTES
        {"nome": "Pote de Vidro 80ml (P)", "categoria": "Recipiente",
         "unidade": "unidade", "qtd": 300, "minimo": 80,
         "ideal": 400, "preco": 3.20, "fornecedor": "Embalagens Premium"},

        {"nome": "Pote de Vidro 200ml (M)", "categoria": "Recipiente",
         "unidade": "unidade", "qtd": 250, "minimo": 60,
         "ideal": 350, "preco": 5.80, "fornecedor": "Embalagens Premium"},

        {"nome": "Pote de Vidro 400ml (G)", "categoria": "Recipiente",
         "unidade": "unidade", "qtd": 150, "minimo": 40,
         "ideal": 200, "preco": 9.50, "fornecedor": "Embalagens Premium"},

        # EMBALAGENS
        {"nome": "Caixa Kraft Individual", "categoria": "Embalagem",
         "unidade": "unidade", "qtd": 500, "minimo": 100,
         "ideal": 600, "preco": 1.80, "fornecedor": "Embalagens Premium"},

        {"nome": "Fita de Cetim 1cm", "categoria": "Embalagem",
         "unidade": "metro", "qtd": 200, "minimo": 50,
         "ideal": 300, "preco": 0.35, "fornecedor": "Embalagens Premium"},
    ]

    # Cria cada insumo no banco de dados
    insumos_criados = []
    for dados in insumos_data:
        insumo = Insumo(
            nome=dados["nome"],
            categoria=dados["categoria"],
            unidade_medida=dados["unidade"],
            quantidade_atual=dados["qtd"],
            quantidade_minima=dados["minimo"],
            quantidade_ideal=dados["ideal"],
            preco_unitario=dados["preco"],
            fornecedor=dados["fornecedor"],
            criado_em=datetime.now() - timedelta(days=365)
            # Simula que foi cadastrado há 1 ano
        )
        db.add(insumo)        # Adiciona à sessão (ainda não salva)
        insumos_criados.append(insumo)

    db.commit()   # Salva todos de uma vez no banco
    print(f"  ✅ {len(insumos_criados)} insumos criados!")
    return insumos_criados


# ================================================================
# FUNÇÃO 2 — Criar as Velas Prontas
# Cria um subconjunto representativo das 3.000 combinações
# ================================================================

def criar_velas(db):
    """
    Cria 200 SKUs de velas representando as combinações mais vendidas.
    SKU = Stock Keeping Unit = código único de cada produto.
    """
    print("🕯️  Criando velas prontas...")

    velas_criadas = []

    # Seleciona combinações com base na popularidade
    # Formatos mais vendidos no mercado artesanal
    formatos_principais = ["Container", "Cilíndrica", "Votiva",
                           "Tealight", "Pilar", "Quadrada",
                           "Cônica", "Esférica", "Flutuante", "Escultural"]

    contador = 0
    for formato in formatos_principais:
        for cor in CORES:
            for perfume in random.sample(PERFUMES, 4):  # 4 perfumes por cor/formato
                for tamanho, info in TAMANHOS.items():

                    # Cria o código único do produto
                    # Exemplo: CON-BRA-LAV-M = Container, Branco, Lavanda, Médio
                    cod_formato = formato[:3].upper()
                    cod_cor     = cor[:3].upper()
                    cod_perfume = perfume[:3].upper()
                    codigo = f"{cod_formato}-{cod_cor}-{cod_perfume}-{tamanho}"

                    # Verifica se já existe (evita duplicatas)
                    existe = db.query(VelaPronta).filter_by(
                        codigo_produto=codigo
                    ).first()
                    if existe:
                        continue

                    # Calcula preço baseado no formato e tamanho
                    preco_base   = PRECO_BASE_FORMATO[formato]
                    preco_venda  = round(preco_base * info["fator_preco"], 2)
                    custo        = round(preco_venda * 0.35, 2)  # Custo = 35% do preço

                    # Estoque inicial aleatório mas realista
                    pop = POPULARIDADE_COR.get(cor, 1)
                    estoque_inicial = random.randint(5 * pop, 20 * pop)

                    vela = VelaPronta(
                        codigo_produto=codigo,
                        cor=cor,
                        formato=formato,
                        perfume=perfume,
                        tamanho=tamanho,
                        peso_gramas=info["peso"],
                        tempo_queima_horas=info["queima"],
                        preco_venda=preco_venda,
                        custo_producao=custo,
                        quantidade_estoque=estoque_inicial,
                        estoque_minimo=5,
                        criado_em=datetime.now() - timedelta(days=365)
                    )
                    db.add(vela)
                    velas_criadas.append(vela)
                    contador += 1

                    # Salva em lotes de 100 para não sobrecarregar a memória
                    if contador % 100 == 0:
                        db.commit()
                        print(f"  ... {contador} velas criadas")

    db.commit()
    print(f"  ✅ {contador} SKUs de velas criados!")
    return velas_criadas


# ================================================================
# FUNÇÃO 3 — Gerar Histórico de Movimentações (12 meses)
# Essa é a parte mais importante para o Machine Learning!
# ================================================================

def gerar_historico(db, insumos, velas):
    """
    Simula 12 meses de movimentações realistas.
    Inclui sazonalidade (mais vendas no fim de ano e Dia das Mães).
    """
    print("📊 Gerando histórico de 12 meses...")

    data_inicio = datetime.now() - timedelta(days=365)
    canais_venda = ["Instagram", "Feira Artesanal", "Loja Online",
                    "Indicação", "WhatsApp", "Mercado Local"]

    # Fator de sazonalidade por mês (1.0 = normal, 2.0 = dobro das vendas)
    # Maio (Dia das Mães) e Dezembro (Natal) são os picos
    sazonalidade = {
        1: 0.7,   # Janeiro  — baixo (pós-festas)
        2: 0.8,   # Fevereiro
        3: 0.9,   # Março
        4: 1.0,   # Abril
        5: 1.8,   # Maio    — PICO (Dia das Mães) 🌸
        6: 0.8,   # Junho
        7: 0.9,   # Julho
        8: 1.0,   # Agosto
        9: 1.1,   # Setembro
        10: 1.2,  # Outubro
        11: 1.4,  # Novembro — subindo para o Natal
        12: 2.0,  # Dezembro — PICO (Natal/Ano Novo) 🎄
    }

    total_movim = 0

    # Itera dia a dia pelos últimos 365 dias
    for dia in range(365):
        data_atual = data_inicio + timedelta(days=dia)
        mes = data_atual.month
        fator = sazonalidade[mes]

        # --- Movimentações de VELAS (vendas diárias) ---
        # Quantas velas vender hoje (média de 3 vendas/dia, ajustada pela sazonalidade)
        num_vendas = int(random.gauss(3 * fator, 1))
        # random.gauss = distribuição normal (mais realista que aleatório puro)

        for _ in range(max(0, num_vendas)):
            # Escolhe uma vela aleatória ponderada pela popularidade
            vela = random.choice(velas)
            if vela.quantidade_estoque <= 0:
                continue

            qtd_venda = random.randint(1, 3)
            qtd_venda = min(qtd_venda, vela.quantidade_estoque)

            anterior = vela.quantidade_estoque
            vela.quantidade_estoque -= qtd_venda

            movim = MovimentacaoVela(
                vela_id=vela.id,
                tipo="saida",
                quantidade=qtd_venda,
                estoque_anterior=anterior,
                estoque_posterior=vela.quantidade_estoque,
                canal_venda=random.choice(canais_venda),
                observacao=f"Venda — {random.choice(canais_venda)}",
                data_movimentacao=data_atual
            )
            db.add(movim)
            total_movim += 1

        # --- Reposição de INSUMOS (a cada 15 dias, aproximadamente) ---
        if dia % 15 == 0:
            for insumo in random.sample(insumos, min(5, len(insumos))):
                # Repõe até atingir o nível ideal
                if insumo.quantidade_atual < insumo.quantidade_ideal * 0.5:
                    qtd_repor = insumo.quantidade_ideal - insumo.quantidade_atual
                    anterior_ins = insumo.quantidade_atual
                    insumo.quantidade_atual += qtd_repor

                    movim_ins = MovimentacaoInsumo(
                        insumo_id=insumo.id,
                        tipo="entrada",
                        quantidade=qtd_repor,
                        estoque_anterior=anterior_ins,
                        estoque_posterior=insumo.quantidade_atual,
                        observacao=f"Compra mensal — NF {fake.numerify('####')}",
                        data_movimentacao=data_atual
                    )
                    db.add(movim_ins)
                    total_movim += 1

        # --- Uso de INSUMOS na produção (a cada 7 dias) ---
        if dia % 7 == 0:
            for insumo in random.sample(insumos, min(8, len(insumos))):
                uso = insumo.quantidade_atual * random.uniform(0.05, 0.15)
                # Consome entre 5% e 15% do estoque atual
                if uso > 0 and insumo.quantidade_atual >= uso:
                    anterior_ins = insumo.quantidade_atual
                    insumo.quantidade_atual -= uso

                    movim_ins = MovimentacaoInsumo(
                        insumo_id=insumo.id,
                        tipo="saida",
                        quantidade=round(uso, 3),
                        estoque_anterior=anterior_ins,
                        estoque_posterior=insumo.quantidade_atual,
                        observacao="Uso na produção semanal",
                        data_movimentacao=data_atual
                    )
                    db.add(movim_ins)
                    total_movim += 1

        # Salva em lotes de 500 para performance
        if total_movim % 500 == 0 and total_movim > 0:
            db.commit()
            print(f"  ... {total_movim} movimentações registradas")

    db.commit()
    print(f"  ✅ {total_movim} movimentações geradas!")


# ================================================================
# FUNÇÃO PRINCIPAL — Orquestra tudo
# ================================================================

def main():
    print("\n" + "="*60)
    print("  🕯️  GERANDO DADOS DO SISTEMA VELAS ESTOQUE IA")
    print("="*60 + "\n")

    # Passo 1: Cria as tabelas no banco
    print("🗄️  Criando banco de dados...")
    criar_tabelas()

    # Passo 2: Abre sessão com o banco
    db = SessionLocal()

    try:
        # Passo 3: Verifica se já tem dados (evita duplicar)
        if db.query(Insumo).count() > 0:
            print("⚠️  Dados já existem! Apague o arquivo .db e rode novamente.")
            return

        # Passo 4: Cria os dados na ordem correta
        insumos = criar_insumos(db)
        velas   = criar_velas(db)

        # Precisa buscar as velas do banco para ter os IDs
        velas_db = db.query(VelaPronta).all()
        gerar_historico(db, insumos, velas_db)

        # Passo 5: Exporta resumo para CSV
        print("\n📄 Exportando resumo para CSV...")
        exportar_csv(db)

        print("\n" + "="*60)
        print("  ✅ DADOS GERADOS COM SUCESSO!")
        print("="*60)
        print(f"  📦 Insumos cadastrados:      {db.query(Insumo).count()}")
        print(f"  🕯️  SKUs de velas:            {db.query(VelaPronta).count()}")
        movim_total = (db.query(MovimentacaoInsumo).count() +
                      db.query(MovimentacaoVela).count())
        print(f"  📊 Movimentações geradas:    {movim_total}")
        print("="*60 + "\n")

    finally:
        db.close()  # Sempre fecha a conexão


def exportar_csv(db):
    """Exporta os dados principais para CSV para análise e documentação"""

    # Exporta insumos
    insumos = db.query(Insumo).all()
    dados_insumos = [{
        "id": i.id, "nome": i.nome, "categoria": i.categoria,
        "unidade": i.unidade_medida, "qtd_atual": i.quantidade_atual,
        "qtd_minima": i.quantidade_minima, "qtd_ideal": i.quantidade_ideal,
        "preco_unit": i.preco_unitario, "fornecedor": i.fornecedor
    } for i in insumos]
    pd.DataFrame(dados_insumos).to_csv("data/insumos.csv", index=False)
    print("  ✅ data/insumos.csv criado")

    # Exporta velas (primeiras 100 para não ficar pesado)
    velas = db.query(VelaPronta).limit(100).all()
    dados_velas = [{
        "codigo": v.codigo_produto, "cor": v.cor,
        "formato": v.formato, "perfume": v.perfume,
        "tamanho": v.tamanho, "preco": v.preco_venda,
        "estoque": v.quantidade_estoque
    } for v in velas]
    pd.DataFrame(dados_velas).to_csv("data/produtos.csv", index=False)
    print("  ✅ data/produtos.csv criado")


# Roda o main() somente se este arquivo for executado diretamente
if __name__ == "__main__":
    main()