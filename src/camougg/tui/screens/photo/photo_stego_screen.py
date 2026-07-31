from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static, RadioButton, RadioSet
from textual.containers import Vertical, Container, Horizontal

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


class PhotoStegoScreen(Screen):

    CSS_PATH = "photo-stego-screen.tcss"

    TITLE = "Camougg"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "main", "Main menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield Vertical(
            Static(WELCOME_MESSAGE, id="logo"),

            Static("Steganography", classes="section_title"),


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

    def action_quit(self) -> None:
        self.app.exit()

    def action_main(self) -> None:
        self.app.pop_screen()