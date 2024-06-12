import json
import requests
import time


def main():
    user = initialization()
    print(user)


class User:
    def __init__(self, username, time_elapsed, is_online, last_blitz_rating) -> None:
        self.username = username
        self.time_elapsed = time_elapsed
        self.is_online = is_online
        self.last_blitz_rating = last_blitz_rating
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
    if user_object is not None:
        username, time_elapsed, is_online, last_blitz_rating = user_object

        return User(username, time_elapsed,
                    is_online, last_blitz_rating)

    else:
        print('user not in local db')
        user_object = fetch_server_user_stats(chesscom_username)

        user_object['time_elapsed'] = 0
        user_object['is_online'] = False
        user_object['last_blitz_rating'] = 3000

        update_stats(chesscom_username, user_object)


def fetch_local_user_stats(username):

    with open("db.json", "r") as infile:
        loaded_data = json.load(infile)
        if username in loaded_data['usernames']:
            print('chesscom username in local database')

            user_data = loaded_data['usernames']

            time_elapsed = user_data['time_elapsed']
            is_online = user_data['is_online']
            last_blitz_rating = user_data['last_blitz_rating']

            return username, time_elapsed, is_online, last_blitz_rating
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
    try:
        pass
    except:
        print('could not fetch is_online information')
    pass


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