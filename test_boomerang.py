from sentence_transformers import SentenceTransformer , util
from PIL import Image

#Loading "CLIP" model 
model = SentenceTransformer('clip-ViT-B-32')
print("Status : Model loaded successfully")

# 2. Load your images (Save two images in your folder named 'img1.jpg' and 'img2.jpg')
try : 
    img1 = Image.open("img1.jpeg")
    img2 = Image.open("img2.jpeg")

    # 3. Encode the images into "Embeddings" (The digital fingerprints)
    embeddings = model.encode([img1, img2]) #embeddings is an array of vectors related to img1 and img2

    # 4. Calculate Similarity (How close are these fingerprints?)
    # This uses "Cosine Similarity" - it returns a score between 0 and 1
    score = util.cos_sim(embeddings[0], embeddings[1])
    print(f"\n--- Boomerang Match Result ---")
    print(f"Similarity Score: {score.item():.4f}")
    
    if score.item() > 0.8:
        print("Final Verdict: EXCELLENT MATCH")
    elif score.item() > 0.5:
        print("Final Verdict: POSSIBLE MATCH (Needs Review)")
    else:
        print("Final Verdict: NOT A MATCH")
except FileNotFoundError: 
    print("\nError: Could not find 'img1.jpg' or 'img2.jpg'.")
    print("Action: Place two images in this folder and rename them to match the script!")

"""
def main():
    # 1. Initialize the Brain (This calls the __init__ )
    brain = BoomerangBrain()

    print("\n--- Boomerang: Back to Base (Project Initialization) ---")
    
    # 2. Define paths
    # We are using the data folder structure we set up
    found_item_path = "data/found/test_found.jpg"
    lost_item_path = "data/lost/test_lost.jpg"

    # 3. Safety check: Do the images exist?
    if not os.path.exists(found_item_path) or not os.path.exists(lost_item_path):
        print(f"Error: Images not found at {found_item_path} and {lost_item_path}")
        print("Please ensure you have placed test images in the data/ subfolders!")
        return

    # 4. Use our OOP Brain to process the images
    print("Computing fingerprints...")
    emb_found = brain.get_embedding(found_item_path)
    emb_lost = brain.get_embedding(lost_item_path)

    # 5. Get the match score
    score = brain.compute_similarity(emb_found, emb_lost)

    print(f"\nMatch Results:")
    print(f"Similarity Score: {score:.4f}")
    
    if score > 0.75:
        print("Verdict: High probability of a match!")
    else:
        print("Verdict: Items do not appear to match.")

if __name__ == "__main__":
    main()
    """


"""Day 2 --- Task 2
def main():
    brain = BoomerangBrain()

    #Define the folder to scan
    found_folder = "data/found"

    print(f"---Scanning folder {found_folder}---")
    # 1. Get the paths
    paths = brain.get_found_images(found_folder)
    # 2. Bulk Encode 
    print(f"Generating embeddings for {len(paths)} items...")
    db = brain.encode_bulk(paths)
    # 3.Verification:
    for filename,vector in db.items():
        print(f" -> {filename} : Vector Shape {vector.shape}") #note len of every vector is 512 

if __name__ == "__main__":
    main()
    """


"""
        # Create 3 columns for a professional gallery look
        col1, col2, col3 = st.columns(3)

        with col1:
            st.image("https://placehold.co/200", caption="Match #1")
            st.metric("Confidence", "90.5%")
            
        with col2:
            st.image("https://placehold.co/200", caption="Match #2")
            st.metric("Confidence", "27.6%")
            
        with col3:
            st.image("https://placehold.co/200", caption="Match #3")
            st.metric("Confidence", "12.1%")
"""