#!/usr/bin/env python3

import curses
import requests
import re
import json
mode = ''
# import mpv


def select(screen, options: list = [], title: str = ""):

    # Set up screen
    screen.clear()
    screen.addstr(
        "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n",
        curses.color_pair(2),
    )
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
        if key == ord('s') and "S to Search" in title:
            screen.clear()
            search(screen)
            return
        if key == ord('l') and "L to change language" in title:
            screen.clear()
            main(screen)
            return
        elif key == ord("\n"):
            break

        # Update screen
        screen.clear()
        screen.addstr(
            "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n",
            curses.color_pair(2),
        )
        screen.addstr(f"{title}:\n\n", curses.color_pair(1))
        for i, option in enumerate(options):
            if i == current_option:
                screen.addstr(" > ", curses.color_pair(2))
                screen.addstr(option + "\n", curses.color_pair(1))
            else:
                screen.addstr("   ")
                screen.addstr(option + "\n")
        screen.refresh()

    return current_option


def get_anime(prompt):
    url = 'https://api.allanime.to/allanimeapi/?query=query($search:SearchInput$limit:Int$page:Int$translationType:VaildTranslationTypeEnumType$countryOrigin:VaildCountryOriginEnumType){shows(search:$search%20limit:$limit%20page:$page%20translationType:$translationType%20countryOrigin:$countryOrigin){edges{_id%20name%20availableEpisodes%20__typename}}}&variables={"search":{"allowAdult":false,"allowUnknown":false,"query":"' + \
        prompt + '"},"limit":20,"page":1,"translationType":"' + \
        mode + '","countryOrigin":"ALL"}'
    response = requests.get(url)
    response.raise_for_status()

    return json.loads(response.text)['data']['shows']['edges']


def search_prompt(screen):
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

def search(screen):
    while True:
        anime_list = get_anime(search_prompt(screen))
        if not anime_list:
            screen.addstr(
                "no results found, please try again with a different prompt...\n", curses.color_pair(3))
            continue
        try:
            choice = select(screen, [str(i['name']) for i in anime_list],
                            f"S to Search, L to change language (currently {mode})")
        except:
            screen.addstr(
                "your search failed, please try again with a different prompt...\n", curses.color_pair(3))
            continue
        print(choice)
        break


def main(screen):
    try:
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        screen.keypad(True)
        curses.start_color()
        curses.use_default_colors()
        screen.scrollok(True)

        # Define color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_BLACK, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)

        # get the mode
        global mode 
        mode = select(screen, ["Sub (japanese)", "Dub (english)"], "Dub or Sub?")
        mode = "sub" if mode == 0 else "dub"
        screen.clear()

        search(screen)
        

    except KeyboardInterrupt:
        print("anipy escaped.")
        exit()


if __name__ == "__main__":
    curses.wrapper(main)
