"""
🔄 Фоновый сервис для проверки цен и отправки уведомлений
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from utils.logger import logger
from database import create_session
from models import User, Coin, UserCoin, Alert
from services.crypto_api import CryptoPriceService


class PriceChecker:
    """
    🔄 Фоновый сервис мониторинга цен
    """
    
    def __init__(self, bot, check_interval: int = 60):
        """
        🔄 Инициализация сервиса
        
        Args:
            bot: Экземпляр бота для отправки уведомлений
            check_interval: Интервал проверки в секундах
        """
        self.bot = bot
        self.check_interval = check_interval
        self.crypto_service = CryptoPriceService()
        self.is_running = False
        self.thread = None
        
        logger.info(f"🚀 PriceChecker инициализирован (интервал: {check_interval}с)")
    
    def start(self):
        """▶️ Запуск фонового мониторинга"""
        if self.is_running:
            logger.warning("⚠️ PriceChecker уже запущен")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("✅ PriceChecker запущен в фоновом режиме")
    
    def stop(self):
        """⏹️ Остановка фонового мониторинга"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ PriceChecker остановлен")
    
    def _run(self):
        """🔄 Основной цикл мониторинга"""
        while self.is_running:
            try:
                logger.debug("🔄 Проверка цен...")
                self._check_prices()
                logger.debug(f"✅ Проверка завершена. Следующая через {self.check_interval}с")
                
            except Exception as e:
                logger.error(f"💥 Ошибка в цикле мониторинга: {e}")
            
            # ⏳ Ожидание до следующей проверки
            for _ in range(self.check_interval):
                if not self.is_running:
                    break
                time.sleep(1)
    
    def _check_prices(self):
        """📊 Проверка всех цен в базе данных"""
        db = create_session()
        
        try:
            # 🔍 Получаем все монеты, которые отслеживаются
            user_coins = db.query(UserCoin).all()
            
            if not user_coins:
                logger.debug("📭 Нет монет для проверки")
                return
            
            # 🔍 Получаем уникальные символы монет
            coin_ids = {uc.coin_id for uc in user_coins}
            coins = db.query(Coin).filter(Coin.id.in_(coin_ids)).all()
            
            # 📊 Получаем актуальные цены
            symbols = [coin.symbol for coin in coins]
            prices_data = self.crypto_service.get_prices_batch(symbols)
            
            # 🔄 Обновляем цены в базе данных
            for coin in coins:
                if coin.symbol in prices_data and prices_data[coin.symbol]:
                    data = prices_data[coin.symbol]
                    new_price = data.get('usd')
                    change = data.get('usd_24h_change')
                    
                    if new_price is not None:
                        coin.current_price = new_price
                        coin.price_change_24h = change
                        coin.last_updated = datetime.utcnow()
            
            db.commit()
            
            # 🔔 Проверяем алерты для каждого пользователя
            for user_coin in user_coins:
                self._check_user_alerts(db, user_coin)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"💥 Ошибка при проверке цен: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _check_user_alerts(self, db, user_coin):
        """🔔 Проверка алертов для конкретной монеты пользователя"""
        try:
            user = db.query(User).filter_by(id=user_coin.user_id).first()
            coin = db.query(Coin).filter_by(id=user_coin.coin_id).first()
            
            if not user or not coin or not coin.current_price:
                return
            
            # 🔍 Получаем активные алерты для этой монеты
            alerts = db.query(Alert).filter_by(
                user_coin_id=user_coin.id,
                is_triggered=False
            ).all()
            
            for alert in alerts:
                self._check_alert(db, alert, user, coin)
                
        except Exception as e:
            logger.error(f"💥 Ошибка проверки алертов: {e}")
    
    def _check_alert(self, db, alert, user, coin):
        """✅ Проверка конкретного алерта"""
        current_price = coin.current_price
        
        if alert.alert_type == "price_reached":
            # 💰 Проверка по достижению цены
            trigger_value = alert.trigger_value
            
            if current_price >= trigger_value:
                self._send_alert(
                    user.telegram_id,
                    coin.symbol,
                    f"💰 Цена {coin.symbol} достигла ${current_price:,.2f}! 🎯 Цель: ${trigger_value:,.2f}"
                )
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                db.commit()
                logger.info(f"🔔 Отправлен ценовой алерт для {user.telegram_id} ({coin.symbol})")
                
        elif alert.alert_type == "price_change":
            # 📊 Проверка по изменению процента
            threshold = alert.trigger_value
            change = coin.price_change_24h
            
            if change is not None and abs(change) >= threshold:
                direction = "📈 выросла" if change > 0 else "📉 упала"
                self._send_alert(
                    user.telegram_id,
                    coin.symbol,
                    f"📊 Цена {coin.symbol} {direction} на {abs(change):.2f}%! ⚡ Текущая: ${current_price:,.2f}"
                )
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                db.commit()
                logger.info(f"🔔 Отправлен процентный алерт для {user.telegram_id} ({coin.symbol})")
    
    def _send_alert(self, telegram_id: int, symbol: str, message: str):
        """📤 Отправка уведомления пользователю"""
        try:
            full_message = f"""
🔔 <b>Уведомление по {symbol}</b>

{message}

📅 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

💡 Для управления алертами используйте меню бота
            """
            
            self.bot.send_message(
                telegram_id,
                full_message,
                parse_mode='HTML'
            )
            
            logger.info(f"✅ Уведомление отправлено пользователю {telegram_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления: {e}")