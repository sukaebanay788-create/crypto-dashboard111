import streamlit as st
import ccxt
import pandas as pd
from streamlit_lightweight_charts import render_lightweight_charts
import time

# --- Настройка страницы ---
st.set_page_config(layout="wide", page_title="Crypto Screener")

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
</style>
""", unsafe_allow_html=True)

# --- Инициализация биржи ---
@st.cache_resource
def init_exchange():
    return ccxt.okx({'enableRateLimit': True})

exchange = init_exchange()

# --- Получение списка пар USDT ---
@st.cache_data(ttl=300)
def get_usdt_symbols():
    markets = exchange.load_markets()
    return [s for s in markets if s.endswith('/USDT')]

# --- Загрузка свечных данных ---
@st.cache_data(ttl=30)  # Кеш на 30 секунд для автообновления
def fetch_ohlcv(symbol, timeframe='1h', limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# --- Инициализация состояния ---
if 'symbol' not in st.session_state:
    st.session_state.symbol = 'BTC/USDT'
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# --- Боковая панель с настройками ---
with st.sidebar:
    st.header("⚙️ Настройки")
    timeframe = st.selectbox(
        "Таймфрейм",
        options=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
        index=4  # '1h'
    )
    st.session_state.auto_refresh = st.checkbox("Автообновление (каждые 10 сек)", value=True)

# --- Основной интерфейс: две колонки ---
left, right = st.columns([4, 1], gap="small")

# --- ЛЕВАЯ КОЛОНКА: ГРАФИК ---
with left:
    st.header(f"{st.session_state.symbol} · {timeframe}")
    df = fetch_ohlcv(st.session_state.symbol, timeframe=timeframe)

    if not df.empty:
        # Подготовка данных для Lightweight Charts
        chart_data = df[['timestamp', 'open', 'high', 'low', 'close']].copy()
        chart_data['time'] = chart_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        chart_data = chart_data.drop('timestamp', axis=1)

        # Преобразование в список словарей
        chart_json = chart_data.to_dict('records')

        # Рендеринг графика
        render_lightweight_charts([{
            "chart": {
                "height": 750,
                "layout": {
                    "background": {"color": "#0e1117"},
                    "textColor": "#d1d4dc"
                },
                "grid": {
                    "vertLines": {"color": "rgba(42, 46, 57, 0)"},
                    "horzLines": {"color": "rgba(42, 46, 57, 0.6)"}
                }
            },
            "series": [{
                "type": "Candlestick",
                "data": chart_json,
                "options": {
                    "upColor": "#26a69a",
                    "downColor": "#ef5350",
                    "borderVisible": False,
                    "wickUpColor": "#26a69a",
                    "wickDownColor": "#ef5350"
                }
            }]
        }])
    else:
        st.warning("Нет данных для отображения")

# --- ПРАВАЯ КОЛОНКА: СКРИНЕР ---
with right:
    st.markdown("**📋 Все монеты (USDT)**")
    search = st.text_input("🔍 Поиск", placeholder="BTC, ETH...", label_visibility="collapsed")
    symbols = get_usdt_symbols()
    filtered = [s for s in symbols if search.upper() in s] if search else symbols

    with st.container(height=650):
        for sym in filtered[:50]:
            if st.button(sym, key=f"btn_{sym}", use_container_width=True,
                         type="secondary" if sym != st.session_state.symbol else "primary"):
                st.session_state.symbol = sym
                st.rerun()

# --- Автообновление ---
if st.session_state.auto_refresh:
    time.sleep(10)  # Пауза 10 секунд
    st.rerun()
