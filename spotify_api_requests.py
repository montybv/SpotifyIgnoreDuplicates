import time

from flask import request
import base64
import secrets
import requests
import json
import threading
from constants import *

STATE = secrets.token_hex(16)
ACCESS_TOKEN = None
USER_ID = None
CONDITION = threading.Condition()
CURRENT_TRACK = None
TRACK_SAVED = False
PLAYED_TRACKS = dict()


def request_get_api(endpoint):
    # Set the authorization header
    headers = {
        'Authorization': 'Bearer {token}'.format(token=ACCESS_TOKEN)
    }

    # Send a GET request to the API endpoint
    response = requests.get(endpoint, headers=headers)
    return response


def request_post_api(endpoint):
    # Set the authorization header
    headers = {
        'Authorization': 'Bearer {token}'.format(token=ACCESS_TOKEN)
    }

    # Send a GET request to the API endpoint
    response = requests.post(endpoint, headers=headers)
    return response


def get_authorisation_code():
    global ACCESS_TOKEN
    authorization_code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode()).decode()
    headers = {'Authorization': f'Basic {auth_header}'}
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': SCOPES
    }
    response = requests.post(token_url, headers=headers, data=data)
    ACCESS_TOKEN = response.json()['access_token']


def skip_to_next():
    endpoint = "https://api.spotify.com/v1/me/player/next"
    response = request_post_api(endpoint)
    # Check if the response was successful
    if response.status_code == 200 or response.status_code == 204:
        # Convert the response to a JSON object
        print(f'Playing next song')
        time.sleep(1)
    else:
        # Print an error message if the response was not successful
        print(f"Error: {response.status_code}\n{response.text}")


def get_current_playing_track():
    global PLAYED_TRACKS
    global CURRENT_TRACK
    global TRACK_SAVED
    # Set the API endpoint
    endpoint = "https://api.spotify.com/v1/me/player/currently-playing"

    response = request_get_api(endpoint)

    # Check if the response was successful
    if response.status_code == 200:
        # Convert the response to a JSON object
        data = json.loads(response.text)
        # Print the name of the currently playing track
        track_id = data['item']['id']
        artist_name = data['item']['artists'][0]['name']
        track_name = data['item']['name']
        progress_ms = data['progress_ms']

        if not CURRENT_TRACK or track_id != CURRENT_TRACK:
            TRACK_SAVED = False
            if track_id in PLAYED_TRACKS and progress_ms < NEXT_TRACK_AFTER_X_MS:
                print(f'Track "{artist_name} - {track_name}" already played. Next track triggered')
                skip_to_next()
            else:
                print(f'Playing "{artist_name} - {track_name}" ({track_id})')
                CURRENT_TRACK = track_id
        else:
            if not TRACK_SAVED and progress_ms > NEXT_TRACK_AFTER_X_MS:
                PLAYED_TRACKS[track_id] = f'{artist_name} - {track_name}'
                TRACK_SAVED = True

    else:
        # Print an error message if the response was not successful
        print(f"Error: {response.status_code}\n{response.text}")


def get_user_profile():
    global USER_ID
    endpoint = "https://api.spotify.com/v1/me"
    response = request_get_api(endpoint)
    # Check if the response was successful
    if response.status_code == 200:
        # Convert the response to a JSON object
        data = json.loads(response.text)
        USER_ID = data['id']
    else:
        # Print an error message if the response was not successful
        print(f"Error: {response.status_code}\n{response.text}")
