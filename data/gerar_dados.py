# ================================================================
# gerar_dados.py — Versão corrigida com códigos únicos garantidos
# ================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
import random
from datetime import datetime, timedelta
import pandas as pd

from src.database import SessionLocal, engine
from src.models import (
    Base, Insumo, VelaPronta,
    MovimentacaoInsumo, MovimentacaoVela
)

fake = Faker("pt_BR")
random.seed(42)

# ================================================================
# CATÁLOGO — com códigos curtos ÚNICOS para cada item
# ================================================================

CORES = {
    "Branco Clássico":    "BRC",
    "Marfim":             "MAR",
    "Rosa Quartzo":       "ROQ",
    "Lavanda":            "LAV",
    "Azul Serenidade":    "AZS",
    "Verde Sage":         "VES",
    "Terracota":          "TER",
    "Preto Obsidiana":    "PRO",
    "Dourado":            "DOU",
    "Vermelho Bordeaux":  "VEB",
}

FORMATOS = {
    "Cilíndrica":  "CIL",
    "Cônica":      "CON",
    "Quadrada":    "QUA",
    "Esférica":    "ESF",
    "Pilar":       "PIL",
    "Votiva":      "VOT",
    "Flutuante":   "FLU",
    "Container":   "CTR",
    "Escultural":  "ESC",
    "Tealight":    "TEA",
}

PERFUMES = {
    "Lavanda & Baunilha":  "LVB",
    "Rosa Búlgara":        "RSB",
    "Sândalo & Âmbar":     "SDA",
    "Cedro & Bergamota":   "CDB",
    "Jasmim Noturno":      "JSN",
    "Baunilha & Canela":   "BVC",
    "Eucalipto & Hortelã": "EUH",
    "Patchouli & Vetiver": "PTV",
    "Figo & Madeira":      "FGM",
    "Sem Perfume":         "SNP",
}

TAMANHOS = {
    "P": {"peso": 80,  "queima": 20, "fator": 1.0},
    "M": {"peso": 180, "queima": 45, "fator": 2.2},
    "G": {"peso": 350, "queima": 80, "fator": 3.8},
}

PRECO_BASE = {
    "Cilíndrica": 25.0, "Cônica": 28.0,   "Quadrada": 30.0,
    "Esférica":   35.0, "Pilar":  32.0,   "Votiva":   18.0,
    "Flutuante":  22.0, "Container": 38.0,"Escultural":45.0,
    "Tealight":   12.0,
}

SAZONALIDADE = {
    1:0.7, 2:0.8, 3:0.9,  4:1.0,
    5:1.8, 6:0.8, 7:0.9,  8:1.0,
    9:1.1, 10:1.2,11:1.4, 12:2.0
}

CANAIS = ["Instagram","Feira Artesanal","Loja Online",
          "Indicação","WhatsApp","Mercado Local"]

FORNECEDORES = [
    "Aromas Brasil Ltda","Ceras & Cia","Embalagens Premium",
    "NaturaCera Fornecimentos","Essências do Vale",
    "Pavios & Moldes ME","Corantes Naturais Brasil"
]


# ================================================================
# FUNÇÃO 1 — Insumos
# ================================================================

