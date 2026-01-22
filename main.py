from fastapi import FastAPI, File, UploadFile, Form  
import shutil
import os
from core.brain import BoomerangBrain
import json
from datetime import datetime

DB_PATH = "data/database.json"

def load_vault():
    """Reads json file and returns a dictionary"""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as f:
                return json.load(f)
        except:
            return{}
    return{}

def save_to_vault(filename, description):
    """Saves a new entry into our JSON record."""
    vault = load_vault()
    
    # Create a new entry for this specific file
    vault[filename] = {
        "description": description,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Write the updated dictionary back to the file
    with open(DB_PATH, "w") as f:
        json.dump(vault, f, indent=4)

brain = BoomerangBrain()

app = FastAPI(title="Boomerang: Back 2 Base API")

# Define a "Health Check" endpoint
# This is a simple URL to verify the server is running correctly
@app.get("/")
def read_root():
    return {
        "status": "Online", 
        "app": "Boomerang: Back 2 Base",
        "campus": "BITS Pilani Hyderabad"
    }

@app.post("/upload")
async def upload_item(file: UploadFile = File(...) , description: str = Form(...)):

    upload_path = os.path.join("data" , "found", file.filename)

    #Save the uploaded file to your disk
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    save_to_vault(file.filename, description)

    # 3. Re-index the database so the new item is searchable
    # We reuse your Day 2 logic here
    found_paths = brain.get_found_images("data/found")
    found_db = brain.encode_bulk(found_paths)
    brain.create_faiss_index(found_db)

    return {
        "info": f"Item '{file.filename}' extracted and indexed!",
        "description_saved": description,
        "total_items": len(found_paths)
    }

@app.post("/search")
async def search_item(file: UploadFile = File(...)):

    vault = load_vault()

    # Save the uploaded "Lost" image temporarily
    temp_path = "temp_search.jpg"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Get the vector for the lost item
    lost_vector = brain.get_embedding(temp_path)

    # 3. Get the list of filenames currently in the system
    # (In Day 7, we will use the JSON file, but for now we scan the folder)
    found_paths = brain.get_found_images("data/found")
    filenames = [os.path.basename(p) for p in found_paths]

    #4. Perform faiss search
    matches = brain.search_faiss(lost_vector,filenames, top_k=3)

    # 5. Clean up the temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # 6. Format and return the results as Json
    formatted_results = []
    for name,score in matches:
        confidence_val = max(0, min(float(score), 1.0)) 

        # Pull description from vault, or provide a fallback if not found
        item_data = vault.get(name, {})
        description = item_data.get("description", "No description provided.")
        timestamp = item_data.get("timestamp", "Unknown time")
    
        formatted_results.append({
            "item_name" : name,
            "confidence": round(confidence_val * 100, 2),
            "search_type" : "image",
            "description": description, # NEW: Send description to UI
            "found_at": timestamp
        })
    
    return {"results" : formatted_results}\

@app.post("/search_text")
async def search_text(query : str = Form(...)):

    vault = load_vault()

    text_vector = brain.get_text_embedding(query)

    found_paths = brain.get_found_images("data/found")
    filenames = [os.path.basename(p) for p in found_paths]

    if not filenames:
        return {"results": [], "message": "Database is empty"}
    
    matches = brain.search_faiss(text_vector, filenames, top_k=3)
    
    # Format and return results
    formatted_results = []

    for name, score in matches:
        # Clamp score between 0 and 1 for clean percentages
        confidence_val = max(0, min(float(score), 1.0))

        item_data = vault.get(name, {})
        description = item_data.get("description", "No description provided.")
        timestamp = item_data.get("timestamp", "Unknown time")

        formatted_results.append({
            "item_name": name,
            "confidence": round(confidence_val * 100, 2),
            "search_type" : "text",
            "description": description, # NEW: Send description to UI
            "found_at": timestamp
        })
    
    return {"results": formatted_results}

#
@app.post("/reset_all")
async def reset_all():
    # 1. Clear JSON
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)
            
    # 2. Clear Images
    folder = "data/found"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
            
    # 3. Clear Index
    if os.path.exists("items.index"):
        os.remove("items.index")
        
    return {"status": "Database wiped clean. System ready for fresh start."}
