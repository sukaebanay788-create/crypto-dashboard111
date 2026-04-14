import streamlit as st
import streamlit.components.v1 as components

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
    }
    .stApp {
        margin: 0;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([4, 1], gap="small")

with left_col:
    # График TradingView через components.html
    chart_html = """
    <div style="height:100vh; width:100%;">
        <div id="tradingview_chart" style="height:100vh; width:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
            "width": "100%",
            "height": "100%",
            "symbol": "BINANCE:BTCUSDT",
            "interval": "60",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "ru",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_chart"
        });
        </script>
    </div>
    """
    components.html(chart_html, height=1000)

with right_col:
    # Скринер TradingView через components.html
    screener_html = """
    <div style="height:100vh; width:100%;">
        <div id="tradingview_screener" style="height:100vh; width:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js"></script>
        <script type="text/javascript">
        new TradingView.ScreenerWidget({
            "width": "100%",
            "height": "100%",
            "defaultColumn": "overview",
            "defaultScreen": "top_gainers",
            "market": "crypto",
            "showToolbar": true,
            "colorTheme": "dark",
            "locale": "ru",
            "container_id": "tradingview_screener"
        });
        </script>
    </div>
    """
    components.html(screener_html, height=1000)
