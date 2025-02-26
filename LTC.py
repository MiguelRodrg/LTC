import requests
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from datetime import datetime, timedelta

# URL de la API de Binance para obtener datos históricos de LTC/USDT
url_historical = "https://api.binance.com/api/v3/klines"
url_realtime = "https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT"

# Parámetros para la consulta de datos históricos (último mes)
symbol = "LTCUSDT"
interval_historical = "1h"  # Intervalo de 1 hora para los datos históricos
interval_2d = "1m"
limit = 1000  # Número máximo de datos que queremos recuperar
limit2d = 2880  # Número máximo de datos (2 días * 1440 minutos por día)


# Obtener la fecha de hace dos días
two_days_ago = datetime.now() - timedelta(days=2)
two_days_ago_timestamp = int(two_days_ago.timestamp() * 1000)  # Convertir a milisegundos


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

    # Filtramos los datos para excluir los últimos dos días
    dates_filtered = [date for date in dates if date.timestamp() < two_days_ago.timestamp()]
    prices_filtered = [price for i, price in enumerate(close_prices) if dates[i].timestamp() < two_days_ago.timestamp()]

    return dates_filtered, prices_filtered

# Función para obtener datos en tiempo real (últimos 2 días)
def get_historical_data_2days():
    params = {
        "symbol": symbol,
        "interval": interval_2d,
        "limit": limit2d
    }
    response = requests.get(url_historical, params=params)
    data = response.json()

    # Extraemos las fechas y precios de cierre
    timestamps = [item[0] for item in data]
    close_prices = [float(item[4]) for item in data]

    # Convertimos timestamps a fechas UTC y luego a la hora local
    dates = [pd.to_datetime(timestamp, unit='ms').tz_localize('UTC').tz_convert('America/New_York') for timestamp in timestamps]

    return dates, close_prices

# Obtener los datos históricos del último mes
dates_month, prices_month = get_historical_data()

# Obtener los datos de los últimos dos días
dates_2d, prices_2d = get_historical_data_2days()

# Combinar ambos conjuntos de datos
dates = dates_month + dates_2d
prices = prices_month + prices_2d


# Obtener los datos históricos
#dates, prices = get_historical_data()

# Configurar la gráfica
fig, ax = plt.subplots(figsize=(6, 4))
line1, = ax.plot(dates, prices, label='Datos Históricos', color='y')

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
    end_time = pd.to_datetime('now', utc=True).tz_convert('America/New_York') + pd.Timedelta(minutes=2)
    start_time = end_time - pd.Timedelta(minutes=45)  # Últimos 5 minutos
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
    x_min, x_max = ax.get_xlim()
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

# Función para ajustar los valores máximos y mínimos del eje Y según los datos visibles
def adjust_y_limits(event):
    # Obtener el rango visible actual en el eje X (fechas) en formato de tiempo en segundos
    x_min, x_max = ax.get_xlim()

    # Convertir x_min y x_max de segundos a pandas.Timestamp
    # Usamos pd.to_datetime() con `unit='s'` para que pandas interprete correctamente los valores en segundos.
    x_min = pd.to_datetime(x_min, unit='d', utc=True)  # Convierte segundos a Timestamp UTC
    x_max = pd.to_datetime(x_max, unit='d', utc=True)  # Convierte segundos a Timestamp UTC

    # Asegurarse de que x_min y x_max tengan la misma zona horaria que las fechas en 'dates' y 'realtime_dates'
    x_min = x_min.tz_convert('America/New_York')  # Localizar a la zona horaria correcta
    x_max = x_max.tz_convert('America/New_York')  # Localizar a la zona horaria correcta

    # Filtrar las fechas visibles dentro del rango x_min, x_max
    visible_dates = [date for date in dates + realtime_dates if x_min <= date <= x_max]

    # Filtrar los precios correspondientes a las fechas visibles
    visible_prices = []
    for date, price in zip(dates + realtime_dates, prices + realtime_prices):
        # Solo agregar los precios correspondientes a las fechas visibles
        if date in visible_dates:
            visible_prices.append(price)

    # Si hay precios visibles, ajustamos los límites de Y
    if visible_prices:
        margin = 0.05

        new_y_min = min(visible_prices)  # Valor mínimo
        new_y_max = max(visible_prices)  # Valor máximo

        new_y_min = new_y_min - (new_y_max - new_y_min) * margin
        new_y_max = new_y_max + (new_y_max - new_y_min) * margin

        # Ajustar los límites del eje Y (añadimos un pequeño margen)
        ax.set_ylim(new_y_min , new_y_max )

        # Actualizar la vista del gráfico
        fig.canvas.draw()





# Función de animación para actualizar en tiempo real
ani = FuncAnimation(fig, update, blit=True, interval=1000, cache_frame_data=False)  # Desactivar la caché

# Establecer el rango predeterminado de la vista
set_default_view()

# Crear botones de zoom in y zoom out
ax_zoom_in_x = plt.axes([0.74, 0.05, 0.065, 0.075])  # Definir el área del botón
ax_zoom_out_x = plt.axes([0.9, 0.05, 0.065, 0.075])  # Definir el área del botón
ax_zoom_in_y = plt.axes([0.82, 0.1, 0.065, 0.075])  # Definir el área del botón
ax_zoom_out_y = plt.axes([0.82, 0.005, 0.065, 0.075])  # Definir el área del botón
ax_adjust_y = plt.axes([0.92, 0.2, 0.075, 0.075])  # Definir el área del botón de ajuste de Y

button_zoom_in_x = Button(ax_zoom_in_x, '+ x')
button_zoom_out_x = Button(ax_zoom_out_x, '- x')
button_zoom_in_y = Button(ax_zoom_in_y, '+ y')
button_zoom_out_y = Button(ax_zoom_out_y, '- y')
button_adjust_y = Button(ax_adjust_y, 'Auto Y')

button_zoom_in_x.on_clicked(zoom_in_x)  # Asignar la acción de hacer zoom in
button_zoom_out_x.on_clicked(zoom_out_x)  # Asignar la acción de hacer zoom out
button_zoom_in_y.on_clicked(zoom_in_y)  # Asignar la acción de hacer zoom in
button_zoom_out_y.on_clicked(zoom_out_y)  # Asignar la acción de hacer zoom out
button_adjust_y.on_clicked(adjust_y_limits)  # Asignar la acción de ajuste del eje Y

# Mostrar el gráfico
plt.show()
