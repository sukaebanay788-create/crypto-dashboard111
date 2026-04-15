import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json

st.set_page_config(page_title="Крипто Скринер", layout="wide")

st.title("📊 Крипто Скринер")
st.markdown("Выберите торговую пару для просмотра графика и данных.")

# --- Боковая панель ---
with st.sidebar:
    st.header("⚙️ Настройки")
    # Расширенный список популярных пар
    symbols_list = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT",
        "XRPUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT"
    ]
    symbol = st.selectbox("Выберите торговую пару:", symbols_list)
    interval = st.selectbox(
        "Интервал графика:",
        ("60", "240", "D", "W"),
        format_func=lambda x: {"60": "1 час", "240": "4 часа", "D": "1 день", "W": "1 неделя"}[x],
        index=0
    )
    # Добавим ручной ввод для продвинутых пользователей
    custom_symbol = st.text_input("Или введите свою пару (например, AVAXUSDT):")
    if custom_symbol:
        symbol = custom_symbol.upper().strip()

# --- Функции для безопасной работы с API Binance ---
@st.cache_data(ttl=60, show_spinner="Загрузка данных с Binance...")
def get_binance_data(symbol):
    """Получает 24-часовую статистику и последние сделки с Binance."""
    ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    trades_url = f"https://api.binance.com/api/v3/trades?symbol={symbol}&limit=20"
    
    # Инициализация пустыми значениями
    ticker_data = None
    trades_data = []
    error_msg = None

    try:
        # Запрос тикера
        resp = requests.get(ticker_url, timeout=5)
        if resp.status_code == 200:
            ticker_data = resp.json()
            # Проверяем, что API вернуло объект, а не сообщение об ошибке
            if "code" in ticker_data and ticker_data["code"] < 0:
                error_msg = f"Binance API Error: {ticker_data.get('msg', 'Неизвестная ошибка')}"
                ticker_data = None
        else:
            error_msg = f"HTTP ошибка {resp.status_code}"
        
        # Запрос сделок
        resp_trades = requests.get(trades_url, timeout=5)
        if resp_trades.status_code == 200:
            trades_data = resp_trades.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"Сетевая ошибка: {e}"
    except json.JSONDecodeError:
        error_msg = "Ошибка парсинга ответа от Binance"

    return ticker_data, trades_data, error_msg

# --- Виджет графика TradingView ---
def get_tradingview_chart(symbol, interval):
    """Возвращает HTML-код для встраивания виджета TradingView."""
    tv_symbol = f"BINANCE:{symbol}"
    return f"""
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
    """

# --- Основной блок приложения ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"График {symbol}")
    chart_html = get_tradingview_chart(symbol, interval)
    components.html(chart_html, height=600)

with col2:
    st.subheader(f"Данные по {symbol}")
    ticker, trades, error = get_binance_data(symbol)
    
    if error:
        st.error(f"⚠️ Не удалось получить данные: {error}")
    elif ticker:
        # Проверяем наличие всех необходимых ключей
        last_price = ticker.get('lastPrice')
        price_change_percent = ticker.get('priceChangePercent')
        quote_volume = ticker.get('quoteVolume')
        high_24h = ticker.get('highPrice')
        low_24h = ticker.get('lowPrice')
        
        # Отображаем метрики, если они есть
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            if last_price:
                st.metric("Цена", f"${float(last_price):,.4f}")
            else:
                st.metric("Цена", "Н/Д")
        with col_metric2:
            if price_change_percent:
                change = float(price_change_percent)
                st.metric("24ч %", f"{change:.2f}%", delta=f"{change:.2f}%")
            else:
                st.metric("24ч %", "Н/Д")
        with col_metric3:
            if quote_volume:
                st.metric("Объём (24ч)", f"${float(quote_volume):,.0f}")
            else:
                st.metric("Объём (24ч)", "Н/Д")
        
        # Дополнительные данные: High/Low
        if high_24h and low_24h:
            st.caption(f"24h High/Low: {float(high_24h):,.4f} / {float(low_24h):,.4f}")
        
        # Таблица последних сделок
        st.subheader("Последние сделки")
        if trades:
            df_trades = pd.DataFrame(trades)
            # Преобразуем время
            df_trades['time'] = pd.to_datetime(df_trades['time'], unit='ms')
            df_trades['price'] = df_trades['price'].astype(float)
            df_trades['qty'] = df_trades['qty'].astype(float)
            # Оставляем нужные колонки
            df_trades = df_trades[['time', 'price', 'qty']]
            df_trades.columns = ['Время', 'Цена', 'Количество']
            # Форматируем таблицу
            st.dataframe(
                df_trades.style.format({'Цена': '{:.4f}', 'Количество': '{:.4f}'}),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Нет данных о последних сделках")
    else:
        st.warning("Нет данных для отображения.")

st.markdown("---")
st.caption("Данные предоставлены Binance API. График от TradingView.")
