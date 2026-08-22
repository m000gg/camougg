import os
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Button, Static, Input


class FilePickerScreen(ModalScreen[str | None]):
    CSS_PATH = "file-picker-screen.tcss"

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, mode: str = "file", start_path: str | None = None, title: str = "Select a file"):
        super().__init__()
        self.mode = mode
        self.start_path = start_path or os.path.expanduser("~")
        self.picker_title = title
        self._selected_dir = str(Path(self.start_path).resolve())

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.picker_title, id="picker_title"),
            Static(f"[dim]{self._selected_dir}[/]", id="picker_current_path"),
            DirectoryTree(self.start_path, id="picker_tree"),
            Horizontal(
                Input(placeholder="Go to path (e.g. ~/Desktop, /)", id="picker_goto_input"),
                Button("Go", id="goto_btn", classes="menu_button path"),
                id="picker_goto_row",
            ),
            Horizontal(
                Button("Select This Directory", id="select_dir_btn", classes="menu_button path")
                if self.mode == "directory" else Static("", classes="picker_spacer"),
                Button("Cancel", id="cancel_btn", classes="menu_button cancel"),
                id="picker_buttons",
            ),
            id="picker_container",
        )

    def on_mount(self) -> None:
        self.query_one("#picker_tree").focus()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self._selected_dir = str(event.path)
        self.query_one("#picker_current_path", Static).update(f"[dim]{self._selected_dir}[/]")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        if self.mode == "file":
            self.dismiss(str(event.path))

    def _jump_to(self, raw_path: str) -> None:
        expanded = os.path.expanduser(raw_path.strip())
        if not expanded:
            return

        if not os.path.isdir(expanded):
            self.notify(f"Not a directory: {expanded}", severity="error")
            return

        resolved = str(Path(expanded).resolve())
        self._selected_dir = resolved
        self.query_one("#picker_current_path", Static).update(f"[dim]{resolved}[/]")

        tree = self.query_one("#picker_tree", DirectoryTree)
        tree.path = resolved

    @on(Button.Pressed, "#goto_btn")
    def handle_goto(self) -> None:
        self._jump_to(self.query_one("#picker_goto_input", Input).value)

    @on(Input.Submitted, "#picker_goto_input")
    def handle_goto_submit(self, event: Input.Submitted) -> None:
        self._jump_to(event.value)

    @on(Button.Pressed, "#select_dir_btn")
    def handle_select_dir(self) -> None:
        self.dismiss(self._selected_dir)

    @on(Button.Pressed, "#cancel_btn")
    def handle_cancel(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)