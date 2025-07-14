import streamlit as st
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import os
from groq import Groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Set page config
st.set_page_config(page_title="Travel Chatbot", page_icon="✈️")

# Application title and description
st.title("Travel Chatbot")
st.markdown("Ask questions about travel destinations and get informed answers!")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
mongodb_uri = "mongodb+srv://tanush2:hVVs6seb1QOOUvjD@cluster0.bnl3hcv.mongodb.net/?appName=Cluster0"

# Define functions for the chatbot
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("thenlper/gte-large")

@st.cache_resource
def init_groq_model():
    return ChatGroq(api_key=api_key, model='llama3-8b-8192')

@st.cache_resource
def init_mongodb_client():
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        st.sidebar.success("Connected to MongoDB!")
    except Exception as e:
        st.sidebar.error(f"MongoDB connection error: {e}")
    return client

def get_embedding(text):
    if not text.strip():
        st.warning("Attempted to get embedding for empty text")
        return []
    embedding_model = load_embedding_model()
    embedding = embedding_model.encode(text)
    return embedding.tolist()

def vector_search(user_query, collection):
    query_embedding = get_embedding(user_query)
    if not query_embedding:
        return "Invalid query or embeddings failed"
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 35,
                "limit": 5,
            }
        },
        {
            "$project": {
                "title": 1,
                "content": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        }
    ]
    
    result = collection.aggregate(pipeline)
    return list(result)

def get_result(query, collection):
    with st.spinner("Searching for relevant information..."):
        result = vector_search(query, collection)
    
    combined_information = ""
    for i in range(len(result)):
        content = result[i]["content"]
        title = result[i]["title"]
        combined_information += f"Title:{title} , Content: {content}\n"
    
    prompt_template = PromptTemplate(
        input_variables=["query", "combined_information"],
        template="""
        You are a helpful travel assistant. You must only answer queries based on the content provided, not from your own knowledge.

        User Query:
        {query}

        Relevant Information:
        {combined_information}

        Answer:"""
    )
    
    chain = LLMChain(llm=groq_model, prompt=prompt_template)
    input_dict = {
        "query": query,
        "combined_information": combined_information
    }

    with st.spinner("Generating response..."):
        response = chain.invoke(input_dict)
    
    return response["text"]

# Initialize resources
try:
    embedding_model = load_embedding_model()
    groq_model = init_groq_model()
    client = init_mongodb_client()
    db = client["travel-db"]
    collection = db["travel2"]
except Exception as e:
    st.error(f"Error initializing resources: {e}")
    st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Get user input
if query := st.chat_input("Ask a travel question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.write(query)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        try:
            response = get_result(query, collection)
            st.write(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_message = f"Error generating response: {e}"
            st.error(error_message)
            # Add error message to chat history
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Sidebar with app information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This travel chatbot uses:
    - Sentence transformers for embeddings
    - MongoDB Atlas for vector search
    - Groq's LLaMA 3 8B model for responses
    
    Ask any travel-related questions to get informed answers based on our travel database.
    """)
    
    # API Key input
    with st.expander("API Configuration"):
        new_api_key = st.text_input("Groq API Key (optional)", type="password", 
                                    help="Enter your Groq API key if you want to use your own")
        if new_api_key and new_api_key != api_key:
            api_key = new_api_key
            os.environ["GROQ_API_KEY"] = api_key
            st.success("API key updated!")
            groq_model = init_groq_model()
