from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Static, Label
from textual.containers import Center
from textual.containers import Vertical


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


class ToBeDoneScreen(Screen):
    CSS_PATH = "to-be-done.tcss"

    TITLE = "Camougg"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "main", "Main menu")
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield Vertical(
            Static(WELCOME_MESSAGE, id="logo"),
            Center(
                Vertical(
                    Static("[bold yellow] WILL BE DONE IN THE FUTURE [/]", id="wip-title"),
                    Label("This feature is currently under development.", id="wip-subtitle"),
                    Label("Press [bold cyan]M[/] to return to the main menu.", id="wip-hint"),
                    classes="wip-box"
                )
            )
        )

    def action_quit(self) -> None:
        self.app.exit()

    def action_main(self) -> None:
        self.app.pop_screen()