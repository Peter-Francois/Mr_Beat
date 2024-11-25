import wave
from array import array

# A sound has a file name and a display name. It's better to separate the two for more flexibility when
# renaming the sound.


class Sound:
    samples = None
    nb_samples = 0

    def __init__(self, filename, displayname):
        self.filename = filename
        self.displayname = displayname
        self.load_sound()

    def load_sound(self):
        wave_file = wave.open(self.filename, mode='rb')
        # frame = sample
        self.nb_samples = wave_file.getnframes()
        frames = wave_file.readframes(self.nb_samples)  # Bytes : 8bits
        # We retrieve an 8-byte file with readframes. To change it to 16 bytes, we use the array module and
        # choose a 16-byte signed mode, either 'h' (short) or 'i' (integer).
        self.samples = array('h', frames)  # The sample is now in 16 bytes.


# A generic sound kit with a function to determine the number of tracks in the kit.
class SoundKit:
    sounds = ()

    def get_nb_tracks(self):
        return len(self.sounds)

    def get_all_samples(self):
        all_sound_samples = []
        for i in range(0, len(self.sounds)):
            all_sound_samples.append(self.sounds[i].samples)
        return all_sound_samples


class SoundKit1(SoundKit):
    sounds = (Sound("sounds/kit1/kick.wav", "KICK"),
              Sound("sounds/kit1/clap.wav", "CLAP"),
              Sound("sounds/kit1/shaker.wav", "SHAKER"),
              Sound("sounds/kit1/snare.wav", "SNARE"))


class SoundKit1All(SoundKit):
    sounds = (Sound("sounds/kit1/kick.wav", "KICK"),
              Sound("sounds/kit1/clap.wav", "CLAP"),
              Sound("sounds/kit1/shaker.wav", "SHAKER"),
              Sound("sounds/kit1/snare.wav", "SNARE"),
              Sound("sounds/kit1/bass.wav", "BASS"),
              Sound("sounds/kit1/effects.wav", "EFFECTS"),
              Sound("sounds/kit1/pluck.wav", "PLUCK"),
              Sound("sounds/kit1/vocal_chop.wav", "VOCAL CHOP"))

# To add sound kits, you can find free kits on Google by searching for "drum kit sounds free."
# The files must be in WAV format, 16-bit, with a sample rate of 44,100 samples per second, and in mono.

# Sound kit management for selecting the kit.
class SoundKitService:
    soundkit = SoundKit1()

    def get_nb_tracks(self):
        return self.soundkit.get_nb_tracks()

    # To retrieve the name of the sound at a certain index.
    def get_sound_at(self, index):
        if index >= len(self.soundkit.sounds):
            return None
        return self.soundkit.sounds[index]