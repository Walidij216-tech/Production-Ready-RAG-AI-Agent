import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime

load_dotenv()

from data_loader import load_and_chunk_pdf,embed_texts
from vector_db import QdrantStorage
from custom_types import RAGChunkAndSrc,RAGUpsertResult,RAGSearchResult,RAGQueryResult
from query_engine import OllamaAdapter

from langchain_ollama import ChatOllama
#call the inngest server:Create Inngest client
inngest_client=inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

#app_id → name of your project
#logger → uses FastAPI server logs (uvicorn)
#is_production=False → running locally
#serializer → handles data (Pydantic objects)


#the decorator of inngest function:Define an Inngest function

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(
  count=2,period=datetime.timedelta(minute=1)
),
# function can run at most 2 times per 1 minute
    rate_limit=inngest.RateLimit(
  limit=1,
  period=datetime.timedelta(hours=4),
  key="event.data.source_id"
)
# For each unique source_id, only 1 execution every 4 hours
)
#=“When event rag/ingest_pdf happens → run this function”
#inngest function
async def rag_ingest_pdf( ctx:inngest.Context):

  def _load(ctx: inngest.Context) -> RAGChunkAndSrc:

    pdf_path= ctx.event.data.get("pdf_path")
    source_id=ctx.event.data.get("source_id",pdf_path)
    chunks=load_and_chunk_pdf(pdf_path)
    return RAGChunkAndSrc(chunks=chunks,source_id=source_id)
    #pydantic model
  def _upsert(chunks_and_src:RAGChunkAndSrc) -> RAGUpsertResult:
    chunks=chunks_and_src.chunks
    source_id=chunks_and_src.source_id
    vecs=embed_texts(chunks)
    ids=[str(uuid.uuid5(uuid.NAMESPACE_URL,f"{source_id}:{i}")) for i in range (len(chunks))]
    #give for each chunk a unique id
    payloads= [{"source": source_id,"text": chunks[i]} for i in range(len(chunks))]
    QdrantStorage().upsert(ids,vecs,payloads)

    return RAGUpsertResult(ingested=len(chunks))

  #calling the steps in inngest
  chunks_and_src=await ctx.step.run("load-and-chunk",lambda:_load(ctx),output_type=RAGChunkAndSrc)
#load-and-chunk:step name
#lamba:_load(ctx):calling the function
  ingested= await ctx.step.run("embed-and-upsert",lambda: _upsert(chunks_and_src),output_type=RAGUpsertResult)

  return ingested.model_dump()#convert the pydantic variable into json or python dictionary

#inngest function for quering our vectordb

@inngest_client.create_function(
  fn_id="RAG: Query PDF",
  trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")

)

async def rag_query_pdf_ai(ctx: inngest.Context):
  
  def _search(question:str,top_k: int=5) -> RAGSearchResult:
    query_vec=embed_texts([question])[0]
    #embed_texts([question]):[[0.12, -0.98, 0.33, ..., 0.77]    embedding of your question]
    #embed_texts([question])[0]:[0.12, -0.98, 0.33, ..., 0.77]
    store=QdrantStorage()
    found=store.search(query_vec,top_k)
    return RAGSearchResult(contexts=found["contexts"],sources=found["sources"])

  question=ctx.event.data["question"]
  #question must be existed
  top_k=int(ctx.event.data.get("top_k",5))
  #top_k may or may not exist
  #if missing: use the 5 value default
  
  found=await ctx.step.run("embed-and-search",lambda: _search(question,top_k),output_type=RAGSearchResult)
  
  #join the contexts
  context_block= "\n \n".join(f"- {c}" for c in found.contexts)
  
  user_content=(
    "Use the following context to answer the question. \n\n"
    f"Context:\n{context_block}\n\n"
    f"Question: {question}\n"
  )
  
  llm=OllamaAdapter()
  answer = await ctx.step.run(
    "llm-answer",
    lambda: llm.call_ollama(user_content)
)


  return {"answer":answer,"sources": found.sources,"num_contexts": len(found.contexts)}
  #found["contexts"]:dict access
  #found.contexts: pydantic model access


app=FastAPI()

#serve the inngest server using the function inserted to run it locally
#Connect Inngest to FastAPI
inngest.fast_api.serve(app,inngest_client, [rag_ingest_pdf,rag_query_pdf_ai])

  #create an ai adapter=brigde between my the code and the llm will be used by sending him the prompt and gives us the result

  #adapter = OllamaAdapter(model="llama3.1", base_url="http://127.0.0.1:11434")
  #run an AI step inside Inngest
  #res= await ctx.step.ai.infer(

    #"llm-answer",
    #adapter=adapter,
    #body={
     # "max_tokens": 1024,
      #"temperature": 0.2,
      #"messages":[
      #  {"role":"system","content": "You answer questions using only the provided context."},
      #  {"role":"user","content":user_content}
     # ]
    #}
 # )
 #the LLM response like:
 #res = {
    #"choices": [
     #   {
      #      "message": {
       #         "content": "Final answer here..."
        #    }
        #}
    #]
#}
  #answer= res["choices"][0]["message"]["content"].strip()