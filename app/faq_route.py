import logging
import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from helper_functions.embedding_function import CPUEmbeddingFunction  # Import the CPU embedding class
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Disable all ChromaDB logs
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

# Resolve faqs_path relative to this file
base_dir = os.path.dirname(os.path.abspath(__file__))
faqs_path = os.path.join(base_dir, "resources", "Myntra_FAQ.csv")

# Load API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY') or st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment variables or Streamlit secrets.")
groq_client = Groq(api_key=GROQ_API_KEY)

GROQ_MODEL = os.getenv("GROQ_MODEL") or st.secrets.get("GROQ_MODEL")
if not GROQ_MODEL:
    raise ValueError("GROQ_MODEL not set in environment variables or Streamlit secrets.")

# Load model on CPU
model = SentenceTransformer('all-MiniLM-L12-v2', device='cpu')

chromadb_client = chromadb.Client()
collection_name_faq = 'faqs'


def ingest_faq_data(path):
    # Delete existing collection if exists to ensure fresh ingestion on deploy
    if collection_name_faq in [c.name for c in chromadb_client.list_collections()]:
        chromadb_client.delete_collection(collection_name_faq)
        print(f"Deleted existing collection: {collection_name_faq}")

    print("Ingesting FAQ data into ChromaDB...")

    # Use custom CPU embedding function
    embedding_function = CPUEmbeddingFunction(model)

    collection = chromadb_client.get_or_create_collection(
        name=collection_name_faq,
        embedding_function=embedding_function
    )

    df = pd.read_csv(path)
    docs = df['QUESTION'].tolist()
    metadata = [{'answer': ans} for ans in df['ANSWER'].tolist()]
    ids = [f"id_{i}" for i in range(len(docs))]

    collection.add(
        documents=docs,
        metadatas=metadata,
        ids=ids
    )

    print(f"FAQ data successfully ingested into ChromaDB collection: {collection_name_faq}")


def get_relevant_qa(query):
    collection = chromadb_client.get_collection(name=collection_name_faq)

    # Compute embeddings for query
    embedding_function = CPUEmbeddingFunction(model)
    query_embedding = embedding_function([query])

    result = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )
    return result


def faq_chain(query):
    result = get_relevant_qa(query)

    # Correct extraction of answer string from metadata dictionary
    if result['metadatas'] and len(result['metadatas']) > 0 and len(result['metadatas'][0]) > 0:
        context = result['metadatas'][0].get('answer', '')
    else:
        context = ''

    prompt = f"""
    You are a question-answering assistant. Answer the QUESTION using ONLY the information provided in the CONTEXT below.

    ### STRICT RULES:
    1. Use ONLY information from the CONTEXT - do not use external knowledge
    2. If the CONTEXT does not contain the answer, respond with: "I don't know based on the provided information."
    3. Never fabricate, guess, or infer information not explicitly stated in the CONTEXT.
    4. Provide direct, factual answers without unnecessary elaboration.

    ### QUESTION:
    {query}

    ### CONTEXT:
    {context}

    """

    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=GROQ_MODEL,
    )

    return chat_completion.choices[0].message.content


# if __name__ == "__main__":
#     # Debug prints to verify paths and keys
#     # import streamlit as st
#     # st.write(f"FAQ CSV Path: {faqs_path}")
#     # st.write(f"GROQ_API_KEY is set: {GROQ_API_KEY is not None}")

#     ingest_faq_data(faqs_path)
#     query = "I want to pay via EMI using my credit card. Which credit cards are accepted for EMI payments?"

#     answer = faq_chain(query)
#     print(answer)
