from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import re
import os
from dotenv import load_dotenv, find_dotenv

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

album_url = "https://open.spotify.com/album/0xpb5NOipAPreVFfJrJ9K7"
album_id = re.search(r'album/([a-zA-Z0-9]+)', album_url).group(1)

album = sp.album(album_id)
# print(album)
album_name = album['name']
tracks = album['tracks']['items']

track_list = []
for track in tracks:
    track_data = {
        'Track Name': track['name'],
        'Artist': track['artists'][0]['name'],
        'Album': album_name,
        'Popularity': track.get('popularity', 'Not Available'), 
        'Duration (minutes)': track['duration_ms'] / 60000
    }
    track_list.append(track_data)

# Store track data in a DataFrame
df = pd.DataFrame(track_list)
print(df)



df.to_csv('spotify_track_data.csv',index = False)

df = pd.read_csv('spotify_track_data.csv')

# Ensure data types are correct, especially if dealing with numerical data that may have been interpreted as strings
df['Popularity'] = pd.to_numeric(df['Popularity'], errors='coerce')
df['Duration (minutes)'] = pd.to_numeric(df['Duration (minutes)'], errors='coerce')

# Sort the DataFrame by popularity to display the most popular tracks
sorted_df = df.sort_values(by='Popularity', ascending=False)

# Plotting
df_sorted = df.sort_values(by='Duration (minutes)', ascending=False)

# Plot Bar Chart
plt.figure(figsize=(12, 6))
plt.barh(df_sorted['Track Name'], df_sorted['Duration (minutes)'], color='purple', edgecolor='black')

# Labels and Title
plt.xlabel('Duration (minutes)')
plt.ylabel('Track Name')
plt.title('Track Durations')
plt.gca().invert_yaxis()  # Invert y-axis to show the longest track at the top

# Show plot
plt.show()