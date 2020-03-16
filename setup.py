from setuptools import setup
from Ava import __version__

setup(
   name='ambiance-voice-assistant',
   version=__version__,
   description='The aim of this project is to create a assistant that auto trigger ambiance change controlling by voice',
   license="GNU GPL3",
   author='Maxime Barbier',
   author_email='maxime@maxime-barbier.fr',
   packages=['Ava'],
   install_requires=[
      'nltk~=3.4',
      'SpeechRecognition~=3.8',
      'pydub~=0.23',
      'py-espeak-ng~=0.1',
      'PyAudio~=0.2',
   ],
)