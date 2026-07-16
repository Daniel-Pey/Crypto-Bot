"""
🪙 Сервис для получения цен криптовалют

Использует CoinGecko API (бесплатно, без ключа) [citation:1][citation:9]
Альтернатива: Binance API [citation:4][citation:12]
"""

import time
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from utils.logger import logger
from config import config


class CryptoPriceService:
    """
    🪙 Сервис для работы с ценами криптовалют
    
    Поддерживает:
    - Получение текущей цены по символу
    - Получение цен для нескольких монет
    - Получение изменения за 24 часа
    - Поиск ID монеты по символу
    """
    
    # 🌐 Базовые URL для API
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_PUBLIC_URL = "https://api.coingecko.com/api/v3"
    
    # ⚡ Лимиты бесплатного API: 10-50 запросов в минуту [citation:3][citation:7]
    REQUEST_DELAY = 2  # Секунд между запросами
    MAX_RETRIES = 3
    
    def __init__(self):
        """🔄 Инициализация сервиса"""
        self.last_request_time = 0
        self._coin_id_cache = {}  # Кэш для ID монет
        logger.info("🚀 CryptoPriceService инициализирован")
    
    def _wait_for_rate_limit(self):
        """
        ⏳ Ожидание перед запросом для соблюдения rate limit
        CoinGecko бесплатный API: 10-50 запросов в минуту [citation:3]
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.REQUEST_DELAY:
            wait_time = self.REQUEST_DELAY - time_since_last
            logger.debug(f"⏳ Ожидание {wait_time:.2f}с перед запросом...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        📡 Выполнение HTTP-запроса с обработкой ошибок и retry
        
        Args:
            url: URL для запроса
            params: Параметры запроса
            
        Returns:
            Optional[Dict]: Ответ API или None при ошибке
        """
        self._wait_for_rate_limit()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"📡 Запрос к API: {url} (попытка {attempt + 1})")
                
                response = requests.get(
                    url,
                    params=params,
                    timeout=10,
                    headers={"Accept": "application/json"}
                )
                
                # ⚠️ Обработка rate limit (429)
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 5  # Экспоненциальная задержка [citation:10]
                    logger.warning(f"⚠️ Rate limit! Ожидание {wait_time}с...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"✅ Успешный запрос к API")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Ошибка запроса: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
                    continue
                return None
        
        return None
    
    def get_coin_id(self, symbol: str) -> Optional[str]:
        """
        🔍 Получение CoinGecko ID по символу [citation:1]
        
        Args:
            symbol: Символ монеты (например, "BTC")
            
        Returns:
            Optional[str]: ID монеты в CoinGecko или None
        """
        symbol = symbol.upper()
        
        # 🔄 Проверяем кэш
        if symbol in self._coin_id_cache:
            return self._coin_id_cache[symbol]
        
        # 📡 Запрашиваем список всех монет
        url = f"{self.COINGECKO_API_URL}/coins/list"
        data = self._make_request(url)
        
        if not data:
            logger.warning(f"⚠️ Не удалось получить список монет для {symbol}")
            return None
        
        # 🔍 Ищем монету по символу
        for coin in data:
            if coin.get('symbol', '').upper() == symbol:
                coin_id = coin.get('id')
                self._coin_id_cache[symbol] = coin_id
                logger.debug(f"✅ Найден ID для {symbol}: {coin_id}")
                return coin_id
        
        logger.warning(f"⚠️ Монета {symbol} не найдена в CoinGecko")
        return None
    
    def get_price(self, symbol: str, currency: str = "usd") -> Tuple[Optional[float], Optional[Dict]]:
        """
        💰 Получение текущей цены монеты [citation:1][citation:9]
        
        Args:
            symbol: Символ монеты (например, "BTC")
            currency: Валюта цены (по умолчанию "usd")
            
        Returns:
            Tuple[Optional[float], Optional[Dict]]: (цена, полные данные)
        """
        # 🔍 Получаем ID монеты
        coin_id = self.get_coin_id(symbol)
        if not coin_id:
            logger.error(f"❌ Не найден ID для {symbol}")
            return None, None
        
        # 📡 Запрашиваем цену
        url = f"{self.COINGECKO_API_URL}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': currency,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        data = self._make_request(url, params)
        
        if not data or coin_id not in data:
            logger.error(f"❌ Не удалось получить цену для {symbol}")
            return None, None
        
        coin_data = data[coin_id]
        price = coin_data.get(currency)
        
        if price is None:
            logger.error(f"❌ Нет данных по цене для {symbol} в {currency}")
            return None, None
        
        logger.info(f"💰 {symbol}: ${price} ({currency.upper()})")
        return float(price), coin_data
    
    def get_prices_batch(self, symbols: List[str], currency: str = "usd") -> Dict[str, Dict]:
        """
        📊 Получение цен для нескольких монет [citation:1]
        
        Args:
            symbols: Список символов монет
            currency: Валюта цены
            
        Returns:
            Dict[str, Dict]: Словарь с данными по каждой монете
        """
        if not symbols:
            return {}
        
        # 🔍 Получаем ID для всех монет
        coin_ids = []
        for symbol in symbols:
            coin_id = self.get_coin_id(symbol)
            if coin_id:
                coin_ids.append(coin_id)
        
        if not coin_ids:
            logger.error("❌ Не найдены ID ни для одной монеты")
            return {}
        
        # 📡 Запрашиваем цены для всех монет
        url = f"{self.COINGECKO_API_URL}/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': currency,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        data = self._make_request(url, params)
        
        if not data:
            logger.error("❌ Не удалось получить цены")
            return {}
        
        # 📝 Формируем результат
        result = {}
        for symbol in symbols:
            coin_id = self.get_coin_id(symbol)
            if coin_id and coin_id in data:
                result[symbol] = data[coin_id]
            else:
                result[symbol] = None
        
        logger.info(f"💰 Получены цены для {len(result)} монет")
        return result
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """
        📊 Получение полных рыночных данных о монете
        
        Args:
            symbol: Символ монеты
            
        Returns:
            Optional[Dict]: Рыночные данные или None
        """
        coin_id = self.get_coin_id(symbol)
        if not coin_id:
            return None
        
        url = f"{self.COINGECKO_API_URL}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false'
        }
        
        data = self._make_request(url, params)
        
        if not data:
            return None
        
        market_data = data.get('market_data', {})
        
        return {
            'symbol': symbol,
            'name': data.get('name', symbol),
            'current_price': market_data.get('current_price', {}).get('usd'),
            'market_cap': market_data.get('market_cap', {}).get('usd'),
            'volume_24h': market_data.get('total_volume', {}).get('usd'),
            'price_change_24h': market_data.get('price_change_percentage_24h'),
            'ath': market_data.get('ath', {}).get('usd'),
            'atl': market_data.get('atl', {}).get('usd'),
            'last_updated': data.get('last_updated')
        }


