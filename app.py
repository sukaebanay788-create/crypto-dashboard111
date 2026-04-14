import streamlit as st
import ccxt
import pandas as pd
from lightweight_charts_v5 import lightweight_charts_v5_component

st.set_page_config(layout="wide", page_title="Crypto Screener")
st.markdown("<style>.block-container{padding:0;}[data-testid=column]{padding:0!important}</style>", unsafe_allow_html=True)

@st.cache_resource
def init_exchange():
    return ccxt.okx({'enableRateLimit': True})

exchange = init_exchange()

@st.cache_data(ttl=300)
def get_usdt_symbols():
    markets = exchange.load_markets()
    return [s for s in markets if s.endswith('/USDT')]

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
    return df

if 'symbol' not in st.session_state:
    st.session_state.symbol = 'BTC/USDT'

left, right = st.columns([4, 1])

with left:
    st.header(st.session_state.symbol)
    df = fetch_ohlcv(st.session_state.symbol)
    if not df.empty:
        chart_data = df[['time', 'open', 'high', 'low', 'close']].rename(
            columns={'time': 'time', 'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close'}
        ).to_dict('records')
        
        # Рендерим график с помощью v5
        lightweight_charts_v5_component(
            name=f"{st.session_state.symbol} Chart",
            charts=[{
                "chart": {
                    "layout": {
                        "background": {"color": "#0e1117"},
                        "textColor": "#d1d4dc"
                    },
                    "grid": {
                        "vertLines": {"color": "rgba(42, 46, 57, 0)"},
                        "horzLines": {"color": "rgba(42, 46, 57, 0.6)"},
                    }
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

with right:
    st.markdown("**📋 Все монеты**")
    search = st.text_input("Поиск", placeholder="BTC...")
    filtered = [s for s in get_usdt_symbols() if search.upper() in s] if search else get_usdt_symbols()
    with st.container(height=650):
        for sym in filtered[:50]:
            if st.button(sym, key=f"btn_{sym}", use_container_width=True):
                st.session_state.symbol = sym
                st.rerun()
