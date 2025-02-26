import requests
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Cursor, Button

# URL de la API de Binance para obtener datos históricos de LTC/USDT
url_historical = "https://api.binance.com/api/v3/klines"
url_realtime = "https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT"

# Parámetros para la consulta de datos históricos (último mes)
symbol = "LTCUSDT"
interval_historical = "1h"  # Intervalo de 1 hora para los datos históricos
limit = 1000  # Número máximo de datos que queremos recuperar

# Función para obtener los datos históricos de Binance (último mes)
def get_historical_data():
    params = {
        "symbol": symbol,
        "interval": interval_historical,
        "limit": limit
    }
    response = requests.get(url_historical, params=params)
    data = response.json()

    # Extraemos las fechas y precios
    timestamps = [item[0] for item in data]
    close_prices = [float(item[4]) for item in data]

    # Convertimos timestamps a fechas UTC y luego a la hora local
    dates = [pd.to_datetime(timestamp, unit='ms').tz_localize('UTC').tz_convert('America/New_York') for timestamp in timestamps]

    return dates, close_prices

# Función para obtener datos en tiempo real (últimos 2 días)
def get_realtime_data():
    response = requests.get(url_realtime)
    data = response.json()
    price = float(data['price'])
    timestamp = pd.to_datetime('now', utc=True).tz_convert('America/New_York')  # Convertir a hora local
    return timestamp, price

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
# cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

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
    timestamp = pd.to_datetime('now', utc=True).tz_convert('America/New_York')  # Convertir a hora local
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

# Configuración de rango de visualización predeterminado (últimos 5 minutos)
def set_default_view():
    end_time = pd.to_datetime('now', utc=True).tz_convert('America/New_York')
    start_time = end_time - pd.Timedelta(minutes=5)  # Últimos 5 minutos
    ax.set_xlim(start_time, end_time)  # Ajustar el rango de fechas a los últimos 5 minutos

# Función de zoom in centrado
def zoom_in_x(event):
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Calcular el centro actual del gráfico
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2

    # Reducir el rango del eje X (acercar la visualización)
    zoom_factor = 0.9  # Factor de zoom, 0.9 para hacer zoom in
    ax.set_xlim(center_x - (center_x - x_min) * zoom_factor, center_x + (x_max - center_x) * zoom_factor)

    # Actualizar la vista
    fig.canvas.draw()

# Función de zoom out centrado
def zoom_out_x(event):
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Calcular el centro actual del gráfico
    center_x = (x_min + x_max) / 2

    # Aumentar el rango del eje X (alejar la visualización)
    zoom_factor = 1.5  # Factor de zoom, 1.1 para hacer zoom out
    ax.set_xlim(center_x - (center_x - x_min) * zoom_factor, center_x + (x_max - center_x) * zoom_factor)

    # Actualizar la vista
    fig.canvas.draw()

def zoom_in_y(event):
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Calcular el centro actual del gráfico
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2

    # Reducir el rango del eje X (acercar la visualización)
    zoom_factor = 0.9  # Factor de zoom, 0.9 para hacer zoom in
    # Establecer límites de Y, si es necesario, para hacer zoom también en el eje Y
    ax.set_ylim(center_y - (center_y - y_min) * zoom_factor, center_y + (y_max - center_y) * zoom_factor)

    # Actualizar la vista
    fig.canvas.draw()

# Función de zoom out centrado
def zoom_out_y(event):
    y_min, y_max = ax.get_ylim()
    y_min, y_max = ax.get_ylim()

    # Calcular el centro actual del gráfico
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2


    # Aumentar el rango del eje X (alejar la visualización)
    zoom_factor = 1.1  # Factor de zoom, 1.1 para hacer zoom out
    # Establecer límites de Y, si es necesario
    ax.set_ylim(center_y - (center_y - y_min) * zoom_factor, center_y + (y_max - center_y) * zoom_factor)

    # Actualizar la vista
    fig.canvas.draw()

# Función de animación para actualizar en tiempo real
ani = FuncAnimation(fig, update, blit=True, interval=1000, cache_frame_data=False)  # Desactivar la caché

# Establecer el rango predeterminado de la vista
set_default_view()

# Crear botones de zoom in y zoom out
ax_zoom_in_x = plt.axes([0.74, 0.10, 0.075, 0.075])  # Definir el área del botón
ax_zoom_out_x = plt.axes([0.9, 0.10, 0.075, 0.075])  # Definir el área del botón
ax_zoom_in_y = plt.axes([0.82, 0.15, 0.075, 0.075])  # Definir el área del botón
ax_zoom_out_y = plt.axes([0.82, 0.05, 0.075, 0.075])  # Definir el área del botón

button_zoom_in_x = Button(ax_zoom_in_x, 'Z+ x')
button_zoom_out_x = Button(ax_zoom_out_x, 'Z- x')
button_zoom_in_y = Button(ax_zoom_in_y, 'Z+ y')
button_zoom_out_y = Button(ax_zoom_out_y, 'Z- y')

button_zoom_in_x.on_clicked(zoom_in_x)  # Asignar la acción de hacer zoom in
button_zoom_out_x.on_clicked(zoom_out_x)  # Asignar la acción de hacer zoom out
button_zoom_in_y.on_clicked(zoom_in_y)  # Asignar la acción de hacer zoom in
button_zoom_out_y.on_clicked(zoom_out_y)  # Asignar la acción de hacer zoom out

# Mostrar el gráfico
plt.show()
