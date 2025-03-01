import requests
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from datetime import datetime, timedelta

# URL de la API de Binance para obtener datos históricos de LTC/USDT
url_historical = "https://api.binance.com/api/v3/klines"
url_realtime = "https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT"

# Parámetros iniciales del proyecto

# Parámetros para la consulta de datos históricos (último mes)
symbol = "LTCUSDT"
interval_historical = "1h"  # Intervalo de 1 hora para los datos históricos
interval_2d = "1m"  # Intervalo para los datos en tiempo real (últimos 2 días)
limit = 1000  # Número máximo de datos que se quieren recuperar
limit2d = 2880  # Número máximo de datos de 2 días (2 * 1440 minutos por día)

# Variables de rango de fechas predeterminado (solo con valores relativos)
default_start_time_offset = pd.Timedelta(minutes=45)  # Desfase de 45 minutos para la fecha de inicio
default_end_time_offset = pd.Timedelta(minutes=5)  # Desfase de 5 minutos para la fecha de fin
# Posibles valores para 'default_start_time_offset' y 'default_end_time_offset':
# Se pueden usar unidades como: 
# - "seconds" (segundos)
# - "minutes" (minutos)
# - "hours" (horas)
# - "days" (días)
# - "weeks" (semanas)
# También se pueden asignar valores como: 
# - "5 minutes" -> pd.Timedelta(minutes=5)
# - "1 hour" -> pd.Timedelta(hours=1)
# - "2 days" -> pd.Timedelta(days=2)
# - "1 week" -> pd.Timedelta(weeks=1)

# Bandera de error de validación
validation_error_flag = False  # Bandera que indica si hubo un error de validación en las fechas

# Obtener la fecha de hace dos días
two_days_ago = datetime.now() - timedelta(hours=16)
two_days_ago_timestamp = int(two_days_ago.timestamp() * 1000)  # Convertir a milisegundos

# Función para validar el rango de fechas
def validate_date_range(start_date_offset, end_date_offset):
    global validation_error_flag

    try:
        # Calcular las fechas reales a partir de los desfases
        default_end_time = pd.to_datetime('now', utc=True).tz_convert('America/New_York') + end_date_offset
        default_start_time = default_end_time - start_date_offset

        # Intentar convertir las fechas a datetime
        start_date_parsed = pd.to_datetime(default_start_time, errors='raise')
        end_date_parsed = pd.to_datetime(default_end_time, errors='raise')

        # Verificar que la fecha de inicio sea anterior a la fecha final
        if start_date_parsed >= end_date_parsed:
            raise ValueError("La fecha de inicio no puede ser mayor o igual a la fecha final.")

        # Si las fechas son válidas, devolverlas
        validation_error_flag = False
        return start_date_parsed, end_date_parsed

    except Exception as e:
        # Si hay un error en la validación, asignar valores por defecto
        print(f"Error de validación de fechas: {e}. Usando valores por defecto.")
        validation_error_flag = True

        # Calcular fechas por defecto: 45 minutos antes y 5 minutos después de la hora actual
        default_end_time = pd.to_datetime('now', utc=True).tz_convert('America/New_York') + pd.Timedelta(minutes=5)
        default_start_time = default_end_time - pd.Timedelta(minutes=45)

        return default_start_time, default_end_time



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
line1, = ax.plot(dates, prices, label='Datos Históricos', color='y', linewidth=0.5)
scatter1 = ax.scatter(0, 0, color='red', zorder=5)  # Marcar el último punto
annotation = ax.annotate("Texto prueba", xy=(0, 0), color='red', xytext=(4,4),
                         fontsize=10,
                         ha='left', va='bottom'
                         #arrowprops=dict(arrowstyle="->", color='red')
                         )
                         # Inicializar la anotación (vacío al principio)


# Etiquetas y título
ax.set_xlabel('Fecha')
ax.set_ylabel('Precio (USDT)')
ax.set_title('Precio Histórico de LTC/USDT con Datos en Tiempo Real')
ax.grid(True)
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

