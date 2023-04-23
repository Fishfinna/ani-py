#!/usr/bin/env python3

# general imports
import subprocess
import platform
import os
import curses
import requests
import json

# global vars
mode = ""


def install_mpv(screen):
    """
    should install mvp onto your computer and add the executable to the path
    This one makes me the most nervous to code lmao
    """
    try:
        # Check if MPV is already installed
        subprocess.check_call(['mpv', '--version'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        # If MPV is not installed, install it
        print('Installing MPV...')
        if sys.platform == 'win32':
            # Windows
            mpv_url = 'https://sourceforge.net/projects/mpv-player-windows/files/64bit-v3/mpv-x86_64-v3-20230423-git-c7a8e71.7z'
            subprocess.run(['powershell', '-Command',
                        f'Invoke-WebRequest -Uri {mpv_url} -OutFile mpv.7z'])
            subprocess.run(['7z', 'x', '-y', 'mpv.7z', '-oc:\\mpv'])
            os.remove('mpv.7z')
        elif sys.platform == 'darwin':
            # macOS
            subprocess.run(['brew', 'install', 'mpv'])
        elif sys.platform.startswith('linux'):
            # Linux
            if 'debian' in platform.dist():
                subprocess.run(['sudo', 'apt-get', 'update'])
                subprocess.run(['sudo', 'apt-get', 'install', 'mpv'])
            elif 'fedora' in platform.dist():
                subprocess.run(['sudo', 'dnf', 'install', 'mpv'])
            elif 'arch' in platform.dist():
                subprocess.run(['sudo', 'pacman', '-S', 'mpv'])

        


def select(screen, options: list = [], title: str = ""):

    # Set up screen
    screen.clear()
    screen.addstr(
        "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n",
        curses.color_pair(2),
    )
    screen.addstr(f"{title}:\n\n", curses.color_pair(1))

    current_option = 0
    page = 0
    page_size = min(15, len(options))
    max_page = (len(options) - 1) // page_size

    while True:
        # Show options for current page
        page_start = page * page_size
        page_options = options[page_start: page_start + page_size]

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
            if current_option < page_size - 1 and current_option < len(page_options) - 1:
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
        elif key == ord('c') and "C to change Search" in title:
            screen.clear()
            search(screen)
            return (None, None)
        elif key == ord('l') and "L to change language" in title:
            screen.clear()
            main(screen)
            return (None, None)

        # Update screen
        screen.clear()
        screen.addstr(
            "Use arrow-keys to navigate. Return to submit. Ctl + C to exit. \n",
            curses.color_pair(2),
        )
        screen.addstr(f"{title}:\n\n", curses.color_pair(1))

    selected_index = page_start + current_option
    return (selected_index, options[selected_index])



def get_anime(prompt):
    url = 'https://api.allanime.to/allanimeapi/?query=query($search:SearchInput$limit:Int$page:Int$translationType:VaildTranslationTypeEnumType$countryOrigin:VaildCountryOriginEnumType){shows(search:$search%20limit:$limit%20page:$page%20translationType:$translationType%20countryOrigin:$countryOrigin){edges{_id%20name%20availableEpisodes%20__typename}}}&variables={"search":{"allowAdult":false,"allowUnknown":false,"query":"' + prompt + '"},"limit":40,"page":1,"translationType":"' + mode + '","countryOrigin":"ALL"}'
    response = requests.get(url)
    response.raise_for_status()

    return json.loads(response.text)['data']['shows']['edges']


def get_episode_url(episode) -> str:
    episode_embed_gql = "query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) { episode(showId: $showId translationType: $translationType episodeString: $episodeString) { episodeString sourceUrls }}"
    return "test"

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
                "No results found. Please try again with a different prompt.\n", curses.color_pair(3))
            continue
        try:
            choice = select(screen, [str(i['name']) for i in anime_list],
                            f"C to change Search, L to change language (currently {mode})")
        except:
            screen.addstr(
                "Your search failed. Please try again with a different prompt.\n", curses.color_pair(3))
            continue
        if choice:
            episode_number = select(screen, [str(i+1) for i in range(anime_list[choice[0]]['availableEpisodes'][mode])],
                                    f"C to change Search, L to change language (currently {mode})\nSelect your episode of {anime_list[choice[0]]['name']}")[0] + 1
            if episode_number:
                url='https://api.allanime.to/allanimeapi?query=query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {    episode(        showId: $showId        translationType: $translationType        episodeString: $episodeString    ) {        episodeString sourceUrls    }}&variables={"showId":"' + anime_list[episode_number]["_id"] + '","translationType":"' + mode + '","episodeString": "' + str(episode_number) + '"}'
                # try:
                response = requests.get(url)
                # except:
                #     screen.addstr(
                #         "There was an error finding your episode! Please try again with a different prompt. If this error continues please insure you have the latest copy of anipy as you may be using an out of date API.\n", curses.color_pair(3))
                #     continue
                episode_url = json.loads(response.text)['data']["episode"]["sourceUrls"][0]["sourceUrl"]
                print(episode_url)
            else:
                screen.addstr(
                    "There are no episodes for your selected show :(\n", curses.color_pair(3))
                continue          
        exit()

def play(screen, episode_url):
    # Create an instance of the player
    player = mpv.MPV()
    player.play('video.mp4')

    # Control playback with keyboard input
    while True:
        key = screen.getch()
        if key == ord('p'):
            player.pause = True
        elif key == ord('r'):
            player.pause = False
        elif key == ord('s'):
            player.stop()
        elif key == ord('q'):
            player.terminate()
            break

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


    # Set up mpv
    install_mpv(screen)

    try:
        # get the mode
        global mode 
        mode = select(screen, ["Sub (japanese)", "Dub (english)"], "Dub or Sub?")
        mode = "sub" if mode[0] == 0 else "dub"
        screen.clear()

        # search for the anime
        episode = search(screen)

        # get the episode url
        # get_episode_url(episode)

        # play the episode
        # play()
        

    except KeyboardInterrupt:
        print("anipy escaped.")
        exit()


if __name__ == "__main__":
    curses.wrapper(main)