from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Center
from textual.binding import Binding
from textual.widgets import Header, Footer, Static, SelectionList
from textual.widgets.selection_list import Selection

class ClearApp(App):
    """An interactive TUI app to clear project data."""

    DESIGN_SYSTEM = None
    COMMAND_PALETTE = False
    ENABLE_COMMAND_PALETTE = False

    BINDINGS = [
        Binding(key="y", action="confirm_selection", description="Confirm"),
        Binding(key="q", action="quit", description="Cancel"),
        Binding(key="n", action="quit", description="Cancel"),
    ]

    CSS = """
    #options {
        padding: 1;
        border: round;
    }
    """

    def __init__(self, items_to_clear: list[tuple[str, str]]):
        super().__init__()
        self.selection_items = [
            Selection(prompt=display_name, value=internal_id, initial_state=False)
            for display_name, internal_id in items_to_clear
        ]
        self.selected_for_deletion = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Center(
            VerticalScroll(
                Static("[bold]Select with Enter. Press (y) to confirm, (n) to cancel.[/bold]", id="title"),
                SelectionList(*self.selection_items, id="options"),
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted to set initial focus."""
        self.query_one(SelectionList).focus()

    def action_confirm_selection(self) -> None:
        """Called when 'y' is pressed."""
        selection_list = self.query_one(SelectionList)
        self.selected_for_deletion = selection_list.selected
        self.exit()
