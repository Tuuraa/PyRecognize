import pvporcupine
import logging, time

from pvrecorder import PvRecorder
from Models.speech_recognize import VoskModel
from config import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecorderConfig:
    def __init__(self, keyword_paths=None) -> None:
        self.keywords = [word for word in pvporcupine.KEYWORDS] 

        if keyword_paths:
            self.porcupine = pvporcupine.create(
                access_key=config.picovoice_access_key, 
                keyword_paths=[keyword_paths]
            )
        else:
            self.porcupine = pvporcupine.create(
                access_key=config.picovoice_access_key,
                keywords=self.keywords
            )

        self.recoder = PvRecorder(
            device_index=-1, 
            frame_length=self.porcupine.frame_length
        )
        self.porcupine = pvporcupine.create(
            access_key=config.picovoice_access_key, 
            keyword_paths=[keyword_paths]
        )

        self.recoder = PvRecorder(
            device_index=-1, 
            frame_length=self.porcupine.frame_length
        )


class Recorder:
    def __init__(self, record_config: RecorderConfig) -> None:
        self.record_config = record_config

        self.recorder = self.record_config.recoder
        self.porcupine = self.record_config.porcupine

        self.vosk_model = VoskModel(config.vosk_small_model_path)

    async def start_recording(self):
        self.recorder.start()
        logger.info("Start listening...")
        while True:
            audio_frame = self.recorder.read()
            keyword_index = self.porcupine.process(audio_frame)
            if keyword_index >= 0:
                await self.process()

    def stop_and_cleanup(self):
        self.recorder.stop()
        self.porcupine.delete()
        self.recorder.delete()

    async def run(self):
        try:
            await self.start_recording()
        except KeyboardInterrupt:
            self.stop_and_cleanup()

    async def process(self):
        logger.info("im listening...")
        
        result = await self.vosk_model.run()
        print(result)
