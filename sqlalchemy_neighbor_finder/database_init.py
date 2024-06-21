from pgvector.sqlalchemy import Vector
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (
    Column, Text, create_engine, text
)

import config as cfg


def _make_connection_url() -> str:
    """

    :return:
    """
    return f'postgresql+psycopg2://' \
           f'{cfg.DB_USER}:' \
           f'{cfg.DB_PASSWORD}@' \
           f'{cfg.DB_HOST}:' \
           f'{cfg.DB_PORT}/' \
           f'{cfg.DB_NAME}'


def crate_engine() -> Engine:
    """
    :return:
    """
    engine = create_engine(_make_connection_url(), echo=True)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    return engine


engine = crate_engine()
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Embeddings(Base):
    """
    """
    __tablename__ = 'embeddings'
    crop_id = Column(Text, primary_key=True)
    embedding_vector = Column(Vector(1024))
    class_name = Column(Text)


Base.metadata.create_all(engine)
