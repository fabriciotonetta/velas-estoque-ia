# ================================================================
# prever_estoque.py — Usa o modelo treinado para fazer previsões
# Carrega os modelos salvos e gera previsões para o dashboard
# ================================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib                          # Carrega os modelos salvos
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.database import SessionLocal
from src.models import Insumo, VelaPronta, PrevisaoML
from src.estoque import EstoqueInsumos


class PrevisaoEstoque:
    """
    Classe que usa os modelos treinados para gerar previsões.
    Carrega os modelos uma única vez ao ser instanciada.
    """

    def __init__(self):
        """Carrega os modelos do disco ao criar a instância"""
        caminho = "ml/modelo_salvo/"

        try:
            # Carrega cada artefato salvo pelo treinar_modelo.py
            self.modelo_insumos = joblib.load(caminho + "modelo_insumos.pkl")
            self.encoder_insumos = joblib.load(caminho + "encoder_insumos.pkl")
            self.modelo_velas    = joblib.load(caminho + "modelo_velas.pkl")
            self.metricas        = joblib.load(caminho + "metricas.pkl")
            self.modelo_carregado = True
            print("✅ Modelos de ML carregados com sucesso!")
        except FileNotFoundError:
            # Se os modelos não existem, avisa mas não quebra o sistema
            self.modelo_carregado = False
            print("⚠️  Modelos não encontrados. Rode ml/treinar_modelo.py primeiro.")

    def prever_consumo_insumo(
        self,
        insumo: Insumo,
        dias_futuro: int = 30
    ) -> Dict:
        """
        Prevê o consumo de um insumo para os próximos N dias.
        Retorna a quantidade prevista e quando o estoque vai acabar.
        """
        if not self.modelo_carregado:
            return {"erro": "Modelo não carregado"}

        # Monta o array de features para hoje
        hoje = datetime.now()

        # Tenta transformar a categoria — se não conhecer, usa 0
        try:
            categoria_cod = self.encoder_insumos.transform([insumo.categoria])[0]
        except ValueError:
            categoria_cod = 0

        proporcao = (
            insumo.quantidade_atual / insumo.quantidade_ideal
            if insumo.quantidade_ideal > 0 else 0
        )

        # Array com as mesmas features usadas no treinamento
        features = np.array([[
            hoje.weekday(),           # dia_semana
            hoje.month,               # mes
            hoje.day,                 # dia_mes
            (hoje.month - 1) // 3 + 1,# trimestre
            categoria_cod,            # categoria (número)
            insumo.preco_unitario,    # preco_unitario
            insumo.quantidade_atual,  # estoque_atual
            insumo.quantidade_minima, # estoque_minimo
            insumo.quantidade_ideal,  # estoque_ideal
            proporcao,                # proporcao_estoque
            0                         # tipo=0 (saída = consumo)
        ]])

        # O modelo prevê o consumo diário médio
        consumo_previsto_diario = float(self.modelo_insumos.predict(features)[0])
        consumo_previsto_diario = max(0, consumo_previsto_diario)
        # max(0,...) garante que não retorna consumo negativo

        # Consumo total previsto para o período
        consumo_total = consumo_previsto_diario * dias_futuro

        # Estoque após o período previsto
        estoque_futuro = insumo.quantidade_atual - consumo_total

        # Em quantos dias o estoque vai acabar
        if consumo_previsto_diario > 0:
            dias_para_acabar = int(
                insumo.quantidade_atual / consumo_previsto_diario
            )
        else:
            dias_para_acabar = 999  # Não prevê acabar

        # Quantidade sugerida para repor
        quantidade_repor = max(
            0,
            insumo.quantidade_ideal - max(0, estoque_futuro)
        )

        # Nível de confiança baseado no R² do modelo
        confianca = self.metricas["insumos"]["r2"]

        return {
            "insumo_id":             insumo.id,
            "insumo_nome":           insumo.nome,
            "estoque_atual":         insumo.quantidade_atual,
            "consumo_diario_previsto": round(consumo_previsto_diario, 4),
            "consumo_total_previsto":  round(consumo_total, 2),
            "estoque_em_30_dias":      round(estoque_futuro, 2),
            "dias_para_acabar":        dias_para_acabar,
            "quantidade_repor":        round(quantidade_repor, 2),
            "custo_reposicao":         round(quantidade_repor * insumo.preco_unitario, 2),
            "nivel_urgencia":          self._calcular_urgencia(dias_para_acabar),
            "confianca_modelo":        round(confianca, 3)
        }

    def _calcular_urgencia(self, dias_para_acabar: int) -> str:
        """
        Classifica a urgência de reposição em 4 níveis.
        Isso aparece no dashboard com cores diferentes.
        """
        if dias_para_acabar <= 7:
            return "🔴 CRÍTICO"       # Menos de 1 semana
        elif dias_para_acabar <= 15:
            return "🟠 URGENTE"       # Menos de 2 semanas
        elif dias_para_acabar <= 30:
            return "🟡 ATENÇÃO"       # Menos de 1 mês
        else:
            return "🟢 NORMAL"        # Estoque confortável

    def prever_todos_insumos(self, db) -> List[Dict]:
        """
        Gera previsão para TODOS os insumos cadastrados.
        Essa é a função que o dashboard chama para montar o relatório.
        """
        insumos = db.query(Insumo).all()
        previsoes = []

        for insumo in insumos:
            previsao = self.prever_consumo_insumo(insumo)
            previsoes.append(previsao)

            # Salva a previsão no banco para histórico
            registro_ml = PrevisaoML(
                tipo_item="insumo",
                item_id=insumo.id,
                item_nome=insumo.nome,
                dias_para_acabar=previsao.get("dias_para_acabar"),
                quantidade_sugerida=previsao.get("quantidade_repor"),
                confianca=previsao.get("confianca_modelo"),
                gerado_em=datetime.now()
            )
            db.add(registro_ml)

        db.commit()

        # Ordena por urgência (os mais críticos primeiro)
        previsoes.sort(key=lambda x: x.get("dias_para_acabar", 999))
        return previsoes

    def prever_demanda_vela(
        self,
        vela: VelaPronta,
        dias_futuro: int = 30
    ) -> Dict:
        """
        Prevê a demanda de uma vela para os próximos N dias.
        """
        if not self.modelo_carregado:
            return {"erro": "Modelo não carregado"}

        hoje = datetime.now()
        mes  = hoje.month

        sazonalidade = {
            1: 0.7, 2: 0.8, 3: 0.9, 4: 1.0,
            5: 1.8, 6: 0.8, 7: 0.9, 8: 1.0,
            9: 1.1, 10: 1.2, 11: 1.4, 12: 2.0
        }

        tamanho_cod = {"P": 1, "M": 2, "G": 3}.get(vela.tamanho, 1)

        features = np.array([[
            hoje.weekday(),
            mes,
            (mes - 1) // 3 + 1,
            sazonalidade.get(mes, 1.0),
            tamanho_cod,
            vela.preco_venda,
            vela.peso_gramas,
            vela.quantidade_estoque
        ]])

        demanda_diaria = float(self.modelo_velas.predict(features)[0])
        demanda_diaria = max(0, demanda_diaria)

        demanda_total   = demanda_diaria * dias_futuro
        estoque_futuro  = vela.quantidade_estoque - demanda_total
        producao_sugerida = max(0, -estoque_futuro + vela.estoque_minimo)

        return {
            "codigo_produto":       vela.codigo_produto,
            "cor":                  vela.cor,
            "formato":              vela.formato,
            "tamanho":              vela.tamanho,
            "estoque_atual":        vela.quantidade_estoque,
            "demanda_diaria":       round(demanda_diaria, 2),
            "demanda_30_dias":      round(demanda_total, 1),
            "estoque_em_30_dias":   round(estoque_futuro, 1),
            "producao_sugerida":    int(producao_sugerida),
            "receita_prevista":     round(demanda_total * vela.preco_venda, 2)
        }

    def resumo_previsoes(self, db) -> Dict:
        """
        Gera um resumo executivo de todas as previsões.
        Usado pelo assistente de IA para criar o relatório em texto.
        """
        previsoes = self.prever_todos_insumos(db)

        criticos  = [p for p in previsoes if "CRÍTICO" in p.get("nivel_urgencia", "")]
        urgentes  = [p for p in previsoes if "URGENTE" in p.get("nivel_urgencia", "")]
        atencao   = [p for p in previsoes if "ATENÇÃO" in p.get("nivel_urgencia", "")]

        custo_total_reposicao = sum(
            p.get("custo_reposicao", 0) for p in previsoes
        )

        return {
            "total_insumos_analisados": len(previsoes),
            "criticos":                 len(criticos),
            "urgentes":                 len(urgentes),
            "atencao":                  len(atencao),
            "normais":                  len(previsoes) - len(criticos) - len(urgentes) - len(atencao),
            "custo_total_reposicao":    round(custo_total_reposicao, 2),
            "insumos_criticos":         [p["insumo_nome"] for p in criticos],
            "insumos_urgentes":         [p["insumo_nome"] for p in urgentes],
            "previsoes_detalhadas":     previsoes[:10],  # Top 10 mais urgentes
            "confianca_modelo":         self.metricas["insumos"]["r2"] if self.modelo_carregado else 0
        }