# Función para ajustar los límites de Y según un rango de fechas
def adjust_y_limits_for_range(start_date, end_date):
    # Filtrar las fechas y precios dentro del rango proporcionado
    visible_dates = [date for date in dates + realtime_dates if start_date <= date <= end_date]
    visible_prices = [price for date, price in zip(dates + realtime_dates, prices + realtime_prices) if date in visible_dates]

    # Si hay precios visibles, ajustamos los límites de Y
    if visible_prices:
        margin = 0.05  # Margen para evitar que los precios toquen el borde del gráfico
        new_y_min = min(visible_prices)
        new_y_max = max(visible_prices)

        new_y_min = new_y_min - (new_y_max - new_y_min) * margin
        new_y_max = new_y_max + (new_y_max - new_y_min) * margin

        return new_y_min, new_y_max
    else:
        # Si no hay precios visibles, no cambiar los límites
        return None, None

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

    #scatter1.set_offsets([(realtime_dates[-1], realtime_prices[-1])])  # Actualiza la posición del scatter al último punto
    # Actualizar la anotación al último punto
    annotation.set_text(f"{realtime_prices[-1]:.2f} USDT")  # Texto con el valor actual
    annotation.set_position((realtime_dates[-1], realtime_prices[-1]))  # Posicionar la anotación
    annotation.xy = (realtime_dates[-1], realtime_prices[-1])  # Ubicar la anotación en el último valor

    # Verificar si el último valor está dentro del rango visible
    x_min, x_max = ax.get_xlim()
    # Convertir x_min y x_max a pandas.Timestamp
    x_min = pd.to_datetime(x_min, unit='d', utc=True).tz_convert('America/New_York')  # Asignar zona horaria a x_min
    x_max = pd.to_datetime(x_max, unit='d', utc=True).tz_convert('America/New_York')  # Asignar zona horaria a x_max
    # Verificar si el último valor de tiempo (realtime_dates[-1]) está dentro del rango visible
    if x_min <= realtime_dates[-1] <= x_max and len(realtime_dates)>1:
        # Si el último dato está dentro del rango visible, desplazar los límites en x
        # Calcular el desplazamiento en el eje x usando la diferencia entre el último y el penúltimo valor
        shift = realtime_dates[-1] - realtime_dates[-2]
        ax.set_xlim(x_min + shift, x_max + shift)
    
    # Actualizar el rango de fechas
    ax.relim()  # Recalcular límites del gráfico
    ax.autoscale_view()  # Autoescala el gráfico para que se ajuste a los nuevos datos

    return line1, annotation#, scatter1


# Función para configurar la gráfica con el rango predeterminado de la vista
def set_default_view():
    global default_start_time_offset, default_end_time_offset, validation_error_flag

    # Validar y calcular las fechas de inicio y fin
    default_start_time, default_end_time = validate_date_range(default_start_time_offset, default_end_time_offset)
    # Ajustar el rango de fechas en el gráfico
    ax.set_xlim(default_start_time, default_end_time)
    # Llamar a la función de ajuste de Y usando el rango validado
    new_y_min, new_y_max = adjust_y_limits_for_range(default_start_time, default_end_time)    
    # Ajustar los límites de Y si se encuentran valores válidos
    if new_y_min is not None and new_y_max is not None:
        ax.set_ylim(new_y_min, new_y_max)


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
    # Obtener el rango visible actual en el eje X (fechas)
    x_min, x_max = ax.get_xlim()

    # Convertir x_min y x_max de segundos a pandas.Timestamp
    x_min = pd.to_datetime(x_min, unit='d', utc=True).tz_convert('America/New_York')
    x_max = pd.to_datetime(x_max, unit='d', utc=True).tz_convert('America/New_York')

    # Llamar a la función que ajusta los límites de Y basados en el rango visible de fechas
    new_y_min, new_y_max = adjust_y_limits_for_range(x_min, x_max)

    # Si se devuelven límites válidos, ajustarlos
    if new_y_min is not None and new_y_max is not None:
        ax.set_ylim(new_y_min, new_y_max)
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
