import logging

# Disable all ChromaDB logs
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from helper_functions.embedding_function import CPUEmbeddingFunction  # Import the CPU embedding class
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Groq client with API key from environment variables
if not os.getenv('GROQ_API_KEY'):
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Load model on CPU
model = SentenceTransformer('all-MiniLM-L12-v2', device='cpu')

faqs_path = "C:/Users/Inspire/Code/Gen AI/Myntra_chat_assistant/app/resources/Myntra_FAQ.csv"

chromadb_client = chromadb.Client()
collection_name_faq = 'faqs'


def ingest_faq_data(path):
    if collection_name_faq not in [c.name for c in chromadb_client.list_collections()]:
        print("Ingesting FAQ data into ChromaDB...")

        # Use CPU embedding function
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
    else:
        print(f"Collection {collection_name_faq} already exists")


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

    context = ''.join([r.get('answer') for r in result['metadatas'][0]])

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
        model=os.environ["GROQ_MODEL"],
    )

    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    ingest_faq_data(faqs_path)
    query = "I want to pay via EMI using my credit card. Which credit cards are accepted for EMI payments?"

    answer = faq_chain(query)
    print(answer)

