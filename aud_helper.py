import bpy
import aud
import wave
import time
def wav_metadata(filename):
    with wave.open(filename) as wav_file:
        metadata = wav_file.getparams()
        return metadata

def import_wave_file(filename):
    sound = aud.Sound(filename)
    sound_np = sound.data()
    return sound_np.T

def play_wav(filename):
    device = aud.Device()

    sound = aud.Sound(filename)
    sound_array = sound.data()
    device = aud.Device()
    sound2 = aud.Sound.buffer(sound_array, 44100)
    handle2 = device.play(sound2)
    sound2.write("test.wav")
#import_wave_file("/home/msanchez/Downloads/356416__mtg__violin-d-major.wav")
#play_wav("/home/msanchez/Downloads/4_channel.wav")