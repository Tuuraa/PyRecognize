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
            
