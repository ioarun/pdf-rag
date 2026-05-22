# PDF RAG
PDF RAG Chatbot

Inspired by [tonykipkemboi's code on RAG with PDFs
](https://github.com/tonykipkemboi/ollama_pdf_rag)

## Overview

This project implements a **Retrieval-Augmented Generation (RAG)** system that allows you to chat with PDF documents. The system uses advanced language models to understand and answer questions about the content of uploaded PDFs.

### How It Works

The PDF RAG pipeline consists of the following components:

1. **Document Loading**: PDFs are loaded and parsed using `UnstructuredPDFLoader` to extract text content.

2. **Text Chunking**: The extracted text is split into manageable chunks (1000 characters with 200 character overlap) using `RecursiveCharacterTextSplitter`. This ensures context is preserved across chunks while maintaining optimal token lengths.

3. **Vector Embeddings**: Text chunks are converted into vector embeddings using the `sentence-transformers/all-mpnet-base-v2` model via HuggingFace embeddings. This allows semantic similarity searches.

4. **Vector Database**: Embeddings are stored in a Chroma vector database for fast retrieval of relevant document passages.

5. **Multi-Query Retrieval**: When you ask a question, the system uses `MultiQueryRetriever` to generate multiple alternative formulations of your query. This helps overcome limitations of distance-based similarity search by retrieving documents from different semantic angles.

6. **LLM Response Generation**: The OpenAI `gpt-4o-mini` language model processes the retrieved context and your question to generate accurate, context-aware answers.

7. **RAG Chain**: All components are connected in a LangChain pipeline that orchestrates the retrieval, prompting, and response generation in a single, coherent workflow.

### Usage

The notebook provides a simple `chat_with_pdf(question)` function that takes a natural language question and returns an answer based exclusively on the PDF content. The system is designed to provide accurate, grounded responses without hallucination.

### Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`
- OpenAI API key (see setup below)

### Setup: OpenAI API Key

1. **Get your OpenAI API key:**
   - Go to [https://platform.openai.com/api/keys](https://platform.openai.com/api/keys)
   - Sign in with your OpenAI account (create one at [https://openai.com](https://openai.com) if needed)
   - Click "Create new secret key"
   - Copy the generated key

2. **Add API key to `.env` file:**
   - Open the `.env` file in the root directory of this project
   - Replace `your-api-key-here` with your actual OpenAI API key:
     ```
     OPENAI_API_KEY=sk-...your-key-here...
     ```
   - Save the file

3. **Important:** 
   - The `.env` file is already listed in `.gitignore`, so your API key will never be committed to git
   - Keep your API key private and never share it
   - Ensure you have billing set up on your OpenAI account to use the API

## Docker build
To build the Docker image, run the following command in the terminal from the root directory of the project:

```bash
docker build -t rag-pdf .
```

## Running with Docker

### Run Streamlit App
```bash
docker run --rm -it -p 8888:8888 -p 8501:8501 -v $(pwd):/workspace rag-pdf bash -c "streamlit run app/streamlit_app.py --server.address=0.0.0.0"
```
Access at: **http://localhost:8501**

### Run Jupyter Notebook in Docker
```bash
docker run --rm -it -p 8888:8888 -p 8501:8501 -v $(pwd):/workspace rag-pdf bash -c "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"
```
Access at: **http://localhost:8888** (copy token from logs)

### Interactive Shell (Choose App Later)
```bash
docker run --rm -it -p 8888:8888 -p 8501:8501 -v $(pwd):/workspace rag-pdf
```
Then run inside container:
- **Streamlit:** `streamlit run app/streamlit_app.py --server.address=0.0.0.0`
- **Jupyter:** `jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root`

**Port Mappings:**
- `8888` - Jupyter Notebook
- `8501` - Streamlit App


## Running the Application

### Option 1: Jupyter Notebook (Recommended for Development)
The notebook provides an interactive environment for exploring RAG capabilities with detailed output.

1. **Run Jupyter:**
   ```bash
   jupyter notebook
   ```

2. **Open and run:**
   - Navigate to `notebooks/rag_notebook.ipynb`
   - Place your PDF in `/workspace/pdfs/` or update the path in the notebook
   - Run the cells sequentially to process the PDF and chat with it

### Option 2: Streamlit Web Application (Recommended for Users)
The Streamlit app provides a user-friendly web interface for uploading PDFs and chatting with them.

1. **Run the Streamlit app:**
   ```bash
   streamlit run app/streamlit_app.py
   ```

2. **Use the app:**
   - Upload a PDF using the sidebar
   - Ask questions about the document in the chat
   - View retrieved context chunks for transparency
   - Adjust model and temperature settings in the sidebar

**Features:**
- 📤 Dynamic PDF upload and processing
- 💬 Multi-turn chat interface
- 📚 View retrieved context chunks
- ⚙️ Adjustable model and temperature settings
- 💾 Chat history within session

