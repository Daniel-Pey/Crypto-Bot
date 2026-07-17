"""
💳 Сервис для обработки платежей и подписок

В будущем можно интегрировать:
- YooKassa (ЮKassa)
- Stripe
- Wallet Pay (TON)
- Telegram Stars
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from utils.logger import logger
from database import create_session
from models import User
from config import config


class PaymentService:
    """
    💳 Сервис для обработки платежей
    
    Поддерживает:
    - Создание платежа
    - Проверку статуса
    - Активацию подписки
    """
    
    # 💰 Статусы платежей
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_EXPIRED = "expired"
    
    def __init__(self):
        """🔄 Инициализация сервиса"""
        logger.info("🚀 PaymentService инициализирован")
    
    def create_payment(self, user_id: int, coins: int, price: int) -> Dict:
        """
        💳 Создание платежа
        
        Args:
            user_id: ID пользователя в Telegram
            coins: Количество монет в тарифе
            price: Стоимость в рублях
            
        Returns:
            Dict: Информация о платеже
        """
        logger.info(f"💳 Создание платежа для user {user_id} на {coins} монет ({price}₽)")
        
        # 🔍 Проверяем тариф
        if coins not in config.SUBSCRIPTION_PRICES:
            logger.error(f"❌ Неверный тариф: {coins}")
            return {'error': 'Неверный тариф'}
        
        # 📝 Создаем платеж (здесь будет интеграция с платежной системой)
        payment_id = f"pay_{user_id}_{coins}_{int(datetime.utcnow().timestamp())}"
        
        return {
            'payment_id': payment_id,
            'user_id': user_id,
            'coins': coins,
            'price': price,
            'status': self.STATUS_PENDING,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'payment_url': f"https://example.com/pay/{payment_id}"  # Заглушка
        }
    
    def confirm_payment(self, payment_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        ✅ Подтверждение платежа
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (успех, сообщение, данные пользователя)
        """
        logger.info(f"✅ Подтверждение платежа: {payment_id}")
        
        # 🔍 Парсим payment_id
        try:
            _, user_id_str, coins_str, _ = payment_id.split('_')
            user_id = int(user_id_str)
            coins = int(coins_str)
        except:
            return False, "❌ Неверный формат платежа", None
        
        # 📊 Получаем сессию БД
        db = create_session()
        
        try:
            # 🔍 Находим пользователя
            user = db.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                logger.error(f"❌ Пользователь {user_id} не найден")
                return False, "❌ Пользователь не найден", None
            
            # 🔄 Активируем подписку
            user.subscription_type = coins
            user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
            db.commit()
            
            logger.info(f"✅ Подписка активирована для user {user_id}: {coins} монет")
            
            return True, "✅ Подписка успешно активирована!", {
                'user_id': user_id,
                'coins': coins,
                'end_date': user.subscription_end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"💥 Ошибка подтверждения платежа: {e}")
            db.rollback()
            return False, "❌ Произошла ошибка", None
        finally:
            db.close()
    
    def get_subscription_info(self, user_id: int) -> Dict:
        """
        📊 Получение информации о подписке пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Dict: Информация о подписке
        """
        db = create_session()
        
        try:
            user = db.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                return {'error': 'Пользователь не найден'}
            
            is_valid = user.has_valid_subscription()
            
            return {
                'user_id': user_id,
                'coins': user.subscription_type,
                'max_coins': user.get_max_coins(),
                'is_active': is_valid,
                'end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                'used_coins': len(user.coins)
            }
            
        except Exception as e:
            logger.error(f"💥 Ошибка получения информации о подписке: {e}")
            return {'error': str(e)}
        finally:
            db.close()


# 💰 Вспомогательные функции для работы с ценами

def format_price(amount: float, currency: str = "₽") -> str:
    """
    💰 Форматирование цены
    
    Args:
        amount: Сумма
        currency: Валюта
        
    Returns:
        str: Отформатированная цена
    """
    return f"{amount:,.2f} {currency}"

def get_subscription_price(coins: int) -> Optional[int]:
    """
    💰 Получение цены тарифа
    
    Args:
        coins: Количество монет
        
    Returns:
        Optional[int]: Цена в рублях или None
    """
    return config.SUBSCRIPTION_PRICES.get(coins)