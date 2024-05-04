from sqlalchemy import Column, Integer, String, DateTime, create_engine, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from data.database.settings import SQLALCHEMY_DATABASE_URL

Base = declarative_base()


class FXTickData(Base):
    __tablename__ = 'fx_tick_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_pair = Column(String)
    timestamp = Column(DateTime, default=func.now())
    bid = Column(Float)
    ask = Column(Float)

    __table_args__ = (
        Index('Idx_Fx_Tick_Data_Currency_Pair_Timestamp', 'currency_pair', 'timestamp'),
    )


engine = create_engine(SQLALCHEMY_DATABASE_URL)
