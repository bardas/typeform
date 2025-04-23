# Typeform RAG Chatbot

A FastAPI-based Retrieval-Augmented Generation (RAG) application over HTML documents.  
It parses raw HTML, chunks and embeds text into Pinecone, and exposes a `/query` endpoint for chat-style Q&A.

---

## Table of Contents

- [Features](#features)  
- [Repository Layout](#repository-layout)  
- [Prerequisites](#prerequisites)  
- [Local Development](#local-development)  
  - [1. Setup Python](#1-setup-python)  
  - [2. Data Preprocessing](#2-data-preprocessing)  
  - [3. Run FastAPI](#3-run-fastapi)  
- [Docker](#docker)  
  - [Build Image](#build-image)  
  - [Run Container](#run-container)  
- [Kubernetes Deployment](#kubernetes-deployment)  
  - [Using kind (Kubernetes in Docker)](#using-kind-kubernetes-in-docker)
- [Cleaning Up](#cleaning-up)  
- [Troubleshooting](#troubleshooting)
---

## Features

- **HTML Parsing** with BeautifulSoup  
- **Text Chunking** via LangChain’s `RecursiveCharacterTextSplitter`  
- **Embedding Generation** using HuggingFace
- **Vector Retrieval** from Pinecone  
- **Chat API** built on FastAPI  
- **Configurable** via YAML files  
- **Structured Logging** 

---

## Repository Layout

```aiignore
.
├── Dockerfile
├── README.md
├── app
│   ├── api
│   │   ├── __init__.py
│   │   └── response.py
│   ├── main.py
│   ├── schemas.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── embed_loader.py
│   │   ├── html_parser.py
│   │   └── retriever.py
│   └── utils
│       ├── __init__.py
│       ├── helper_functions.py
│       └── logging.py
├── configs
│   ├── __init__.py
│   ├── logging_config.yaml
│   └── settings.yaml
├── data
│   └── raw
│       ├── 1.html
│       └── 2.html
├── k8s
│   ├── configmap.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── logs
├── requirements.txt
└── tests
    ├── __init__.py
    ├── temp_test.py
    └── test_parser.py

```


---

## Prerequisites

- Python 3.12+  
- Docker 20.10+  
- `kubectl` CLI (v1.24+)  
- For local K8s: **kind** or **Docker Desktop** with Kubernetes enabled  
- Pinecone account & API key
---

## Local Development

### 1. Setup Python

```bash
    git clone https://github.com/your-org/typeform-rag-chatbot.git
    cd typeform-rag-chatbot
    
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
```

### 2. Data Preprocessing
Run each step in order to prepare your index:
```bash
    python app/services/html_parser.py
    python app/services/chunker.py
    python app/services/embed_loader.py
```

###  3. Run FastAPI
```bash
    uvicorn app.main:app \
      --host 0.0.0.0 --port 8000 --reload
```

Visit http://localhost:8000/docs to test.

##  Docker

### Build Image

```bash
    docker build -t typeform-rag-chatbot:local .
```

### Run Container
1. Data & configs are baked in; ensure data/raw contains your .html files.
2. Launch, which will run parser → chunker → FastAPI:
```bash
docker run --rm -p 8000:8000 typeform-rag-chatbot:local
```
4. Call the API from host:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"How to create multi-language forms?"}'
```

## Kubernetes Deployment

### Using kind (Kubernetes in Docker)

1. **Create cluster**  
```bash
   kind create cluster --name rag-demo
```
2. **Load your local image**
```bash
    kind load docker-image typeform-rag-chatbot:local --name rag-demo
```
3. **Apply manifests**

```bash
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
```
4. **Wait for pods to become ready**

```bash
    kubectl get pods -l app=typeform-rag --watch
```
5. **Port-forward & test**

```bash
    kubectl port-forward svc/typeform-rag 8080:80
    curl -X POST http://localhost:8000/query \
      -H "Content-Type: application/json" \
      -d '{"question":"How to create multi-language forms?"}'
```
6. **Tear down**
```bash
    kind delete cluster --name rag-demo
```

## Cleaning Up
1. **Stop & remove all containers**

```bash
    docker rm -f $(docker ps -aq)
```

2. **Remove all images**

```bash
    docker rmi -f $(docker images -aq)
```

3. **Delete kind cluster**
```bash
    kind delete cluster --name rag-demo
```

## Troubleshooting
* OOM / Killed on model load
Increase Docker’s memory to ≥ 8 GB or pre-download the model at build time.