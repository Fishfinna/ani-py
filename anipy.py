import curses


def select(screen, options: list = [], title: str = "") -> str:

    # Set up screen
    screen.clear()
    screen.addstr(
        "Use arrow-keys. Return to submit.\n", curses.color_pair(2))
    screen.addstr(f"{title}:\n\n", curses.color_pair(1))

    for i, option in enumerate(options):
        if i == 0:
            screen.addstr(" > ", curses.color_pair(2))
            screen.addstr(option + "\n", curses.color_pair(1))
        else:
            screen.addstr("   ")
            screen.addstr(option + "\n")
    screen.refresh()

    # Get user input
    current_option = 0
    while True:
        key = screen.getch()
        if key == curses.KEY_UP:
            if current_option > 0:
                current_option -= 1
        elif key == curses.KEY_DOWN:
            if current_option < len(options) - 1:
                current_option += 1
        elif key == ord("\n"):
            break

        # Update screen
        screen.clear()
        screen.addstr(
            "Use arrow-keys. Return to submit.\n", curses.color_pair(2))
        screen.addstr(f"{title}:\n\n", curses.color_pair(1))
        for i, option in enumerate(options):
            if i == current_option:
                screen.addstr(" > ", curses.color_pair(2))
                screen.addstr(option + "\n", curses.color_pair(1))
            else:
                screen.addstr("   ")
                screen.addstr(option + "\n")
        screen.refresh()

    return options[current_option]


def main():
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    screen.keypad(True)
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_BLACK, -1)

    language = select(
        screen, ["Sub (japanese)", "Dub (english)"], "Dub or Sub?")


if __name__ == "__main__":
    main()
