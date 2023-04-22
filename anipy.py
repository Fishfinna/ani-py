#!/usr/bin/env python3

import subprocess
import curses
import requests
import json
# import mpv
mode = ''


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
        elif key == ord('s') and "S to Search" in title:
            screen.clear()
            search(screen)
            return
        elif key == ord('l') and "L to change language" in title:
            screen.clear()
            main(screen)
            return

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
                            f"S to Search, L to change language (currently {mode})")[0]
        except:
            screen.addstr(
                "Your search failed. Please try again with a different prompt.\n", curses.color_pair(3))
            continue
        if choice:
            episode_number = select(screen, [str(i+1) for i in range(anime_list[choice]['availableEpisodes'][mode])],
                                    f"S to Search, L to change language(currently {mode})\nSelect your episode")[0] + 1  # compensate for range starting at 0
            print(episode_number)
        break

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


# def get_episode_url(id, mode, ep_no, quality):
#     # get the embed urls of the selected episode
#     episode_embed_gql = "query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) { episode(showId: $showId translationType: $translationType episodeString: $episodeString) { episodeString sourceUrls }}"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
#     data = {
#         "query": episode_embed_gql,
#         "variables": {
#             "showId": id,
#             "translationType": mode,
#             "episodeString": ep_no
#         }
#     }
#     url = f"https://api.allanime.xyz/allanimeapi?{urlencode(data)}"
#     resp = requests.get(url, headers=headers).json()
#     source_urls = resp["data"]["episode"]["sourceUrls"]

#     # generate links into sequential files
#     cache_dir = "/path/to/cache/dir"
#     provider = 1
#     for i in range(6):
#         subprocess.Popen(["generate_link", str(provider)],
#                          stdout=open(f"{cache_dir}/{i}", "w"))
#         provider = (provider % 6) + 1

#     # wait for all links to be generated
#     subprocess.check_call(["wait"])

#     # select the link with matching quality
#     links = []
#     for path in glob.glob(f"{cache_dir}/*"):
#         with open(path) as f:
#             link = f.read().strip()
#             link = link.replace("Mp4-", "")
#             links.append(link)
#     links.sort(key=lambda x: int(x.split(":")[-1]), reverse=True)
#     episode = select_quality(links, quality)
#     if episode is None:
#         raise Exception("Episode not released!")
#     return episode


# def select_quality(links, quality):
#     for link in links:
#         if quality in link:
#             return link
#     return None
