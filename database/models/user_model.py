from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db_session import SqlAlchemyBase

# ============================================================
# 👤 МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================

class User(SqlAlchemyBase):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    subscription_type = Column(Integer, default=1)  # 1 - бесплатный, 5, 10, 15, 20
    subscription_end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    coins = relationship("UserCoin", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    
    def get_max_coins(self):
        """Возвращает максимальное количество монет для пользователя"""
        if self.subscription_type == 1:
            return 1
        return self.subscription_type
    
    def has_valid_subscription(self):
        """Проверяет активность подписки"""
        if self.subscription_type == 1:
            return True
        if not self.subscription_end_date:
            return False
        return datetime.utcnow() < self.subscription_end_date