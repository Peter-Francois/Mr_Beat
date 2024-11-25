from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton

Builder.load_file("track.kv")


# A step button
class TrackStepButton(ToggleButton):
    pass

# A button that will display the name of the sound.

class TrackSoundButton(Button):
    pass


# Creation of track buttons and their corresponding step buttons.
class TrackWidget(BoxLayout):
    def __init__(self, sound, audio_engine, tracks_nb_steps, track_source, steps_left_align,
                 tracks_widget_size_hint_min_y, tracks_widget_size_hint_max_y, **kwargs):
        super(TrackWidget, self).__init__(**kwargs)
        self.audio_engine = audio_engine
        self.size_hint_max_y = tracks_widget_size_hint_max_y
        self.size_hint_min_y = tracks_widget_size_hint_min_y
        self.sound = sound
        self.track_source = track_source
        box_layout_sound_button_and_separator = BoxLayout()
        box_layout_sound_button_and_separator.size_hint_x = None
        # Retrieval of the offset for the step buttons and the separator to adjust the position of the play_indicator.
        box_layout_sound_button_and_separator.width = steps_left_align
        sound_button = TrackSoundButton()
        # Retrieving the sound name from main.py (sound).
        sound_button.text = sound.displayname
        sound_button.on_press = self.on_sound_button_press
        sound_button.background_normal = "images/sound_button_normal.png"
        sound_button.background_down = "images/sound_button_down.png"
        box_layout_sound_button_and_separator.add_widget(sound_button)
        # separator
        separateur_image = Image(source="images/track_separator.png")
        separateur_image.size_hint_x = None
        separateur_image.width = dp(15)
        box_layout_sound_button_and_separator.add_widget(separateur_image)
        self.add_widget(box_layout_sound_button_and_separator)

        self.step_buttons = []
        self.tracks_nb_steps = tracks_nb_steps
        for i in range(0, tracks_nb_steps):
            step_button = TrackStepButton()
            # Change the color of the speed every 4 steps.
            if int(i/4) % 2 == 0:
                step_button.background_normal = "images/step_normal2.png"
            else:
                step_button.background_normal = "images/step_normal1.png"
            # We bind (link) the state change of the step_button with the function on_step_button_state.
            step_button.bind(state=self.on_step_button_state)
            self.step_buttons.append(step_button)
            self.add_widget(step_button)

    def on_sound_button_press(self):
        self.audio_engine.play_sound(self.sound.samples)

    def on_step_button_state(self, widget, value):
        steps = []
        for i in range(0, self.tracks_nb_steps):
            if self.step_buttons[i].state == "down":
                steps.append(1)
            else:
                steps.append(0)

        self.track_source.set_steps(steps)

