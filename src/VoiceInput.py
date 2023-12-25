import yaml, io, queue, tempfile, os, threading
import torch
import speech_recognition as sr
import whisper
import numpy as np
from pydub import AudioSegment
# import redis

class VoiceInput:
    def __init__(self):
        #TODO: using relative path is bad
        with open('config.yml', 'r') as file:
            mic_config = yaml.safe_load(file)
        model = mic_config['mic']['model']
        english = mic_config['mic']['english']
        verbose = mic_config['mic']['verbose']
        energy = mic_config['mic']['energy']
        dynamic_energy = mic_config['mic']['dynamic_energy']
        pause = mic_config['mic']['pause']
        save_file = mic_config['mic']['save_file']
        # self.redis_instance = redis.Redis(
        #     host='127.0.0.1',
        #     port=6379,
        #     decode_responses=True
        # )

        self.main(model, english, verbose, energy, pause, dynamic_energy, save_file)

    def main(self, model, english,verbose, energy, pause,dynamic_energy,save_file):
        temp_dir = tempfile.mkdtemp() if save_file else None
        #there are no english models for large
        if model != "large" and english:
            model = model + ".en"
        audio_model = whisper.load_model(model)
        audio_queue = queue.Queue()
        threading.Thread(target=self.record_audio,
                        args=(audio_queue, energy, pause, dynamic_energy, save_file, temp_dir)).start()
        threading.Thread(target=self.transcribe_forever,
                        args=(audio_queue, audio_model, english, verbose, save_file)).start()

        # while True:
        #     print(self.result_queue.get())

    def record_audio(self, audio_queue, energy, pause, dynamic_energy, save_file, temp_dir):
        #load the speech recognizer and set the initial energy threshold and pause threshold
        r = sr.Recognizer()
        r.energy_threshold = energy
        r.pause_threshold = pause
        r.dynamic_energy_threshold = dynamic_energy

        with sr.Microphone(sample_rate=16000) as source:
            print("Say something!")
            i = 0
            while True:
                #get and save audio to wav file
                audio = r.listen(source)
                if save_file:
                    data = io.BytesIO(audio.get_wav_data())
                    audio_clip = AudioSegment.from_file(data)
                    filename = os.path.join(temp_dir, f"temp{i}.wav")
                    audio_clip.export(filename, format="wav")
                    audio_data = filename
                else:
                    torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
                    audio_data = torch_audio

                audio_queue.put_nowait(audio_data)
                i += 1


    def transcribe_forever(self, audio_queue, audio_model, english, verbose, save_file):
        while True:
            audio_data = audio_queue.get()
            if english:
                result = audio_model.transcribe(audio_data,language='english')
            else:
                result = audio_model.transcribe(audio_data)

            if not verbose:
                predicted_text = result["text"]
                # print("You said: " + predicted_text)
            #TODO: Create this as a utility function which is imported into functions
            #TODO: Separate this into another threaded process to adhere to clean code
            predicted_text = predicted_text.lower()
            if 'sara' in predicted_text:
                substring = 'sara'
                str_list = predicted_text.split(substring)
                output_string = "".join(str_list)
                # self.publish_latest_result(output_string)
            elif 'sarah' in predicted_text:
                substring = 'sarah'
                str_list = predicted_text.split(substring)
                output_string = "".join(str_list)
                # self.publish_latest_result(output_string)
            else:
                pass

            if save_file:
                os.remove(audio_data)

    # def get_result_queue(self):
    #     return self.result_queue
    
    # def get_result_queue_latest(self):
    #     return self.result_queue.get()

    # def publish_latest_result(self, result):
    #     print(result)
    #     self.redis_instance.publish("voice-input", result)

VoiceInput()