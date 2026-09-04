import sys
sys.path.insert(0, '.')
from app.domains import get_anchor_store
from app.providers.embeddings import get_embedding_provider

store = get_anchor_store()
provider = get_embedding_provider()

eng_query = "Regarding Gujarat's agriculture, my cotton crop has been spoiled. What should I do now?"
embedding = provider.embed_texts([eng_query], task="retrieval.query")[0]
domain, score = store.classify(eng_query, embedding)
print(f"Domain: {domain}, Score: {score}")

# Also test the second query
eng_query2 = "Rajkot APMC groundnut market price today"
embedding2 = provider.embed_texts([eng_query2], task="retrieval.query")[0]
domain2, score2 = store.classify(eng_query2, embedding2)
print(f"Domain: {domain2}, Score: {score2}")
