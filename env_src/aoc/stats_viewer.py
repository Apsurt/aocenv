from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.events import Resize
from rich.table import Table
from rich.text import Text

class StatsApp(App):
    """An interactive TUI app to view Advent of Code stats."""

    DESIGN_SYSTEM = None
    COMMAND_PALETTE = False
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    App, Screen {
        background: transparent;
    }
    """

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="left", action="scroll_left", description="Left"),
        Binding(key="right", action="scroll_right", description="Right"),
    ]

    def __init__(self, progress_data: dict):
        super().__init__()
        self.progress_data = progress_data
        self.scroll_x = 1

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static(id="stats_table")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted. Initial draw."""
        self.update_table()

    def on_resize(self, event: Resize) -> None:
        """Called automatically when the terminal window is resized."""
        self.update_table()

    def update_table(self) -> None:
        """Re-renders the statistics table."""
        table = self.build_table()
        self.query_one("#stats_table").update(table)

    def action_scroll_left(self) -> None:
        """Called when the user presses the left arrow key."""
        self.scroll_x = max(1, self.scroll_x - 1)
        self.update_table()

    def action_scroll_right(self) -> None:
        """Called when the user presses the right arrow key."""
        num_days_to_show = (self.size.width - 8) // 5

        # Calculate the maximum possible starting day. This ensures that
        # day 25 is the last day visible on the far right of the screen.
        max_scroll_x = max(1, 26 - num_days_to_show)

        # Increment scroll, but not past the calculated maximum.
        self.scroll_x = min(max_scroll_x, self.scroll_x + 1)
        self.update_table()

    def build_table(self) -> Table:
        """Builds and returns the Rich Table object to display."""
        table = Table(box=None, expand=True, show_edge=False)
        table.add_column("Year", style="bold", width=6)

        num_days_to_show = (self.size.width - 8) // 5
        start_day = self.scroll_x
        end_day = min(25, start_day + num_days_to_show - 1)

        for day in range(start_day, end_day + 1):
            table.add_column(f"{day}", justify="center", width=3)

        years = sorted(self.progress_data.keys(), reverse=True)
        for year in years:
            row = [f"[bold]{year}[/bold]"]
            year_progress = self.progress_data[year]
            for day in range(start_day, end_day + 1):
                stars = year_progress.get(str(day), 0)
                if stars == 2:
                    symbol = Text("★★", style="yellow")
                elif stars == 1:
                    symbol = Text("★ ", style="bright_black")
                else:
                    symbol = Text("  ", style="black")
                row.append(symbol)
            table.add_row(*row)

        return table
