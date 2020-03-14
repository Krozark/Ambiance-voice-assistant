import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

r.non_speaking_duration = 0.3
r.pause_threshold = 0.6

try:
    print("A moment of silence, please...")
    with m as source: r.adjust_for_ambient_noise(source, duration=2)
    print("Set minimum energy threshold to {}".format(r.energy_threshold))
    while True:
        print("Say something!")
        with m as source: audio = r.listen(source, phrase_time_limit=5)
        print("Got it! Now to recognize it...")
        try:
            # recognize speech using Google Speech Recognition
            value = r.recognize_google(audio, language="fr-FR")

            # we need some special handling here to correctly print unicode characters to standard output
            if str is bytes:  # this version of Python uses bytes for strings (Python 2)
                print(u">{}".format(value).encode("utf-8"))
            else:  # this version of Python uses unicode for strings (Python 3+)
                print(">{}".format(value))
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
except KeyboardInterrupt:
    pass
