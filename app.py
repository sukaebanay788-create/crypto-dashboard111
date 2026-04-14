import streamlit as st

st.set_page_config(layout="wide", page_title="Терминал")

# Убираем отступы
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
    iframe {
        border: none;
        display: block;
        width: 100%;
        height: 100vh;
    }
    .stApp {
        margin: 0;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([4, 1], gap="small")

with left_col:
    # Используем iframe для графика
    st.iframe(
        src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=BINANCE:BTCUSDT&interval=60&theme=dark&style=1&locale=ru&toolbar_bg=%23f1f3f6&hide_side_toolbar=false&allow_symbol_change=true&save_image=false&studies=RSI%40tv-basicstudies",
        height=1000,
        scrolling=False
    )

with right_col:
    # iframe для скринера
    st.iframe(
        src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_screener&market=crypto&defaultScreen=top_gainers&colorTheme=dark&locale=ru",
        height=1000,
        scrolling=False
    )
