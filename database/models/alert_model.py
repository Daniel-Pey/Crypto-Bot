from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db_session import SqlAlchemyBase

# ============================================================
# 🔔 МОДЕЛЬ СООБЩЕНИЙ
# ============================================================

class Alert(SqlAlchemyBase):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_coin_id = Column(Integer, ForeignKey('user_coins.id'), nullable=False)
    alert_type = Column(String(20))  # 'price_reached', 'price_change'
    trigger_value = Column(Float)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    
    # Связи
    user = relationship("User", back_populates="alerts")
    user_coin = relationship("UserCoin")