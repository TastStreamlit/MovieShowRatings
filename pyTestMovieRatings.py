import streamlit as st
import requests

# Access the API key from Streamlit secrets
api_key = st.secrets["api_key"]

fu = 0
#mediatype = 'any' #movie / show / any





movie_data = {
    "search":[
        {"title":"Jaws","year":1975,"score":86,"score_average":86,"type":"movie","ids":{"imdbid":"tt0073195","tmdbid":578,"traktid":457,"malid":"null","tvdbid":"null"}},
        {"title":"Jaws 2","year":1978,"score":54,"score_average":54,"type":"movie","ids":{"imdbid":"tt0077766","tmdbid":579,"traktid":458,"malid":"null","tvdbid":"null"}}
        ],"total":65}

ratings_data = {"provider_id":"tmdb","provider_rating":"tomatoes","mediatype":"movie","ratings":[{"id":578,"rating":97}]}

def check_api_requests():
    # Send GET request
    response = requests.get(f'https://api.mdblist.com/user?apikey={api_key}')

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response into a dictionary
        data = response.json()  # This converts the response to a dictionary

        # Convert values to integers before calculation
        api_requests = int(data["api_requests"])
        api_requests_count = int(data["api_requests_count"])

        # Calculate remaining API calls
        remaining_api_calls = api_requests - api_requests_count

        #remaining_api = int(response.text[1]) - int(response.text[0])
        st.write(f"{remaining_api_calls}/{api_requests} remaining")
        #st.write("API requests remaining: " {remaining_api})
    else:
        st.error(f"Error: {response.status_code}")

mediatype = "Movies"
ico=":material/tv_gen:"
fu = 0
def changeType():
    global mediatype, ico, fu
    st.write("changeType function called!")
    st.write(f"Value of fu before: {fu}")
    if fu == 0:
        mediatype = 'movie'
        ico = ":material/tv_gen:"
        fu = 1
    elif fu == 1:
        mediatype = 'show'
        ico = ":material/tv:"
        fu = 0
    st.write(f"Value of fu after: {fu}")
    st.write(f"Mediatype inside changeType: {mediatype}")
    st.write(f"Icon inside changeType: {ico}")


with st.sidebar:
    type = st.segmented_control("Type", ["Movies", "Shows"], default="Movies", label_visibility="hidden")

    # Update mediatype and ico based on the selected value
    if type == "Movies":
        mediatype = "movie"
        #ico = ":material/tv_gen:"
    elif type == "Shows":
        mediatype = "show"
        #ico = ":material/tv:"

    sort = st.toggle("Sort by rating")

    st.divider()
    if st.button("Check API requests"):
        check_api_requests()

# Function to search movie
def search_movie(title, api_key):
    #url = f"https://api.mdblist.com/search/movie?query={title}&apikey={api_key}"
    url = f"https://api.mdblist.com/search/{mediatype}?query={title}&sort_by_score={sort}&apikey={api_key}"

    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to get movie ratings
def get_ratings(id, return_rating_type, api_key):
    #mediatype_rating = 'movie' #show
    #return_rating = 'tomatoes' #trakt , imdb , tmdb , letterboxd , tomatoes , audience , metacritic , rogerebert , mal , score , score_average
    url = f"https://api.mdblist.com/rating/{mediatype}/{return_rating_type}?apikey={api_key}"

    if return_rating_type == "tomatoes" or return_rating_type == "audience":
        return_rating_type = "tmdb"

    # Data to send in the request body
    body = {
        'ids': [id],
        'provider': return_rating_type
    }

    try:
        response = requests.post(url, json=body)
        #st.write(response)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    
# Function to apply color based on rating
def color_rating(rating):
    if rating is None:
        return "color: gray"  # Or any default color for missing ratings
    rating = int(rating)  # Ensure rating is an integer
    r = int(255 * (100 - rating) / 100)
    g = int(255 * rating / 100)
    b = 0
    return f"color: rgb({r}, {g}, {b})"

