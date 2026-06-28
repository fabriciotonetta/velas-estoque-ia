# ================================================================
# ia_assistente.py — Assistente de IA (versão simulada)
# Estrutura completa pronta para integrar Claude API real.
# Para ativar o Claude real: descomente o bloco "VERSÃO REAL"
# e adicione sua ANTHROPIC_API_KEY no arquivo .env
# ================================================================

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

from src.database import SessionLocal
from src.models import Insumo, VelaPronta
from src.estoque import EstoqueInsumos, EstoqueVelas

load_dotenv()


class AssistenteEstoque:
    """
    Assistente inteligente de gestão de estoque.
    Versão atual: simulada (sem custo de API).
    Versão Claude real: ativar bloco comentado abaixo.
    """

    def __init__(self):
        self.modelo = "claude-sonnet-4-6"  # Pronto para quando ativar
        self.ativo  = False                # False = simulado, True = Claude real

        # ── VERSÃO REAL (descomente quando tiver créditos) ──────
        # import anthropic
        # self.cliente = anthropic.Anthropic(
        #     api_key=os.getenv("ANTHROPIC_API_KEY")
        # )
        # self.ativo = True
        # ────────────────────────────────────────────────────────

        self.contexto_negocio = """
Você é um assistente especializado em gestão de estoque para uma
fabricante artesanal de velas chamada "Velas & Arte".
Sempre responda em português brasileiro de forma profissional e objetiva.
"""

    # ================================================================
    # MÉTODO 1 — Relatório completo
    # ================================================================

    def gerar_relatorio_estoque(self, db) -> str:
        """Gera relatório completo do estoque com análise de IA."""
        dados = self._coletar_dados_estoque(db)

        if self.ativo:
            return self._chamar_claude_relatorio(dados)

        # ── Resposta simulada realista ───────────────────────────
        n_alertas    = len(dados['insumos_alerta'])
        n_velas_alert= len(dados['velas_alerta'])
        receita      = dados['resumo_vendas']['receita_total']
        unidades     = dados['resumo_vendas']['total_unidades']
        top          = dados['top_vendidas']

        alertas_txt = ""
        if dados['insumos_alerta']:
            for i in dados['insumos_alerta'][:3]:
                deficit = i.get('deficit', 0)
                alertas_txt += f"   • {i['nome']}: déficit de {deficit} {i.get('unidade','un')} — contatar {i['fornecedor']}\n"
        else:
            alertas_txt = "   • Nenhum insumo em alerta crítico no momento.\n"

        top_txt = ""
        for v in top[:3]:
            top_txt += f"   • {v['codigo']} — {v['total_vendido']} unidades vendidas (R$ {v['receita_total']:.2f})\n"

        relatorio = f"""
📋 RELATÓRIO DE ESTOQUE — {datetime.now().strftime('%d/%m/%Y às %H:%M')}
{'='*55}

🚨 1. ALERTAS URGENTES
{alertas_txt}
   Total de insumos em alerta:  {n_alertas}
   Total de velas em alerta:    {n_velas_alert}

📊 2. SITUAÇÃO GERAL DO ESTOQUE
   • {len(dados['todos_insumos'])} insumos cadastrados no sistema
   • Vendas nos últimos 30 dias: {unidades} unidades
   • Receita no período: R$ {receita:.2f}
   • Ticket médio por venda: R$ {dados['resumo_vendas']['ticket_medio']:.2f}

📦 3. PLANO DE REPOSIÇÃO SUGERIDO
   Baseado no consumo médio dos últimos 30 dias:
{alertas_txt}
   ⚠️  Recomenda-se fazer os pedidos em até 5 dias úteis
   para evitar ruptura de estoque.

🕯️ 4. TOP 3 PRODUTOS MAIS VENDIDOS
{top_txt}
   Esses produtos devem ter estoque reforçado,
   especialmente em períodos de alta sazonalidade
   (Maio — Dia das Mães / Dezembro — Natal).

💡 5. RECOMENDAÇÕES ESTRATÉGICAS
   1. Mantenha estoque de segurança de 30 dias para
      insumos críticos (ceras e essências).
   2. Reforce a produção das velas mais vendidas antes
      dos picos sazonais de Maio e Dezembro.
   3. Negocie entregas quinzenais com fornecedores para
      reduzir capital imobilizado em estoque.
   4. Monitore diariamente os insumos em alerta vermelho.
   5. Considere diversificar fornecedores para insumos
      com alto consumo e poucos fornecedores cadastrados.

{'='*55}
⚙️  [MODO SIMULADO — Integração Claude API disponível]
    Para ativar análise real com IA, adicione créditos
    em console.anthropic.com e configure o .env
"""
        self._salvar_relatorio(relatorio, "relatorio_estoque")
        return relatorio

    # ================================================================
    # MÉTODO 2 — Sugestão de reposição
    # ================================================================

    def sugerir_reposicao(
        self,
        db,
        insumo_id: int,
        previsao_ml: Optional[Dict] = None
    ) -> str:
        """Sugestão de reposição para um insumo específico."""
        est    = EstoqueInsumos(db)
        insumo = est.buscar_por_id(insumo_id)

        if not insumo:
            return "❌ Insumo não encontrado."

        consumo = est.consumo_medio_diario(insumo_id)
        dias    = est.dias_ate_acabar(insumo_id)

        if self.ativo:
            return self._chamar_claude_reposicao(insumo, consumo, dias, previsao_ml)

        # ── Resposta simulada ────────────────────────────────────
        if dias is None or dias > 30:
            urgencia = "🟢 NORMAL"
            prazo    = "30 dias"
        elif dias > 15:
            urgencia = "🟡 ATENÇÃO"
            prazo    = "15 dias"
        elif dias > 7:
            urgencia = "🟠 URGENTE"
            prazo    = "5 dias úteis"
        else:
            urgencia = "🔴 CRÍTICO"
            prazo    = "IMEDIATO"

        qtd_repor = max(0, insumo.quantidade_ideal - insumo.quantidade_atual)
        custo     = round(qtd_repor * insumo.preco_unitario, 2)

        return f"""
🔍 ANÁLISE DE REPOSIÇÃO — {insumo.nome}
{'='*45}
Urgência: {urgencia}
Estoque atual:   {insumo.quantidade_atual:.2f} {insumo.unidade_medida}
Estoque mínimo:  {insumo.quantidade_minima:.2f} {insumo.unidade_medida}
Consumo diário:  {consumo:.4f} {insumo.unidade_medida}/dia
Dias restantes:  {dias if dias else 'N/A'} dias

📦 SUGESTÃO DE PEDIDO
   Quantidade:  {qtd_repor:.2f} {insumo.unidade_medida}
   Custo:       R$ {custo:.2f}
   Fornecedor:  {insumo.fornecedor}
   Prazo:       Fazer pedido em até {prazo}

⚙️  [MODO SIMULADO]
"""

    # ================================================================
    # MÉTODO 3 — Chat livre
    # ================================================================

    def chat(
        self,
        pergunta: str,
        db,
        historico_chat: List = None
    ) -> str:
        """Chat livre sobre o estoque."""
        dados = self._coletar_dados_estoque(db)

        if self.ativo:
            return self._chamar_claude_chat(pergunta, dados, historico_chat)

        # ── Respostas simuladas por palavra-chave ────────────────
        p = pergunta.lower()

        if any(w in p for w in ["natal", "dezembro", "fim de ano"]):
            return """
🎄 PREPARAÇÃO PARA O NATAL

O Natal é o pico máximo de vendas (fator 2.0x).
Recomendações:
- Reforce estoque de ceras em 100% até novembro
- Priorize velas Container e Cilíndrica (mais presentes)
- Aumente produção de perfumes Baunilha & Canela e Lavanda
- Prepare embalagens Kraft com antecedência (lead time maior)
- Meta: ter 60 dias de estoque em outubro

⚙️ [MODO SIMULADO]
"""
        elif any(w in p for w in ["mãe", "maio", "mothers"]):
            return """
🌸 PREPARAÇÃO PARA O DIA DAS MÃES

Segundo pico do ano (fator 1.8x) — ocorre em Maio.
Recomendações:
- Reforce estoque de Rosa Búlgara e Lavanda & Baunilha
- Velas Rosa Quartzo e Lavanda são as mais presentes
- Prepare kits de presente (vela + embalagem especial)
- Inicie preparação em Março para não faltar insumos

⚙️ [MODO SIMULADO]
"""
        elif any(w in p for w in ["urgente", "crítico", "faltando", "acabando"]):
            alertas = dados['insumos_alerta']
            if alertas:
                lista = "\n".join([f"• {i['nome']} (déficit: {i['deficit']})" for i in alertas[:5]])
                return f"""
🚨 INSUMOS MAIS URGENTES AGORA

{lista}

Ação recomendada: contate os fornecedores hoje mesmo
e solicite entrega expressa se possível.

⚙️ [MODO SIMULADO]
"""
            else:
                return "✅ Nenhum insumo em situação crítica no momento!"

        elif any(w in p for w in ["mais vendida", "vendidos", "popular"]):
            top = dados['top_vendidas'][:3]
            lista = "\n".join([f"• {v['codigo']}: {v['total_vendido']} unidades" for v in top])
            return f"""
🏆 PRODUTOS MAIS VENDIDOS

{lista}

Mantenha esses produtos sempre com estoque reforçado!

⚙️ [MODO SIMULADO]
"""
        else:
            return f"""
🤖 Entendi sua pergunta: "{pergunta}"

Com base no estoque atual:
- {len(dados['insumos_alerta'])} insumos precisam de atenção
- {len(dados['velas_alerta'])} velas com estoque baixo
- Receita últimos 30 dias: R$ {dados['resumo_vendas']['receita_total']:.2f}

Para análises mais detalhadas e personalizadas,
ative a integração com Claude AI no arquivo .env.

⚙️ [MODO SIMULADO]
"""

    # ================================================================
    # MÉTODO 4 — Análise de sazonalidade
    # ================================================================

    def analisar_sazonalidade(self, db) -> str:
        """Análise do padrão sazonal de vendas."""
        est_velas = EstoqueVelas(db)
        df        = est_velas.vendas_por_periodo(dias=365)

        if df.empty:
            return "⚠️ Dados insuficientes para análise."

        df['mes']    = df['data'].apply(lambda x: x.month)
        vendas_mes   = df.groupby('mes')['quantidade'].sum().to_dict()
        receita_mes  = df.groupby('mes')['receita'].sum().to_dict()

        mes_pico     = max(vendas_mes, key=vendas_mes.get)
        mes_baixo    = min(vendas_mes, key=vendas_mes.get)
        nomes_meses  = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",
                        5:"Maio",6:"Junho",7:"Julho",8:"Agosto",
                        9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

        if self.ativo:
            return self._chamar_claude_sazonalidade(vendas_mes, receita_mes)

        return f"""
📈 ANÁLISE DE SAZONALIDADE — Últimos 12 meses
{'='*50}

🏆 Mês de maior venda: {nomes_meses.get(mes_pico,'N/A')}
   ({vendas_mes.get(mes_pico,0):.0f} unidades / R$ {receita_mes.get(mes_pico,0):.2f})

📉 Mês de menor venda: {nomes_meses.get(mes_baixo,'N/A')}
   ({vendas_mes.get(mes_baixo,0):.0f} unidades / R$ {receita_mes.get(mes_baixo,0):.2f})

🎯 MESES CRÍTICOS PARA PREPARAR ESTOQUE:
   1. Abril  → preparar para o Dia das Mães (Maio)
   2. Outubro → preparar para o Natal (Dezembro)
   3. Novembro → reforço final para Natal/Ano Novo

📦 RECOMENDAÇÃO DE ESTOQUE PRÉ-PICO:
   • Aumente 80% nos meses antes dos picos
   • Mantenha 45 dias de cobertura em Outubro/Novembro
   • Reduza compras em Janeiro/Fevereiro (pós-festas)

⚡ AÇÃO PARA ESTE MÊS ({nomes_meses.get(datetime.now().month,'N/A')}):
   Verifique se o estoque cobre a demanda prevista
   para as próximas 4 semanas com base na sazonalidade.

⚙️  [MODO SIMULADO — Ative Claude API para análise real]
"""

    # ================================================================
    # MÉTODOS AUXILIARES
    # ================================================================

    def _coletar_dados_estoque(self, db) -> Dict:
        """Coleta todos os dados relevantes do banco."""
        est_ins   = EstoqueInsumos(db)
        est_velas = EstoqueVelas(db)

        insumos_alerta = [{
            "nome":      i.nome,
            "categoria": i.categoria,
            "atual":     round(i.quantidade_atual, 2),
            "minimo":    i.quantidade_minima,
            "deficit":   round(i.quantidade_minima - i.quantidade_atual, 2),
            "unidade":   i.unidade_medida,
            "preco":     i.preco_unitario,
            "fornecedor":i.fornecedor
        } for i in est_ins.insumos_em_alerta()]

        todos_insumos = [{
            "nome":   i.nome,
            "atual":  round(i.quantidade_atual, 2),
            "minimo": i.quantidade_minima,
            "status": "⚠️" if i.quantidade_atual <= i.quantidade_minima else "✅"
        } for i in est_ins.listar_todos()]

        velas_alerta = [{
            "codigo":  v.codigo_produto,
            "cor":     v.cor,
            "formato": v.formato,
            "tamanho": v.tamanho,
            "estoque": v.quantidade_estoque,
            "minimo":  v.estoque_minimo
        } for v in est_velas.velas_em_alerta()[:10]]

        top_vendidas  = est_velas.top_mais_vendidas(10)

        df = est_velas.vendas_por_periodo(30)
        resumo_vendas = {
            "periodo":       "últimos 30 dias",
            "total_unidades": int(df["quantidade"].sum()) if not df.empty else 0,
            "receita_total":  round(df["receita"].sum(), 2) if not df.empty else 0,
            "ticket_medio":   round(df["receita"].mean(), 2) if not df.empty else 0,
        }

        return {
            "insumos_alerta": insumos_alerta,
            "todos_insumos":  todos_insumos,
            "velas_alerta":   velas_alerta,
            "top_vendidas":   top_vendidas,
            "resumo_vendas":  resumo_vendas
        }

    def _salvar_relatorio(self, texto: str, nome: str):
        """Salva o relatório em arquivo .txt"""
        os.makedirs("docs/relatorios", exist_ok=True)
        ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = f"docs/relatorios/{nome}_{ts}.txt"
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"  ✅ Relatório salvo em {caminho}")

    # ── Métodos para Claude real (usados quando self.ativo = True) ──

    def _chamar_claude_relatorio(self, dados: Dict) -> str:
        prompt = f"Analise o estoque e gere relatório executivo:\n{json.dumps(dados, ensure_ascii=False)}"
        r = self.cliente.messages.create(
            model=self.modelo, max_tokens=2000,
            system=self.contexto_negocio,
            messages=[{"role":"user","content":prompt}]
        )
        texto = r.content[0].text
        self._salvar_relatorio(texto, "relatorio_estoque")
        return texto

    def _chamar_claude_reposicao(self, insumo, consumo, dias, previsao_ml) -> str:
        prompt = f"Sugira reposição para {insumo.nome}: estoque={insumo.quantidade_atual}, consumo={consumo}/dia, dias_restantes={dias}"
        r = self.cliente.messages.create(
            model=self.modelo, max_tokens=600,
            system=self.contexto_negocio,
            messages=[{"role":"user","content":prompt}]
        )
        return r.content[0].text

    def _chamar_claude_chat(self, pergunta, dados, historico) -> str:
        msgs = historico or []
        msgs.append({"role":"user","content":f"Contexto:{json.dumps(dados,ensure_ascii=False)}\n\nPergunta:{pergunta}"})
        r = self.cliente.messages.create(
            model=self.modelo, max_tokens=1000,
            system=self.contexto_negocio, messages=msgs
        )
        return r.content[0].text

    def _chamar_claude_sazonalidade(self, vendas_mes, receita_mes) -> str:
        prompt = f"Analise sazonalidade: vendas={vendas_mes}, receita={receita_mes}"
        r = self.cliente.messages.create(
            model=self.modelo, max_tokens=800,
            system=self.contexto_negocio,
            messages=[{"role":"user","content":prompt}]
        )
        return r.content[0].text


# ================================================================
# TESTE DIRETO
# ================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🤖 TESTANDO ASSISTENTE DE IA (MODO SIMULADO)")
    print("="*60 + "\n")

    assistente = AssistenteEstoque()
    db         = SessionLocal()

    try:
        print("📋 Gerando relatório completo...\n")
        print(assistente.gerar_relatorio_estoque(db))

        print("\n" + "="*60)
        print("💬 Testando chat...\n")
        print(assistente.chat("Quais insumos estão mais urgentes?", db))

    finally:
        db.close()