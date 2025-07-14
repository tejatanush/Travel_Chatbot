# %%
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import os
from groq import Groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import nbimporter
from sentence_transformers import SentenceTransformer
from helper import get_images_text,search_image_by_keyword

# %%
embedding_model=SentenceTransformer("thenlper/gte-large")

# %%
def get_embedding(text):
    
    if not text.strip():
        print("attempted to get embedding for empty text")
        return []
    embedding=embedding_model.encode(text)
    return embedding.tolist()

# %%
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = api_key

# Initialize the Groq model
groq_model = ChatGroq(api_key=api_key, model='llama3-8b-8192')


# %%
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://tanush2:hVVs6seb1QOOUvjD@cluster0.bnl3hcv.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# %%
db=client["travel-db"]

# %%
collection=db["travel2"]

# %%
collection2=db["travel-images"]

# %%
#print(db.list_collection_names())


# %%
'''for index in collection.list_indexes():
    print(index)'''




# %%
def vector_search(user_query,collection):
    query_embedding=get_embedding(user_query)
    #print(query_embedding)
    #print(type(query_embedding))
    if query_embedding is None:
        return "Invalid query or embeddings is failed"
    pipeline=[
    {
        "$vectorSearch":{
            "index":"vector_index",
            "queryVector":query_embedding,
            "path":"embedding",
            "numCandidates":35,
            "limit":7
        }},
    {
        "$project":{
            "title":1,
            "content":1,
            "score":{"$meta":"vectorSearchScore"},
        }}]
    result=collection.aggregate(pipeline)
    return list(result)

# %%
def get_result(query,collection):
    result=vector_search(query,collection)
    if result is None:
        return "Sorry we are  not able to provide the answer you need!!! We will comeback soon!"
    combined_information=""
    for i in range(len(result)):
        content=result[i]["content"]
        title=result[i]["title"]
        combined_information+=f"Title:{title} , Content: {content}\n"
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

    # Get the response
    response = chain.invoke(input_dict)
    return response["text"]

# %%
while True:
    query = input("Enter your query (type 'ESC' to exit): ")

    if query != "ESC":
        # Step 1: Process the query and get the answer
        answer = get_result(query, collection)
        print(f"\nQuery: {query}")
        print(f"Answer: {answer}")

        # Step 2: Extract keywords from the answer for image search
        images_needed = get_images_text(answer)
        print(f"Keywords for image search: {images_needed}")

        # Step 3: Search for images using those keywords
        final_image_result = []
        for image_keyword in images_needed:
            image_search_result = search_image_by_keyword(image_keyword, collection2)
            if image_search_result is not None:
                final_image_result.append(image_search_result)  # Save the dictionary result

        # Step 4: Print all image search results
        print("\nImage Search Results:")
        for result in final_image_result:
            print(result)

        print("Done.\n")

    else:
        print("Exiting the program.")
        break



