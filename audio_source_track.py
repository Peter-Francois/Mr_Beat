from array import array
from audiostream.sources.thread import ThreadSource


class AudioSourceTrack(ThreadSource):  # thread = fil
    steps = ()
    step_nb_samples = 0

    def __init__(self, output_steam, wav_samples, bpm, sample_rate, min_bpm, *args, **kwargs):
        ThreadSource.__init__(self, output_steam, *args, **kwargs)
        self.current_sample_index = 0
        self.current_step_index = 0
        self.wav_samples = wav_samples
        self.nb_wav_samples = len(wav_samples)
        self.min_bpm = min_bpm
        self.bpm = bpm
        self.sample_rate = sample_rate
        self.last_sound_sample_star_index = 0
        self.step_nb_samples = self.compute_step_nb_samples(bpm)
        # on definé la taille du buffer par la valeur maximal qu'il peut atteindre donc avec le min_bpm
        self.buffer_nb_samples = self.compute_step_nb_samples(min_bpm)
        # le buffer a une taille de 64 bytes, on le remplie de bytes avec le b"\x00\x00"
        # que l'on multiplie par step_nb_samples
        self.silence = array('h', b"\x00\x00" * self.buffer_nb_samples)

        # il semblerait que l'implémentation suivante a été remplacé par la fonction compute_step_nb_samples
        # if not self.bpm == 0:
            # n = int(self.sample_rate * 15 / self.bpm)
            # if not n == self.step_nb_samples:
                # self.step_nb_samples = n

    def set_steps(self, steps):
        # pour repartir à zero si le nombre de step a changé entre temps
        if not len(steps) == len(self.steps):
            self.current_step_index = 0
        self.steps = steps

    def set_bpm(self, bpm):
        self.bpm = bpm
        # on rapelle la fonction compute_step_nb_samples afin de métre à jour le nb d'échantillonage par step
        # car on a modifié la valeur du bpm
        self.step_nb_samples = self.compute_step_nb_samples(bpm)

    def compute_step_nb_samples(self, bpm_value):
        if not bpm_value == 0:
            n = int(self.sample_rate * 30 / bpm_value)
            return n
        return 0

    def no_steps_activate(self):
        if len(self.steps) == 0:
            return True
        for i in range(len(self.steps)):
            if self.steps[i] == 1:
                return False
        return True

    """AVANT OPTIMISATION
    def get_bytes_array(self):
            for i in range(0, self.step_nb_samples):
                # on regarde si on a des steps
                if len(self.steps) > 0 and not self.no_steps_activate():
                    # on regarde si on a des steps active et si l'index et plus etit que notre nombre de wav sample
                    # pour évité que le son soit joué 2 fois si il est plus petit que le get_bytes
                    if self.steps[self.current_step_index] == 1 and i < self.nb_wav_samples:
                        # on copie le sample wav dans le bufer
                        self.buf[i] = self.wav_samples[i]
                        # on viens enregistré la valeur de l'index de départ du son
                        if i == 0:
                            self.last_sound_sample_star_index = self.current_sample_index
                    else:
                        # on déduit la valeur de l'index courant par rapport au start index du son
                        index = self.current_sample_index - self.last_sound_sample_star_index
                        # si l'index et plus petit que nb_wav_samples alors il y a encore des samples a joué donc
                        # on les copy dans le bufer
                        if index < self.nb_wav_samples:
                            self.buf[i] = self.wav_samples[index]
                        # le son est terminé, on remet le buffer a 0
                        else:
                            self.buf[i] = 0
                # pas de step donc bufer a zero
                else:
                    self.buf[i] = 0
                self.current_sample_index += 1
            self.current_step_index += 1
            # pour faire bouclé il faut faire revenir a zero le current_step_index
            if self.current_step_index >= len(self.steps):
                self.current_step_index = 0
            # On ne retourne que le buffer de la taille du step_nb_samples
            return self.buf[0: self.step_nb_samples]

    def get_bytes(self, *args, ** kwargs):
        return self.get_bytes_array().tobytes()"""

    '''RETIRER POUR LAISSER PLACE A LA NOUVELLE FONCTION PREND EN COMPTE LE BPM
    if self.nb_wav_samples > 0:
        for i in range(0, self.chunk_nb_samples):
            # pour renvoyer des 0 une fois que le son est terminé, on compare le current_sample_index a
            # la taille du sample : nb_wav_samples
            if self.current_sample_index < self.nb_wav_samples:
                self.buf[i] = self.wav_samples[self.current_sample_index]
            else:
                self.buf[i] = 0
            # on utilise self.current_sample_index pour avancé dans le samples, si on utilise i on envoie que
            # les 32 premier bytes en boucles au buffer
            self.current_sample_index += 1
    # audiostream demande un retour un buffeur en string don on le converti
    return self.buf.tobytes()'''

    def get_bytes_array(self):
        # Optimisation

        result_buf = None
        # 1 - aucun step activé -> Silence
        if self.no_steps_activate():
            result_buf = self.silence[0: self.step_nb_samples]

        elif self.steps[self.current_step_index] == 1:
            # on viens enregistré la valeur de l'index de départ du son
            self.last_sound_sample_star_index = self.current_sample_index

            # 2 - step activé et le son a plus de sample que 1 step
            if self.nb_wav_samples >= self.step_nb_samples:
                result_buf = self.wav_samples[0: self.step_nb_samples]
            else:
                # 3 le step activé et le son a moins de samples que 1 step. On  viens combler de 0 pour
                # joué le reste du son
                silence_nb_samples = self.step_nb_samples - self.nb_wav_samples
                result_buf = self.wav_samples[0:self.nb_wav_samples]
                result_buf.extend(self.silence[0:silence_nb_samples])

        else:
            # on viens enregistré la valeur de l'index à l'interieur du fichier wav
            index = self.current_sample_index - self.last_sound_sample_star_index

            # 4 le step n'est pas activé et on a fini de joué le son -> silence
            if index > self.nb_wav_samples:
                result_buf = self.silence[0: self.step_nb_samples]

            # 5 le step n'est pas activé mais on doit joué la suite du son

            # 5.1 ce qui nous reste a jouer et plus long qu'un step
            elif self.nb_wav_samples - index >= self.step_nb_samples:
                result_buf = self.wav_samples[index: self.step_nb_samples + index]

            # 5.2 ce qui nous reste a jouer et plus petit qu'un step
            else:
                silence_nb_samples = self.step_nb_samples - self.nb_wav_samples + index
                result_buf = self.wav_samples[index: self.nb_wav_samples]
                result_buf.extend(self.silence[0:silence_nb_samples])

        self.current_sample_index += self.step_nb_samples
        self.current_step_index += 1
        # pour faire bouclé il faut faire revenir à zero le current_step_index
        if self.current_step_index >= len(self.steps):
            self.current_step_index = 0

        # on protège le code
        if result_buf is None:
            print("result buf is none")
        elif not len(result_buf) == self.step_nb_samples:
            print('result len is not same as step_nb_samples')
        # On ne retourne que le buffer de la taille du step_nb_samples
        return result_buf

    def get_bytes(self, *args, **kwargs):
        return self.get_bytes_array().tobytes()

