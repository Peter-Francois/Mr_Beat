from audiostream.core import get_output
from audio_source_mixer import AudioSourceMixer
from audio_source_one_shot import AudioSourceOneShoot
from audio_source_track import AudioSourceTrack


class AudioEngine:
    NB_CHANNELS = 1  # 1=mono 2=stereo
    SAMPLE_RATE = 44100  # cd sample rate. It is a good standard of audio quality.
    BUFFER_SIZE = 1024

    def __init__(self):
        # Connection to the sound card output.
        # Audio engine encoding defaults to 16-bit.
        self.output_stream = get_output(channels=self.NB_CHANNELS,
                                        rate=self.SAMPLE_RATE,
                                        buffersize=self.BUFFER_SIZE)

        self.audio_source_one_shot = AudioSourceOneShoot(self.output_stream)
        self.audio_source_one_shot.start()

    def play_sound(self, wav_samples):
        self.audio_source_one_shot.set_wav_samples(wav_samples)

    def create_mixer(self, all_wav_samples, bpm, nb_steps, on_current_step_changed, min_bpm):
        source_mixer = AudioSourceMixer(self.output_stream, all_wav_samples, bpm, self.SAMPLE_RATE, nb_steps,
                                        on_current_step_changed, min_bpm)
        source_mixer.start()
        return source_mixer
