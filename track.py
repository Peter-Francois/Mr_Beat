from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty, ListProperty

Builder.load_file("track.kv")


# A step button
class TrackStepButton(ToggleButton):
    pass

# A button that will display the name of the sound.

class TrackSoundButton(Button):
    pass

# A button that clear the steps of the track.

class TrackClearButton(Button):
    pass

# A button that mute the track.

class TrackMuteButton(ToggleButton):
    pass

# A button that play in solo the track.

class TrackSoloButton(ToggleButton):
    pass

# Creation of track buttons and their corresponding step buttons.
class TrackWidget(BoxLayout):
    solo_button = ObjectProperty()
    track_index = NumericProperty(-1)
    def __init__(self, sound, audio_engine, tracks_nb_steps, track_source, steps_left_align,
                 tracks_widget_size_hint_min_y, tracks_widget_size_hint_max_y, track_index, solo_callback, **kwargs):
        super(TrackWidget, self).__init__(**kwargs)
        self.audio_engine = audio_engine
        self.size_hint_max_y = tracks_widget_size_hint_max_y
        self.size_hint_min_y = tracks_widget_size_hint_min_y
        self.sound = sound 
        self.track_source = track_source
        self.track_index = track_index
        box_layout_actions_button = BoxLayout()
        box_layout_actions_button.size_hint_x = None
        # Retrieval of the offset for the step buttons and the separator to adjust the position of the play_indicator.
        box_layout_actions_button.width = steps_left_align
        self.sound_button = TrackSoundButton()
        self.sound_button.size_hint_x = None
        self.sound_button.width = box_layout_actions_button.width * .5
        # Retrieving the sound name from main.py (sound).
        self.sound_button.text = sound.displayname
        self.sound_button.on_press = self.on_sound_button_press
        self.sound_button.background_normal = "images/sound_button_normal.png"
        self.sound_button.background_down = "images/sound_button_down.png"
        box_layout_actions_button.add_widget(self.sound_button)

        # box layout for volume control
        box_layout_volume_control = BoxLayout()
        box_layout_volume_control.orientation = "vertical"
        box_layout_volume_control.size_hint_x = None
        box_layout_volume_control.pos_hint = {"center_y": .62}
        box_layout_volume_control.width = box_layout_actions_button.width * .25
        label_volume = Label()
        label_volume.text = "VOLUME"
        label_volume.font_size = dp(9)
        label_volume.size_hint_y = None
        label_volume.height = dp(10)
        box_layout_volume_control.add_widget(label_volume)
        
        # Slider for volume control
        self.volume_slider = Slider(min=0, max=1, value=1)
        self.volume_slider.size_hint_x = None
        self.volume_slider.width = box_layout_actions_button.width * .25
        self.volume_slider.size_hint_y = None
        self.volume_slider.height = dp(20)
        self.volume_slider.bind(value=self.on_volume_change)
        self.volume_slider.cursor_image = "images/track_separator.png"
        box_layout_volume_control.add_widget(self.volume_slider)

        # Volume level display
        relative_layout_volume_level = RelativeLayout()
        relative_layout_volume_level.size_hint_y = None
        relative_layout_volume_level.height = dp(22)
        relative_layout_volume_level.size_hint_x = None
        relative_layout_volume_level.width = dp(28)
        relative_layout_volume_level.pos_hint = {"center_x": .5}
        background_image = Image()
        background_image.source = "images/bpm_lcd_background.png"
        background_image.allow_stretch = True
        background_image.keep_ratio = False
        relative_layout_volume_level.add_widget(background_image)
        relative_layout_volume_level.add_widget(Label(text="888",pos_hint={"center_y": .57}, font_name="fonts/Lcd.ttf", font_size=dp(20), opacity=.1))
        self.volume_level = Label(text="100",pos_hint={"center_y": .57}, font_name="fonts/Lcd.ttf", font_size=dp(20))
        relative_layout_volume_level.add_widget(self.volume_level)
        box_layout_volume_control.add_widget(relative_layout_volume_level)
        box_layout_actions_button.add_widget(box_layout_volume_control)

        box_layout_clear_mute_solo_button = BoxLayout()
        box_layout_clear_mute_solo_button.pos_hint = {"center_y": .62}
        box_layout_clear_mute_solo_button.spacing = dp(-2)
        box_layout_clear_mute_solo_button.size_hint_x = None
        box_layout_clear_mute_solo_button.width = box_layout_actions_button.width * .25
        box_layout_clear_mute_solo_button.orientation = "vertical"
        # clear button
        clear_button = TrackClearButton()
        clear_button.on_press = self.on_clear_button_press
        box_layout_clear_mute_solo_button.add_widget(clear_button)
        # mute button
        self.mute_button = TrackMuteButton()
        self.mute_button.on_press = self.on_mute_button_pressed
        box_layout_clear_mute_solo_button.add_widget(self.mute_button)

        # solo button
        self.solo_button = TrackSoloButton()
        if self.solo_button:
            self.solo_button.on_press = lambda: solo_callback(self.track_index)
        box_layout_clear_mute_solo_button.add_widget(self.solo_button)

        box_layout_actions_button.add_widget(box_layout_clear_mute_solo_button)
        self.add_widget(box_layout_actions_button)

        # step buttons
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
    
    def clear_track(self):
        for i in range(0, self.tracks_nb_steps):
            self.step_buttons[i].state = "normal"

    def on_volume_change(self, instance, value):
        self.track_source.set_volume(value)
        # We update the volume level display.
        self.volume_level.text = str(int(value * 100))

    def on_sound_button_press(self):
        self.audio_engine.play_sound(self.sound.samples)

    def on_clear_button_press(self):
        for i in range(0, self.tracks_nb_steps):
            self.step_buttons[i].state = "normal"

    def on_mute_button_pressed(self):
        if self.volume_slider.value == 0:
            self.volume_slider.value = 1
            self.mute_button.color = [1, 1, 1, 1]
        else:
            self.volume_slider.value = 0
            self.mute_button.color = [0, 0, 0, 1]
    
    def on_solo_button_pressed(self):
        for i in range(0, self.nb_tracks):
            if self.sound_button.text != "down":
                pass
            else:
                self.mute_button.state = "down"
                self.on_mute_button_pressed()

    def set_mute(self, mute_state: bool):
        if mute_state:
            self.volume_slider.value = 0
            self.mute_button.color = [0, 0, 0, 1]
        else:
            self.volume_slider.value = 1
            self.mute_button.color = [1, 1, 1, 1]


    def on_step_button_state(self, widget, value):
        steps = []
        for i in range(0, self.tracks_nb_steps):
            if self.step_buttons[i].state == "down":
                steps.append(1)
            else:
                steps.append(0)
        self.track_source.set_steps(steps)
