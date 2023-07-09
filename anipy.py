#!/usr/bin/env python3

# general imports
import curses
import requests
import json
import os

path_to_add = os.path.dirname(__file__)
if path_to_add not in os.environ["PATH"]:
    os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
import mpv


# global vars :(
mode = ""
referer = "https://allanime.to"


def select(screen, options: list = [], title: str = ""):
    # Set up screen
    screen.clear()
    screen.addstr(
        "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n",
        curses.color_pair(2),
    )

    if title:
        screen.addstr(f"{title}:\n\n", curses.color_pair(1))
    else:
        screen.addstr("\n\n", curses.color_pair(1))

    current_option = 0
    page = 0
    page_size = min(13, len(options))
    max_page = (len(options) - 1) // page_size

    while True:
        # Show options for current page
        page_start = page * page_size
        page_options = options[page_start : page_start + page_size]

        for i, option in enumerate(page_options):
            if i == current_option:
                screen.addstr(" > ", curses.color_pair(2))
                screen.addstr(option + "\n", curses.color_pair(1))
            else:
                screen.addstr("   ")
                screen.addstr(option + "\n")

        # Show page navigation instructions if needed
        if max_page > 0:
            screen.addstr("\n")
            if page > 0:
                screen.addstr(" ← ", curses.color_pair(2))
                screen.addstr("prev  ", curses.color_pair(1))
            else:
                screen.addstr("    ")
            if page < max_page:
                screen.addstr("next ", curses.color_pair(1))
                screen.addstr(" → ", curses.color_pair(2))

        screen.refresh()

        # Get user input
        key = screen.getch()
        if key in [curses.KEY_UP, ord("w")]:
            if current_option > 0:
                current_option -= 1
            else:
                current_option = page_size - 1
                if max_page > 0 and page > 0:
                    page -= 1
        elif key in [curses.KEY_DOWN, ord("s")]:
            if (
                current_option < page_size - 1
                and current_option < len(page_options) - 1
            ):
                current_option += 1
            else:
                current_option = 0
                if max_page > 0 and page < max_page:
                    page += 1
        elif key in [curses.KEY_LEFT, ord("a")]:
            if page > 0:
                page -= 1
                current_option = min(current_option, len(page_options) - 1)
        elif key in [curses.KEY_RIGHT, ord("d")]:
            if page < max_page:
                page += 1
                current_option = min(current_option, len(page_options) - 1)
        elif key == ord("\n"):
            break
        elif key == ord("c") and "C to change Search" in title:
            screen.clear()
            search(screen)
            return (None, None)
        elif key == ord("l") and "L to change language" in title:
            screen.clear()
            main(screen)
            return (None, None)

        # Update screen
        screen.clear()
        screen.addstr(
            "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n",
            curses.color_pair(2),
        )
        if title:
            screen.addstr(f"{title}:\n\n", curses.color_pair(1))
        else:
            screen.addstr("\n\n", curses.color_pair(1))

    selected_index = page_start + current_option
    return (selected_index, options[selected_index])


def set_mode(screen):
    global mode
    mode = select(screen, ["Sub (japanese)", "Dub (english)"], "Dub or Sub?")
    mode = "sub" if mode[0] == 0 else "dub"


def get_anime_list(prompt):
    url = (
        'https://api.allanime.day/allanimeapi/?query=query($search:SearchInput$limit:Int$page:Int$translationType:VaildTranslationTypeEnumType$countryOrigin:VaildCountryOriginEnumType){shows(search:$search%20limit:$limit%20page:$page%20translationType:$translationType%20countryOrigin:$countryOrigin){edges{_id%20name%20availableEpisodes%20__typename}}}&variables={"search":{"allowAdult":false,"allowUnknown":false,"query":"'
        + prompt
        + '"},"limit":40,"page":1,"translationType":"'
        + mode
        + '","countryOrigin":"ALL"}'
    )
    response = requests.get(url, headers={"Referer": referer})
    response.raise_for_status()

    return json.loads(response.text)["data"]["shows"]["edges"]


