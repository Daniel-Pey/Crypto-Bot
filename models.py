"""
📊 Модели данных для базы данных SQLite
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ============================================================
# 👤 МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================

class User(Base):
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

# ============================================================
# 🪙 МОДЕЛИ КРИПТОВАЛЮТ
# ============================================================

class Coin(Base):
    __tablename__ = 'coins'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)  # BTC, ETH и т.д.
    name = Column(String(100))
    current_price = Column(Float)
    price_change_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user_coins = relationship("UserCoin", back_populates="coin")

class UserCoin(Base):
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

# ============================================================
# 🔔 МОДЕЛЬ АЛЕРТОВ
# ============================================================

class Alert(Base):
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