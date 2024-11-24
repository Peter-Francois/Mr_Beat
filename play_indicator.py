from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
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
            # avant de reconstruir le widget, on remet les valeur a 0. Clear_widgets efface tout les widgets
            self.lights = []
            self.clear_widgets()
            # Pour mettre caller les lights sur les steps, on ajoute un empty widget de la largeur de left_align
            dummy_widget = Widget()
            dummy_widget.size_hint_x = None
            dummy_widget.width = self.left_align
            # désactivé le boutton dummy (cela ne le fait pas disparétre)
            dummy_widget.disabled = True
            self.add_widget(dummy_widget)

            # reconstruire le widget
            for i in range(0, nb_steps):
                light = PlayIndicatorLight()
                light.source = "images/indicator_light_off.png"
                self.lights.append(light)
                self.add_widget(light)
            self.nb_steps = nb_steps

