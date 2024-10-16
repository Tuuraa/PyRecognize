import asyncio
from config import config
import websockets
from Models.recorder import Recorder, RecorderConfig
from Models.speech_recognize import VoskModel

async def websocket_handler(websocket, path, model, recorder):
    try:
        async for message in websocket:
            if message == 'start': 
                print("Start listening for speech...")

                message = await recorder.run(websocket)
                # print(message)
                # await websocket.send(message)

                # async for word in message:
                #     if message:
                #         await websocket.send(word) 
            else:
                print(f"Unknown command received: {message}")


    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    model = VoskModel("./ReModels/vosk_small_model") 
    recorder = Recorder(
        record_config=RecorderConfig(config.sky_model_path),
        vosk_model=model
    )


    # await recorder.run()
    async with websockets.serve(lambda ws, path: websocket_handler(ws, path, model, recorder), "localhost", 5000):
        print("WebSocket server started on ws://localhost:5000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
