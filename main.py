from flask import Flask
import threading
import webbrowser
import os
from spotify_api_requests import *
import signal
from constants import *

app = Flask(__name__)
server_thread = None
request_stop = False


def save_playlist():
    print('Saving playlist')
    with open(SAVED_PLAYLIST, 'w') as f:
        for track in PLAYED_TRACKS:
            f.write(f'{track},{PLAYED_TRACKS[track]}\n')


def open_playlist():
    if os.path.exists(SAVED_PLAYLIST):
        print('Reading playlist')
        with open(SAVED_PLAYLIST, 'r') as f:
            for line in f.readlines():
                values = line.rstrip('\n').split(',')
                if len(values) == 2:
                    PLAYED_TRACKS[values[0]] = values[1]
    else:
        print('No playlist to open')


def sigint_handler(signal, frame):
    global request_stop
    print('Requested to shutdown')
    save_playlist()
    request_stop = True
    # Here you can add any code you want to execute when SIGINT is received
    # For example, you can clean up resources or exit the program gracefully
    try:
        requests.post('http://localhost:5000/shutdown', timeout=2)
    except:
        pass


@app.route('/')
def callback():
    get_authorisation_code()
    with CONDITION:
        CONDITION.notify_all()
    return 'Access token obtained'


@app.post('/shutdown')
def shutdown():
    exit(1)


if __name__ == '__main__':
    server_thread = threading.Thread(target=app.run)
    server_thread.start()
    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope={SCOPES}&redirect_uri={SPOTIFY_REDIRECT_URI}&state={STATE}'
    webbrowser.open(auth_url)
    with CONDITION:
        CONDITION.wait()
    signal.signal(signal.SIGINT, sigint_handler)
    open_playlist()
    while not request_stop:
        get_current_playing_track()
        time.sleep(0.1)
    server_thread.join()
