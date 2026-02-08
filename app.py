import streamlit as st
import pickle
import requests
from pathlib import Path


# =====================================================
# CONFIG
# =====================================================
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"   # replace if expired


st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

st.title("🎬 Movie Recommender System")
st.write("Get similar movies instantly!")


# =====================================================
# LOAD DATA (cached → loads only once)
# =====================================================
@st.cache_data
def load_data():

    if not Path("movie_list.pkl").exists():
        st.error("❌ movie_list.pkl not found")
        st.stop()

    if not Path("similarity.pkl").exists():
        st.error("❌ similarity.pkl not found")
        st.stop()

    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))

    return movies, similarity


# =====================================================
# FETCH POSTER (safe + fast)
# =====================================================
@st.cache_data
def fetch_poster(movie_id):

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

        response = requests.get(url, timeout=4)

        if response.status_code != 200:
            return "https://via.placeholder.com/300x450?text=No+Poster"

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"

    except:
        return "https://via.placeholder.com/300x450?text=Error"


# =====================================================
# RECOMMENDATION LOGIC
# =====================================================
def recommend(movie, movies, similarity):

    index = movies[movies["title"] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    names = []
    posters = []

    for i in distances:
        movie_id = movies.iloc[i[0]].movie_id
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters


# =====================================================
# MAIN APP
# =====================================================
with st.spinner("Loading data..."):
    movies, similarity = load_data()


selected_movie = st.selectbox(
    "Select a movie",
    movies["title"].values
)


if st.button("Recommend 🎯"):

    with st.spinner("Finding best movies for you..."):
        names, posters = recommend(selected_movie, movies, similarity)

    cols = st.columns(5)

    for col, name, poster in zip(cols, names, posters):
        with col:
            st.image(poster, use_container_width=True)
            st.caption(name)
