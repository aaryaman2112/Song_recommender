import streamlit as st
import google.generativeai as genai
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# ========== CONFIG ==========
st.set_page_config(page_title="🎵 Song Recommender", layout="centered")
st.title("🎵 Song Recommender")

# ========== API KEYS ==========
genai.configure(api_key="AIzaSyArF992mt3ed9ZAH1cKxv5JzwpQ3pu-Sf0")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="8b06976fab42432fa7486a5a866d01b9",
    client_secret="06a2761ac7a34c758a77856a6ec42531"
))

# ========== FUNCTIONS ==========

def get_recommendations(prompt):
    """Ask Gemini to suggest songs based on a mood or theme."""
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(
        f"You are a song recommendation engine. Suggest a list of 5 songs based on this: {prompt}. Give the song and artist names only."
    )
    return response.text

def search_spotify_songs(recommendation_text):
    """Use Spotify API to get links and cover art for each Gemini recommendation."""
    tracks = []
    lines = recommendation_text.strip().split("\n")

    for line in lines:
        # Try to extract song name and artist
        if " - " in line:
            name, artist = line.split(" - ", 1)
        elif " by " in line:
            name, artist = line.split(" by ", 1)
        else:
            continue  # skip if format is off

        query = f"{name} {artist}"
        result = sp.search(q=query, limit=1, type="track")
        items = result["tracks"]["items"]

        if items:
            track = items[0]
            song_url = track["external_urls"]["spotify"]
            cover_art = track["album"]["images"][0]["url"]
            tracks.append((name.strip(), artist.strip(), song_url, cover_art))
    return tracks

def get_song_description(song, artist):
    """Generate a 1-2 line description of the song using Gemini."""
    prompt = f"Give a short, 1-2 line description of the song '{song}' by {artist}. Don't include release year or chart info."
    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    return response.text.strip()

def spotify_button(url):
    """HTML button styled like Spotify."""
    return f"""
    <a href="{url}" target="_blank">
        <button style='padding: 6px 12px; background-color: #1DB954; 
                       color: white; border: none; border-radius: 5px;
                       font-size: 14px; cursor: pointer;'>
            🎧 Listen on Spotify
        </button>
    </a>
    """

# ========== MAIN UI ==========

user_input = st.text_input("What are you in the mood for? (e.g., chill sunset drive, late night coding, heartbreak, etc.)")

if user_input:
    with st.spinner("Getting personalized recommendations..."):
        rec_text = get_recommendations(user_input)
        spotify_tracks = search_spotify_songs(rec_text)

    if spotify_tracks:
        st.markdown("## 🔥 Your Recommended Tracks")
        for name, artist, url, cover in spotify_tracks:
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.image(cover, width=80)
                with col2:
                    st.markdown(f"### {name}")
                    st.markdown(f"**Artist**: {artist}")
                    description = get_song_description(name, artist)
                    st.markdown(f"*{description}*")
                    st.markdown(spotify_button(url), unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.error("Couldn’t find any tracks on Spotify for those recommendations. Try changing your prompt.")
