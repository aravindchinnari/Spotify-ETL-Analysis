from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import re
import mysql.connector
import os
from dotenv import load_dotenv, find_dotenv

# Initialize Spotipy with SpotifyClientCredentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

# MySQL Database Connection
db_config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE")
}
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Read album URLs from a text file
file_path = r"C:\Personal Projects\Spotify ETL Analysis\albumsList.txt"  # Ensure this file exists in the script directory

with open(file_path, "r") as file:
    album_urls = [line.strip() for line in file if line.strip()]  # Remove empty lines

# Loop through each album URL
for album_url in album_urls:
    album_match = re.search(r'album/([a-zA-Z0-9]+)', album_url)

    if album_match:
        album_id = album_match.group(1)
    else:
        print(f"Invalid album URL format: {album_url}")
        continue  # Skip invalid URLs and move to the next one

    try:
        # Fetch album details
        album = sp.album(album_id)
        album_name = album['name']

        # Fetch all tracks from the album
        tracks = sp.album_tracks(album_id)['items']

        for track in tracks:
            track_name = track['name']
            artist_name = track['artists'][0]['name']

            # Ensure popularity is an integer or set to 0 if missing
            popularity = track.get('popularity', 0)  

            duration_minutes = track['duration_ms'] / 60000  # Convert duration from milliseconds to minutes

            # Prepare and execute insert query
            insert_query = """
            INSERT INTO spotify_tracks (track_name, artist, album, popularity, duration_minutes)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                track_name,
                artist_name,
                album_name,
                popularity,
                duration_minutes
            ))

            print(f"Inserted Track: '{track_name}' by {artist_name} from '{album_name}' into the database.")

        connection.commit()  # Commit after processing each album

    except Exception as e:
        print(f"Error processing album {album_id}: {e}")
        continue  # Skip this album and move to the next one

# Close the database connection
cursor.close()
connection.close()

print("All tracks inserted successfully.")
