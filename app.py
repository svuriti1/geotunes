from flask import Flask, redirect, request, session
import requests
import base64

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Choose a secret key for session management

# Spotify OAuth settings
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
    }
    client_creds_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Authorization': f"Basic {client_creds_b64}",
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    token_response = requests.post(token_url, data=token_data, headers=headers)
    token_response_data = token_response.json()
    access_token = token_response_data.get('access_token')

    session['access_token'] = access_token  # Store the token in the session
    return redirect('/top-items')


@app.route('/top-items')
def top_items():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect('/')

    headers = {
        'Authorization': f"Bearer {access_token}",
    }
    response = requests.get(f"{base_url}/me/top/artists", headers=headers)
    if response.status_code != 200:
        return 'Could not fetch', response.status_code

    current_track = response.json()
    return current_track


if __name__ == '__main__':
    app.run(debug=True)
