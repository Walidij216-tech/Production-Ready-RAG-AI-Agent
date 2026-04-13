from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams,Distance,PointStruct


class QdrantStorage:
    def __init__(self,url="http://localhost:6333",collection="docs",dim=768):
        # Create a client to connect to Qdrant server
        self.client=QdrantClient (url=url,timeout=30)
        self.collection=collection
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
            # Define how vectors are stored:
            # size = dimension of embeddings (e.g., 3072 for some LLM embeddings)
            # distance = similarity metric (COSINE = most common for embeddings)

                vectors_config=VectorParams(size=dim,distance=Distance.COSINE)
            )
    def upsert(self,ids,vectors,payloads):
        # Build a list of "points" to send to Qdrant
        # Each point = (id, vector, metadata)
        points=[PointStruct(id=ids[i],vector=vectors[i],payload=payloads[i]) for i in range(len(ids))]
        # Insert or update the points in the collection
        # If ID exists → update
        # If ID does not exist → insert
        self.client.upsert(self.collection,points=points)
    
    def search(self,query_vector,top_k:int=5):
        results=self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k
        )

        points = results.points
        contexts=[]
        sources=set()
        #print("Results from Qdrant:", results)
 
        for r in points:
            #print(type(r), r)
            #print("ID:", r.id, "Score:", getattr(r, "score", None), "Payload:", getattr(r, "payload", {}))

            payload = r.payload or {}
            print(payload)
            text=payload.get("text","")
            print(text)
            source=payload.get("source","")
            print(source)
            if text:
                contexts.append(text)
                sources.add(source)
        print(contexts)
        print(sources)
            
        return{"contexts":contexts,"sources":list(sources)}