def criar_insumos(db):
    print("📦 Criando insumos...")

    insumos_data = [
        {"nome":"Cera de Parafina","categoria":"Cera","unidade":"kg",
         "qtd":85.0,"min":20.0,"ideal":100.0,"preco":12.50,"forn":"Ceras & Cia"},
        {"nome":"Cera de Soja","categoria":"Cera","unidade":"kg",
         "qtd":60.0,"min":15.0,"ideal":80.0,"preco":18.90,"forn":"Ceras & Cia"},
        {"nome":"Cera de Carnaúba","categoria":"Cera","unidade":"kg",
         "qtd":30.0,"min":8.0,"ideal":40.0,"preco":32.00,"forn":"NaturaCera Fornecimentos"},
        {"nome":"Cera de Abelha","categoria":"Cera","unidade":"kg",
         "qtd":15.0,"min":5.0,"ideal":25.0,"preco":45.00,"forn":"NaturaCera Fornecimentos"},
        {"nome":"Essência Lavanda & Baunilha","categoria":"Essência","unidade":"litro",
         "qtd":4.5,"min":1.0,"ideal":6.0,"preco":89.00,"forn":"Aromas Brasil Ltda"},
        {"nome":"Essência Rosa Búlgara","categoria":"Essência","unidade":"litro",
         "qtd":3.2,"min":0.8,"ideal":5.0,"preco":125.00,"forn":"Essências do Vale"},
        {"nome":"Essência Sândalo & Âmbar","categoria":"Essência","unidade":"litro",
         "qtd":2.8,"min":0.8,"ideal":4.0,"preco":98.00,"forn":"Aromas Brasil Ltda"},
        {"nome":"Essência Cedro & Bergamota","categoria":"Essência","unidade":"litro",
         "qtd":2.0,"min":0.5,"ideal":3.5,"preco":112.00,"forn":"Essências do Vale"},
        {"nome":"Essência Baunilha & Canela","categoria":"Essência","unidade":"litro",
         "qtd":5.0,"min":1.2,"ideal":7.0,"preco":76.00,"forn":"Aromas Brasil Ltda"},
        {"nome":"Essência Jasmim Noturno","categoria":"Essência","unidade":"litro",
         "qtd":2.5,"min":0.6,"ideal":4.0,"preco":95.00,"forn":"Essências do Vale"},
        {"nome":"Pavio Algodão 15cm","categoria":"Pavio","unidade":"unidade",
         "qtd":800,"min":200,"ideal":1000,"preco":0.45,"forn":"Pavios & Moldes ME"},
        {"nome":"Pavio Algodão 20cm","categoria":"Pavio","unidade":"unidade",
         "qtd":500,"min":150,"ideal":700,"preco":0.60,"forn":"Pavios & Moldes ME"},
        {"nome":"Corante Branco/Marfim","categoria":"Corante","unidade":"kg",
         "qtd":2.5,"min":0.5,"ideal":3.0,"preco":55.00,"forn":"Corantes Naturais Brasil"},
        {"nome":"Corante Rosa/Vermelho","categoria":"Corante","unidade":"kg",
         "qtd":1.8,"min":0.4,"ideal":2.5,"preco":62.00,"forn":"Corantes Naturais Brasil"},
        {"nome":"Corante Azul/Lavanda","categoria":"Corante","unidade":"kg",
         "qtd":1.5,"min":0.3,"ideal":2.0,"preco":58.00,"forn":"Corantes Naturais Brasil"},
        {"nome":"Corante Verde/Terracota/Dourado","categoria":"Corante","unidade":"kg",
         "qtd":1.2,"min":0.3,"ideal":2.0,"preco":65.00,"forn":"Corantes Naturais Brasil"},
        {"nome":"Pote de Vidro 80ml (P)","categoria":"Recipiente","unidade":"unidade",
         "qtd":300,"min":80,"ideal":400,"preco":3.20,"forn":"Embalagens Premium"},
        {"nome":"Pote de Vidro 200ml (M)","categoria":"Recipiente","unidade":"unidade",
         "qtd":250,"min":60,"ideal":350,"preco":5.80,"forn":"Embalagens Premium"},
        {"nome":"Pote de Vidro 400ml (G)","categoria":"Recipiente","unidade":"unidade",
         "qtd":150,"min":40,"ideal":200,"preco":9.50,"forn":"Embalagens Premium"},
        {"nome":"Caixa Kraft Individual","categoria":"Embalagem","unidade":"unidade",
         "qtd":500,"min":100,"ideal":600,"preco":1.80,"forn":"Embalagens Premium"},
    ]

    criados = []
    for d in insumos_data:
        ins = Insumo(
            nome=d["nome"], categoria=d["categoria"],
            unidade_medida=d["unidade"], quantidade_atual=d["qtd"],
            quantidade_minima=d["min"], quantidade_ideal=d["ideal"],
            preco_unitario=d["preco"], fornecedor=d["forn"],
            criado_em=datetime.now() - timedelta(days=365)
        )
        db.add(ins)
        criados.append(ins)

    db.commit()
    print(f"  ✅ {len(criados)} insumos criados!")
    return criados


# ================================================================
# FUNÇÃO 2 — Velas com códigos ÚNICOS garantidos
# ================================================================

def criar_velas(db):
    print("🕯️  Criando velas prontas...")

    criadas = []
    codigos_usados = set()  # Controla códigos já usados — evita duplicatas

    for fmt_nome, fmt_cod in FORMATOS.items():
        for cor_nome, cor_cod in CORES.items():
            for perf_nome, perf_cod in PERFUMES.items():
                for tam, info in TAMANHOS.items():

                    # Código 100% único: FMT-COR-PRF-TAM
                    codigo = f"{fmt_cod}-{cor_cod}-{perf_cod}-{tam}"

                    # Dupla verificação — pula se já existir
                    if codigo in codigos_usados:
                        continue
                    codigos_usados.add(codigo)

                    preco  = round(PRECO_BASE[fmt_nome] * info["fator"], 2)
                    custo  = round(preco * 0.35, 2)
                    estoque = random.randint(5, 30)

                    vela = VelaPronta(
                        codigo_produto=codigo,
                        cor=cor_nome, formato=fmt_nome,
                        perfume=perf_nome, tamanho=tam,
                        peso_gramas=info["peso"],
                        tempo_queima_horas=info["queima"],
                        preco_venda=preco, custo_producao=custo,
                        quantidade_estoque=estoque,
                        estoque_minimo=5,
                        criado_em=datetime.now() - timedelta(days=365)
                    )
                    db.add(vela)
                    criadas.append(vela)

                    if len(criadas) % 200 == 0:
                        db.commit()
                        print(f"  ... {len(criadas)} velas criadas")

    db.commit()
    print(f"  ✅ {len(criadas)} SKUs de velas criados!")
    return criadas


