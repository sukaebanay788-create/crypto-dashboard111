import streamlit as st
import streamlit.components.v1 as components

# Настройка страницы: широкий режим, без боковых отступов
st.set_page_config(layout="wide", page_title="Терминал")

# Убираем все лишние отступы у основного контейнера и колонок
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

# Создаем две колонки: левая (график) – широкая, правая (скринер) – узкая
# gap="small" убирает зазор между колонками
left_col, right_col = st.columns([4, 1], gap="small")

with left_col:
    # Встраиваем виджет "График" от TradingView
    chart_widget = """
    <div class="tradingview-widget-container" style="height:100vh; width:100%">
      <div id="tradingview_chart" style="height:100vh; width:100%"></div>
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
    components.html(chart_widget, height=1000)  # Задаем высоту, чтобы график занял весь экран

with right_col:
    # Встраиваем виджет "Скринер криптовалют"
    screener_widget = """
    <div class="tradingview-widget-container" style="height:100vh; width:100%">
      <div class="tradingview-widget-container__widget" style="height:100vh; width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
      {
      "width": "100%",
      "height": "100%",
      "defaultColumn": "overview",
      "defaultScreen": "top_gainers",
      "market": "crypto",
      "showToolbar": true,
      "colorTheme": "dark",
      "locale": "ru"
      }
      </script>
    </div>
    """
    components.html(screener_widget, height=1000)
