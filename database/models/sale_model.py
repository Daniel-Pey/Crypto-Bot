from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db_session import SqlAlchemyBase

# ============================================================
# 🎯 МОДЕЛЬ АКЦИЙ
# ============================================================


class Sale(SqlAlchemyBase):
    """
    🎯 Модель для хранения информации об акциях
    """
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # Название акции
    description = Column(Text, nullable=True)    # Описание акции
    
    # 🪙 Параметры акции
    coins = Column(Integer, nullable=False)     # Количество монет
    price_rub = Column(Integer, nullable=True)   # Цена в рублях (если есть)
    price_stars = Column(Integer, nullable=True) # Цена в Stars (если есть)
    
    # 📅 Период действия
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)   # None = бессрочная
    
    # 🏷️ Статус
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False) # Показывать ли в топе
    
    # 📊 Статистика использования
    used_count = Column(Integer, default=0)      # Сколько раз использована
    max_uses = Column(Integer, nullable=True)    # Максимальное количество использований
    
    # 🕐 Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, nullable=True)  # ID админа, создавшего акцию
    
    def is_valid(self) -> bool:
        """
        ✅ Проверка, активна ли акция сейчас
        
        Returns:
            bool: True если акция активна
        """
        if not self.is_active:
            return False
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        
        if self.end_date and datetime.utcnow() > self.end_date:
            return False
        
        return True
    
    def get_price_display(self) -> str:
        """
        💰 Форматированное отображение цены
        
        Returns:
            str: Цена в удобном формате
        """
        if self.price_stars:
            return f"⭐{self.price_stars} Stars"
        elif self.price_rub:
            return f"{self.price_rub} ₽"
        return "Бесплатно"
    
    def get_coins_display(self) -> str:
        """
        🪙 Форматированное отображение монет
        
        Returns:
            str: Количество монет с эмодзи
        """
        if self.coins == 1:
            return "1 монета"
        elif self.coins <= 4:
            return f"{self.coins} монеты"
        else:
            return f"{self.coins} монет"