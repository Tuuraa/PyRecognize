import pvporcupine
import logging

from pvrecorder import PvRecorder
from config import PicovoiceAccessKey

'''
    Настройка доп логов для файла
'''

#file_handler = logging.FileHandler('log_file.log')
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecorderConfig:
    def __init__(self, keyword_paths=None) -> None:
        
        '''
            self.keywords - Все wake word слова от Picovoice
            keyword_paths = Путь до файла с моделью Hey Sky
        '''

        self.keywords = [word for word in pvporcupine.KEYWORDS] 

        if keyword_paths:
            self.porcupine = pvporcupine.create(
                access_key=PicovoiceAccessKey, 
                keyword_paths=[keyword_paths]
            )
        else:
            self.porcupine = pvporcupine.create(
                access_key=PicovoiceAccessKey,
                keywords=self.keywords
            )

        self.recoder = PvRecorder(
            device_index=-1, 
            frame_length=self.porcupine.frame_length
        )
        self.porcupine = pvporcupine.create(
            access_key=PicovoiceAccessKey, 
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

    def start_recording(self):
        self.recorder.start()
        logger.info("Start listening...")
        while True:
            audio_frame = self.recorder.read()
            keyword_index = self.porcupine.process(audio_frame)
            if keyword_index >= 0:
                self.process()

    def stop_and_cleanup(self):
        self.recorder.stop()
        self.porcupine.delete()
        self.recorder.delete()

    def run(self):
        try:
            self.start_recording()
        except KeyboardInterrupt:
            self.stop_and_cleanup()

    def process(self):
        logger.info("DETECTED")