# Streamlit app
def app():
    #mcol1, mcol2 = st.columns([3, 1])
    #with mcol1:
    st.title(f"Ratings App")

    
    col1, col2 = st.columns([3, 1])
    with col1:
        movie_title = st.text_input("Enter title", "Jaws", icon=ico, label_visibility="collapsed")
    
    # Load movie data from session state if it exists
    if 'movie_data' not in st.session_state:
        st.session_state['movie_data'] = None
    
    # Search button
    with col2:
        #if mediatype == 'movie': type = "Movie"
        #if mediatype == 'show': type = "Show"
        if st.button(f"Search {type}", use_container_width=True):
            if movie_title and api_key:
                with st.spinner("Searching..."):
                    movie_data = search_movie(movie_title, api_key)

                    if movie_data:
                        st.session_state['movie_data'] = movie_data
                    else:
                        st.session_state['movie_data'] = None

    # Display search results (if available)
    if st.session_state['movie_data']:
        movie_data = st.session_state['movie_data']
        
        if movie_data.get("search"):
            #st.write(f"Found {movie_data['total']} results")
            #st.divider()

            
            
            i = 0
            amount = st.empty()
            amount.markdown(i)
            for movie in movie_data['search']:
                
                if int(movie['score']) > 0:
                    amount.markdown(f"Found {i+1}/{movie_data['total']} results with available ratings")
                    #button_label = f"{movie['title']} ({movie['year']}): {movie['score']}%, Average: {movie['score_average']}%"

                    button_label = f"{movie['title']} ({movie['year']})"

                    with st.container():
                        colM1, colM2, colM3 = st.columns([0.5, 0.25, 0.25])
                        with colM1:
                            if st.button(button_label):
                                imdbid = movie_data["search"][i]["ids"]["imdbid"]
                                if imdbid:
                                    with st.spinner("Searching..."):
                                        ratings_imdb = get_ratings(imdbid, "imdb", api_key)   #trakt , imdb , tmdb , letterboxd , tomatoes , audience , metacritic , rogerebert , mal , score , score_average
                                        if ratings_imdb and ratings_imdb["ratings"]:
                                            imdb_rating = ratings_imdb["ratings"][0]["rating"]
                                            imdb_rating = int(imdb_rating * 10)
                                            st.markdown(f'<p style="{color_rating(imdb_rating)}">IMDB Ratings: {imdb_rating}%</p>', unsafe_allow_html=True)
                                        else:
                                            st.write("IMDB Ratings: N/A")
                                tmdbid = movie_data["search"][i]["ids"]["tmdbid"]
                                if tmdbid:
                                    with st.spinner("Searching..."):
                                        ratings_tmdb = get_ratings(tmdbid, "tomatoes", api_key)
                                        if ratings_tmdb and ratings_tmdb["ratings"]:
                                            tomatoes_rating = ratings_tmdb["ratings"][0]["rating"]
                                            st.markdown(f'<p style="{color_rating(tomatoes_rating)}">Tomatoes Ratings: {tomatoes_rating}%</p>', unsafe_allow_html=True)
                                        else:
                                            st.write("Tomatoes Ratings: N/A")
                                    with st.spinner("Searching..."):
                                        ratings_tmdb2 = get_ratings(tmdbid, "audience", api_key)
                                        if ratings_tmdb2 and ratings_tmdb2["ratings"]:
                                            audience_rating = ratings_tmdb2["ratings"][0]["rating"]
                                            st.markdown(f'<p style="{color_rating(audience_rating)}">Audience Ratings: {audience_rating}%</p>', unsafe_allow_html=True)
                                        else:
                                            st.write("Audience Ratings: N/A")
                                else:
                                    st.error("No id found")

                        with colM2:
                            #rating_label = f"{movie['score']}%, Average: {movie['score_average']}%"
                        
                            score = movie['score']
                            st.markdown(f'<p style="{color_rating(score)}">Ratings: {score}%</p>', unsafe_allow_html=True)

                        with colM3:
                            score_avg = movie['score_average']
                            st.markdown(f'<p style="{color_rating(score_avg)}">Average: {score_avg}%</p>', unsafe_allow_html=True)


                i = i+1
                #amount.markdown = i
        else:
            st.warning("No results found.")
    else:
        st.warning(f"Please search for {type}")

if __name__ == "__main__":
    app()
