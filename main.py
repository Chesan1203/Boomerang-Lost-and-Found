from fastapi import FastAPI, File, UploadFile, Form  
import shutil
import os
from core.brain import BoomerangBrain

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
async def upload_item(file: UploadFile = File(...)):
    upload_path = os.path.join("data" , "found", file.filename)

    #Save the uploaded file to your disk
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Re-index the database so the new item is searchable
    # We reuse your Day 2 logic here
    found_paths = brain.get_found_images("data/found")
    found_db = brain.encode_bulk(found_paths)
    brain.create_faiss_index(found_db)

    return {
        "info": f"Item '{file.filename}' extracted and indexed!",
        "total_items": len(found_paths)
    }

@app.post("/search")
async def search_item(file: UploadFile = File(...)):
    # 1. Save the uploaded "Lost" image temporarily
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
    
        formatted_results.append({
            "item_name" : name,
            "confidence": round(confidence_val * 100, 2),
            "search_type" : "image" 
        })
    
    return {"results" : formatted_results}\

@app.post("/search_text")
async def search_text(query : str = Form(...)):
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
        formatted_results.append({
            "item_name": name,
            "confidence": round(confidence_val * 100, 2),
            "search_type" : "text"
        })
    
    return {"results": formatted_results}
