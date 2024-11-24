import wave
from array import array

# un sound comporte un file name et un display name. Mieux vos separé les 2 pour plus de
# liberté quand au renomage du sound


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
        # on recupére un fichier 8 bytes avec readframes. Pour changé en 16 bytes on utilise la lib aray.aray et
        # on choisie un mode 16 bytes signed 'h' ou 'i'
        self.samples = array('h', frames)  # le sample est donc maintenant en 16 bytes


# Sound kit générique avec la fonction pour savoir le nombre de tracks dans le kit
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

# pour ajouté des sound kit, sur google on peut trouvé des kit gratuit: drum kit sounds free
# il faut que les fichier soit en wav 16 bit et 44100 samples/s et sample mono

# sound kit managment pour selection du kit
class SoundKitService:
    soundkit = SoundKit1()

    def get_nb_tracks(self):
        return self.soundkit.get_nb_tracks()

    # pour recupéré le nom du son a un certain index
    def get_sound_at(self, index):
        if index >= len(self.soundkit.sounds):
            return None
        return self.soundkit.sounds[index]