# ================================================================
# FUNÇÃO 3 — Histórico de 12 meses
# ================================================================

def gerar_historico(db, insumos, velas):
    print("📊 Gerando histórico de 12 meses...")

    data_inicio = datetime.now() - timedelta(days=365)
    total = 0

    for dia in range(365):
        data_atual = data_inicio + timedelta(days=dia)
        mes    = data_atual.month
        fator  = SAZONALIDADE[mes]

        # Vendas diárias de velas
        num_vendas = max(0, int(random.gauss(3 * fator, 1)))
        for _ in range(num_vendas):
            vela = random.choice(velas)
            if vela.quantidade_estoque <= 0:
                continue
            qtd = min(random.randint(1, 3), vela.quantidade_estoque)
            ant = vela.quantidade_estoque
            vela.quantidade_estoque -= qtd
            db.add(MovimentacaoVela(
                vela_id=vela.id, tipo="saida",
                quantidade=qtd, estoque_anterior=ant,
                estoque_posterior=vela.quantidade_estoque,
                canal_venda=random.choice(CANAIS),
                observacao=f"Venda — {random.choice(CANAIS)}",
                data_movimentacao=data_atual
            ))
            total += 1

        # Reposição de insumos a cada 15 dias
        if dia % 15 == 0:
            for ins in random.sample(insumos, min(5, len(insumos))):
                if ins.quantidade_atual < ins.quantidade_ideal * 0.5:
                    qtd_rep = ins.quantidade_ideal - ins.quantidade_atual
                    ant_ins = ins.quantidade_atual
                    ins.quantidade_atual += qtd_rep
                    db.add(MovimentacaoInsumo(
                        insumo_id=ins.id, tipo="entrada",
                        quantidade=qtd_rep, estoque_anterior=ant_ins,
                        estoque_posterior=ins.quantidade_atual,
                        observacao=f"Compra — NF {fake.numerify('####')}",
                        data_movimentacao=data_atual
                    ))
                    total += 1

        # Uso de insumos na produção a cada 7 dias
        if dia % 7 == 0:
            for ins in random.sample(insumos, min(8, len(insumos))):
                uso = ins.quantidade_atual * random.uniform(0.05, 0.15)
                if uso > 0 and ins.quantidade_atual >= uso:
                    ant_ins = ins.quantidade_atual
                    ins.quantidade_atual -= uso
                    db.add(MovimentacaoInsumo(
                        insumo_id=ins.id, tipo="saida",
                        quantidade=round(uso, 3),
                        estoque_anterior=ant_ins,
                        estoque_posterior=ins.quantidade_atual,
                        observacao="Uso na produção semanal",
                        data_movimentacao=data_atual
                    ))
                    total += 1

        if total % 500 == 0 and total > 0:
            db.commit()
            print(f"  ... {total} movimentações registradas")

    db.commit()
    print(f"  ✅ {total} movimentações geradas!")


# ================================================================
# FUNÇÃO PRINCIPAL
# ================================================================

def main():
    print("\n" + "="*60)
    print("  🕯️  GERANDO DADOS DO SISTEMA VELAS ESTOQUE IA")
    print("="*60 + "\n")

    # Recria as tabelas do zero — garante banco limpo
    print("🗄️  Recriando banco de dados do zero...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("  ✅ Banco limpo e recriado!\n")

    db = SessionLocal()
    try:
        insumos  = criar_insumos(db)
        velas    = criar_velas(db)
        velas_db = db.query(VelaPronta).all()
        gerar_historico(db, insumos, velas_db)

        # Exporta CSVs
        print("\n📄 Exportando CSVs...")
        pd.DataFrame([{
            "id":i.id,"nome":i.nome,"categoria":i.categoria,
            "unidade":i.unidade_medida,"qtd_atual":i.quantidade_atual,
            "qtd_minima":i.quantidade_minima,"preco":i.preco_unitario,
            "fornecedor":i.fornecedor
        } for i in insumos]).to_csv("data/insumos.csv", index=False)

        velas_sample = db.query(VelaPronta).limit(100).all()
        pd.DataFrame([{
            "codigo":v.codigo_produto,"cor":v.cor,"formato":v.formato,
            "perfume":v.perfume,"tamanho":v.tamanho,
            "preco":v.preco_venda,"estoque":v.quantidade_estoque
        } for v in velas_sample]).to_csv("data/produtos.csv", index=False)

        print("  ✅ data/insumos.csv criado")
        print("  ✅ data/produtos.csv criado")

        from src.models import MovimentacaoInsumo, MovimentacaoVela
        print("\n" + "="*60)
        print("  ✅ DADOS GERADOS COM SUCESSO!")
        print("="*60)
        print(f"  📦 Insumos:         {db.query(Insumo).count()}")
        print(f"  🕯️  SKUs de velas:   {db.query(VelaPronta).count()}")
        print(f"  📊 Movimentações:   {db.query(MovimentacaoInsumo).count() + db.query(MovimentacaoVela).count()}")
        print("="*60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()