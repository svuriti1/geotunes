from flask import Flask, redirect, request, session, jsonify
import requests
import base64

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Choose a secret key for session management

# Spotify OAuth settings
# Should put the client_id and secret in a .env file when we're done 
client_id = 'f7c9aceb42184fa8bfd9cd928ffcd84e'
client_secret = 'a4b3f8f3d1ab4a098f532917bde15f28'
redirect_uri = 'http://127.0.0.1:5000/callback'
scope = ['user-top-read', 'user-read-private', 'user-read-email']

# Spotify URLs
oauth_url = 'https://accounts.spotify.com/authorize'
token_url = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1'


@app.route('/')
def home():
    auth_url = f"{oauth_url}?response_type=code&client_id={client_id}&scope={scope[0]}&redirect_uri={redirect_uri}"
    return f'<h2><a href="{auth_url}">Sign in with Spotify</a></h2>'


@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'scopes': scope
    }
    client_creds_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Authorization': f"Basic {client_creds_b64}",
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    token_response = requests.post(token_url, data=token_data, headers=headers, verify=True)
    token_response_data = token_response.json()
    access_token = token_response_data.get('access_token')

    session['access_token'] = access_token  # Store the token in the session
    return redirect('/top-items')

# Function to get song IDs by name for scraped songs so that we can get their audio featues after
# Once we read the songs from the scraped songs, we can call this function
# Query needs to be structured like this: 'track:"Nice For What" artist:Drake'
def track_search(query, access_token):
    base_url = "https://api.spotify.com/v1/search"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': query,
        'type': 'track',
        'limit': 1,
    }
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        tracks = response.json().get('tracks', {}).get('items', [])
        if tracks:
            return tracks[0]['id']
        else:
            return "No track found."
    else:
        return f"Error: {response.status_code}"

# Get the speicifc audio features for each of the tracks
def track_audio_features(track_ids, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    track_ids_str = ','.join(track_ids)
    response = requests.get(f'{base_url}/audio-features?ids={track_ids_str}', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch audio features', 'status_code': response.status_code}

@app.route('/top-items')
def top_items():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect('/')

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{base_url}/me/top/tracks", headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Could not fetch top tracks', 'status_code': response.status_code})

    # Get Track IDs for each of users top songs
    track_ids = [track['id'] for track in response.json().get('items', [])]

    # Now get audio features for these tracks
    audio_features = track_audio_features(track_ids, access_token)
    
    return jsonify(audio_features)


if __name__ == '__main__':
    app.run(debug=True)
