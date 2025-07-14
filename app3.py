import streamlit as st
from main import get_result, collection, collection2
from helper import get_images_text, search_image_by_keyword

# Streamlit app configuration
st.set_page_config(page_title="Travel Assistant", layout="wide")

# Custom CSS to adjust layout
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
    .image-caption {
        text-align: center;
        font-size: 0.9em;
        margin-top: -10px;
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
        
        # Display images if they exist in the message
        if message.get("images"):
            cols = st.columns(3)
            for idx, (img_url, keyword) in enumerate(message["images"]):
                if img_url:  # Check if img_url is not None
                    cols[idx % 3].image(img_url, width=200)
                    cols[idx % 3].caption(keyword)  # Add caption with the keyword

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
        
        # Search for images and collect URLs with their keywords
        image_data = []
        if images_needed:  # Check if images_needed is not None or empty
            for image_keyword in images_needed:
                image_result = search_image_by_keyword(image_keyword, collection2)
                if image_result and "image_urls" in image_result and image_result["image_urls"]:
                    for img_url in image_result["image_urls"]:
                        if img_url:  # Check if img_url is not None
                            image_data.append((img_url, image_keyword))
        
        # Display images in a grid layout if we have any
        if image_data:
            st.markdown("<div class='image-row'>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, (img_url, keyword) in enumerate(image_data):
                if idx < len(cols):  # Ensure we don't exceed column count
                    cols[idx].image(img_url, width=200)
                    cols[idx].caption(keyword)  # Add caption with the keyword
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "images": image_data if image_data else []  # Store list of (url, keyword) tuples
        })