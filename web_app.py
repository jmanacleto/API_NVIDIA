# IA Generativa e RAG - Frontend
# Módulo da Interface Web e Consulta à API

import re                   # Importa o módulo re de expressão regular
import streamlit as st      # Importa o módulo streamlit com o alias st - monta interface web
import requests             # Importa o módulo requests - requisições na api
import json                 # Importa o módulo json
import warnings             # Filtra warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Proret - Busca com IA Generativa e RAG", page_icon=":bulb:", layout="centered")   # Configurando o título da página e outras configurações (favicon)
st.image("query_mate_logo.png",  use_column_width=True)
# Define o título do aplicativo Streamlit
st.title('_:green[Query Mate]_')
st.title('_:blue[Busca com IA Generativa]_')

question = st.text_input("Digite Uma Pergunta Para a IA Executar Consulta nos Documentos:", "")     # Cria uma caixa de texto para entrada de perguntas

if st.button("Enviar"):         # Verifica se o botão "Perguntar" foi clicado
    st.write("A pergunta foi: \"", question+"\"")       # Exibe a pergunta feita
    url = "http://127.0.0.1:8000/LLM_RAG_api"                   # Define a URL da API
    payload = json.dumps({"query": question})           # Cria o payload da requisição em formato JSON
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}        # Define os cabeçalhos da requisição
    response = requests.request("POST", url, headers=headers, data=payload)         # Faz a requisição POST à API
    if response.status_code == 200:
        try:
            answer = json.loads(response.text).get("answer", "Sem resposta no JSON")
            st.write(f"Resposta da API: {answer}")
        except json.JSONDecodeError:
            st.error("Erro ao tentar decodificar o JSON.")
            st.write(f"Resposta bruta da API: {response.text}")  # Mostra a resposta bruta para depuração
    else:
        st.error(f"Erro na requisição: {response.status_code}")
        st.write(f"Conteúdo da resposta: {response.text}")
    
    
    if response.text:
        try:
                answer = json.loads(response.text)["answer"]
        except json.JSONDecodeError:
                st.error("Erro ao tentar decodificar a resposta JSON")
    else:
        st.error("Resposta da API está vazia")
        
    print(response.text)
    answer = json.loads(response.text)["answer"]        # Obtém a resposta da API e extrai o texto da resposta à pergunta
    rege = re.compile("\\[Document\\ [0-9]+\\]|\\[[0-9]+\\]")        # Compila uma expressão regular para encontrar referências a documentos
    m = rege.findall(answer)        # Encontra todas as referências a documentos na resposta
    num = []        # Inicializa uma lista para armazenar os números dos documentos
    
    for n in m:         # Extrai os números dos documentos das referências encontradas
        num = num + [int(s) for s in re.findall(r'\b\d+\b', n)]
    st.markdown(answer)         # Exibe a resposta da pergunta usando markdown
    documents = json.loads(response.text)['context']        # Obtém os documentos do contexto da resposta
    show_docs = []              # Inicializa uma lista para armazenar os documentos que serão exibidos
    
    for n in num:               # Adiciona os documentos correspondentes aos números extraídos à lista show_docs
        for doc in documents:
            if int(doc['id']) == n:
                show_docs.append(doc)
    
    ds_id = 1                           # Inicializa uma variável para o identificador dos botões de download
    for doc in show_docs:               # Exibe os documentos expandidos com botões de download
        with st.expander(str(doc['id'])+" - "+doc['path']):         # Cria um expansor para cada documento
            st.write(doc['content'])        # Exibe o conteúdo do documento
            with open(doc['path'], 'rb') as f:      # Abre o arquivo do documento e cria um botão de download
                st.download_button("Download do Arquivo", f, file_name = doc['path'].split('/')[-1], key = ds_id)
                ds_id = ds_id + 1         # Incrementa o identificador do botão para download