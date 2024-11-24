from array import array
from audiostream.sources.thread import ThreadSource


class AudioSourceOneShoot(ThreadSource):  # thread = fil

    wav_samples = None
    nb_wav_samples = 0
    def __init__(self, output_steam, *args, **kwargs):

        ThreadSource.__init__(self, output_steam, *args, **kwargs)
        # Le chunk est la taille des samples que l'on va envoyer à l'audioEngine, une taille de chunk de 32 échantillons
        # est un compromis qui peut fonctionner efficacement pour des environnements à basse latence
        self.chunk_nb_samples = 32
        self.current_sample_index = 0
        # le buffer a une taille de 64 bytes, pour le remplir du coup on le remplie de bytes avec le b"\x00\x00" que
        # l'on multiplie par chunk_nb_samples
        self.buf = array('h', b"\x00\x00" * self.chunk_nb_samples)

    def set_wav_samples(self, wav_samples):
        # on récupère les samples pour les réduire à la taille du chunk et les envoyé au buffer
        self.wav_samples = wav_samples
        # on doit remettre à la fin du son le self.current_sample_index à 0 sinon on ne peut pas jouer d'autre son
        self.current_sample_index = 0
        self.nb_wav_samples = len(wav_samples)

    def get_bytes(self, *args, **kwargs):
        if self.nb_wav_samples > 0:
            for i in range(0, self.chunk_nb_samples):
                # pour renvoyer des 0 une fois que le son est terminé, on compare le current_sample_index à
                # la taille du sample : nb_wav_samples
                if self.current_sample_index < self.nb_wav_samples:
                    self.buf[i] = self.wav_samples[self.current_sample_index]
                else:
                    self.buf[i] = 0
                # on utilise self.current_sample_index pour avancé dans le samples, si on utilise i on envoie que
                # les 32 premier bytes en boucles au buffer
                self.current_sample_index += 1
        # audiostream demande le retour d'un buffer en string donc on le convertie
        return self.buf.tobytes()

