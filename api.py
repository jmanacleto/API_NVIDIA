# IA Generativa e RAG 
# Módulo da API

#----------------------------------------------------------------------------------------------------------------------------------
# Infra
import os                                           # Importa o módulo os
import env_var                                      # Importa o módulo env_var com a API para o LLM
from fastapi import FastAPI                         # Importa a classe FastAPI do módulo fastapi para criar a API
from langchain_qdrant import Qdrant                 # Importa a classe Qdrant do módulo langchain_qdrant para instanciar o banco vetorial
from qdrant_client import QdrantClient              # Importa a classe QdrantClient do módulo qdrant_client para conectar no banco vetorial
from pydantic import BaseModel                      # Importa a classe BaseModel do módulo pydantic para validar os dados enviados para a API
from langchain_huggingface import HuggingFaceEmbeddings     # Importa a classe HuggingFaceEmbeddings do módulo langchain_huggingface para gerar as embeddings


class Item(BaseModel):                              # Define a classe Item que herda de BaseModel
    query: str
model_name = "sentence-transformers/msmarco-bert-base-dot-v5"       # Define o nome do modelo (tokenizador)
model_kwargs = {'device': 'cpu'}                    # Define os argumentos do modelo
encode_kwargs = {'normalize_embeddings': True}      # Define os argumentos de codificação

hf = HuggingFaceEmbeddings(                         # Cria uma instância de HuggingFaceEmbeddings
    model_name = model_name,
    model_kwargs = model_kwargs,
    encode_kwargs = encode_kwargs)

use_nvidia_api = False                              # Define a variável use_nvidia_api como False

if env_var.nvidia_key != "":                        # Verifica se a chave da Nvidia está disponível
    from openai import OpenAI                       # Importa a classe OpenAI do módulo openai
    client_ai = OpenAI(base_url = "https://integrate.api.nvidia.com/v1", api_key = env_var.nvidia_key)  # Cria uma instância de OpenAI com a URL base e a chave da API
    use_nvidia_api = True                           # Define use_nvidia_api como True
else:
    print("Não é possível usar um LLM.")            # Imprime uma mensagem indicando que não é possível usar um LLM

client = QdrantClient("http://localhost:6333")      # Cria uma instância para conectar ao banco vetorial
collection_name = "vectordb"                     # Define o nome da coleção
qdrant = Qdrant(client, collection_name, hf)        # Cria uma instância de Qdrant para enviar os dados para o banco vetorial

#----------------------------------------------------------------------------------------------------------------------------------
#Criação da API
app = FastAPI()                                     # Cria uma instância de FastAPI
@app.get("/")                                       # Define a rota raiz com o método GET
async def root():
    return {"message": "LLM com RAG"}

@app.post("/LLM_RAG_api")                               # Define a rota /LLM_RAG_api com o método POST
async def dsa_api(item: Item):
    query = item.query                              # Obtém a query do item
    search_result = qdrant.similarity_search(query = query, k = 10)         # Realiza a busca de similaridade
    list_res = []                                   # Inicializa a lista de resultados, contexto e mapeamento
    context = ""
    mappings = {}
   
    for i, res in enumerate(search_result):         # Constrói o contexto e a lista de resultados
        context += f"{i}\n{res.page_content}\n\n"
        mappings[i] = res.metadata.get("path")
        list_res.append({"id": i, "path": res.metadata.get("path"), "content": res.page_content})
  
    rolemsg = {"role": "system",                    # Define a mensagem de sistema
               "content": "Responda à pergunta do usuário usando documentos fornecidos no contexto. No contexto estão documentos que devem conter uma resposta. Sempre faça referência ao ID do documento (entre colchetes, por exemplo [0],[1]) do documento que foi usado para fazer uma consulta. Use quantas citações e documentos forem necessários para responder à pergunta."}
    messages = [rolemsg, {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"}]        # Define as mensagens
   
    if use_nvidia_api:                              # Verifica se a API da Nvidia está sendo usada
        resposta = client_ai.chat.completions.create(model = "meta/llama3-70b-instruct",        # Cria a instância do LLM usando a API da Nvidia
                                                     messages = messages,
                                                     temperature = 0.5,
                                                     top_p = 1,
                                                     max_tokens = 1024,
                                                     stream = False)
        response = resposta.choices[0].message.content      # Obtém a resposta do LLM
    
    else:
        print("Não é possível usar um LLM.")        # Imprime uma mensagem indicando que não é possível usar um LLM
    
    return {"context": list_res, "answer": response}