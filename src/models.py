# ================================================================
# models.py — Define a estrutura das tabelas do banco de dados
# É como criar o "esqueleto" de cada tabela antes de inserir dados
# ================================================================

# Importa as ferramentas do SQLAlchemy para criar tabelas
from sqlalchemy import (
    Column,      # Define uma coluna na tabela
    Integer,     # Tipo: número inteiro (1, 2, 3...)
    String,      # Tipo: texto ("Lavanda", "Rosa"...)
    Float,       # Tipo: número decimal (1.5, 99.99...)
    DateTime,    # Tipo: data e hora
    ForeignKey,  # Liga duas tabelas entre si
    Enum,        # Tipo: lista fixa de opções
    Text         # Tipo: texto longo
)
from sqlalchemy.orm import relationship, declarative_base
# relationship = define como as tabelas se relacionam
# declarative_base = classe base que todas as tabelas herdam

from datetime import datetime  # Para registrar a data/hora atual
import enum                    # Para criar listas de opções fixas

# Cria a "classe base" — todas as tabelas do projeto herdam dela
Base = declarative_base()


# ================================================================
# ENUMS — Listas fixas de opções (não mudam)
# Isso garante que ninguém cadastre uma cor inexistente, por ex.
# ================================================================

class CorVela(enum.Enum):
    """As 10 cores disponíveis no catálogo"""
    BRANCO_CLASSICO   = "Branco Clássico"
    MARFIM            = "Marfim"
    ROSA_QUARTZO      = "Rosa Quartzo"
    LAVANDA           = "Lavanda"
    AZUL_SERENIDADE   = "Azul Serenidade"
    VERDE_SAGE        = "Verde Sage"
    TERRACOTA         = "Terracota"
    PRETO_OBSIDIANA   = "Preto Obsidiana"
    DOURADO           = "Dourado"
    VERMELHO_BORDEAUX = "Vermelho Bordeaux"


class FormatoVela(enum.Enum):
    """Os 10 formatos disponíveis no catálogo"""
    CILINDRICA  = "Cilíndrica"
    CONICA      = "Cônica"
    QUADRADA    = "Quadrada"
    ESFERICA    = "Esférica"
    PILAR       = "Pilar"
    VOTIVA      = "Votiva"
    FLUTUANTE   = "Flutuante"
    CONTAINER   = "Container"
    ESCULTURAL  = "Escultural"
    TEALIGHT    = "Tealight"


class PerfumeVela(enum.Enum):
    """Os 10 perfumes disponíveis no catálogo"""
    LAVANDA_BAUNILHA    = "Lavanda & Baunilha"
    ROSA_BULGARA        = "Rosa Búlgara"
    SANDALO_AMBAR       = "Sândalo & Âmbar"
    CEDRO_BERGAMOTA     = "Cedro & Bergamota"
    JASMIM_NOTURNO      = "Jasmim Noturno"
    BAUNILHA_CANELA     = "Baunilha & Canela"
    EUCALIPTO_HORTELA   = "Eucalipto & Hortelã"
    PATCHOULI_VETIVER   = "Patchouli & Vetiver"
    FIGO_MADEIRA        = "Figo & Madeira"
    SEM_PERFUME         = "Sem Perfume"


class TamanhoVela(enum.Enum):
    """Os 3 tamanhos disponíveis"""
    PEQUENO = "P"   # 80g  — ~20h de queima
    MEDIO   = "M"   # 180g — ~45h de queima
    GRANDE  = "G"   # 350g — ~80h de queima


class TipoMovimentacao(enum.Enum):
    """Tipos de movimentação no estoque"""
    ENTRADA  = "entrada"   # Chegou produto/insumo
    SAIDA    = "saida"     # Saiu produto/insumo (venda ou uso)
    AJUSTE   = "ajuste"    # Correção manual de estoque
    PERDA    = "perda"     # Produto danificado/descartado


class CategoriaInsumo(enum.Enum):
    """Categorias dos insumos de fabricação"""
    CERA        = "Cera"
    ESSENCIA    = "Essência"
    RECIPIENTE  = "Recipiente"
    PAVIO       = "Pavio"
    CORANTE     = "Corante"
    EMBALAGEM   = "Embalagem"
    OUTROS      = "Outros"


# ================================================================
# TABELA 1 — Insumos
# Guarda todos os materiais usados para fabricar as velas
# Ex: Cera de Carnaúba, Essência de Lavanda, Pote de Vidro...
# ================================================================

class Insumo(Base):
    __tablename__ = "insumos"  # Nome da tabela no banco de dados

    # Identificador único — gerado automaticamente (1, 2, 3...)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Nome do insumo — ex: "Cera de Carnaúba"
    nome = Column(String(100), nullable=False)

    # Categoria do insumo (usa o Enum definido acima)
    categoria = Column(String(50), nullable=False)

    # Unidade de medida — ex: "kg", "litro", "unidade"
    unidade_medida = Column(String(20), nullable=False)

    # Quantidade atual em estoque
    quantidade_atual = Column(Float, default=0.0)

    # Quantidade mínima — abaixo disso, gera alerta
    quantidade_minima = Column(Float, nullable=False)

    # Quantidade ideal para repor (ponto de pedido)
    quantidade_ideal = Column(Float, nullable=False)

    # Preço por unidade de medida (em reais)
    preco_unitario = Column(Float, nullable=False)

    # Nome do fornecedor principal
    fornecedor = Column(String(100))

    # Data em que o insumo foi cadastrado no sistema
    criado_em = Column(DateTime, default=datetime.now)

    # Relacionamento: um insumo pode ter várias movimentações
    movimentacoes = relationship("MovimentacaoInsumo", back_populates="insumo")

    def __repr__(self):
        # Define como o objeto aparece quando você o imprime
        return f"<Insumo: {self.nome} | Qtd: {self.quantidade_atual} {self.unidade_medida}>"


