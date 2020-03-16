import logging
from queue import Queue
from threading import Thread
import time
import speech_recognition
from espeakng import ESpeakNG
from pydub import AudioSegment
from pydub.playback import play

from Ava import config

logger = logging.getLogger(__package__)


class Ava(object):
    def __init__(self):
        self.source = self._get_source()
        self.recognizer = self._get_recognizer()
        logging.info("A moment of silence, please...")
        self.recognizer_listen_kwargs=dict(
            phrase_time_limit=5
        )

        self.tts_engine = self._get_tts_engine()
        self._audio_queue = Queue()
        self._stt_recognize_worker_thread = None
        self._stt_running = False

    def run(self):
        thread = Thread(target=self._stt_start)
        thread.daemon = True
        thread.start()

        while self._stt_running:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self._stt_running = False
        self._stt_join()

        thread.join()

    def _get_source(self):
        return speech_recognition.Microphone()

    def _get_recognizer(self):
        r = speech_recognition.Recognizer()
        r.non_speaking_duration = 0.3
        r.pause_threshold = 0.6
        return r

    def _get_tts_engine(self):
        engine = ESpeakNG()
        engine.voice = "fr"
        engine.pitch = 32
        engine.speed = 150
        return engine


    def _stt_recognize_worker(self):
        # this runs in a background thread
        i = 1
        while True:
            audio = self._audio_queue.get()  # retrieve the next audio processing job from the main thread
            if audio is None: break  # stop processing if the main thread is done

            #if config.DEBUG:
            #    i += 1
            #    filename = "%s.wav" % i
            #    self._save(audio, filename)
            #    self._play(filename)

            # received audio data, now we'll recognize it using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                value = self.recognizer.recognize_google(audio, language=config.LANGUAGE_RECONGITION)
                logger.debug(">" + value)
                self._tts(value)
            except speech_recognition.UnknownValueError:
                logger.debug("Google Speech Recognition could not understand audio")
            except speech_recognition.RequestError as e:
                logger.debug("Could not request results from Google Speech Recognition service; {0}".format(e))

            self._audio_queue.task_done()  # mark the audio processing job as completed in the queue

    def _stt_start(self):
        # start a new thread to recognize audio, while this thread focuses on listening
        self._stt_running = True
        self._stt_recognize_worker_thread = Thread(target=self._stt_recognize_worker)
        self._stt_recognize_worker_thread.daemon = True
        self._stt_recognize_worker_thread.start()

        with self.source as src:
            self.recognizer.adjust_for_ambient_noise(src, duration=2)
            logger.info("Set minimum energy threshold to {}".format(self.recognizer.energy_threshold))

            while self._stt_running:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
                logger.debug("Listen....")
                audio = self.recognizer.listen(src, **self.recognizer_listen_kwargs)
                logger.debug("End Listen....")
                self._audio_queue.put(audio)


    def _stt_join(self):
        self._audio_queue.join()  # block until all current audio processing jobs are done
        self._audio_queue.put(None)  # tell the recognize_thread to stop
        self._stt_recognize_worker_thread.join()  # wait for the recognize_thread to actually stop


    def _tts(self, text, wait=True):
        self.tts_engine.say(text)

    def _play(self, filename):
        song = AudioSegment.from_wav(filename)
        play(song)

    def _save(self, audio, filename):
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ava = Ava()
    ava.run()