import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
import time
from datetime import datetime

st.set_page_config(page_title="Крипто Скринер", layout="wide")

st.title("📊 Крипто Скринер")
st.markdown("Выберите торговую пару для просмотра графика и данных.")

# --- Конфигурация API (переключатель между источниками) ---
API_SOURCES = {
    "OKX (рекомендуется)": {
        "base_url": "https://www.okx.com",
        "ticker_endpoint": "/api/v5/market/ticker",
        "trades_endpoint": "/api/v5/market/trades",
        "symbol_format": lambda s: s.replace("USDT", "-USDT"),  # BTCUSDT -> BTC-USDT
    },
    "Bybit": {
        "base_url": "https://api.bybit.com",
        "ticker_endpoint": "/v5/market/tickers",
        "trades_endpoint": "/v5/market/recent-trade",
        "symbol_format": lambda s: s,  # Bybit принимает BTCUSDT без дефиса
    },
}

# --- Боковая панель ---
with st.sidebar:
    st.header("⚙️ Настройки")
    
    # Выбор источника данных
    source_name = st.selectbox(
        "Источник данных:",
        list(API_SOURCES.keys()),
        index=0
    )
    api_config = API_SOURCES[source_name]  # оставляем для локального использования
    
    symbols_list = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT",
        "XRPUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT",
        "AVAXUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT"
    ]
    symbol = st.selectbox("Выберите торговую пару:", symbols_list)
    custom_symbol = st.text_input("Или введите свою пару (например, AVAXUSDT):")
    if custom_symbol:
        symbol = custom_symbol.upper().strip()
    
    interval = st.selectbox(
        "Интервал графика:",
        ("60", "240", "D", "W"),
        format_func=lambda x: {"60": "1 час", "240": "4 часа", "D": "1 день", "W": "1 неделя"}[x],
        index=0
    )
    
    if st.button("🔄 Принудительно обновить данные"):
        st.cache_data.clear()
        st.rerun()

