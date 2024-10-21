from typing import AsyncGenerator
import pyaudio, json, time
import asyncio

from vosk import Model, KaldiRecognizer

CHANELS = 1
RATE = 16000
FRAME_PER_BUFFER = 8000
INPUT = True

class VoskModel:
    def __init__(self, model_path) -> None:
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.p_audio = pyaudio.PyAudio()
        
        self.stream = self.p_audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )


    def listen_normal_mode(self) -> str:
        self.stream.start_stream()

        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.rec.Result())
                if answer['text']:
                    return answer['text']

    async def listen_partial_mode(self) -> AsyncGenerator:
        self.stream.start_stream()
        previous_partial = ""  

        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                partial_result = self.rec.PartialResult()
                if partial_result:
                    result = json.loads(partial_result)
                    current_partial = result.get('partial', '')

                    if current_partial and current_partial != previous_partial:
                        previous_partial = current_partial
                        await asyncio.sleep(0.1)
                        yield current_partial
            await asyncio.sleep(0.1)


    '''
        Пока что только полный режим прослушивания
    '''
    async def run(self):
        return self.listen_normal_mode()
