"""Streamlit application for PDF RAG system."""

import streamlit as st
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.rag_utils import RAGSystem


st.set_page_config(page_title="PDF RAG Chat", layout="wide")


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pdf_loaded" not in st.session_state:
        st.session_state.pdf_loaded = False
    if "pdf_name" not in st.session_state:
        st.session_state.pdf_name = None


def main():
    """Main Streamlit application."""
    st.title("📄 PDF RAG Chat")
    st.markdown("Upload a PDF and chat with it using AI-powered retrieval augmented generation.")

    initialize_session_state()

    # Sidebar for PDF upload
    with st.sidebar:
        st.header("⚙️ Configuration")

        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name

            if not st.session_state.pdf_loaded or st.session_state.pdf_name != uploaded_file.name:
                with st.spinner("Processing PDF... This may take a moment."):
                    try:
                        # Initialize RAG system
                        rag_system = RAGSystem(
                            model="gpt-4o",
                            temperature=0.5,
                            max_tokens=512
                        )

                        # Load and process PDF
                        documents = rag_system.load_pdf(tmp_path)
                        chunks = rag_system.split_text(documents)
                        rag_system.create_vector_db(chunks)
                        rag_system.setup_retriever(k=5)
                        rag_system.setup_chain()

                        st.session_state.rag_system = rag_system
                        st.session_state.pdf_loaded = True
                        st.session_state.pdf_name = uploaded_file.name
                        st.session_state.chat_history = []

                        st.success(f"✅ PDF loaded successfully! ({len(chunks)} chunks)")

                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
                    finally:
                        os.unlink(tmp_path)

        st.divider()

        model = st.selectbox(
            "Select Model",
            ["gpt-4o", "gpt-4-turbo", "gpt-4o-mini"],
            help="Choose the OpenAI model to use"
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )

        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    # Main chat area
    if not st.session_state.pdf_loaded:
        st.info("👈 Upload a PDF file to get started!")
        return

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])

    # User input
    if user_input := st.chat_input("Ask a question about the PDF..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        # Get context and generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get relevant context
                    context_docs = st.session_state.rag_system.get_context(user_input, k=5)

                    # Generate response
                    response = st.session_state.rag_system.query(user_input)

                    st.write(response)

                    # Add assistant message to history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

                    # Show context in expandable section
                    with st.expander("📚 View Retrieved Context"):
                        for i, doc in enumerate(context_docs, 1):
                            st.markdown(f"**Chunk {i}:**")
                            st.text(doc[:500] + "..." if len(doc) > 500 else doc)
                            st.divider()

                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")


if __name__ == "__main__":
    main()
