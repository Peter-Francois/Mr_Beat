from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget


class PlayIndicatorLight(Image):
    pass


class PlayIndicatorWidget(BoxLayout):
    nb_steps = 0
    lights = []
    left_align = NumericProperty(0)

    def set_current_step_index(self, index):
        if index >= self.nb_steps:
            return
        for i in range(0, self.nb_steps):
            light = self.lights[i]
            if i == index:
                light.source = "images/indicator_light_on.png"
            else:
                light.source = "images/indicator_light_off.png"

    def set_nb_steps(self, nb_steps):
        if not nb_steps == self.nb_steps:
            # Before rebuilding the widget, we reset the values to 0. clear_widgets removes all the widgets.
            self.lights = []
            self.clear_widgets()
            # To align the lights on the steps, we add an empty widget with the width of left_align.
            dummy_widget = Widget()
            dummy_widget.size_hint_x = None
            dummy_widget.width = self.left_align
            # Disable the dummy button (this doesn't make it disappear).
            dummy_widget.disabled = True
            self.add_widget(dummy_widget)

            # Rebuilding the widget.
            for i in range(0, nb_steps):
                light = PlayIndicatorLight()
                light.source = "images/indicator_light_off.png"
                self.lights.append(light)
                self.add_widget(light)
            self.nb_steps = nb_steps