def get_episode_url(episode_data) -> str:
    episode_url = [
        i["sourceUrl"]
        for i in episode_data["sourceUrls"]
        if i["sourceUrl"].startswith("http://")
        or i["sourceUrl"].startswith("https://")
        and i["type"] == "player"
    ]
    if episode_url:
        return episode_url[0]
    else:
        print("no episode url found")
        exit()


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
    screen.clear()
    while True:
        anime_list = get_anime_list(search_prompt(screen))
        if not anime_list:
            screen.addstr(
                "No results found. Please try again with a different prompt.\n",
                curses.color_pair(3),
            )
            continue
        try:
            choice = select(
                screen,
                [str(i["name"].replace("[", "").replace("]", "")) for i in anime_list],
                f"C to change Search, L to change language (currently {mode})",
            )
        except:
            screen.addstr(
                "\nYour search failed. Please try again with a different prompt.\n",
                curses.color_pair(3),
            )
            continue
        if choice:
            episode_number = (
                select(
                    screen,
                    [
                        str(i + 1)
                        for i in range(anime_list[choice[0]]["availableEpisodes"][mode])
                    ],
                    f"C to change Search, L to change language (currently {mode})\nSelect your episode of {anime_list[choice[0]]['name']}",
                )[0]
                + 1
            )
            if episode_number:
                url = (
                    'https://api.allanime.day/allanimeapi?query=query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {    episode(        showId: $showId        translationType: $translationType        episodeString: $episodeString    ) {        episodeString sourceUrls    }}&variables={"showId":"'
                    + anime_list[choice[0]]["_id"]
                    + '","translationType":"'
                    + mode
                    + '","episodeString": "'
                    + str(episode_number)
                    + '"}'
                )
                response = requests.get(url, headers={"Referer": referer})

                if json.loads(response.text)["data"]["episode"]["sourceUrls"]:
                    screen.clear()
                    screen.addstr("Loading the episode...\n", curses.color_pair(2))
                    return (
                        json.loads(response.text)["data"]["episode"],
                        anime_list[choice[0]],
                    )


def play_from_url(episode_url):
    # Create an instance of the player
    player = mpv.MPV(
        player_operation_mode="pseudo-gui",
        script_opts="osc-layout=box,osc-seekbarstyle=bar,osc-deadzonesize=0,osc-minmousemove=3",
        input_default_bindings=True,
        input_vo_keyboard=True,
        osc=True,
    )
    player.play(episode_url)
    player.wait_for_playback()
    player.terminate()


def post_episode_menu(screen, episode_data, series):
    options = ["Replay", "Change Show", "Change Language", "Exit"]
    if (
        int(episode_data["episodeString"]) <= series["availableEpisodes"][mode]
        and int(episode_data["episodeString"]) > 1
    ):
        options = ["Previous Episode"] + options

    if int(episode_data["episodeString"]) < series["availableEpisodes"][mode]:
        options = ["Next Episode"] + options
    return select(
        screen,
        options,
        f"You were just watching {series['name']}, episode {episode_data['episodeString']}",
    )[1]


def play_following_episode(direction, episode_data, series, screen):
    episode_number = int(episode_data["episodeString"])

    if direction == "prev":
        episode_number -= 1
    if direction == "next":
        episode_number += 1

    url = 'https://api.allanime.day/allanimeapi?query=query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {    episode(        showId: $showId        translationType: $translationType        episodeString: $episodeString    ) {        episodeString sourceUrls    }}&variables={"showId":"' + series["_id"] + '","translationType":"'+ mode + '","episodeString": "'+ str(episode_number) + '"}'

    response = requests.get(url, headers={"Referer": referer})
    play_from_url(get_episode_url(json.loads(response.text)["data"]["episode"]))

    new_episode_data = json.loads(response.text)["data"]["episode"]
    return post_episode_menu(screen, new_episode_data, series), {
        "episode": new_episode_data,
        "series": series,
    }


def play(screen):
    episode_data, series = search(screen)
    play_from_url(get_episode_url(episode_data))
    post_episode_action = post_episode_menu(screen, episode_data, series)
    return post_episode_action, {"episode": episode_data, "series": series}


def main(screen):
    # project set up
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

    set_mode(screen)

    # lets play some anime
    try:
        next_action, episode_data = play(screen)

        while True:
            if next_action == "Previous Episode":
                next_action, episode_data = play_following_episode(
                    "prev", episode_data["episode"], episode_data["series"], screen
                )

            elif next_action == "Next Episode":
                next_action, episode_data = play_following_episode(
                    "next", episode_data["episode"], episode_data["series"], screen
                )
            
            elif next_action == "Replay":
                next_action, episode_data = play_following_episode(None, episode_data["episode"], episode_data["series"], screen)

            elif next_action == "Change Show":
                next_action, episode_data = play(screen)

            elif next_action == "Change Language":
                main(screen)

            elif next_action == "Exit":
                print("exiting ani-py...")
                exit()

    except KeyboardInterrupt:
        print("exiting ani-py...")


if __name__ == "__main__":
    curses.wrapper(main)
