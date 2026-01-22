import streamlit as st
import requests
import os

#----The BRIDGE----

def call_text_search_api(query_text):
    url = "http://127.0.0.1:8000/search_text"
    data = {"query": query_text}
    try:
        response = requests.post(url, data=data)
        return response.json() if response.status_code == 200 else None
    except:
        return None
    
def call_search_api(image_file):
    #define API addreass
    url = "http://127.0.0.1:8000/search" #same url as search in main.py

    # We pass the file name and the actual data (read as bytes)
    files = {"file": (image_file.name, image_file.getvalue(), image_file.type)}
    #getvalue() extracts the raw binary bytes (the actual 0s and 1s of the image) so they can be sent.

    try:
        response = requests.post(url, files=files)

        #if server answers, return the json results
        if response.status_code == 200:     #200 means "OK/Success."
            return response.json()
        else:
            st.error("Server error. Please try again later")
            return None
        
    except Exception as e:
        st.error(f"Cound not connect to server: {e}")
        return None

def call_upload_api(image_file, description_text):
    url = "http://127.0.0.1:8000/upload"
    files = {"file": (image_file.name, image_file.getvalue(), image_file.type)}
    data = {"description" : description_text}
    
    try:
        response = requests.post(url, files=files, data=data)
        return response.status_code == 200
    except:
        return False
#----BRIDGE ENDS-----

#-----UI-----
# 1. Page Configuration (The tab title in your browser)
st.set_page_config(page_title="Boomerang: BPHC Lost & Found", page_icon="🪃")

# 2. Sidebar - Global Info
with st.sidebar:
    st.title("🪃 Boomerang")
    st.markdown("---")
    st.info("Helping BITSians find what they've lost using AI.")

# 3. Main Header
st.title("🪃 Boomerang - Back 2 you")
st.write("Select an option below.")

tab1 , tab2 = st.tabs(["Lost" , "Found"])

with tab1:
    st.header("Lost something?")
    st.write("Upload a photo of what you lost, and our AI will scan the database.")

    lost_file = st.file_uploader("Option 1: Upload a photo")
    query_text = st.text_input("Option 2: Or describe it (e.g., 'blue keys')")

    results = None

    if lost_file is not None:
        with st.spinner("🔍 AI is scanning the BPHC database..."):
            results = call_search_api(lost_file)
    elif query_text:
        with st.spinner(f"🔍 Searching for '{query_text}'..."):
            results = call_text_search_api(query_text)

    if results and "results" in results:
        st.subheader("Top Matches")
        # Create dynamic columns based on number of results
        matches = results["results"]
        cols = st.columns(min(len(matches),3))

        # Loop through results and display them
        for i, match in enumerate(matches):
            with cols[i]:
                # Construct the path to the found image
                image_path = os.path.join("data", "found", match["item_name"])
                # Display the image and the real confidence score
                st.image(image_path, caption=f"Match #{i+1}")

                # Show the description from the Vault
                st.write(f"**Details:** {match['description']}")
                st.caption(f"Added: {match['found_at']}")

                if "search_type" in match and match["search_type"] == "image": #display confidence level only if search_type is image
                    st.metric("Confidence", f"{match['confidence']}%")
    else:
        st.warning("No matches found. Try a different angle or check back later!")


with tab2:
    st.header("Found Something?")
    st.write("Help a fellow BITSian! Upload a photo and description here")

    uploaded_file = st.file_uploader("Upload Item Photo", type=["jpg", "jpeg", "png"], key="found_upload")
    description = st.text_input("Where did you find it?")

    if st.button("Submit"):
        if uploaded_file is not None:
            with st.spinner("Uploading..."):
                # Pass both the file AND the description
                success = call_upload_api(uploaded_file, description)
            
            if success:
                st.success(f"Success! Added to database.")
                st.balloons()
            else:
                st.error("Failed to connect to the Brain. Is the server running?")
            # --- THE CONNECTION END ---
        else:
            st.error("Please select an image first.")

