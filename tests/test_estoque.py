# ================================================================
# test_estoque.py — Testes automatizados das regras de negócio
# Pytest roda todos os métodos que começam com "test_"
# Para rodar: pytest tests/ -v
# ================================================================

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Insumo, VelaPronta
from src.estoque import EstoqueInsumos, EstoqueVelas
from src.database import criar_tabelas

# Usa banco em memória para testes (não afeta o banco real)
engine_teste = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine_teste)
SessionTeste = sessionmaker(bind=engine_teste)


@pytest.fixture
def db():
    """Cria uma sessão de banco limpa para cada teste"""
    session = SessionTeste()
    yield session
    session.rollback()  # Desfaz tudo após cada teste
    session.close()


@pytest.fixture
def insumo_exemplo(db):
    """Cria um insumo de exemplo para os testes"""
    insumo = Insumo(
        nome="Cera de Teste",
        categoria="Cera",
        unidade_medida="kg",
        quantidade_atual=50.0,
        quantidade_minima=10.0,
        quantidade_ideal=60.0,
        preco_unitario=15.0,
        fornecedor="Fornecedor Teste"
    )
    db.add(insumo)
    db.commit()
    db.refresh(insumo)
    return insumo


def test_listar_insumos(db, insumo_exemplo):
    """Testa se a listagem de insumos funciona"""
    estoque = EstoqueInsumos(db)
    insumos = estoque.listar_todos()
    assert len(insumos) >= 1
    assert insumos[0].nome == "Cera de Teste"


def test_registrar_entrada(db, insumo_exemplo):
    """Testa se a entrada de insumo aumenta o estoque corretamente"""
    estoque = EstoqueInsumos(db)
    estoque_inicial = insumo_exemplo.quantidade_atual

    movim = estoque.registrar_entrada(insumo_exemplo.id, 10.0, "Teste")

    assert movim.tipo == "entrada"
    assert movim.quantidade == 10.0
    assert insumo_exemplo.quantidade_atual == estoque_inicial + 10.0


def test_registrar_saida(db, insumo_exemplo):
    """Testa se a saída de insumo diminui o estoque corretamente"""
    estoque = EstoqueInsumos(db)
    estoque_inicial = insumo_exemplo.quantidade_atual

    movim = estoque.registrar_saida(insumo_exemplo.id, 5.0, "Teste")

    assert movim.tipo == "saida"
    assert insumo_exemplo.quantidade_atual == estoque_inicial - 5.0


def test_saida_estoque_insuficiente(db, insumo_exemplo):
    """Testa se o sistema impede saída maior que o estoque disponível"""
    estoque = EstoqueInsumos(db)

    # Tenta retirar mais do que tem — deve lançar erro
    with pytest.raises(ValueError, match="Estoque insuficiente"):
        estoque.registrar_saida(insumo_exemplo.id, 9999.0)


def test_insumo_em_alerta(db):
    """Testa se o alerta é disparado quando estoque fica abaixo do mínimo"""
    insumo_critico = Insumo(
        nome="Insumo Crítico",
        categoria="Cera",
        unidade_medida="kg",
        quantidade_atual=2.0,    # Abaixo do mínimo!
        quantidade_minima=10.0,
        quantidade_ideal=30.0,
        preco_unitario=10.0,
        fornecedor="Teste"
    )
    db.add(insumo_critico)
    db.commit()

    estoque = EstoqueInsumos(db)
    alertas = estoque.insumos_em_alerta()

    # O insumo crítico deve aparecer na lista de alertas
    nomes_alerta = [i.nome for i in alertas]
    assert "Insumo Crítico" in nomes_alerta


def test_quantidade_negativa_bloqueada(db, insumo_exemplo):
    """Testa se quantidade negativa é rejeitada"""
    estoque = EstoqueInsumos(db)

    with pytest.raises(ValueError):
        estoque.registrar_entrada(insumo_exemplo.id, -5.0)


def test_resumo_estoque(db, insumo_exemplo):
    """Testa se o resumo do estoque retorna as chaves corretas"""
    estoque = EstoqueInsumos(db)
    resumo = estoque.resumo_estoque()

    assert "total_insumos" in resumo
    assert "em_alerta" in resumo
    assert "valor_total_estoque" in resumo
    assert resumo["total_insumos"] >= 1