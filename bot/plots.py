import matplotlib.pyplot as plt
from aiogram import types
from io import BytesIO

def plot_temperature(logs, sensor_name):
    times = [log.timestamp for log in logs]
    values = [log.value for log in logs]
    plt.figure(figsize=(8, 4))
    plt.plot(times, values, marker='o')
    plt.title(f"Температура: {sensor_name}")
    plt.xlabel("Время")
    plt.ylabel("Температура, °C")
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

async def send_temperature_plot(message: types.Message, logs, sensor_name):
    buf = plot_temperature(logs, sensor_name)
    await message.answer_photo(buf, caption=f"График температуры {sensor_name}")
