import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go

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
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

if 'symbol' not in st.session_state:
    st.session_state.symbol = 'BTC/USDT'

left, right = st.columns([4, 1])

with left:
    st.header(st.session_state.symbol)
    df = fetch_ohlcv(st.session_state.symbol)
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )])
        fig.update_layout(
            height=750,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_rangeslider_visible=False,
            dragmode='pan',
            template='plotly_dark',
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117'
        )
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': False})
    else:
        st.warning("Нет данных")

with right:
    st.markdown("**📋 Все монеты**")
    search = st.text_input("Поиск", placeholder="BTC...")
    symbols = get_usdt_symbols()
    filtered = [s for s in symbols if search.upper() in s] if search else symbols
    with st.container(height=650):
        for sym in filtered[:50]:
            if st.button(sym, key=f"btn_{sym}", use_container_width=True):
                st.session_state.symbol = sym
                st.rerun()
