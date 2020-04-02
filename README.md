# Ambiance-voice-assistant
The aim of this project is to create a assistant that auto trigger ambiance change controlling by voice.
The current configuration is for French but you can easily change it to other
languages by changing language informations in data/ava.json 



# Installation

## From pypi

```
pip install ambiance-voice-assistant
python -m spacy download fr_core_news_md
apt install mbrola-fr1
```

## Fom source

```
python setup.py install
python -m spacy download fr_core_news_md
apt install mbrola-fr1 # or change voices in data/data.json
```


# Run
## No install

```
python Ava/ava.py
```

## With install
```
python -m Ava
# or
Ava
```

## Configure the actions

Please edit data/ava.json to customize the actions to make with specifique sentences.