# ================================================================
# TABELA 2 — Velas Prontas (Produtos Acabados)
# Guarda o estoque de velas já fabricadas, prontas para venda
# ================================================================

class VelaPronta(Base):
    __tablename__ = "velas_prontas"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Código único do produto — ex: "CIL-BRA-LAV-M"
    codigo_produto = Column(String(30), unique=True, nullable=False)

    # As 4 características que definem cada vela
    cor      = Column(String(50), nullable=False)
    formato  = Column(String(50), nullable=False)
    perfume  = Column(String(50), nullable=False)
    tamanho  = Column(String(5),  nullable=False)  # P, M ou G

    # Peso em gramas conforme o tamanho
    peso_gramas = Column(Integer, nullable=False)

    # Tempo de queima em horas
    tempo_queima_horas = Column(Integer, nullable=False)

    # Preço de venda sugerido
    preco_venda = Column(Float, nullable=False)

    # Custo de produção (soma dos insumos usados)
    custo_producao = Column(Float, nullable=False)

    # Quantidade em estoque pronta para venda
    quantidade_estoque = Column(Integer, default=0)

    # Estoque mínimo — abaixo disso, precisa fabricar mais
    estoque_minimo = Column(Integer, default=5)

    # Data de cadastro
    criado_em = Column(DateTime, default=datetime.now)

    # Relacionamento com movimentações
    movimentacoes = relationship("MovimentacaoVela", back_populates="vela")

    def __repr__(self):
        return f"<Vela: {self.codigo_produto} | {self.cor} {self.formato} {self.perfume} {self.tamanho} | Estoque: {self.quantidade_estoque}>"


# ================================================================
# TABELA 3 — Movimentações de Insumos
# Registra CADA entrada ou saída de insumo com data e motivo
# É o "extrato bancário" do estoque de insumos
# ================================================================

class MovimentacaoInsumo(Base):
    __tablename__ = "movimentacoes_insumos"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Qual insumo foi movimentado (ligação com a tabela Insumo)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=False)

    # Tipo: entrada, saída, ajuste ou perda
    tipo = Column(String(20), nullable=False)

    # Quantidade movimentada (sempre positiva)
    quantidade = Column(Float, nullable=False)

    # Estoque ANTES da movimentação (para histórico)
    estoque_anterior = Column(Float, nullable=False)

    # Estoque DEPOIS da movimentação
    estoque_posterior = Column(Float, nullable=False)

    # Motivo ou observação — ex: "Compra NF 1234", "Uso na produção"
    observacao = Column(Text)

    # Data e hora exata da movimentação
    data_movimentacao = Column(DateTime, default=datetime.now)

    # Relacionamento inverso com Insumo
    insumo = relationship("Insumo", back_populates="movimentacoes")

    def __repr__(self):
        return f"<Movim.Insumo: {self.tipo} | {self.quantidade} | {self.data_movimentacao}>"


# ================================================================
# TABELA 4 — Movimentações de Velas Prontas
# Registra cada entrada (fabricação) ou saída (venda) de velas
# ================================================================

class MovimentacaoVela(Base):
    __tablename__ = "movimentacoes_velas"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Qual vela foi movimentada
    vela_id = Column(Integer, ForeignKey("velas_prontas.id"), nullable=False)

    # Tipo: entrada (fabricada) ou saída (vendida)
    tipo = Column(String(20), nullable=False)

    # Quantidade
    quantidade = Column(Integer, nullable=False)

    # Estoques antes e depois para rastreabilidade
    estoque_anterior = Column(Integer, nullable=False)
    estoque_posterior = Column(Integer, nullable=False)

    # Canal de venda — ex: "Instagram", "Feira", "Loja Online"
    canal_venda = Column(String(50))

    # Observação livre
    observacao = Column(Text)

    # Data da movimentação
    data_movimentacao = Column(DateTime, default=datetime.now)

    # Relacionamento inverso
    vela = relationship("VelaPronta", back_populates="movimentacoes")

    def __repr__(self):
        return f"<Movim.Vela: {self.tipo} | {self.quantidade}un | {self.data_movimentacao}>"


# ================================================================
# TABELA 5 — Previsões do Modelo ML
# Guarda o histórico de previsões feitas pelo modelo
# Isso permite avaliar a precisão do modelo ao longo do tempo
# ================================================================

class PrevisaoML(Base):
    __tablename__ = "previsoes_ml"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # O que está sendo previsto: "insumo" ou "vela"
    tipo_item = Column(String(20), nullable=False)

    # ID do insumo ou vela previsto
    item_id = Column(Integer, nullable=False)

    # Nome para facilitar leitura
    item_nome = Column(String(100), nullable=False)

    # Em quantos dias o estoque vai acabar (previsão)
    dias_para_acabar = Column(Integer)

    # Quantidade sugerida para repor
    quantidade_sugerida = Column(Float)

    # Nível de confiança do modelo (0 a 1)
    confianca = Column(Float)

    # Data em que a previsão foi gerada
    gerado_em = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Previsão: {self.item_nome} | Acaba em {self.dias_para_acabar} dias>"