import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Крипто Скринер", layout="wide")

st.title("📊 Крипто Скринер")
st.markdown("Выберите торговую пару для просмотра графика и данных.")

# --- Боковая панель для настроек и фильтров ---
with st.sidebar:
    st.header("⚙️ Настройки")
    symbol = st.selectbox(
        "Выберите торговую пару:",
        ("BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"),
        index=0
    )
    interval = st.selectbox(
        "Интервал графика:",
        ("60", "240", "D", "W"),
        format_func=lambda x: {"60": "1 час", "240": "4 часа", "D": "1 день", "W": "1 неделя"}[x],
        index=0
    )

# --- Функции для работы с Binance API ---
@st.cache_data(ttl=60) # Кэшируем данные на 60 секунд
def get_binance_data(symbol):
    """Получает 24-часовую статистику и последние сделки с Binance."""
    ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    trades_url = f"https://api.binance.com/api/v3/trades?symbol={symbol}&limit=25"
    try:
        ticker_data = requests.get(ticker_url).json()
        trades_data = requests.get(trades_url).json()
        return ticker_data, trades_data
    except Exception as e:
        st.error(f"Ошибка получения данных: {e}")
        return {}, []

# --- Виджет графика TradingView ---
def get_tradingview_chart(symbol, interval):
    """Возвращает HTML-код для встраивания виджета TradingView."""
    # Используем формат BINANCE:{SYMBOL} для корректного отображения
    tv_symbol = f"BINANCE:{symbol}"
    return f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%; width:100%">
      <div id="tradingview_chart" style="height:600px; width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{tv_symbol}",
        "interval": "{interval}",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "ru",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    <!-- TradingView Widget END -->
    """

# --- Основной блок приложения ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"График {symbol}")
    # Встраиваем график как HTML-компонент
    chart_html = get_tradingview_chart(symbol, interval)
    components.html(chart_html, height=600)

with col2:
    st.subheader(f"Данные по {symbol}")
    ticker, trades = get_binance_data(symbol)
    
    if ticker:
        # Отображаем ключевые метрики
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Цена", f"${float(ticker['lastPrice']):,.2f}")
        with col_metric2:
            price_change = float(ticker['priceChangePercent'])
            st.metric("24ч %", f"{price_change:.2f}%", delta=f"{price_change:.2f}%")
        with col_metric3:
            st.metric("Объём (24ч)", f"${float(ticker['quoteVolume']):,.0f}")
        
        # Таблица последних сделок
        st.subheader("Последние сделки")
        if trades:
            df_trades = pd.DataFrame(trades)
            df_trades['time'] = pd.to_datetime(df_trades['time'], unit='ms')
            df_trades['price'] = df_trades['price'].astype(float).round(2)
            df_trades['qty'] = df_trades['qty'].astype(float).round(4)
            df_trades = df_trades[['time', 'price', 'qty']]
            df_trades.columns = ['Время', 'Цена', 'Количество']
            # Добавим визуальное форматирование
            st.dataframe(df_trades, use_container_width=True, hide_index=True)
    else:
        st.warning("Нет данных для отображения.")

st.markdown("---")
st.caption("Данные предоставлены Binance API. График от TradingView.")
