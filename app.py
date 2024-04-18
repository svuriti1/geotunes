from flask import Flask, redirect, request, session, jsonify, render_template
import requests
import base64
import ast
import pandas as pd 
import numpy as np
from glob import glob
import os 


app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  

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
    if 'access_token' in session:
        return redirect('/map')
    else:
        auth_url = f"{oauth_url}?response_type=code&client_id={client_id}&scope={scope[0]}&redirect_uri={redirect_uri}"
        return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    client_creds_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Authorization': f"Basic {client_creds_b64}",
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_response = requests.post(token_url, data=token_data, headers=headers)
    token_response_data = token_response.json()
    access_token = token_response_data.get('access_token')
    session['access_token'] = access_token
    return redirect('/map')

@app.route('/map')
def map_page():
    if 'access_token' not in session:
        return redirect('/')
    return render_template('map.html') 

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

# Get the specific audio features for each of the tracks
def track_audio_features(track_ids, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    track_ids_str = ','.join(track_ids)
    response = requests.get(f'{base_url}/audio-features?ids={track_ids_str}', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch audio features', 'status_code': response.status_code}
    
def get_similarities(user_audio_features, country):
    directory_path = 'country_audio_features'
    search_pattern = os.path.join(directory_path, f"*{country}*.csv")
    file_list = glob(search_pattern)
    
    csv_file = file_list[0]

    country_audio_features = pd.read_csv(csv_file)
 
    country_audio_features = country_audio_features.dropna()
    
    # Creating matrices for the user songs and country songs
    user_matrix = np.zeros((len(user_audio_features['audio_features']), 4))
    country_matrix = np.zeros((len(country_audio_features['audio_features']), 4))
    for i, track in enumerate(user_audio_features['audio_features']):
        user_matrix[i] = np.array([
            track['danceability'], track['energy'], track['valence'], track['tempo']
        ])
    for i, track in enumerate(country_audio_features['audio_features']):
        track = ast.literal_eval(track)
        country_matrix[i] = np.array([
            track['danceability'], track['energy'], track['valence'], track['tempo']
        ])
    
    # Standardizing the matrices
    user_matrix_mean = user_matrix.mean(axis=0)
    user_matrix_std = user_matrix.std(axis=0)
    user_matrix = (user_matrix - user_matrix_mean) / user_matrix_std
    country_matrix_mean = country_matrix.mean(axis=0)
    country_matrix_std = country_matrix.std(axis=0)
    country_matrix = (country_matrix - country_matrix_mean) / country_matrix_std

    # Normalizing the matrices
    norm_user = np.linalg.norm(user_matrix, axis=1, keepdims=True)
    norm_country = np.linalg.norm(country_matrix, axis=1, keepdims=True)
    user_matrix = user_matrix / norm_user
    country_matrix = country_matrix / norm_country

    # Multiplying the matrices and grabbing the user, country song pair with the highest similarity
    similarity_scores = np.dot(user_matrix, country_matrix.T)
    best_pair_indices = np.unravel_index(np.argmax(similarity_scores), similarity_scores.shape)
    best_pair = {
        'country_song': ast.literal_eval(country_audio_features.iloc[best_pair_indices[1]]['audio_features'])
    }

    return best_pair, user_matrix_mean

@app.route('/top-items/<country>')
def top_items(country):
    access_token = session.get('access_token')
    if access_token is None:
        return redirect('/')

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{base_url}/me/top/tracks", headers=headers)
    if response.status_code != 200:
        return jsonify({'error': 'Could not fetch top tracks', 'status_code': response.status_code})

    # Get Track IDs for each of user's top songs
    track_ids = [track['id'] for track in response.json().get('items', [])]

    # Get audio features for these tracks
    user_audio_features = track_audio_features(track_ids, access_token)

    # Get similar tracks based on country user clicked on
    similar_tracks, mean_audio_features = get_similarities(user_audio_features, country.lower()) 

    # Getting Recommendations
    recommendations = get_recommendations(
        similar_tracks['country_song']['id'],
        mean_audio_features[3],  # tempo
        mean_audio_features[1],  # energy
        mean_audio_features[0],  # danceability
        mean_audio_features[2]   # valence
    )

    songs = {}
    for rec in recommendations['tracks']:
        song_link = rec['external_urls']['spotify'] if 'external_urls' in rec else None
        album_image_url = rec['album']['images'][0]['url'] if rec['album']['images'] else None

        songs[rec['id']] = {
            'name': rec['name'],
            'artists': [artist['name'] for artist in rec['artists']],
            'song_link': song_link,
            'album_image': album_image_url
        }
    
    return jsonify(songs)


def country_charts():
    directory_path = "bilboard_charts"
    output_directory = "country_audio_features"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)  

    files = os.listdir(directory_path)

    for csv_file in files:
        df = pd.read_csv(csv_file)
        access_token = session.get('access_token')
        if access_token is None:
            return redirect('/')

        track_ids = []
        for _, row in df.iterrows():
            song_name = row['Title']
            artist_name = row['Artist']
            query = f'track:"{song_name}" artist:{artist_name}'
            track_id = track_search(query, access_token)
            if track_id:
                track_ids.append(track_id)

        audio_features = track_audio_features(track_ids, access_token)

        if audio_features:
            new_df = pd.DataFrame(audio_features)
            country_name = os.path.basename(csv_file).split('-')[0]
            new_df.to_csv(f'{output_directory}/{country_name}_audio_features.csv', index=False)

    return jsonify({'message': 'Audio features collected for all countries.'})


def get_recommendations(seed_tracks, target_tempo, target_energy, target_danceability, target_valence):
    access_token = session.get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'seed_tracks': seed_tracks,
        'target_tempo': target_tempo,
        'target_energy': target_energy,
        'target_danceability': target_danceability,
        'target_valence': target_valence,
        'limit': 10  
    }

    response = requests.get(f"{base_url}/recommendations", headers=headers, params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Could not get recommendations', 'status_code': response.status_code})

    return response.json()

if __name__ == '__main__':
    app.run(debug=True)
