import streamlit as st
from lightweight_charts_v5 import lightweight_charts_v5_component
import ccxt
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime

# --- Настройка страницы ---
st.set_page_config(layout="wide")

# --- CSS для идеального прилегания ---
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    div[data-testid="column"] {
        padding: 0px !important;
    }
    .stApp {
        margin: 0;
        padding: 0;
    }
    iframe {
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# --- Инициализация и кэширование данных ---
@st.cache_resource
def init_exchange():
    """Подключаемся к OKX для получения данных"""
    exchange = ccxt.okx({'enableRateLimit': True})
    return exchange

exchange = init_exchange()

@st.cache_data(ttl=300)
def get_usdt_symbols():
    """Получаем список всех пар к USDT на OKX"""
    markets = exchange.load_markets()
    usdt_pairs = [symbol for symbol in markets if symbol.endswith('/USDT')]
    popular = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
               'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT', 'DOT/USDT', 'LTC/USDT',
               'AVAX/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT', 'ETC/USDT']
    result = popular + [p for p in usdt_pairs if p not in popular][:35]
    return result

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, timeframe='1h', limit=200):
    """Загружаем свечные данные с биржи"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()

# --- Управление состоянием (state) ---
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = 'BTC/USDT'

symbols = get_usdt_symbols()
if not symbols:
    st.stop()

# --- Создание интерфейса: две колонки впритык ---
left_col, right_col = st.columns([4, 1], gap="small")

# --- ПРАВАЯ КОЛОНКА: Скринер (Виджет TradingView) ---
with right_col:
    # Этот виджет должен работать, т.к. это не сложный график
    screener_html = """
    <div class="tradingview-widget-container" style="height:100vh; width:100%">
      <div id="tradingview_screener"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
      {
      "width": "100%",
      "height": "100%",
      "defaultColumn": "overview",
      "defaultScreen": "top_gainers",
      "market": "crypto",
      "showToolbar": true,
      "colorTheme": "dark",
      "locale": "ru",
      "container_id": "tradingview_screener"
      }
      </script>
    </div>
    """
    components.html(screener_html, height=1000)

# --- ЛЕВАЯ КОЛОНКА: График (Библиотека Lightweight Charts) ---
with left_col:
    st.header(f"{st.session_state.selected_symbol}")

    # Загружаем данные
    df = fetch_ohlcv(st.session_state.selected_symbol, timeframe='1h', limit=200)

    if not df.empty:
        # Преобразуем данные в формат для графика
        chart_data = [
            {
                "time": str(row['timestamp'].date()),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close'])
            }
            for _, row in df.iterrows()
        ]

        # Рендерим график с помощью библиотеки
        lightweight_charts_v5_component(
            name=f"{st.session_state.selected_symbol} Chart",
            charts=[{
                "chart": {
                    "layout": {
                        "background": {"color": "#131722"},
                        "textColor": "#d1d4dc",
                    },
                    "grid": {
                        "vertLines": {"color": "rgba(42, 46, 57, 0)"},
                        "horzLines": {"color": "rgba(42, 46, 57, 0.6)"},
                    },
                    "height": 800,
                },
                "series": [{
                    "type": "Candlestick",
                    "data": chart_data,
                    "options": {
                        "upColor": "#26a69a",
                        "downColor": "#ef5350",
                        "borderVisible": False,
                        "wickUpColor": "#26a69a",
                        "wickDownColor": "#ef5350"
                    }
                }],
            }],
            height=800
        )
    else:
        st.warning("Нет данных для отображения")

    # Кнопки для управления (можно добавить логику позже)
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Загрузить историю", use_container_width=True)
    with col2:
        st.button("🔄 Обновить", use_container_width=True)
