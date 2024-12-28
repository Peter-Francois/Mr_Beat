from kivy import Config
Config.set('graphics', 'width', '780')
Config.set('graphics', 'height', '360')
Config.set('graphics', 'minimum_width', '650')
Config.set('graphics', 'minimum_height', '300')

from kivy.uix.widget import Widget
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, Clock
from kivy.uix.relativelayout import RelativeLayout

from audio_engine import AudioEngine
from sound_kit_service import SoundKitService, SoundKit
from track import TrackWidget

Builder.load_file("track.kv")
Builder.load_file("play_indicator.kv")

TRACK_NB_STEPS = 16
MIN_BPM = 80
MAX_BPM = 180


class VerticalSpacingWidget(Widget):
    pass


class MainWidget(RelativeLayout):
    tracks_layout = ObjectProperty()
    play_indicator_widget = ObjectProperty()
    TRACK_STEPS_LEFT_ALIGN = NumericProperty(dp(180))
    step_index = 0
    bpm = NumericProperty(120)
    button_less_bpm = ObjectProperty()
    button_add_bpm = ObjectProperty()
    nb_tracks = NumericProperty(0)
    tracks_widget_size_hint_min_y = NumericProperty(dp(45))
    tracks_widget_size_hint_max_y = NumericProperty(dp(75))

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.sound_kit_service = SoundKitService()
        self.nb_tracks = self.sound_kit_service.get_nb_tracks()
        self.audio_engine = AudioEngine()
        self.audio_mixer = self.audio_engine.create_mixer(self.sound_kit_service.soundkit.get_all_samples(),
                                                          self.bpm, TRACK_NB_STEPS, self.on_mixer_current_step_changed
                                                          , MIN_BPM)

    def on_parent(self, widget, parent):
        # Once the KV file is loaded, we create the different buttons and spaces.
        self.play_indicator_widget.set_nb_steps(TRACK_NB_STEPS)
        for i in range(0, self.sound_kit_service.soundkit.get_nb_tracks()):
            # To transmit the sound name to the track file coming from the sound in the sound_kit_service.
            sound = self.sound_kit_service.get_sound_at(i)
            # We add empty widgets to create a margin between the tracks.
            self.tracks_layout.add_widget(VerticalSpacingWidget())
            self.tracks_layout.add_widget(TrackWidget(sound, self.audio_engine, TRACK_NB_STEPS,
                                                      self.audio_mixer.tracks[i], self.TRACK_STEPS_LEFT_ALIGN,
                                                      self.tracks_widget_size_hint_min_y,
                                                      self.tracks_widget_size_hint_max_y))

        # The last empty widget is for the bottom margin of the app.
        self.tracks_layout.add_widget(VerticalSpacingWidget())

    # WE MUST NEVER CALL UI ELEMENTS FROM ANOTHER THREAD THAN THE MAIN THREAD. INSTEAD, WE WILL USE Clock TO EXECUTE
    # THE FUNCTION ON THE MAIN THREAD. IT IS CRUCIAL THAT EVERYTHING WE MANIPULATE FROM THE UI IS DONE FROM
    # THE MAIN THREAD.
    def on_mixer_current_step_changed(self, step_index):
        # We store the step_index to send it to update_play_indicator_cbk.
        self.step_index = step_index
        # We instruct to trigger an event on the main thread.
        Clock.schedule_once(self.update_play_indicator_cbk, 0)  # The 0 is for the trigger time.

    def update_play_indicator_cbk(self, dt):
        if self.play_indicator_widget is not None:
            self.play_indicator_widget.set_current_step_index(self.step_index)

    def on_bpm(self, widget, value):
        if value <= MIN_BPM:
            self.button_less_bpm.disabled = True
            return
        elif value >= MAX_BPM:
            self.button_add_bpm.disabled = True
            return
        else:
            self.button_add_bpm.disabled = False
            self.button_less_bpm.disabled = False
        self.audio_mixer.set_bpm(self.bpm)


class MrBeatApp(App):
    pass


MrBeatApp().run()
