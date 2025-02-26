import requests
import matplotlib.pyplot as plt
import time

# URL de la API de Binance para obtener el precio de LTC/USDT
url = "https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT"

# Listas para almacenar los valores de tiempo y precio
timestamps = []
prices = []

# Configurar la gráfica
plt.ion()  # Activar el modo interactivo para actualizaciones en tiempo real
fig, ax = plt.subplots()
line, = ax.plot(timestamps, prices, label='Precio LTC/USDT', color='b')
ax.set_xlabel('Tiempo (segundos)')
ax.set_ylabel('Precio (USDT)')
ax.set_title('Precio en tiempo real de LTC/USDT')
ax.legend()

# Variable para el contador de tiempo
start_time = time.time()

# Bucle para obtener los datos y actualizar la gráfica en tiempo real
while True:
    try:
        # Obtener el precio de LTC/USDT desde la API de Binance
        response = requests.get(url)
        data = response.json()

        # Extraer el precio actual y el tiempo transcurrido
        price = float(data['price'])
        elapsed_time = time.time() - start_time

        # Agregar los nuevos datos a las listas
        timestamps.append(elapsed_time)
        prices.append(price)

        # Limitar el número de puntos en la gráfica para no sobrecargarla
        if len(timestamps) > 50:
            timestamps.pop(0)
            prices.pop(0)

        # Actualizar la gráfica
        line.set_xdata(timestamps)
        line.set_ydata(prices)

        # Ajustar los límites de los ejes
        ax.set_xlim(min(timestamps), max(timestamps) + 1)
        ax.set_ylim(min(prices) - 1, max(prices) + 1)

        # Redibujar la gráfica
        plt.draw()
        plt.pause(1)  # Pausa de 1 segundo antes de la siguiente actualización

    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        time.sleep(1)
