import glob
import os
import pygame as pg
import serial
import time

class SoundSystem:
    def __init__(self):
        self.setup_mixer()

    def checkifComplete(self, channel):
        while channel.get_busy():
            pg.time.wait(800)
        channel.stop()

    def setup_mixer(self):
        pg.mixer.init(
            frequency = 48000,
            size = -16,
            channels = 2,
            buffer = 2048
        )
        pg.init()
        pg.mixer.set_num_channels(50)

        # find the sounds we have saved
        src_dir = os.path.dirname(__file__)
        self.sound_dir = os.path.abspath(os.path.join(src_dir, '../panels/sounds'))
        all_sounds = os.path.join(self.sound_dir, '*.wav')
        self.sounds = dict((os.path.basename(name)[:-4], name) for name in glob.glob(all_sounds))

        # thread management
        self.channels = []

    def get_filepath(file):
        return os.path.join(self.sound_dir, file)

    def play_sounds(self, song_array):
        for song in song_array:
            channel = pg.mixer.find_channel(True)
            print "Playing audio : ", song
            sound = pg.mixer.Sound(self.get_filepath(song))
            sound.set_volume(1)
            channel.play(sound)
