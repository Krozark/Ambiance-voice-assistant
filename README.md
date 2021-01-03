# Ambiance-voice-assistant
The aim of this project is to create a assistant that auto trigger ambiance change controlling by voice.
The current configuration is for French but you can easily change it to other
languages by changing language informations in data/ava.json

The software run offline, so all data are contained to your computer.


As Vosk is use for the Speach to text, you need to download a langage model (https://alphacephei.com/vosk/models) and place it in data/models/<language>/.


# Installation

## From pypi

```
pip install ambiance-voice-assistant[linux] # for linux
pip install ambiance-voice-assistant[android] # for android
```

## Fom source

```
python setup.py install .[linux] # for linux
python setup.py install .[android] # for android
```

## Requirements for linux

```
python -m spacy download fr_core_news_md
apt install mbrola-fr1 # or change voices in data/ava.json
```

## Requierment for speach to text (French)

```
wget https://alphacephei.com/vosk/models/vosk-model-fr-0.6-linto.zip
unzip vosk-model-fr-0.6-linto
mv vosk-model-fr-0.6-linto data/models/fr
```

# Run
## No install

```
python Ava/
```

## With install
```
python -m Ava
# or
Ava
```

## Configure the actions

Please edit data/ava.json to customize the actions to make with specifics sentences.