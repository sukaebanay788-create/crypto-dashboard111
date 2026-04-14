import streamlit as st

# --- Настройка страницы: широкий режим и плотное размещение ---
st.set_page_config(layout="wide", page_title="Crypto Screener")

# CSS для удаления всех отступов и промежутков
st.markdown("""
<style>
    /* Убираем отступы у основного контейнера Streamlit */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    /* Убираем отступы у колонок (div-ов с атрибутом data-testid="column") */
    div[data-testid="column"] {
        padding: 0px !important;
    }
    /* Убираем лишние внешние отступы у самого приложения */
    .stApp {
        margin: 0;
        padding: 0;
    }
    /* Убираем рамку у iframe и делаем его блочным элементом */
    iframe {
        border: none;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# --- Создаем две колонки: левая (график) – широкая, правая (скринер) – узкая ---
# gap="small" минимизирует расстояние между колонками
left_col, right_col = st.columns([4, 1], gap="small")

# --- ЛЕВАЯ КОЛОНКА: ГРАФИК TRADINGVIEW ---
with left_col:
    # URL для виджета "Advanced Chart" (можно менять символ и настройки)
    chart_url = "https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=BINANCE%3ABTCUSDT&interval=60&theme=dark&style=1&locale=ru&toolbar_bg=%23f1f3f6&hide_side_toolbar=false&allow_symbol_change=true&save_image=false&studies=RSI%40tv-basicstudies"
    
    # Встраиваем виджет через iframe
    st.components.v1.iframe(
        src=chart_url,
        height=1000,   # Высота подбирается под экран (можно увеличить)
        scrolling=False
    )

# --- ПРАВАЯ КОЛОНКА: СКРИНЕР МОНЕТ TRADINGVIEW ---
with right_col:
    # URL для виджета "Screener" с сортировкой по росту за 24ч
    screener_url = "https://s.tradingview.com/widgetembed/?frameElementId=tradingview_screener&market=crypto&defaultScreen=top_gainers&colorTheme=dark&locale=ru"
    
    st.components.v1.iframe(
        src=screener_url,
        height=1000,
        scrolling=False
    )
