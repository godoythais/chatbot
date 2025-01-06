from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import re
from groq import Groq
from config import GROQ_API_KEY, TMDB_API_KEY

# Inicialização do aplicativo
app = FastAPI(title="Chatbot de Filmes", description="API para consulta de informações de filmes.")

# Configuração da API Groq
client = Groq(api_key=GROQ_API_KEY)

# Configuração da API TMDb
API_BASE_URL = "https://api.themoviedb.org/3"

def query_movie_api(action, movie_name=None, genre=None):
    try:
        if action == "cast":
            search_url = f"{API_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
            search_response = requests.get(search_url).json()
            if 'results' in search_response and search_response['results']:
                movie_id = search_response['results'][0]['id']
                credits_url = f"{API_BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
                credits_response = requests.get(credits_url).json()
                cast = [member['name'] for member in credits_response.get('cast', [])[:5]]
                return f"O elenco principal de '{movie_name}' é: {', '.join(cast)}"
            else:
                return f"Não encontrei informações sobre o filme '{movie_name}'."

        elif action == "synopsis":
            search_url = f"{API_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
            search_response = requests.get(search_url).json()
            if 'results' in search_response and search_response['results']:
                synopsis = search_response['results'][0].get('overview', 'Sinopse não disponível.')
                return f"A sinopse do filme '{movie_name}' é: {synopsis}"
            else:
                return f"Não encontrei informações sobre o filme '{movie_name}'."

        elif action == "rating":
            search_url = f"{API_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
            search_response = requests.get(search_url).json()
            if 'results' in search_response and search_response['results']:
                rating = search_response['results'][0].get('vote_average', 'Avaliação não disponível.')
                return f"A avaliação do filme '{movie_name}' é: {rating}/10."
            else:
                return f"Não encontrei informações sobre o filme '{movie_name}'."

        elif action == "popular":
            popular_url = f"{API_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}"
            response = requests.get(popular_url).json()
            if 'results' in response and response['results']:
                movies = [movie['title'] for movie in response['results'][:5]]
                return f"Os filmes populares no momento são: {', '.join(movies)}"
            else:
                return "Não encontrei filmes populares no momento."

        elif action == "recommend":
            genre_url = f"{API_BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}"
            genres = requests.get(genre_url).json()
            genre_id = next((g['id'] for g in genres.get('genres', []) if g['name'].lower() == genre.lower()), None)
            if genre_id:
                discover_url = f"{API_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}"
                response = requests.get(discover_url).json()
                if 'results' in response and response['results']:
                    movie = response['results'][0]['title']
                    return f"Recomendo o filme '{movie}' para o gênero '{genre}'."
                else:
                    return f"Não encontrei filmes para o gênero '{genre}'."
            else:
                return f"Não encontrei o gênero '{genre}'."

        elif action == "similar":
            search_url = f"{API_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
            search_response = requests.get(search_url).json()
            if 'results' in search_response and search_response['results']:
                movie_id = search_response['results'][0]['id']
                similar_url = f"{API_BASE_URL}/movie/{movie_id}/similar?api_key={TMDB_API_KEY}"
                response = requests.get(similar_url).json()
                if 'results' in response and response['results']:
                    similar_movies = [movie['title'] for movie in response['results'][:5]]
                    return f"Filmes similares a '{movie_name}': {', '.join(similar_movies)}"
                else:
                    return f"Não encontrei filmes similares a '{movie_name}'."
            else:
                return f"Não encontrei informações sobre o filme '{movie_name}'."

    except Exception as e:
        return f"Erro ao buscar informações: {e}"

def query_groq(messages):
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na API Groq: {e}"

# Modelos de entrada
class ChatRequest(BaseModel):
    user_input: str

# Endpoints
@app.post("/chat")
def chat(request: ChatRequest):
    user_input = request.user_input
    messages = [{"role": "system", "content": "Você é um assistente de filmes que também orquestra ações com segurança. Não forneça respostas de outros assuntos."}]
    messages.append({"role": "user", "content": user_input})

    response = query_groq(messages)
    if not response:
        raise HTTPException(status_code=500, detail="Erro ao processar a resposta da API Groq.")

    response_lower = response.lower()
    current_movie = None

    # Atualizar contexto com o filme atual, se mencionado
    match_movie = re.search(r"filme\s*['\"]?(.+?)['\"]?$", user_input, re.IGNORECASE)
    if match_movie:
        current_movie = match_movie.group(1).strip()

    # Processar intenções
    if "elenco" in response_lower:
        if current_movie:
            return {"response": query_movie_api("cast", movie_name=current_movie)}
        else:
            return {"response": "Por favor, forneça o nome do filme para buscar o elenco."}

    elif "sinopse" in response_lower:
        if current_movie:
            return {"response": query_movie_api("synopsis", movie_name=current_movie)}
        else:
            return {"response": "Por favor, forneça o nome do filme para buscar a sinopse."}

    elif "avaliação" in response_lower:
        if current_movie:
            return {"response": query_movie_api("rating", movie_name=current_movie)}
        else:
            return {"response": "Por favor, forneça o nome do filme para buscar a avaliação."}

    elif "filmes populares" in response_lower:
        return {"response": query_movie_api("popular")}

    elif "recomendação" in response_lower:
        match_genre = re.search(r"gosto por\s*(.+)", response_lower)
        if match_genre:
            genre = match_genre.group(1).strip()
            return {"response": query_movie_api("recommend", genre=genre)}
        else:
            return {"response": "Por favor, forneça o gênero para recomendações."}

    elif "similar" in response_lower:
        if current_movie:
            return {"response": query_movie_api("similar", movie_name=current_movie)}
        else:
            return {"response": "Por favor, forneça o nome do filme para buscar similares."}

    return {"response": response}

@app.get("/popular")
def popular_movies():
    return {"response": query_movie_api("popular")}

@app.get("/recommend/{genre}")
def recommend_movies(genre: str):
    return {"response": query_movie_api("recommend", genre=genre)}
