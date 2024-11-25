from array import array
from audiostream.sources.thread import ThreadSource


class AudioSourceOneShoot(ThreadSource):

    wav_samples = None
    nb_wav_samples = 0
    def __init__(self, output_steam, *args, **kwargs):

        ThreadSource.__init__(self, output_steam, *args, **kwargs)

        # The chunk is the size of the samples that will be sent to the audio engine. A chunk size of 32 samples
        # is a compromise that can work efficiently for low-latency environments.
        self.chunk_nb_samples = 32
        self.current_sample_index = 0
        # The buffer has a size of 64 bytes. To fill it, we populate it with bytes using b"\x00\x00",
        # which we multiply by chunk_nb_samples.
        self.buf = array('h', b"\x00\x00" * self.chunk_nb_samples)

    def set_wav_samples(self, wav_samples):
        self.wav_samples = wav_samples
        # We need to reset self.current_sample_index to 0 at the end of the sound, otherwise,
        # we won't be able to play another sound.
        self.current_sample_index = 0
        self.nb_wav_samples = len(wav_samples)

    def get_bytes(self, *args, **kwargs):
        if self.nb_wav_samples > 0:
            for i in range(0, self.chunk_nb_samples):
                # To send zeros once the sound is finished, we compare current_sample_index to the size
                # of the sample: nb_wav_samples.
                if self.current_sample_index < self.nb_wav_samples:
                    self.buf[i] = self.wav_samples[self.current_sample_index]
                else:
                    self.buf[i] = 0
                #
                # We use self.current_sample_index to move through the samples. If we use i, we will only send
                # the first 32 bytes in a loop to the buffer.
                self.current_sample_index += 1
        # Audiostream requires the buffer to be returned as a string, so we convert it.
        return self.buf.tobytes()

