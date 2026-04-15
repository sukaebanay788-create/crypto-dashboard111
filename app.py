import streamlit as st
import requests
import pandas as pd
from streamlit_lightweight_charts import render_lightweight_charts
import time
from datetime import datetime, timedelta

# --- Настройка страницы ---
st.set_page_config(layout="wide", page_title="Crypto Screener")

# --- CSS для плотного интерфейса ---
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; max-width: 100%;
    }
    div[data-testid="column"] {
        padding: 0px !important;
    }
    .stApp {
        margin: 0; padding: 0;
    }
    iframe {
        border: none; display: block;
    }
</style>
""", unsafe_allow_html=True)

# --- Константы API ---
BASE_URL = "https://api.coincap.io/v2"

# --- Кэшируемые функции для работы с API ---
@st.cache_data(ttl=60)
def get_top_assets(limit=50):
    """Получить список топовых активов"""
    resp = requests.get(f"{BASE_URL}/assets", params={"limit": limit})
    if resp.status_code == 200:
        return resp.json()["data"]
    else:
        st.error("Ошибка загрузки списка монет")
        return []

@st.cache_data(ttl=30)
def get_asset_history(asset_id, interval="h1", limit=200):
    """
    Получить историю цены для актива.
    interval: m1, m5, m15, m30, h1, h2, h6, h12, d1
    """
    end = int(datetime.now().timestamp() * 1000)
    start = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
    url = f"{BASE_URL}/assets/{asset_id}/history"
    params = {
        "interval": interval,
        "start": start,
        "end": end,
        "limit": limit
    }
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()["data"]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        df["open"] = df["priceUsd"].astype(float)
        df["high"] = df["priceUsd"].astype(float)
        df["low"] = df["priceUsd"].astype(float)
        df["close"] = df["priceUsd"].astype(float)
        return df
    else:
        st.error(f"Ошибка загрузки истории для {asset_id}")
        return pd.DataFrame()

# --- Инициализация состояния ---
if "symbol" not in st.session_state:
    st.session_state.symbol = "bitcoin"
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# --- Боковая панель ---
with st.sidebar:
    st.header("⚙️ Настройки")
    interval = st.selectbox(
        "Интервал",
        options=["m1", "m5", "m15", "m30", "h1", "h2", "h6", "h12", "d1"],
        index=4  # h1
    )
    st.session_state.auto_refresh = st.checkbox("Автообновление (30 сек)", value=True)

# --- Загрузка списка монет ---
assets = get_top_assets(50)
if not assets:
    st.stop()

# --- Поиск выбранного актива ---
selected = next((a for a in assets if a["id"] == st.session_state.symbol), assets[0])
symbol_name = f"{selected['name']} ({selected['symbol']})"

# --- Основной интерфейс ---
left, right = st.columns([4, 1], gap="small")

# --- ЛЕВАЯ КОЛОНКА: ГРАФИК ---
with left:
    st.header(f"{symbol_name} · {interval}")
    df = get_asset_history(st.session_state.symbol, interval=interval)

    if not df.empty:
        # Подготовка данных для Lightweight Charts
        chart_data = df[["time", "open", "high", "low", "close"]].copy()
        chart_data["time"] = chart_data["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        chart_json = chart_data.to_dict("records")

        render_lightweight_charts([{
            "chart": {
                "height": 750,
                "layout": {
                    "background": {"color": "#0e1117"},
                    "textColor": "#d1d4dc"
                },
                "grid": {
                    "vertLines": {"color": "rgba(42, 46, 57, 0)"},
                    "horzLines": {"color": "rgba(42, 46, 57, 0.6)"}
                }
            },
            "series": [{
                "type": "Candlestick",
                "data": chart_json,
                "options": {
                    "upColor": "#26a69a",
                    "downColor": "#ef5350",
                    "borderVisible": False,
                    "wickUpColor": "#26a69a",
                    "wickDownColor": "#ef5350"
                }
            }]
        }])
    else:
        st.warning("Нет данных для отображения")

# --- ПРАВАЯ КОЛОНКА: СКРИНЕР ---
with right:
    st.markdown("**📋 Топ 50 монет**")
    search = st.text_input("🔍 Поиск", placeholder="BTC, ETH...", label_visibility="collapsed")
    filtered = [a for a in assets if search.upper() in a["id"].upper() or search.upper() in a["symbol"].upper()] if search else assets

    with st.container(height=650):
        for asset in filtered:
            label = f"{asset['name']} ({asset['symbol']})"
            change = float(asset.get("changePercent24Hr", 0))
            change_str = f"{change:+.2f}%"
            color = "#26a69a" if change >= 0 else "#ef5350"
            # Кнопка с цветным индикатором изменения
            btn_type = "primary" if asset["id"] == st.session_state.symbol else "secondary"
            if st.button(f"{label}  {change_str}", key=f"btn_{asset['id']}", use_container_width=True, type=btn_type):
                st.session_state.symbol = asset["id"]
                st.rerun()

# --- Автообновление ---
if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()
