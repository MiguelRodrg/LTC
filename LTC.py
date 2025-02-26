import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Cursor

# URL de la API de Binance para obtener datos históricos de LTC/USDT
url_historical = "https://api.binance.com/api/v3/klines"
url_realtime = "https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT"

# Parámetros para la consulta de datos históricos (último mes)
symbol = "LTCUSDT"
interval = "1h"  # Intervalo de 1 hora para los datos históricos
limit = 1000  # Número máximo de datos que queremos recuperar (ajustar según el intervalo)

# Función para obtener los datos históricos de Binance
def get_historical_data():
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url_historical, params=params)
    data = response.json()

    # Extraemos las fechas y precios
    timestamps = [item[0] for item in data]
    close_prices = [float(item[4]) for item in data]

    # Convertimos timestamps a fechas legibles
    dates = [pd.to_datetime(timestamp, unit='ms') for timestamp in timestamps]

    return dates, close_prices

# Obtener los datos históricos
dates, prices = get_historical_data()

# Configurar la gráfica
fig, ax = plt.subplots(figsize=(10, 6))
line1, = ax.plot(dates, prices, label='Datos Históricos', color='b')

# Etiquetas y título
ax.set_xlabel('Fecha')
ax.set_ylabel('Precio (USDT)')
ax.set_title('Precio Histórico de LTC/USDT con Datos en Tiempo Real')
ax.legend()

# Hacer el gráfico interactivo con cursor
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

# Formato de fecha
fig.autofmt_xdate()

# Variables para los datos en tiempo real
realtime_dates = []
realtime_prices = []

# Función para obtener datos en tiempo real
def get_realtime_data():
    response = requests.get(url_realtime)
    data = response.json()
    price = float(data['price'])
    timestamp = pd.to_datetime('now')  # Timestamp actual
    return timestamp, price

# Función para actualizar el gráfico con datos en tiempo real
def update(frame):
    # Obtener el nuevo precio en tiempo real
    timestamp, price = get_realtime_data()

    # Agregar los nuevos datos al gráfico
    realtime_dates.append(timestamp)
    realtime_prices.append(price)

    # Actualizar los datos en el gráfico (combinamos históricos y en tiempo real)
    line1.set_xdata(dates + realtime_dates)
    line1.set_ydata(prices + realtime_prices)

    # Actualizar el rango de fechas
    ax.relim()  # Recalcular límites del gráfico
    ax.autoscale_view()  # Autoescala el gráfico para que se ajuste a los nuevos datos

    return line1,

# Función de animación para actualizar en tiempo real
ani = FuncAnimation(fig, update, blit=True, interval=1000)  # Actualiza cada segundo (1000 ms)

# Mostrar el gráfico
plt.show()
