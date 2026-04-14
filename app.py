import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import tradingview_ta

# Функция для получения данных о криптовалютах
def get_crypto_data():
    response = requests.get('https://api.coinmarketcap.com/v1/ticker/')
    data = json.loads(response.text)
    return data

# Функция для отображения графика
def display_chart(data):
    prices = [item['price_usd'] for item in data]
    dates = [item['last_updated'] for item in data]
    plt.plot(dates, prices)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.title('Crypto Prices')
    st.pyplot(plt.gcf())

# Функция для отображения списка монет
def display_crypto_list(data):
    st.write('List of Cryptocurrencies')
    for item in data:
        st.write(item['symbol'])

# Основная функция для вашего приложения
def main():
    st.title('Crypto Screener')
    data = get_crypto_data()
    display_chart(data)
    display_crypto_list(data)
    # Используйте библиотеку TradingView для анализа данных
    st.write('TradingView Analysis')
    analysis = tradingview_ta.get_multiple_analysis(
        symbols=[item['symbol'] for item in data],
        interval='1d',
        type='point&figure'
    )
    for symbol, analysis_result in analysis.items():
        st.write(f'{symbol}: {analysis_result}')

if __name__ == '__main__':
    main()
