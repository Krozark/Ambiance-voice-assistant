import os

import setuptools

from Ava import __version__


def read(fname):
   return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
   name='ambiance-voice-assistant',
   version=__version__,
   description='The aim of this project is to create a assistant that auto trigger ambiance change controlling by voice',
   long_description=read('README.md'),
   long_description_content_type="text/markdown",
   license="GNU GPL3",
   author='Maxime Barbier',
   author_email='maxime.barbier1991+ava@gmail.com',
   url="https://github.com/Krozark/Ambiance-voice-assistant",
   keywords="ambiance voice assistant",
   packages=setuptools.find_packages(),
   classifiers=[
      "Programming Language :: Python",
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      "Operating System :: OS Independent",
    ],
   install_requires=[
      'nltk~=3.4',
      'pydub~=0.23',
      'PyAudio~=0.2',
      'spacy~=2.2',
      "wikipedia>=1.4",
      "krozark-json-include>=3.1",
      "meteofrance-api",
      "sound-player~=0.2",
      "Unidecode>=1.1",
      "vosk==0.3.15",
      "text2num==2.2.1"
   ],
   extras_require={
      'linux': [
         'py-espeak-ng~=0.1'
      ],
      'android': [
         "kivy~=1.11",
         "pyjnius"
      ]
   },
   entry_points={
      'console_scripts': [
        'ava = Ava.__main__:main',
      ],
   },
   python_requires='>=3.6',
)