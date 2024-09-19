import asyncio

from Models.recorder import Recorder, RecorderConfig
from config import config


async def main():
    recorder = Recorder(record_config=RecorderConfig(config.sky_model_path))
    await recorder.run()


if __name__ == "__main__":
    asyncio.run(main())