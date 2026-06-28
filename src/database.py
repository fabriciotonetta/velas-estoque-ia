# ================================================================
# database.py — Gerencia a conexão com o banco de dados SQLite
# É a "ponte" entre o Python e o arquivo do banco de dados
# ================================================================

# Importa as ferramentas necessárias do SQLAlchemy
from sqlalchemy import create_engine
# create_engine = cria a "ponte" de conexão com o banco

from sqlalchemy.orm import sessionmaker
# sessionmaker = fábrica de sessões (cada sessão é uma conversa com o banco)

from dotenv import load_dotenv
# load_dotenv = carrega as variáveis do arquivo .env

import os  # Permite ler variáveis de ambiente do sistema

# Carrega as variáveis do arquivo .env para o ambiente Python
load_dotenv()

# Lê a URL do banco de dados do arquivo .env
# Se não encontrar, usa o valor padrão (SQLite local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/estoque_velas.db")

# Cria o "motor" de conexão com o banco de dados
# check_same_thread=False permite usar o banco em múltiplas threads (necessário para FastAPI)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Mude para True se quiser ver os SQLs gerados no terminal
)

# Cria a fábrica de sessões configurada com nosso motor
# autocommit=False = as mudanças só são salvas quando você chamar .commit()
# autoflush=False  = as mudanças não são enviadas ao banco automaticamente
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def criar_tabelas():
    """
    Cria todas as tabelas no banco de dados.
    Só executa se as tabelas ainda não existirem.
    Chame esta função uma vez ao iniciar o sistema.
    """
    # Importa o Base e todos os models para que o SQLAlchemy os conheça
    from src.models import Base
    
    # Cria as tabelas no banco de dados baseado nos models definidos
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")


def get_db():
    """
    Função geradora que fornece uma sessão de banco de dados.
    Usada pelo FastAPI para injetar a sessão em cada requisição.
    Garante que a sessão seja fechada após o uso, mesmo se der erro.
    """
    # Abre uma nova sessão
    db = SessionLocal()
    try:
        yield db          # Entrega a sessão para quem precisar
    finally:
        db.close()        # Sempre fecha a sessão ao terminar


if __name__ == "__main__":
    # Se você rodar este arquivo diretamente (python src/database.py),
    # ele vai criar as tabelas no banco de dados
    criar_tabelas()