# --- Функции для работы с API выбранной биржи ---
@st.cache_data(ttl=60, show_spinner="Загрузка данных...")
def get_market_data(symbol, source_name):
    """
    Получает тикер и последние сделки с выбранной биржи.
    source_name - строка, ключ из API_SOURCES.
    """
    # Получаем конфиг внутри функции, чтобы аргументы были хешируемыми
    api_config = API_SOURCES[source_name]
    formatted_symbol = api_config["symbol_format"](symbol)
    base_url = api_config["base_url"]
    
    ticker_data = None
    trades_data = []
    error_msg = None

    try:
        if "OKX" in source_name:
            # --- OKX API ---
            ticker_url = f"{base_url}{api_config['ticker_endpoint']}?instId={formatted_symbol}"
            resp = requests.get(ticker_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "0" and data.get("data"):
                    ticker_data = data["data"][0]
                else:
                    error_msg = f"OKX API Error: {data.get('msg', 'Неизвестная ошибка')}"
            else:
                error_msg = f"HTTP ошибка {resp.status_code}"
            
            # Сделки OKX
            trades_url = f"{base_url}{api_config['trades_endpoint']}?instId={formatted_symbol}&limit=20"
            resp_trades = requests.get(trades_url, timeout=5)
            if resp_trades.status_code == 200:
                data = resp_trades.json()
                if data.get("code") == "0" and data.get("data"):
                    trades_data = data["data"]
                    
        elif "Bybit" in source_name:
            # --- Bybit API ---
            ticker_url = f"{base_url}{api_config['ticker_endpoint']}?category=spot&symbol={formatted_symbol}"
            resp = requests.get(ticker_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                    ticker_data = data["result"]["list"][0]
                else:
                    error_msg = f"Bybit API Error: {data.get('retMsg', 'Неизвестная ошибка')}"
            else:
                error_msg = f"HTTP ошибка {resp.status_code}"
            
            # Сделки Bybit
            trades_url = f"{base_url}{api_config['trades_endpoint']}?category=spot&symbol={formatted_symbol}&limit=20"
            resp_trades = requests.get(trades_url, timeout=5)
            if resp_trades.status_code == 200:
                data = resp_trades.json()
                if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                    trades_data = data["result"]["list"]
                    
    except requests.exceptions.RequestException as e:
        error_msg = f"Сетевая ошибка: {e}"
    except json.JSONDecodeError:
        error_msg = "Ошибка парсинга ответа от API"

    return ticker_data, trades_data, error_msg

# --- Нормализация данных из разных источников в единый формат ---
def normalize_ticker_data(raw_data, source_name):
    """Приводит данные из разных API к единой структуре."""
    if not raw_data:
        return {}
    if "OKX" in source_name:
        last = float(raw_data.get("last", 0))
        open24 = float(raw_data.get("open24h", 0))
        change_pct = ((last - open24) / open24 * 100) if open24 != 0 else 0
        return {
            "last": last,
            "change_pct": change_pct,
            "high": float(raw_data.get("high24h", 0)),
            "low": float(raw_data.get("low24h", 0)),
            "volume": float(raw_data.get("vol24h", 0)),
        }
    elif "Bybit" in source_name:
        last = float(raw_data.get("lastPrice", 0))
        change_pct = float(raw_data.get("price24hPcnt", 0)) * 100
        return {
            "last": last,
            "change_pct": change_pct,
            "high": float(raw_data.get("highPrice24h", 0)),
            "low": float(raw_data.get("lowPrice24h", 0)),
            "volume": float(raw_data.get("turnover24h", 0)),
        }
    return {}

def normalize_trades_data(raw_trades, source_name):
    """Приводит список сделок к единому формату DataFrame."""
    if not raw_trades:
        return pd.DataFrame()
    
    if "OKX" in source_name:
        df = pd.DataFrame(raw_trades)
        df['time'] = pd.to_datetime(df['ts'].astype(float), unit='ms')
        df['price'] = df['px'].astype(float)
        df['qty'] = df['sz'].astype(float)
        df['side'] = df['side']
    elif "Bybit" in source_name:
        df = pd.DataFrame(raw_trades)
        df['time'] = pd.to_datetime(df['time'].astype(float), unit='ms')
        df['price'] = df['price'].astype(float)
        df['qty'] = df['size'].astype(float)
        df['side'] = df['side']
    else:
        return pd.DataFrame()
    
    return df[['time', 'price', 'qty', 'side']]

# --- Виджет графика TradingView ---
def get_tradingview_chart(symbol, interval):
    """Возвращает HTML-код для встраивания виджета TradingView."""
    # Для TradingView используем префикс OKX
    tv_symbol = f"OKX:{symbol}"
    return f"""
    <div class="tradingview-widget-container" style="height:100%; width:100%">
      <div id="tradingview_chart" style="height:600px; width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{interval}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "ru",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """

# --- Основной блок приложения ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"График {symbol}")
    chart_html = get_tradingview_chart(symbol, interval)
    components.html(chart_html, height=600)

with col2:
    st.subheader(f"Данные по {symbol} (источник: {source_name})")
    ticker_raw, trades_raw, error = get_market_data(symbol, source_name)
    
    if error:
        st.error(f"⚠️ Не удалось получить данные: {error}")
        st.info("💡 Попробуйте другой источник данных в боковом меню или проверьте правильность символа.")
    elif ticker_raw:
        ticker = normalize_ticker_data(ticker_raw, source_name)
        if ticker:
            change_pct = ticker.get("change_pct", 0)
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                st.metric("Цена", f"${ticker.get('last', 0):,.4f}")
            with col_metric2:
                st.metric("24ч %", f"{change_pct:.2f}%", delta=f"{change_pct:.2f}%")
            with col_metric3:
                st.metric("Объём (24ч)", f"${ticker.get('volume', 0):,.0f}")
            
            high = ticker.get('high', 0)
            low = ticker.get('low', 0)
            st.caption(f"24h High/Low: {high:,.4f} / {low:,.4f}")
            
            st.subheader("Последние сделки")
            df_trades = normalize_trades_data(trades_raw, source_name)
            if not df_trades.empty:
                def color_side(val):
                    if val == 'buy':
                        return 'color: #00ff00'
                    elif val == 'sell':
                        return 'color: #ff5555'
                    return ''
                
                styled_df = df_trades.style.applymap(color_side, subset=['side'])
                st.dataframe(
                    styled_df.format({'price': '{:.4f}', 'qty': '{:.4f}'}),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "time": "Время",
                        "price": "Цена",
                        "qty": "Объём",
                        "side": "Сторона"
                    }
                )
            else:
                st.info("Нет данных о последних сделках")
        else:
            st.warning("Не удалось распарсить данные тикера")
    else:
        st.warning("Нет данных для отображения.")

st.markdown("---")
st.caption(f"Данные предоставлены {source_name}. График от TradingView. Обновлено: {datetime.now().strftime('%H:%M:%S')}")
