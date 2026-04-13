import pydantic


class RAGChunkAndSrc(pydantic.BaseModel):
    chunks:list[str]
    source_id: str=None


class RAGUpsertResult(pydantic.BaseModel):
    ingested: int
#ingested=number of points from upsert method (derived from the input : point:(id,vector,payload))

class RAGSearchResult(pydantic.BaseModel):
    contexts:list[str]
    sources:list[str]


class RAGQueryResult(pydantic.BaseModel):
    answer: str
    sources: list[str]
    num_contexts: int