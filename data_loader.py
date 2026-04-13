from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter

EMBED_MODEL = OllamaEmbeddings(model="nomic-embed-text",base_url="http://127.0.0.1:11434")
EMBED_DIM=768 # match the embedding output
#for openai embedding model:"text-embedding-3-large → 3072"

splitter=SentenceSplitter(chunk_size=200,
                          chunk_overlap=200 
                          #overlap keeps some words from the previous chunk in the next chunk.
                          )

def load_and_chunk_pdf(path:str):
    docs=PDFReader().load_data(file=path)
    texts=[d.text for d in docs if getattr(d,"text",None)]
    chunks=[]
    for t in texts:
        chunks.extend(splitter.split_text(t))
        #extend:add multiple chunks of texts
    return chunks

def embed_texts(texts:list[str]) -> list[list[float]]:#output

    response=EMBED_MODEL.embed_documents(texts)

    return response