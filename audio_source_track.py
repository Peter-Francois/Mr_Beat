from array import array
from audiostream.sources.thread import ThreadSource


class AudioSourceTrack(ThreadSource):
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
        # We define the buffer size by the maximum value it can reach, based on the min_bpm.
        self.buffer_nb_samples = self.compute_step_nb_samples(min_bpm)
        # The buffer has a size of 64 bytes. We fill it with bytes using b"\x00\x00",
        # which we multiply by step_nb_samples.
        self.silence = array('h', b"\x00\x00" * self.buffer_nb_samples)

    def set_steps(self, steps):
        # To reset to zero if the number of steps has changed in the meantime.
        if not len(steps) == len(self.steps):
            self.current_step_index = 0
        self.steps = steps

    def set_bpm(self, bpm):
        self.bpm = bpm
        # We call the compute_step_nb_samples function again to update the number of samples per step,
        # because we have modified the BPM value.
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

    def get_bytes_array(self):

        result_buf = None
        # 1 - No step activated -> Silence.
        if self.no_steps_activate():
            result_buf = self.silence[0: self.step_nb_samples]

        elif self.steps[self.current_step_index] == 1:
            # We record the starting index value of the sound.
            self.last_sound_sample_star_index = self.current_sample_index

            # 2 - Step activated and the sound has more samples than 1 step.
            if self.nb_wav_samples >= self.step_nb_samples:
                result_buf = self.wav_samples[0: self.step_nb_samples]

            else:
                # 3 - The step is activated, and the sound has fewer samples than 1 step.
                # We fill the remaining space with 0 to play the rest of the sound.
                silence_nb_samples = self.step_nb_samples - self.nb_wav_samples
                result_buf = self.wav_samples[0:self.nb_wav_samples]
                result_buf.extend(self.silence[0:silence_nb_samples])

        else:
            # We record the index value inside the WAV file.
            index = self.current_sample_index - self.last_sound_sample_star_index

            # 4 - The step is not activated, and the sound has finished playing -> silence.
            if index > self.nb_wav_samples:
                result_buf = self.silence[0: self.step_nb_samples]

            # 5 - The step is not activated, but we need to play the rest of the sound.

            # 5.1 - What we have left to play is longer than one step.
            elif self.nb_wav_samples - index >= self.step_nb_samples:
                result_buf = self.wav_samples[index: self.step_nb_samples + index]

            # 5.2 What we have left to play is shorter than one step.
            else:
                silence_nb_samples = self.step_nb_samples - self.nb_wav_samples + index
                result_buf = self.wav_samples[index: self.nb_wav_samples]
                result_buf.extend(self.silence[0:silence_nb_samples])

        self.current_sample_index += self.step_nb_samples
        self.current_step_index += 1
        # To loop, the current_step_index must be reset to zero.
        if self.current_step_index >= len(self.steps):
            self.current_step_index = 0


        if result_buf is None:
            print("result buf is none")
        elif not len(result_buf) == self.step_nb_samples:
            print('result len is not same as step_nb_samples')
        # We only return the buffer of the size of step_nb_samples.
        return result_buf

    def get_bytes(self, *args, **kwargs):
        return self.get_bytes_array().tobytes()

