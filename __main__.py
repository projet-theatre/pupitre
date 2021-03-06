import json
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from omxplayer.player import OMXPlayer
import RPi.GPIO as GPIO

from core import event
from core import light

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")
file_handler = RotatingFileHandler("/home/pi/pupitre.log", "a", 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

logger.info("le script est initialisé")

event = event.Event()
event.start()


with open("/home/pi/pupitre/config.json") as json_file:
    global json_datas
    json_datas = json.load(json_file)

GPIO.setmode(GPIO.BCM)
[
    GPIO.setup(handler, GPIO.OUT, initial=GPIO.HIGH)
    for handler in json_datas["leds_handlers"]
]

logger.info("GPIO initialisés")


@event.on_with_just_sound
def with_just_sound():
    logger.info("demande de jouer le son")
    path = Path(json_datas["music_path"])
    OMXPlayer(path)
    logger.info("jouer le son fini")


@event.on_with_sound_and_leds
def with_sound_and_led():
    logger.info("jouer le son et animer les lumières demandé")
    path = Path(json_datas["music_path"])
    OMXPlayer(path)
    light.animation(5, json_datas["leds_handlers"])
    logger.info("jouer le son et animer les lumières fini")


@event.on_with_leds
def with_leds():
    logger.info("animer les lumières")
    light.animation(json_datas["animation_iterations"], json_datas["leds_handlers"])
    logger.info("animer les lumières fini")


event.join()
