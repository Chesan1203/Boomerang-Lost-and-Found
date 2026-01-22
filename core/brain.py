from sentence_transformers import SentenceTransformer , util
from PIL import Image
import torch
import os
import faiss
import numpy as np

class BoomerangBrain:
    def __init__(self, model_name='clip-ViT-B-32'):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name).to(self.device)

    def get_embedding(self, image_path):
        img = Image.open(image_path)
        return self.model.encode(img, convert_to_tensor=True)
    
    def get_found_images(self, folder_path):
        """
        Scans the folder and returns a list of paths for all images.
        """
        valid_extensions = ('.jpg', '.jpeg', '.png')
        image_paths = []

        # List all files in the directory
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_extensions):
                # Construct the full path: data/found/item.jpg
                full_path = os.path.join(folder_path, filename)
                image_paths.append(full_path)
        
        return image_paths
    
    def encode_bulk(self, image_paths):
        database = {}
        for path in image_paths:
            filename = os.path.basename(path)
            vector = self.get_embedding(path)
            database[filename] = vector # Store it in our temporary 'database' - a dict with filenmae: corresponding vector
        return database
    
    def search(self, lost_vector, database):
        """
        Compares a lost vector against the database of found vectors and
        Returns a list of (filename, score) sorted by highest score.
        """
        results=[]
        for filename,found_vector in database.items():
            # Calculate similarity between the lost item and this found item
            score = self.compute_similarity(lost_vector , found_vector)
            results.append((filename, score))
        # Sort the results so the highest score is at the top
        results.sort(key=lambda x: x[1], reverse=True)
        return results


    def compute_similarity(self, emb1, emb2):
        return util.cos_sim(emb1, emb2).item()
    
    def create_faiss_index(self,database):
        """Converts the dictionary of vectors into a FAISS index file."""
        #1. extract all vectors in db and convert them to np array
        # FAISS requires a specific mathematical format - is extremely picky and only accepts 32-bit floating-point numbers.
        filenames = list(database.keys())
        vectors = np.array([v.cpu().numpy() for v in database.values()]).astype('float32')
        
        # 2. Reshape vectors if they have an extra dimension
        if len(vectors.shape) == 3:
            vectors = vectors.reshape(vectors.shape[0], -1)

        # 3. Create the index (512 is the dimension of CLIP vectors)
        faiss.normalize_L2(vectors)
        index = faiss.IndexFlatIP(512) # Inner Product is used for Cosine Similarity
        index.add(vectors)
        
        # 4. Save the index and the filename mapping
        faiss.write_index(index, "items.index")
        return filenames

    def search_faiss(self, lost_vector, filenames, top_k=3):
        """
        Searches the .index file for the closest matches.
        """
        # Load the index
        index = faiss.read_index("items.index")
        
        # Prepare the search vector
        query_vector = lost_vector.cpu().numpy().astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_vector)

        # Search! 'D' is distances, 'I' is indices
        distances, indices = index.search(query_vector, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1: # FAISS returns -1 if no match found
                results.append((filenames[idx], distances[0][i]))
        
        return results
    
    def get_text_embedding(self, text_query):
        """Converts a string of text into a normalized CLIP vector using SentenceTransformers."""
        # SentenceTransformers handles tokenization and 'no_grad' automatically
        # We just pass the string directly to .encode()
        text_features = self.model.encode(text_query, convert_to_tensor=True)
        
        # Ensure it is a 2D tensor (1, 512) for FAISS consistency
        if len(text_features.shape) == 1:
            text_features = text_features.unsqueeze(0)
            
        return text_features