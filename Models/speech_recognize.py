import pyaudio, json, time
import asyncio
import threading

from vosk import Model, KaldiRecognizer

CHANELS = 1
RATE = 16000
FRAME_PER_BUFFER = 8000
INPUT = True

class VoskModel:
    def __init__(self, model_path):
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


    def _listen_normal_mode(self):
        self.stream.start_stream()

        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.rec.Result())
                if answer['text']:
                    yield answer['text']

    async def listen_partial_mode(self):
        """
        Асинхронное прослушивание и распознавание с частичными результатами.
        Отправляем уникальные результаты.
        """
        self.stream.start_stream()
        previous_partial = ""  # Храним предыдущий результат для сравнения

        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                partial_result = self.rec.PartialResult()
                if partial_result:
                    result = json.loads(partial_result)
                    current_partial = result.get('partial', '')

                    # Отправляем только если результат изменился
                    if current_partial and current_partial != previous_partial:
                        previous_partial = current_partial
                        await asyncio.sleep(0.1)
                        yield current_partial
            await asyncio.sleep(0.1)


    async def run(self, listen_mode='normal'):
        if listen_mode == 'partial':
            for text in self._listen_partial_mode():
                yield text
        else:
            for text in self._listen_normal_mode():
                yield text

    def __init__(self, model_path):
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        self.p_audio = pyaudio.PyAudio()
        # self.loop = asyncio.get_event_loop()
        # self.stop_event = threading.Thread()

        self.stream = self.p_audio.open(
            format=pyaudio.paInt16, 
            channels=CHANELS, 
            frames_per_buffer=FRAME_PER_BUFFER,
            rate=RATE, 
            input=INPUT
        ) 

    def __listen_normal_mode(self):
        self.stream.start_stream()

        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.rec.Result())

                if answer['text']:
                    yield answer['text']
    
    def __listen_partial_mode(self):  # Частичный режим прослушивания, пока что не доработан
        self.stream.start_stream()
        while True:
            data = self.stream.read(400, exception_on_overflow=False)
            if data and self.rec.AcceptWaveform(data):
                partial_result = self.rec.PartialResult()
                if partial_result:
                    yield partial_result
            time.sleep(0.1)

    # def stop_listening(self):
    #     time.sleep(10)
        
    #     self.stop_event.set()

    async def run(self, listen_mode='normal'):
        # threading.Thread(target=self.stop_listening).start()

        if listen_mode == 'partical':
            for text in self.__listen_partial_mode():
                print(text)
                return
            
        for text in self.__listen_normal_mode():
            return text
            