# ================================================================
# EXECUÇÃO DIRETA — Para testar as previsões no terminal
# ================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🔮 SISTEMA DE PREVISÕES — VELAS ESTOQUE IA")
    print("="*60 + "\n")

    previsor = PrevisaoEstoque()

    if not previsor.modelo_carregado:
        print("❌ Execute ml/treinar_modelo.py primeiro!")
        sys.exit(1)

    db = SessionLocal()
    try:
        resumo = previsor.resumo_previsoes(db)

        print(f"📊 RESUMO DAS PREVISÕES (próximos 30 dias):")
        print(f"   Total analisado:   {resumo['total_insumos_analisados']} insumos")
        print(f"   🔴 Críticos:       {resumo['criticos']}")
        print(f"   🟠 Urgentes:       {resumo['urgentes']}")
        print(f"   🟡 Atenção:        {resumo['atencao']}")
        print(f"   🟢 Normais:        {resumo['normais']}")
        print(f"   💰 Custo repor:    R$ {resumo['custo_total_reposicao']:.2f}")
        print(f"   🎯 Confiança ML:   {resumo['confianca_modelo']*100:.1f}%")

        if resumo["insumos_criticos"]:
            print(f"\n   🔴 CRÍTICOS: {', '.join(resumo['insumos_criticos'])}")

    finally:
        db.close()