from textual import work, on
from textual.binding import Binding
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static, Button
from textual.containers import Vertical, Container, Horizontal
import os
from camougg.core.camougg_engine import CamouggEngine

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
    saved_image_path = ""
    saved_secret_text = ""
    saved_password = ""
    output_image_path = ""

    CSS_PATH = "photo-stego-screen.tcss"

    TITLE = "Camougg"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "main", "Main menu"),
        Binding("r", "reset", "Reset / Back to Start"),
    ]

    current_step = "mode_select"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield Vertical(
            Static(WELCOME_MESSAGE, id="logo"),
            Static("Steganography", classes="section_title"),

            # Mode selection with buttons
            Container(
                Horizontal(
                    Button("Write", id="mode_write", classes="menu_button write"),
                    Static("Hide secret in image", classes="menu_desc"),
                    classes="menu_row"
                ),
                Horizontal(
                    Button("Read", id="mode_read", classes="menu_button read"),
                    Static("Extract secret from image", classes="menu_desc"),
                    classes="menu_row"
                ),
                id="mode_buttons_container"
            ),

            Container(
                Horizontal(
                    Button("Other Directory", id="path_other", classes="menu_button path"),
                    Static("Save to custom location", classes="menu_desc"),
                    classes="menu_row"
                ),
                Horizontal(
                    Button("Same Directory", id="path_same", classes="menu_button path"),
                    Static("Save in source directory", classes="menu_desc"),
                    classes="menu_row"
                ),
                id="output_path_container",
                classes="hidden"
            ),

            RichLog(
                id="echo_log",
                auto_scroll=True,
                markup=True,
            ),

            Input(
                placeholder="[Camougg] >",
                id="cli_input",
            ),
        )

        yield Footer()

    def on_mount(self) -> None:
        cli_input = self.query_one("#cli_input")
        cli_input.disabled = True
        cli_input.display = False

        log = self.query_one("#echo_log")
        log.write("[bold yellow]? Choose operation mode:[/]")

        self.query_one("#mode_write").focus()

    @on(Button.Pressed, "#mode_write")
    def handle_write_mode(self):
        if self.current_step != "mode_select":
            return

        log = self.query_one("#echo_log")
        cli_input = self.query_one("#cli_input")

        self.query_one("#mode_buttons_container").add_class("hidden")

        log.write(f"\n[bold green]✓ Mode:[/] Write (Hide secret)")
        self.current_step = "image_path"

        cli_input.disabled = False
        cli_input.display = True
        cli_input.focus()

        log.write("\n[bold yellow]? Input image Path (image_path):[/]")

    @on(Button.Pressed, "#mode_read")
    def handle_read_mode(self):
        if self.current_step != "mode_select":
            return

        log = self.query_one("#echo_log")
        self.query_one("#mode_buttons_container").add_class("hidden")

        log.write(f"\n[bold green]✓ Mode:[/] Read (Extract secret)")
        log.write("[bold cyan]ℹ Read mode activated.[/]")

        cli_input = self.query_one("#cli_input")
        cli_input.disabled = False
        cli_input.display = True
        cli_input.focus()
        self.current_step = "read_image_path"
        log.write("\n[bold yellow]? Enter path of the image to read from:[/]")

    @on(Button.Pressed, "#path_other")
    def handle_path_other(self):
        if self.current_step != "set_directory":
            return

        log = self.query_one("#echo_log")
        cli_input = self.query_one("#cli_input")

        self.query_one("#output_path_container").add_class("hidden")

        log.write(f"\n[bold green]✓ Choice:[/] Other Directory")
        log.write("[bold yellow]? Enter custom output path (with file name):[/]")

        cli_input.disabled = False
        cli_input.display = True
        cli_input.focus()

        self.current_step = "custom_output_path"

    @on(Button.Pressed, "#path_same")
    def handle_path_same(self):
        if self.current_step != "set_directory":
            return

        log = self.query_one("#echo_log")
        cli_input = self.query_one("#cli_input")

        self.output_image_path = "same"
        log.write(f"\n[bold green]✓ Choice:[/] Same Directory")
        log.write("[bold green]✓ Using default output path.[/]")

        self.current_step = "ready"
        cli_input.disabled = True
        cli_input.display = False
        self.query_one("#output_path_container").add_class("hidden")

        self.encrypt_message(self.saved_image_path, self.saved_secret_text, self.saved_password,
                             self.output_image_path)

    @work(thread=True)
    def encrypt_message(self, image_path: str, secret: str, password: str, output_image_path: str) -> None:
        log_widget = self.query_one("#echo_log")

        engine = CamouggEngine(log_callback=log_widget.write, app=self)

        try:
            engine.embed(image_path, secret, password, output_image_path)
            log_widget.write("Ready! press m to go to main menu or q to quit.")
        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error")
            log_widget.write(f"[bold red]✗ Error: {str(e)}[/]")

    @work(thread=True)
    def decrypt_message(self, image_path: str, password: str):
        log_widget = self.query_one("#echo_log")

        engine = CamouggEngine(log_callback=log_widget.write, app=self)

        try:
            secret = engine.extract(image_path, password)
            if secret is not None:
                log_widget.write(f"Your secret message is: [bold red] {secret} [/]" )
                log_widget.write("Ready! press m to go to main menu or q to quit.")
            else:
                log_widget.write("[bold red]✗ Failed to decrypt message[/]")
        except Exception as e:
            self.app.notify(f"Error: {str(e)}", severity="error")
            log_widget.write(f"[bold red]✗ Error: {str(e)}[/]")

    @on(Input.Submitted, "#cli_input")
    def handle_enter(self, event: Input.Submitted):
        user_input = event.value.strip()
        event.input.value = ""

        if not user_input:
            return

        log = self.query_one("#echo_log")

        if self.current_step == "image_path":
            if not os.path.isfile(user_input):
                log.write(f"[bold red]✗ Error:[/] File '{user_input}' not found.")
                log.write("[bold yellow]? Try enter the path once again:[/]")
                return

            self.saved_image_path = user_input
            log.write(f"[bold green]✓ Found file, path saved:[/] {self.saved_image_path}")

            self.current_step = "secret_text"
            log.write("\n[bold yellow]? Write your secret:[/]")

        elif self.current_step == "secret_text":
            self.saved_secret_text = user_input
            log.write(f"[bold green]✓ Secret text saved[/]")

            self.current_step = "password"
            log.write("\n[bold yellow]? Write your password for encryption:[/]")
            event.input.password = True

        elif self.current_step == "password":
            self.saved_password = user_input
            log.write(f"[bold green]✓ Password set[/]")
            event.input.password = False

            self.current_step = "set_directory"

            output_container = self.query_one("#output_path_container")
            output_container.remove_class("hidden")
            self.query_one("#path_other").focus()

            log.write("\n[bold yellow]? Choose the output path option:[/]")
            event.input.disabled = True
            event.input.display = False

        elif self.current_step == "custom_output_path":
            self.output_image_path = user_input

            log.write(f"[bold green]✓ Custom path saved:[/] {self.output_image_path}")

            self.current_step = "ready"
            event.input.disabled = True
            event.input.display = False
            self.query_one("#output_path_container").add_class("hidden")

            self.encrypt_message(self.saved_image_path, self.saved_secret_text, self.saved_password,
                                 self.output_image_path)

        elif self.current_step == "read_image_path":
            if not os.path.isfile(user_input):
                log.write(f"[bold red]✗ Error:[/] File '{user_input}' not found.")
                log.write("[bold yellow]? Try enter the path once again:[/]")
                return

            self.saved_image_path = user_input
            log.write(f"[bold green]✓ Found file, path saved:[/] {self.saved_image_path}")
            self.current_step = "read_password"
            log.write("\n[bold yellow]? Write the password for decryption:[/]")
            event.input.password = True

        elif self.current_step == "read_password":
            self.saved_password = user_input
            log.write(f"[bold green]✓ Password set[/]")
            event.input.password = False
            self.current_step = "read_ready"
            event.input.disabled = True
            event.input.display = False
            self.decrypt_message(self.saved_image_path, self.saved_password)

    def action_quit(self) -> None:
        self.app.exit()

    def action_main(self) -> None:
        self.app.pop_screen()

    def action_reset(self) -> None:
        self.saved_image_path = ""
        self.saved_secret_text = ""
        self.saved_password = ""
        self.output_image_path = ""

        self.current_step = "mode_select"
        log = self.query_one("#echo_log")
        cli_input = self.query_one("#cli_input")
        mode_container = self.query_one("#mode_buttons_container")
        output_container = self.query_one("#output_path_container")

        log.clear()
        log.write("[bold cyan]⟳ Resetting to main menu...[/]")
        log.write("[bold yellow]? Choose operation mode:[/]")

        mode_container.remove_class("hidden")
        output_container.add_class("hidden")
        self.query_one("#mode_write").focus()

        cli_input.disabled = True
        cli_input.display = False
        cli_input.value = ""
        cli_input.password = False

        self.app.notify("Returned to mode selection", severity="information")
