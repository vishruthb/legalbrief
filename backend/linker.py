from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import Dict, List, Tuple

class ArgumentLinker:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.6

    def get_embeddings(self, text: str) -> np.ndarray:
        """
        Generate embeddings for text using sentence transformer
        """
        return self.model.encode(text, convert_to_tensor=True)

    def find_matching_phrases(self, text1: str, text2: str) -> List[Tuple[str, str]]:
        """
        Find similar phrases between two texts
        """
        # Split texts into sentences
        sentences1 = text1.split('. ')
        sentences2 = text2.split('. ')
        
        matches = []
        
        # Get embeddings for all sentences
        embeddings1 = self.model.encode(sentences1)
        embeddings2 = self.model.encode(sentences2)
        
        # Calculate similarity matrix
        similarities = cosine_similarity(embeddings1, embeddings2)
        
        # Find top matching sentences
        for i, row in enumerate(similarities):
            max_idx = np.argmax(row)
            if row[max_idx] > self.similarity_threshold:
                matches.append((sentences1[i], sentences2[max_idx]))
        
        return matches[:3]  # Return top 3 matching pairs

def link_arguments(moving_brief: Dict, response_brief: Dict) -> List[Dict]:
    """
    Link arguments between moving and response briefs
    """
    linker = ArgumentLinker()
    links = []
    
    for moving_arg in moving_brief["arguments"]:
        moving_text = f"{moving_arg['heading']} {moving_arg['content']}"
        moving_embedding = linker.get_embeddings(moving_text)
        
        for response_arg in response_brief["arguments"]:
            response_text = f"{response_arg['heading']} {response_arg['content']}"
            response_embedding = linker.get_embeddings(response_text)
            
            # Calculate similarity
            similarity = cosine_similarity(
                moving_embedding.reshape(1, -1),
                response_embedding.reshape(1, -1)
            )[0][0]
            
            if similarity > linker.similarity_threshold:
                # Find specific matching phrases
                matching_phrases = linker.find_matching_phrases(
                    moving_arg['content'],
                    response_arg['content']
                )
                
                links.append({
                    "moving_brief_heading": moving_arg["heading"],
                    "response_brief_heading": response_arg["heading"],
                    "similarity_score": float(similarity),
                    "matching_phrases": matching_phrases,
                    "explanation": generate_explanation(similarity, matching_phrases)
                })
    
    return links

def generate_explanation(similarity_score: float, matching_phrases: List[Tuple[str, str]]) -> str:
    """
    Generate a human-readable explanation for the link
    """
    explanation = f"Similarity score: {similarity_score:.2f}\n\n"
    explanation += "Key matching concepts:\n"
    
    for moving_phrase, response_phrase in matching_phrases:
        explanation += f"- Moving brief: '{moving_phrase}'\n"
        explanation += f"  Response: '{response_phrase}'\n"
    
    return explanation
