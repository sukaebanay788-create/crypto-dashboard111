import streamlit as st
import ccxt
import pandas as pd
from streamlit_lightweight_charts import render_lightweight_charts

# Настройка страницы
st.set_page_config(layout="wide", page_title="Крипто-Скринер")
st.markdown("<style>.block-container{padding:0;}[data-testid=column]{padding:0!important}</style>", unsafe_allow_html=True)

# Инициализация биржи
@st.cache_resource
def init_exchange():
    return ccxt.okx({'enableRateLimit': True})

exchange = init_exchange()

# Получение списка пар USDT
@st.cache_data(ttl=300)
def get_usdt_symbols():
    markets = exchange.load_markets()
    return [s for s in markets if s.endswith('/USDT')]

# Загрузка свечных данных
@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
    return df

# Управление состоянием
if 'symbol' not in st.session_state:
    st.session_state.symbol = 'BTC/USDT'

# --- ИНТЕРФЕЙС ---
left, right = st.columns([4, 1])

with left:
    st.header(st.session_state.symbol)
    df = fetch_ohlcv(st.session_state.symbol)
    if not df.empty:
        chart_data = df[['time', 'open', 'high', 'low', 'close']].rename(
            columns={'time': 'time', 'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close'}
        ).to_dict('records')
        
        render_lightweight_charts([{
            "chart": {"height": 750, "layout": {"background": {"color": "#0e1117"}, "textColor": "#d1d4dc"}},
            "series": [{"type": "Candlestick", "data": chart_data, "options": {"upColor": "#26a69a", "downColor": "#ef5350"}}]
        }])

with right:
    st.markdown("**📋 Все монеты**")
    search = st.text_input("Поиск", placeholder="BTC...")
    filtered = [s for s in get_usdt_symbols() if search.upper() in s] if search else get_usdt_symbols()
    with st.container(height=650):
        for sym in filtered[:50]:
            if st.button(sym, key=f"btn_{sym}", use_container_width=True):
                st.session_state.symbol = sym
                st.rerun()
