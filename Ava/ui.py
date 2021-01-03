import logging
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from Ava.ava import Ava as Ava_class

logger = logging.getLogger(__name__)


Builder.load_string('''
<AvaGui>:
    title : "Ava"
    BoxLayout:
        orientation: 'vertical'
        padding: 20

        TextInput:
            id: input_text
            text: 'text'

        TextInput:
            id: output_text
            hint_text: 'output'

        Button:
            text: 'Read'
            size_hint_y: 0.2
            on_press: root.do_read()
            
        Button:
            text: 'Start'
            id: start_stop
            size_hint_y: 0.2
            on_press: root.do_start_stop()
''')


class AvaGui(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ava = None

    def do_read(self):
        text = self.ids.input_text.text
        if self.ava:
            for i in text.split():
                i = i.lower().strip()
                if i:
                    self.ava._text_source.output_push(i)
            self.ids.input_text.text = ""

    def do_start_stop(self):
        text = self.ids.start_stop.text
        if text == "Start":
            if self.ava is None:
                self.ava = Ava_class()
                self.ava.load_from_file()
                self.ids.output_text.text = self.ava.dump()
            self.ids.start_stop.text = "Exit"
            self.ava.run(blocking=False)
        elif text == "Exit":
            self.ids.start_stop.text = "Exit...."
            self.ava.stop()
            self.ava.join()
            App.get_running_app().stop()

class MainApp(App):
    def build(self):
        return AvaGui()

    def on_pause(self):
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = MainApp()
    app.run()
