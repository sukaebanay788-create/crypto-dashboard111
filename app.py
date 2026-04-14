import streamlit as st
import ccxt
import pandas as pd
from streamlit_lightweight_charts_pro import renderChart

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

# --- Инициализация и кэширование данных ---
@st.cache_resource
def init_exchange():
    exchange = ccxt.okx({'enableRateLimit': True})
    return exchange

exchange = init_exchange()

@st.cache_data(ttl=300)
def get_usdt_symbols():
    markets = exchange.load_markets()
    usdt_pairs = [symbol for symbol in markets if symbol.endswith('/USDT')]
    popular = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
               'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT', 'DOT/USDT', 'LTC/USDT']
    result = popular + [p for p in usdt_pairs if p not in popular][:35]
    return result

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, timeframe='1h', limit=200):
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

# --- Создание интерфейса ---
left_col, right_col = st.columns([4, 1], gap="small")

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
        chart = {
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
        }
        
        renderChart(chart, height=800)
    else:
        st.warning("Нет данных для отображения")

with right_col:
    st.markdown("**📋 Все монеты (USDT)**")
    search = st.text_input("🔍 Поиск", placeholder="BTC, ETH...", label_visibility="collapsed")
    filtered_symbols = symbols if not search else [s for s in symbols if search.upper() in s]

    with st.container(height=650):
        for sym in filtered_symbols:
            if st.button(sym, key=f"btn_{sym}", use_container_width=True,
                         type="secondary" if sym != st.session_state.selected_symbol else "primary"):
                st.session_state.selected_symbol = sym
                st.rerun()
