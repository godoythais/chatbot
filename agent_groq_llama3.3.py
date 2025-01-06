import requests
import re
from groq import Groq
from config import GROQ_API_KEY, TMDB_API_KEY

# Configuração da API Groq
client = Groq(
    api_key=GROQ_API_KEY,  # Configurar a variável de ambiente para a chave de API
)

# Configuração da API TMDb
API_BASE_URL = "https://api.themoviedb.org/3"

def query_movie_api(action, movie_name=None, genre=None):
    """
    Realiza ações específicas na API de filmes.
    """
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
    """
    Envia mensagens para a API Groq e decide a ação com base na resposta.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile"  # Modelo a ser utilizado
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro na API Groq: {e}"

def interactive_agent():
    """
    Chatbot interativo com orquestração via Groq e integração de filmes.
    """
    print("Bem-vindo ao Chatbot Orquestrador com API Groq e integração de filmes!")
    current_movie = None  # Armazena o filme atual no contexto

    while True:
        user_input = input("--------------------------------------\n\nUsuário: ")
        messages = [{"role": "system", "content": "Você é um assistente de filmes que também orquestra ações."}]
        if user_input.lower() in {"sair", "exit", "quit"}:
            print("Encerrando o assistente. Até logo!")
            break
        
        messages.append({"role": "user", "content": user_input})

        # Envia a mensagem para a API Groq para decidir a intenção
        response = query_groq(messages)
        print(f"ChatBot: {response}")

        if response:  # Certifique-se de que há um `response` processável
            response_lower = response.lower()

            # Atualizar contexto com novo filme, se mencionado
            match_movie = re.search(r"filme\s*['\"]?(.+?)['\"]?$", user_input, re.IGNORECASE)
            if match_movie:
                current_movie = match_movie.group(1).strip()

            # Ações baseadas na intenção do usuário
            if "elenco" in response_lower:
                if current_movie:
                    print(query_movie_api("cast", movie_name=current_movie))
                else:
                    print("Por favor, forneça o nome do filme para que eu possa buscar o elenco.")

            elif "sinopse" in response_lower:
                if current_movie:
                    print(query_movie_api("synopsis", movie_name=current_movie))
                else:
                    print("Por favor, forneça o nome do filme para que eu possa buscar a sinopse.")

            elif "avaliação" in response_lower:
                if current_movie:
                    print(query_movie_api("rating", movie_name=current_movie))
                else:
                    print("Por favor, forneça o nome do filme para que eu possa buscar a avaliação.")

            elif "filmes populares" in response_lower:
                print(query_movie_api("popular"))

            elif "recomendação" in response_lower:
                match_genre = re.search(r"gosto por\s*(.+)", response_lower)
                if match_genre:
                    genre = match_genre.group(1).strip()
                    print(query_movie_api("recommend", genre=genre))
                else:
                    print("Por favor, forneça o gênero para recomendações.")

            elif "similar" in response_lower:
                if current_movie:
                    print(query_movie_api("similar", movie_name=current_movie))
                else:
                    print("Por favor, forneça o nome do filme para buscar similares.")

            elif "fale mais sobre este filme" in response_lower:
                if current_movie:
                    print(f"Consultando mais informações sobre '{current_movie}'.")
                    print(query_movie_api("synopsis", movie_name=current_movie))
                else:
                    print("Não há um filme no contexto atual. Por favor, especifique o nome do filme.")
        else:
            print("Erro ao processar a resposta da API Groq. Tente novamente.")

if __name__ == "__main__":
    interactive_agent()
