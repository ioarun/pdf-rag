# PDF RAG
PDF RAG Chatbot

## Docker
To build the Docker image, run the following command in the terminal from the root directory of the project:

```bash
docker build -t rag-pdf .
docker run --gpus all --rm -it -p 8888:8888 -v $(pwd):/workspace rag-pdf
```
