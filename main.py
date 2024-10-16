import asyncio
import websockets
from Models.speech_recognize import VoskModel

async def websocket_handler(websocket, path, model):
    """
    WebSocket-обработчик, который получает аудиопоток, распознает его и отправляет результат клиенту.
    """
    try:
        async for message in websocket:
            if message == 'start':  # Если получаем команду 'start', запускаем распознавание
                print("Start listening for speech...")

                # Вызываем метод прослушивания в частичном режиме асинхронно
                async for partial_text in model.listen_partial_mode():
                    if partial_text:
                        await websocket.send(partial_text)  # Отправляем частичный результат клиенту
            else:
                print(f"Unknown command received: {message}")

    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed")

async def main():
    """
    Основная функция для запуска WebSocket-сервера и инициализации модели Vosk.
    """
    model_path = "model"  # Укажите путь к вашей модели
    model = VoskModel("./ReModels/vosk_small_model")  # Инициализируем модель для распознавания речи
    
    # Запуск WebSocket-сервера на порту 5000
    async with websockets.serve(lambda ws, path: websocket_handler(ws, path, model), "localhost", 5000):
        print("WebSocket server started on ws://localhost:5000")
        await asyncio.Future()  # Ждем подключений

if __name__ == "__main__":
    asyncio.run(main())
