import pygame as pg
import serial
import time
import os

class SoundSystem:
  def __init__(self):
    self.setup_mixer()

def checkifComplete(channel):
    while channel.get_busy():
        pg.time.wait(800)
    channel.stop()

def setup_mixer():
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
    sound_dir = os.path.abspath(os.path.join(src_dir, '../sounds'))
    all_sounds = os.path.join(sound_dir, '*.wav')
    self.sounds = dict((os.path.basename(name)[:-4], name) for name in glob.glob(all_sounds))

    print(self.sounds)

    # thread management
    self.channels = []

# def get_filepath(file):
#     return os.path.join(os.getcwd(), file)

def play_sounds(song_array):
    for song in song_array:
        channel = pg.mixer.find_channel(True)
        print "Playing audio : ", song
        sound = pg.mixer.Sound(get_filepath(song))
        sound.set_volume(1)
        channel.play(sound)

def find_and_play_sounds(x, y):
    print x, y
    return play_sounds(soundDict[pinAssign[x]][pinAssign[y]])

if __name__ == "__main__":
    #set up the mixer
    setup_mixer()
    while True :
        state = ser.readline()
        if state:
            x, y = state.split(' ')
            print state
            find_and_play_sounds(int(x), int(y))
