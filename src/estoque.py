# ================================================================
# estoque.py — Regras de negócio do sistema de estoque
# Aqui ficam todas as operações que o sistema pode fazer:
# consultar, adicionar, remover, alertar, etc.
# ================================================================

from sqlalchemy.orm import Session        # Tipo da sessão do banco
from sqlalchemy import desc, func         # Funções de ordenação e agregação
from datetime import datetime, timedelta  # Manipulação de datas
from typing import List, Optional, Dict   # Tipos para anotações
import pandas as pd                       # Manipulação de dados

from src.models import (
    Insumo, VelaPronta,
    MovimentacaoInsumo, MovimentacaoVela,
    PrevisaoML
)


# ================================================================
# CLASSE 1 — Operações com Insumos
# ================================================================

class EstoqueInsumos:
    """
    Centraliza todas as operações relacionadas a insumos.
    Cada método representa uma ação que o sistema pode fazer.
    """

    def __init__(self, db: Session):
        # Recebe a sessão do banco de dados ao ser criada
        # Isso é chamado de "injeção de dependência"
        self.db = db

    def listar_todos(self) -> List[Insumo]:
        """Retorna todos os insumos cadastrados, ordenados por nome"""
        return self.db.query(Insumo).order_by(Insumo.nome).all()

    def buscar_por_id(self, insumo_id: int) -> Optional[Insumo]:
        """Busca um insumo específico pelo seu ID"""
        return self.db.query(Insumo).filter(
            Insumo.id == insumo_id
        ).first()
        # .first() retorna o primeiro resultado ou None se não encontrar

    def buscar_por_categoria(self, categoria: str) -> List[Insumo]:
        """Retorna todos os insumos de uma categoria específica"""
        return self.db.query(Insumo).filter(
            Insumo.categoria == categoria
        ).order_by(Insumo.nome).all()

    def insumos_em_alerta(self) -> List[Insumo]:
        """
        Retorna insumos com estoque abaixo do mínimo.
        Esses são os que precisam de reposição URGENTE.
        """
        return self.db.query(Insumo).filter(
            Insumo.quantidade_atual <= Insumo.quantidade_minima
        ).order_by(Insumo.quantidade_atual).all()

    def registrar_entrada(
        self,
        insumo_id: int,
        quantidade: float,
        observacao: str = ""
    ) -> MovimentacaoInsumo:
        """
        Registra a ENTRADA de um insumo (compra/recebimento).
        Atualiza o estoque e cria um registro histórico.
        """
        # Busca o insumo no banco
        insumo = self.buscar_por_id(insumo_id)
        if not insumo:
            raise ValueError(f"Insumo ID {insumo_id} não encontrado")
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        # Guarda o valor antes para o histórico
        estoque_antes = insumo.quantidade_atual

        # Atualiza o estoque somando a quantidade recebida
        insumo.quantidade_atual += quantidade

        # Cria o registro histórico da movimentação
        movimentacao = MovimentacaoInsumo(
            insumo_id=insumo_id,
            tipo="entrada",
            quantidade=quantidade,
            estoque_anterior=estoque_antes,
            estoque_posterior=insumo.quantidade_atual,
            observacao=observacao,
            data_movimentacao=datetime.now()
        )

        self.db.add(movimentacao)   # Adiciona à sessão
        self.db.commit()            # Salva no banco
        self.db.refresh(movimentacao)  # Recarrega para pegar o ID gerado
        return movimentacao

    def registrar_saida(
        self,
        insumo_id: int,
        quantidade: float,
        observacao: str = "Uso na produção"
    ) -> MovimentacaoInsumo:
        """
        Registra a SAÍDA de um insumo (uso na fabricação).
        Verifica se há estoque suficiente antes de subtrair.
        """
        insumo = self.buscar_por_id(insumo_id)
        if not insumo:
            raise ValueError(f"Insumo ID {insumo_id} não encontrado")
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")

        # Regra de negócio: não pode sair mais do que tem em estoque
        if quantidade > insumo.quantidade_atual:
            raise ValueError(
                f"Estoque insuficiente. Disponível: "
                f"{insumo.quantidade_atual} {insumo.unidade_medida}"
            )

        estoque_antes = insumo.quantidade_atual
        insumo.quantidade_atual -= quantidade  # Subtrai do estoque

        movimentacao = MovimentacaoInsumo(
            insumo_id=insumo_id,
            tipo="saida",
            quantidade=quantidade,
            estoque_anterior=estoque_antes,
            estoque_posterior=insumo.quantidade_atual,
            observacao=observacao,
            data_movimentacao=datetime.now()
        )

        self.db.add(movimentacao)
        self.db.commit()
        self.db.refresh(movimentacao)
        return movimentacao

    def historico_movimentacoes(
        self,
        insumo_id: int,
        limite: int = 30
    ) -> List[MovimentacaoInsumo]:
        """
        Retorna as últimas N movimentações de um insumo.
        Ordenado do mais recente para o mais antigo.
        """
        return (
            self.db.query(MovimentacaoInsumo)
            .filter(MovimentacaoInsumo.insumo_id == insumo_id)
            .order_by(desc(MovimentacaoInsumo.data_movimentacao))
            .limit(limite)
            .all()
        )

    def consumo_medio_diario(self, insumo_id: int) -> float:
        """
        Calcula quanto desse insumo é consumido por dia em média.
        Usa os últimos 30 dias para o cálculo.
        Esse número alimenta o modelo de Machine Learning.
        """
        # Define o período de análise: últimos 30 dias
        data_limite = datetime.now() - timedelta(days=30)

        # Soma todas as saídas no período
        resultado = (
            self.db.query(func.sum(MovimentacaoInsumo.quantidade))
            .filter(
                MovimentacaoInsumo.insumo_id == insumo_id,
                MovimentacaoInsumo.tipo == "saida",
                MovimentacaoInsumo.data_movimentacao >= data_limite
            )
            .scalar()  # .scalar() retorna um único valor em vez de lista
        )

        # Se não houve saídas, retorna 0 para não dar erro
        total_saidas = resultado or 0.0

        # Divide pelo número de dias para obter a média diária
        return round(total_saidas / 30, 4)

    def dias_ate_acabar(self, insumo_id: int) -> Optional[int]:
        """
        Estima em quantos dias o insumo vai acabar.
        Fórmula: estoque_atual ÷ consumo_médio_diário
        Retorna None se o consumo for zero (não há previsão).
        """
        insumo = self.buscar_por_id(insumo_id)
        if not insumo:
            return None

        consumo_diario = self.consumo_medio_diario(insumo_id)

        # Se o consumo for zero, não conseguimos prever
        if consumo_diario == 0:
            return None

        # Calcula quantos dias restam com o estoque atual
        dias = insumo.quantidade_atual / consumo_diario
        return int(dias)

    def resumo_estoque(self) -> Dict:
        """
        Retorna um resumo geral do estoque de insumos.
        Usado pelo dashboard para os cards de resumo no topo.
        """
        todos = self.listar_todos()
        em_alerta = self.insumos_em_alerta()

        # Calcula o valor total do estoque
        valor_total = sum(
            i.quantidade_atual * i.preco_unitario for i in todos
        )

        return {
            "total_insumos":      len(todos),
            "em_alerta":          len(em_alerta),
            "valor_total_estoque": round(valor_total, 2),
            "insumos_criticos":   [i.nome for i in em_alerta]
        }


