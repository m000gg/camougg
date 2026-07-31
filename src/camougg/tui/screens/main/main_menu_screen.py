from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static, RadioButton, RadioSet
from textual.containers import Vertical
from textual import on

SERIOUS_ASCII_LOGO = """
 ██████╗ █████╗ ███╗   ███╗ ██████╗ ██╗   ██╗ ██████╗  ██████╗
██╔════╝██╔══██╗████╗ ████║██╔═══██╗██║   ██║██╔════╝ ██╔════╝
██║     ███████║██╔████╔██║██║   ██║██║   ██║██║  ███╗██║  ███╗
██║     ██╔══██║██║╚██╔╝██║██║   ██║██║   ██║██║   ██║██║   ██║
╚██████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝  ╚═════╝
                                                    > < > + -
                                        hide files inside media.

 """
WELCOME_MESSAGE = f"[green]{SERIOUS_ASCII_LOGO}[/]"

class MainMenuScreen(Screen):

    CSS_PATH = "main-screen.tcss"

    TITLE = "Camougg"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield Vertical(
            Static(WELCOME_MESSAGE, id="logo"),

            Static("Steganography", classes="section_title"),

            RadioSet(
                RadioButton("Video"),
                RadioButton("Photo"),
                RadioButton("Audio"),
                id="steg_type",
            ),

            RichLog(
                id="echo_log",
                auto_scroll=True,
                markup=True,
            ),

            Input(
                placeholder="[Camougg] >",
                id="message_input",
            ),
        )

        yield Footer()

    @on(RadioSet.Changed, "#steg_type")
    def handle_radio_choice(self, event: RadioSet.Changed):

        choice = str(event.pressed.label)

        if choice == "Photo":
            self.app.push_screen("photo")
        elif choice == "Video":
            self.app.push_screen("video")
        elif choice == "Audio":
            self.app.push_screen("audio")


    def action_quit(self) -> None:
        self.app.exit()
