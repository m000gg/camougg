from textual import on
from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, RichLog, Static, Button
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


class MainMenuScreen(Screen):

    CSS_PATH = "main-screen.tcss"

    TITLE = "Camougg"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="root"):
            yield Static(WELCOME_MESSAGE, id="logo")

            with Container(id="menu_container"):
                yield Static("Steganography", classes="section_title")

                with Horizontal(classes="menu_row"):
                    yield Button("[$]  Photo", id="btn_photo", classes="menu_button photo")
                    yield Static(
                        "hide data inside images (png, bmp, ...)",
                        classes="menu_desc",
                    )

                with Horizontal(classes="menu_row"):
                    yield Button("[>]  Video", id="btn_video", classes="menu_button video")
                    yield Static(
                        "hide data inside video frames",
                        classes="menu_desc",
                    )

                with Horizontal(classes="menu_row"):
                    yield Button("[~]  Audio", id="btn_audio", classes="menu_button audio")
                    yield Static(
                        "hide data inside audio waveforms",
                        classes="menu_desc",
                    )

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#menu_container", Container).border_title = "menu"

    @on(Button.Pressed)
    def handle_buttons(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "btn_photo":
            self.app.push_screen("photo")
        elif button_id == "btn_video":
            self.app.push_screen("to_be_done")
        elif button_id == "btn_audio":
            self.app.push_screen("to_be_done")

    def action_quit(self) -> None:
        self.app.exit()