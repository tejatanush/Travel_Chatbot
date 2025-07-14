import streamlit as st
from main import get_result, collection, collection2
from helper import get_images_text, search_image_by_keyword

# Streamlit app configuration
st.set_page_config(page_title="Travel Assistant", layout="wide")

# Custom CSS to remove image captions and adjust layout
st.markdown("""
    <style>
    .stImage > img {
        border-radius: 10px;
        margin: 5px;
    }
    .image-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# App title and description
st.title("🌍 Travel Assistant")
st.write("Ask me anything about travel destinations, and I'll provide information with relevant images!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Display images if they exist in the message and are not None
        if message.get("images"):
            cols = st.columns(3)
            for idx, img_url in enumerate(message["images"]):
                if img_url:  # Check if img_url is not None
                    cols[idx % 3].image(img_url, width=200)

# Accept user input
if prompt := st.chat_input("Ask your travel question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Get the text response
        response = get_result(prompt, collection)
        st.write(response)
        
        # Get keywords for images
        images_needed = get_images_text(response)
        
        # Search for images and collect URLs
        image_urls = []
        if images_needed:  # Check if images_needed is not None or empty
            for image_keyword in images_needed:
                image_result = search_image_by_keyword(image_keyword, collection2)
                if image_result and "image_urls" in image_result and image_result["image_urls"]:
                    image_urls.extend(image_result["image_urls"])
        
        # Display images in a grid layout if we have any
        if image_urls:
            st.markdown("<div class='image-row'>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, img_url in enumerate(image_urls):
                if img_url:  # Check if img_url is not None
                    cols[idx % 3].image(img_url, width=200)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "images": image_urls if image_urls else []  # Store empty list instead of None
        })