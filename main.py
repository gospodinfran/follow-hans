import json
import requests
import time
from bs4 import BeautifulSoup as bs


def main():
    user = initialization()
    update_blitz_rating(user.username)

    check_online_status(user.username)


class User:
    def __init__(self, player_id, id, url, username, followers, country, last_online, joined, status, is_streamer, verified, streaming_platforms, time_elapsed, is_online, last_blitz_rating, avatar=None, location=None, league=None, name=None, title=None, twitch_url=None):
        self.avatar = avatar
        self.player_id = player_id
        self.id = id
        self.url = url
        self.name = name
        self.username = username
        self.followers = followers
        self.country = country
        self.location = location
        self.last_online = last_online
        self.joined = joined
        self.status = status
        self.is_streamer = is_streamer
        self.verified = verified
        self.league = league
        self.streaming_platforms = streaming_platforms
        self.time_elapsed = time_elapsed
        self.is_online = is_online
        self.last_blitz_rating = last_blitz_rating
        self.title = title
        self.twitch_url = twitch_url
        print('initialized user class instance')

    def __str__(self) -> str:
        return f'username: {self.username}\ntime_elapsed: {self.time_elapsed}\nis_online: {self.is_online}\nlast_blitz_rating: {self.last_blitz_rating}'


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.chess.com',
    'Origin': 'https://www.chess.com'
}


def initialization():
    print('started running')

    chesscom_username = input(
        "Which user to follow: ").strip().lower()

    user_object = fetch_local_user_stats(chesscom_username)
    if user_object is None:
        print('user not in local db')
        user_object = fetch_server_user_stats(chesscom_username)

        user_object['id'] = user_object['@id']
        user_object.pop('@id')

        user_object['time_elapsed'] = 0
        user_object['is_online'] = False
        user_object['last_blitz_rating'] = None

        update_stats(chesscom_username, user_object)

    update_blitz_rating(chesscom_username, user_object)

    return User(**user_object)


def fetch_local_user_stats(username):

    with open("db.json", "r") as infile:
        loaded_data = json.load(infile)
        if username in loaded_data['usernames']:

            user_data = loaded_data['usernames'][username]

            return user_data
        else:
            print('chesscom username not in local database')

            return None


def fetch_server_user_stats(username):
    profile_url = f'https://api.chess.com/pub/player/{username}'
    try:
        res = requests.get(profile_url, headers=headers)
        response = res.json()

        return response
    except:
        print('failed to fetch serverside user stats.')


def update_stats(username, user_object):
    with open("db.json", "r") as infile:
        db_cpy = json.load(infile)

    db_cpy['usernames'][username] = user_object

    with open("db.json", "w") as outfile:
        json.dump(db_cpy, outfile, indent=1)


def check_if_online(username):
    # endpoint does not seem to work any more
    try:
        pass
    except:
        print('could not fetch is_online information')


def update_blitz_rating(username, user_object=None):
    stats_url = f'https://api.chess.com/pub/player/{username}/stats'
    res = requests.get(stats_url, headers=headers)
    response = res.json()
    blitz_rating = response['chess_blitz']['last']['rating']

    user_obj = user_object if user_object else fetch_local_user_stats(username)
    user_obj['last_blitz_rating'] = blitz_rating

    update_stats(username, user_obj)


def track_if_in_game():
    pass


def check_online_status(username):
    res = requests.get(
        f'https://www.chess.com/member/{username}', headers=headers)

    if res.status_code == 200:
        soup = bs(res.content, 'html.parser')
        results = soup.find(id='view-profile')
        print(results.prettify())

        status_text = results.find(
            'div', string='profile-card-info-item-value')

        if status_text:
            print(status_text.text)
    else:
        print('failed to reach chesscom')


def main_loop():
    while True:
        refresh_every = 5
        chesscom_username = 'mirko'
        try:
            all_games_url = f'https://api.chess.com/pub/player/{chesscom_username}/games/archives'

            months = requests.get(all_games_url, headers=headers)
            months.raise_for_status()

            response = months.json()
            archives = response['archives']
            if archives:
                current_month = archives[-1]

                all_games_res = requests.get(current_month, headers=headers)
                all_games_res.raise_for_status()

                games = all_games_res.json()['games']
                print(f'type of games is {type(all_games_res)}')
                games = sorted(games, key=lambda x: x['end_time'])
                print(f'first game: {games[0]}\nlast game: {games[-1]}')

            else:
                print('Cannot find games archives.')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except requests.Exception as err:
            print(f'Other error occurred: {err}')

        print(time_elapsed)
        time.sleep(refresh_every)
        time_elapsed += refresh_every


if __name__ == "__main__":
    main()
