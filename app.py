from core import BoomerangBrain
import os

def main():
    brain = BoomerangBrain()

    # prepare databse with found items
    found_folder = "data/found"
    found_paths = brain.get_found_images(found_folder)
    found_db = brain.encode_bulk(found_paths)

    #create faiss api
    filenames = brain.create_faiss_index(found_db)
    print("FAISS Index created and saved as 'items.index'")

    # Process the Lost item photo
    lost_item_path = "data/lost/test_lost.jpg" 
    print(f"\nSearching for item: {lost_item_path}...")
    lost_vector = brain.get_embedding(lost_item_path)

    # Do the SEARCH
    matches = brain.search_faiss(lost_vector , filenames)

    # Display the results:
    print("\n--- Top Boomerang Matches ---")
    for filename, score in matches[:3]:
        print(f"Match: {filename} | Confidence: {score:.4f}")

if __name__ == "__main__":
    main()