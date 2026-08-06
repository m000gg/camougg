from textual.app import App
from .screens.main.main_menu_screen import MainMenuScreen
from .screens.photo.photo_stego_screen import PhotoStegoScreen
from .screens.other.to_be_done_screen import ToBeDoneScreen



class CamouggApp(App):

    SCREENS = {
        "menu": MainMenuScreen,
        "photo": PhotoStegoScreen,
        "to_be_done": ToBeDoneScreen,
    }

    def on_mount(self):
        self.push_screen("menu")


def run() -> None:
    app = CamouggApp()
    app.run()