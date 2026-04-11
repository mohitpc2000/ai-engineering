import numpy as np
def cosine_similarity(veca,vecb):
    a = np.array(veca)
    b = np.array(vecb)
    dot_product = np.dot(a,b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

def find_most_similar(query_embedding, knowledge_base, top_k = 3):
    results = []
    for item in knowledge_base:
        score = cosine_similarity(query_embedding, item['embedding'])
        results.append((item['text'], score))
    results.sort(key = lambda x:x[1], reverse=True)
    return results[:top_k]
