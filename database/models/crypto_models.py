from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db_session import SqlAlchemyBase

# ============================================================
# 🪙 МОДЕЛИ КРИПТОВАЛЮТ
# ============================================================

class Coin(SqlAlchemyBase):
    __tablename__ = 'coins'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)  # BTC, ETH и т.д.
    name = Column(String(100))
    current_price = Column(Float)
    price_change_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user_coins = relationship("UserCoin", back_populates="coin")

class UserCoin(SqlAlchemyBase):
    __tablename__ = 'user_coins'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    target_price = Column(Float)  # Целевая цена для алерта
    alert_threshold = Column(Float)  # Процент изменения для алерта
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="coins")
    coin = relationship("Coin", back_populates="user_coins")