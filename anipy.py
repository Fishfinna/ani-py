#!/usr/bin/env python3

import curses
import requests
import re
# import mpv

DOMAIN = "allanime.to"
AGENT = "Mozilla/5.0 (Windows NT 6.1; Win64; rv:109.0) Gecko/20100101 Firefox/109.0"


def select(screen, options: list = [], title: str = "") -> str:

    # Set up screen
    screen.clear()
    screen.addstr(
        "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n", curses.color_pair(2))
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
            "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n", curses.color_pair(2))
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


def get_anime(prompt, mode):
    anime_list = []
    url = f"https://api.{DOMAIN}/allanimeapi"
    search_gql = "query(        $search: SearchInput        $limit: Int        $page: Int        $translationType: VaildTranslationTypeEnumType        $countryOrigin: VaildCountryOriginEnumType    ) {    shows(        search: $search        limit: $limit        page: $page        translationType: $translationType        countryOrigin: $countryOrigin    ) {        edges {            _id name availableEpisodes __typename       }    }}"
    headers = {"User-Agent": AGENT}
    params = {
        "query": search_gql,
        "variables": {
            "search": {
                "allowAdult": False,
                "allowUnknown": False,
                "query": prompt
            },
            "limit": 40,
            "page": 1,
            "translationType": mode,
            "countryOrigin": "ALL"
        }
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    regex = r'_id":"([^"]*)","name":"([^"]*)".*' + mode + '":([1-9][^,]*).*'
    anime_list = re.findall(regex, response.text)

    print(response.text)

    print(anime_list)

    return ([f"{_id}\t{name} ({episodes} episodes)" for _id, name, episodes in anime_list])


def search(screen):
    while True:
        curses.echo()
        curses.curs_set(1)
        screen.addstr("Search: ", curses.color_pair(1))
        search_input = screen.getstr()

        if not search_input:
            screen.clear()
            continue

        # make it url compatible
        search_input = search_input.decode().replace(" ", "+")

        # clean prompt
        curses.curs_set(0)
        curses.noecho()

        return search_input


def main(screen):
    try:
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        screen.keypad(True)
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_BLACK, -1)

        # get the language
        language = select(
            screen, ["Sub (japanese)", "Dub (english)"], "Dub or Sub?")[:3].lower()
        screen.clear()

        # search
        user_search = search(screen)

        # find matching anime
        print(get_anime(user_search, language))

    except KeyboardInterrupt:
        print("anipy escaped.")
        exit(1)


if __name__ == "__main__":
    curses.wrapper(main)
