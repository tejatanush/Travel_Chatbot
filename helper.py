import spacy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from groq import Groq
from langchain_groq import ChatGroq
import regex as re
import os
from dotenv import load_dotenv
import requests
import ast
nlp = spacy.load("en_core_web_sm")
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = api_key

# Initialize the Groq model
groq_model = ChatGroq(api_key=api_key, model='llama3-8b-8192')

api_key2 = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key2
cse_id = os.getenv("CSE_ID")
os.environ["CSE_ID"] = cse_id

def fetch_image_links(api_key2, cse_id, query, num_images):
    service_url = "https://www.googleapis.com/customsearch/v1"
    image_urls = []
    start = 1

    
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key2,
        "searchType": "image",
        "start": start,
        "num":num_images   # API allows maximum 10 results per request
    }

    response = requests.get(service_url, params=params)
    results = response.json()

    if "items" not in results:
        print(f"No more results found. Status: {results}")

    for item in results["items"]:
        image_urls.append(item["link"])
        if len(image_urls) >= num_images:
            break

    start += 10

    return image_urls

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile")

# Prompt template
prompt = PromptTemplate(
    input_variables=["text"],
    template="""
You are a smart keyword extractor.
Extract specific and important keywords from the following travel response that relate only to the following categories, including full names where applicable:

Food names 
Places 
Hotels 
Beaches 
Shopping spots 
Parks 

Return keywords only, as mentioned in the text not any dictinary format just i need only keywords releated to above categories. Do not include generic categories like "Caves", "Fort", "Temple", "Island", "Food", "Shopping", or "Stores" unless accompanied by a specific name.

Format the output as a Python list, with keywords in quotes, separated by commas.



Response:
{text}
"""
)

# Create chain
keyword_chain = LLMChain(llm=llm, prompt=prompt)

# Final keyword extraction function
def get_images_text(text: str) -> list:
    result = keyword_chain.invoke({"text": text})  # invoke is preferred now
    if isinstance(result, dict) and "text" in result:
        output = result["text"].strip()
    else:
        output = str(result).strip()

    # Extract only list part using regex
    match = re.search(r"\[.*?\]", output)
    if match:
        try:
            final_list = ast.literal_eval(match.group(0))
            return final_list
        except Exception as e:
            raise ValueError(f"Failed to parse list: {e}")
    else:
        raise ValueError("No valid Python list found in model output.")
'''def images_names_extractor(text):
    doc = nlp(text)
    cleaned_entities = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            # Remove leading/trailing spaces and check for stop words
            cleaned = " ".join([
                token.text for token in ent if not token.is_stop and not token.is_punct
            ])
            if cleaned:  # Only add non-empty results
                cleaned_entities.append(cleaned)
                
    return cleaned_entities'''
def normalize_keyword(kw):
    return kw.replace(" ", "").lower()
def search_image_by_keyword(user_input,collection):
    #collection = get_mongo_client()
    normalized = normalize_keyword(user_input)

    results = collection.find({"normalized_keywords": normalized})

    image_urls = [doc["image_url"] for doc in results]

    if image_urls:
        return {
            "user_input": user_input,
            "image_urls": image_urls 
        }
    else:
        return