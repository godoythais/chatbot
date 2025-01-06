# Chatbot para Filmes - Integração com APIs Groq e TMDb

Este projeto é um chatbot inteligente que combina a API Groq para processar linguagem natural e a API TMDb para fornecer informações detalhadas sobre filmes. Com ele, você pode:

- Perguntar sobre elenco, sinopse, avaliação de um determinado filme.
- Conseguir indicações de filmes com base em um gênero.
- Pesquisar informações sobre filmes populares no momento.

## Tecnologias Utilizadas
- **Python** para o backend.
- **Groq API** para processamento de linguagem natural.
- **TMDB API** para consulta de dados sobre filmes e séries.

## Pré requisitos
- Chave particular para as APIs Groq e TMDb;
- Python 3.9+;
- Bibliotecas como FastAPI e Groq.

## Arquitetura
├── agent_groq_llama3.3.py  # Código usado para testar as integrações e funcionamento do chatbot via CLI  

├── config.py               # Arquivo com as chaves particulares para uso das APIs  

├── main.py                 # Arquivo principal do chatbot que deve ser usado para executar o microserviço  

├── README.md               # Documentação  

## Instalação
- Clone o repositório;
- Garanta que as bibliotecas necessárias estão instaladas;
- Configure o arquivo config.py com as chaves particulares para cada API.

## Como usar
O link a seguir contém um vídeo com a explicação audiovisual do código e seu funcionamento. Qualquer problema com o acesso do vídeo, entrar em contato.

-> https://drive.google.com/file/d/1xOhX-PsVNgRP27FbQDvCkO8MO44W44tE/view?usp=sharing
