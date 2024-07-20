import colorama
from colorama import Fore, Style
from tabulate import tabulate

class ColoredTable:
    def __init__(self):
        # Initialize colorama
        colorama.init()

    def colored_cell(self, content, color):
        """Wrap content with color codes."""
        return f"{color}{content}{Style.RESET_ALL}"

    def create_colored_table(self, data, headers):
        """Create a table with colored cells."""
        colored_data = []
        for row in data:
            colored_row = [self.colored_cell(str(cell), Fore.YELLOW if idx % 2 == 0 else Fore.CYAN) for idx, cell in enumerate(row)]
            colored_data.append(colored_row)
        return tabulate(colored_data, headers=headers, tablefmt="grid")

    def display_table(self, data, headers):
        """Create and print the colored table."""
        table = self.create_colored_table(data, headers)
        print(table)