# ================================================================
# CLASSE 2 — Operações com Velas Prontas
# ================================================================

class EstoqueVelas:
    """
    Centraliza todas as operações de velas prontas (produtos acabados).
    """

    def __init__(self, db: Session):
        self.db = db

    def listar_todas(
        self,
        cor: str = None,
        formato: str = None,
        perfume: str = None,
        tamanho: str = None
    ) -> List[VelaPronta]:
        """
        Lista velas com filtros opcionais.
        Se não passar filtro, retorna todas.
        """
        # Começa com a query base
        query = self.db.query(VelaPronta)

        # Aplica os filtros que foram informados
        if cor:
            query = query.filter(VelaPronta.cor == cor)
        if formato:
            query = query.filter(VelaPronta.formato == formato)
        if perfume:
            query = query.filter(VelaPronta.perfume == perfume)
        if tamanho:
            query = query.filter(VelaPronta.tamanho == tamanho)

        return query.order_by(VelaPronta.codigo_produto).all()

    def buscar_por_codigo(self, codigo: str) -> Optional[VelaPronta]:
        """Busca uma vela pelo código único do produto"""
        return self.db.query(VelaPronta).filter(
            VelaPronta.codigo_produto == codigo
        ).first()

    def velas_em_alerta(self) -> List[VelaPronta]:
        """Retorna velas com estoque abaixo do mínimo"""
        return self.db.query(VelaPronta).filter(
            VelaPronta.quantidade_estoque <= VelaPronta.estoque_minimo
        ).order_by(VelaPronta.quantidade_estoque).all()

    def registrar_venda(
        self,
        codigo_produto: str,
        quantidade: int,
        canal_venda: str = "Direto"
    ) -> MovimentacaoVela:
        """
        Registra a venda de velas prontas.
        Subtrai do estoque e cria registro histórico.
        """
        vela = self.buscar_por_codigo(codigo_produto)
        if not vela:
            raise ValueError(f"Produto {codigo_produto} não encontrado")
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        if quantidade > vela.quantidade_estoque:
            raise ValueError(
                f"Estoque insuficiente. Disponível: {vela.quantidade_estoque} unidades"
            )

        estoque_antes = vela.quantidade_estoque
        vela.quantidade_estoque -= quantidade

        movimentacao = MovimentacaoVela(
            vela_id=vela.id,
            tipo="saida",
            quantidade=quantidade,
            estoque_anterior=estoque_antes,
            estoque_posterior=vela.quantidade_estoque,
            canal_venda=canal_venda,
            observacao=f"Venda via {canal_venda}",
            data_movimentacao=datetime.now()
        )

        self.db.add(movimentacao)
        self.db.commit()
        self.db.refresh(movimentacao)
        return movimentacao

    def registrar_producao(
        self,
        codigo_produto: str,
        quantidade: int
    ) -> MovimentacaoVela:
        """
        Registra a fabricação de novas velas (entrada no estoque).
        """
        vela = self.buscar_por_codigo(codigo_produto)
        if not vela:
            raise ValueError(f"Produto {codigo_produto} não encontrado")

        estoque_antes = vela.quantidade_estoque
        vela.quantidade_estoque += quantidade

        movimentacao = MovimentacaoVela(
            vela_id=vela.id,
            tipo="entrada",
            quantidade=quantidade,
            estoque_anterior=estoque_antes,
            estoque_posterior=vela.quantidade_estoque,
            observacao="Produção de novas velas",
            data_movimentacao=datetime.now()
        )

        self.db.add(movimentacao)
        self.db.commit()
        self.db.refresh(movimentacao)
        return movimentacao

    def vendas_por_periodo(
        self,
        dias: int = 30
    ) -> pd.DataFrame:
        """
        Retorna um DataFrame com as vendas dos últimos N dias.
        DataFrame é como uma planilha Excel dentro do Python.
        Essa função alimenta os gráficos do dashboard.
        """
        data_limite = datetime.now() - timedelta(days=dias)

        # Busca todas as saídas no período
        movimentacoes = (
            self.db.query(MovimentacaoVela)
            .filter(
                MovimentacaoVela.tipo == "saida",
                MovimentacaoVela.data_movimentacao >= data_limite
            )
            .order_by(MovimentacaoVela.data_movimentacao)
            .all()
        )

        if not movimentacoes:
            return pd.DataFrame()

        # Transforma em DataFrame para análise
        dados = []
        for m in movimentacoes:
            vela = self.db.query(VelaPronta).filter(
                VelaPronta.id == m.vela_id
            ).first()
            dados.append({
                "data":       m.data_movimentacao.date(),
                "codigo":     vela.codigo_produto if vela else "N/A",
                "cor":        vela.cor if vela else "N/A",
                "formato":    vela.formato if vela else "N/A",
                "perfume":    vela.perfume if vela else "N/A",
                "tamanho":    vela.tamanho if vela else "N/A",
                "quantidade": m.quantidade,
                "canal":      m.canal_venda,
                "receita":    m.quantidade * (vela.preco_venda if vela else 0)
            })

        return pd.DataFrame(dados)

    def top_mais_vendidas(self, limite: int = 10) -> List[Dict]:
        """
        Retorna as N velas mais vendidas de todos os tempos.
        Usado no dashboard para o ranking de produtos.
        """
        # Agrupa as saídas por vela e soma as quantidades
        resultado = (
            self.db.query(
                MovimentacaoVela.vela_id,
                func.sum(MovimentacaoVela.quantidade).label("total_vendido")
            )
            .filter(MovimentacaoVela.tipo == "saida")
            .group_by(MovimentacaoVela.vela_id)
            .order_by(desc("total_vendido"))
            .limit(limite)
            .all()
        )

        top = []
        for vela_id, total in resultado:
            vela = self.db.query(VelaPronta).filter(
                VelaPronta.id == vela_id
            ).first()
            if vela:
                top.append({
                    "codigo":        vela.codigo_produto,
                    "cor":           vela.cor,
                    "formato":       vela.formato,
                    "perfume":       vela.perfume,
                    "tamanho":       vela.tamanho,
                    "total_vendido": int(total),
                    "receita_total": round(total * vela.preco_venda, 2)
                })
        return top

    def resumo_estoque(self) -> Dict:
        """Resumo geral das velas para os cards do dashboard"""
        todas = self.db.query(VelaPronta).all()
        em_alerta = self.velas_em_alerta()

        valor_estoque = sum(
            v.quantidade_estoque * v.preco_venda for v in todas
        )

        return {
            "total_skus":          len(todas),
            "em_alerta":           len(em_alerta),
            "valor_estoque":       round(valor_estoque, 2),
            "total_unidades":      sum(v.quantidade_estoque for v in todas),
            "produtos_criticos":   [v.codigo_produto for v in em_alerta[:5]]
        }