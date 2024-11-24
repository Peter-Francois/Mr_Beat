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
from kivy.uix.button import Button
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

# idée pour amélioré l'aplli:
# - clear step / track
# - activé / désactivé track (mute)
# - activé / désactivé les autre track (solo)
# - volume / track (recupéré la valeur du slider au niveau de l'audio source, à inplémenté au niveau du
# AudioSourceTrack en multipliant tout les samples par la valeur de commande)
# - sauvegarder des paternes (4) pour pouvoir créé une musique
# - Menu de démarage avec selection de sound pour composé le sound kit
# - ajouté un selection des sound kit préenregistré avec possibilité d'écouté les sound en one-shot
# - lecture des samples dans le menu pour choisir les sound à ajouté on sound kit
# - Création d'autre thème graphique avec possibilité de choisir le thème
# - permettre le renomage d'un sound (displayname)
# - Créé des test pour l'appli


class MainWidget(RelativeLayout):
    tracks_layout = ObjectProperty()
    play_indicator_widget = ObjectProperty()
    TRACK_STEPS_LEFT_ALIGN = NumericProperty(dp(120))
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
        # un fois le fichier kv charger, on créé les différents boutton ou autre
        self.play_indicator_widget.set_nb_steps(TRACK_NB_STEPS)
        for i in range(0, self.sound_kit_service.soundkit.get_nb_tracks()):
            # pour transmetre le nom du son au fichier track venant du sound du sound_kit_service
            sound = self.sound_kit_service.get_sound_at(i)
            # on ajoute des empty widget pour faire une marge entre les tracks
            self.tracks_layout.add_widget(VerticalSpacingWidget())
            self.tracks_layout.add_widget(TrackWidget(sound, self.audio_engine, TRACK_NB_STEPS,
                                                      self.audio_mixer.tracks[i], self.TRACK_STEPS_LEFT_ALIGN,
                                                      self.tracks_widget_size_hint_min_y,
                                                      self.tracks_widget_size_hint_max_y))

        # dernier empty widget pour la marge du bas de l'app
        self.tracks_layout.add_widget(VerticalSpacingWidget())

    """ON NE DOIT JAMAIS APPELLE DES ELEMENTS DE LA UI DEPUIS UNE AUTRE THREAD
    def on_mixer_current_step_changed(self, step_index):
        # Ici on ajout la condition suivant pour la raise condition, c'est a dire que le moteur audio et le UI
        # fonctionnent en paralélle et que l'on est pas sur que le moteur audio est déja pres a nous envoyé
        # le step_index
        if self.play_indicator_widget is not None:
            self.play_indicator_widget.set_current_step_index(step_index)
            
            ON VA DU COUP UTILISER Clock POUR EXECUTER LA FONCTION SUR LA MAIN_THREAD
            IL EST FONDAMENTAL QUE TOUT CE QUE L'ON MANIPULE DEPUIS LA UI SOIS FAIT DEPUIS LE MAIN_THREAD
            """

    def on_mixer_current_step_changed(self, step_index):
        # on enregistre le step_index pour le renvoyé a update_play_indicator_cbk
        self.step_index = step_index
        # On dit de déclanché un événement sur la main_thread
        Clock.schedule_once(self.update_play_indicator_cbk, 0)  # le 0 et pour le temps de déclanchement

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