#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import time
import speech_recognition as sr
import keyboard

mic_num = 1
use_name = ""
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    if index == mic_num:
        use_name = name
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

print(f"Using Mic: {use_name}")


class Speech():
    def __init__(self):
        self.running = False
        self.r = sr.Recognizer()
        #self.r.energy_threshold = 3000
        self.m = sr.Microphone(device_index=mic_num)
        with self.m as source:
            self.r.adjust_for_ambient_noise(source,duration=1)  # we only need to calibrate once, before we start listening

    def start(self):
        if not self.running:
            self.running = True
            self.stop_listening = self.r.listen_in_background(self.m, callback)
            print("listening")

    def stop(self):
        if self.running:
            print("Stopping")
            self.stop_listening(wait_for_stop=False)
            self.running = False

# this is called from the background thread
def callback(recognizer, audio):
    print("AUDIO HAS CALLBACKED")
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        words = recognizer.recognize_google(audio)
        print("Google Speech Recognition thinks you said " + words)
        keyboard.write(words)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


if __name__ == "__main__":
    sp = Speech()

    sp.start()

    # do some unrelated computations for 5 seconds
    for _ in range(50): time.sleep(0.1)  # we're still listening even though the main thread is doing other things

    sp.stop()

    for _ in range(50): time.sleep(0.1)  # we're still listening even though the main thread is doing other things
    
    print("Number 2")
    
    sp.start()

    # do some unrelated computations for 5 seconds
    for _ in range(50): time.sleep(0.1)  # we're still listening even though the main thread is doing other things

    sp.stop()


    # do some more unrelated things
    while True: time.sleep(0.1)  # we're not listening anymore, even though the background thread might still be running for a second or two while cleaning up and stopping