class BinancePriceService:
    """
    🪙 Альтернативный сервис через Binance API [citation:4][citation:12]
    
    Используется как запасной вариант или для получения дополнительных данных
    """
    
    BINANCE_API_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        """🔄 Инициализация сервиса Binance"""
        logger.info("🚀 BinancePriceService инициализирован")
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        💰 Получение цены через Binance API
        
        Args:
            symbol: Символ пары (например, "BTCUSDT")
            
        Returns:
            Optional[float]: Цена или None
        """
        try:
            url = f"{self.BINANCE_API_URL}/ticker/price"
            params = {'symbol': symbol.upper()}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = float(data.get('price', 0))
            
            logger.info(f"💰 Binance {symbol}: ${price}")
            return price
            
        except Exception as e:
            logger.error(f"❌ Ошибка Binance API: {e}")
            return None
    
    def get_24h_stats(self, symbol: str) -> Optional[Dict]:
        """
        📊 Получение статистики за 24 часа через Binance [citation:12]
        
        Args:
            symbol: Символ пары
            
        Returns:
            Optional[Dict]: Статистика или None
        """
        try:
            url = f"{self.BINANCE_API_URL}/ticker/24hr"
            params = {'symbol': symbol.upper()}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': symbol,
                'price': float(data.get('lastPrice', 0)),
                'price_change': float(data.get('priceChange', 0)),
                'price_change_percent': float(data.get('priceChangePercent', 0)),
                'high_24h': float(data.get('highPrice', 0)),
                'low_24h': float(data.get('lowPrice', 0)),
                'volume': float(data.get('volume', 0)),
                'quote_volume': float(data.get('quoteVolume', 0))
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка Binance API: {e}")
            return None