# IA Generativa e RAG - Módulo da API

Este projeto implementa uma API utilizando FastAPI que integra um modelo de linguagem (LLM) com um banco de dados vetorial (Qdrant) para realizar consultas e gerar respostas baseadas em documentos contextuais. O sistema utiliza embeddings gerados pelo modelo `sentence-transformers/msmarco-bert-base-dot-v5`.

## Estrutura do Repositório

```plaintext
IA_Generativa_RAG/
│
├── __pycache__/                  # Cache de arquivos compilados
│
├── README.md                     # Documentação do projeto
│
├── api.py                        # Implementação principal da API
│
├── env_var.py                    # Variáveis de ambiente e configuração da API da Nvidia
│
├── query_mate_logo.png           # Logotipo para a aplicação web
│
├── rag.py                        # Lógica de recuperação e geração de respostas
│
├── requirements.txt              # Lista de dependências do projeto
│
├── start_api.py                  # Script para iniciar a API
│
└── web_app.py                    # Interface da aplicação web (se aplicável)
