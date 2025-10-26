# -*- coding: utf-8 -*-
from pydantic_ai import Agent
import chromadb
import re
import dotenv
from typing import List, Optional, Callable
import hashlib
from collections import Counter

dotenv.load_dotenv()  # GEMINI_API_KEY

def split_markdown(markdown_text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Splits a markdown text by headers and paragraphs with sentence-based overlap."""
    # Split by headers
    header_splits = re.split(r'(^#+\s.*)', markdown_text, flags=re.MULTILINE)

    chunks = []

    # Process the splits to form chunks
    for i in range(1, len(header_splits), 2):
        header = header_splits[i]
        content = header_splits[i+1]

        # Further split content by paragraphs
        paragraphs = content.split('\n\n')
        current_chunk = header

        for p in paragraphs:
            if len(current_chunk) + len(p) > chunk_size:
                chunks.append(current_chunk)
                # Sentence-based overlap
                sentences = current_chunk.split('. ')
                overlap_text = ". ".join(sentences[-2:]) if len(sentences) > 1 else sentences[0]
                current_chunk = overlap_text + '\n\n' + p
            else:
                current_chunk += '\n\n' + p

        if current_chunk:
            chunks.append(current_chunk)

    # Handle the case where there are no headers
    if not chunks and markdown_text:
        paragraphs = markdown_text.split('\n\n')
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) > chunk_size:
                chunks.append(current_chunk)
                sentences = current_chunk.split('. ')
                overlap_text = ". ".join(sentences[-2:]) if len(sentences) > 1 else sentences[0]
                current_chunk = overlap_text + '\n\n' + p
            else:
                current_chunk += '\n\n' + p
        if current_chunk:
            chunks.append(current_chunk)

    return [c.strip() for c in chunks if c.strip()]



from pydantic import BaseModel, Field
class SearchResult(BaseModel):
    """Pydantic model for a structured search result."""
    source: str = Field(..., description="The source of the document chunk.")
    content: str = Field(..., description="The content of the document chunk.")


class DB:
    def __init__(self, name:str):
        self._name=name
        db = chromadb.PersistentClient(path=self._name)
        self.collection = db.get_or_create_collection("docs")

    def _get_embedding(self,text: str):
        # if self.embedding_model == "openai":
        #     response = self.openai_client.embeddings.create(
        #         input=text,
        #         model="text-embedding-ada-002"
        #     )
        #     return response.data[0].embedding
        return None  # Let ChromaDB handle it

    def feed(self, source:str, content:str,chunk_size: int = 1000, overlap: int = 200):
        chunks = split_markdown(content, chunk_size, overlap)
        metadatas = [{"source": source} for _ in chunks]

        def feed_chunks(docs: List[str], metadatas: Optional[List[dict]] = None):
            for i, text in enumerate(docs):
                doc_id = hashlib.md5(text.encode()).hexdigest()
                embedding = self._get_embedding(text)
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                if embedding:
                    self.collection.add(documents=[text], ids=[doc_id], metadatas=[metadata], embeddings=[embedding])
                else:
                    self.collection.add(documents=[text], ids=[doc_id], metadatas=[metadata])

        feed_chunks(chunks, metadatas)

    def find(self, query: str, nb_docs: int = 2) -> List[SearchResult]:
        """recherche dans les documents disponibles, ceux qui te paraissent interessant pour la query 'query', retourne les documents"""

        query_embedding = self._get_embedding(query)
        if query_embedding:
            qresult = self.collection.query(query_embeddings=[query_embedding], n_results=nb_docs)
        else:
            qresult = self.collection.query(query_texts=[query], n_results=nb_docs)

        docs_found = []
        if qresult and "documents" in qresult and qresult["documents"]:
            for i, doc in enumerate(qresult["documents"][0]):
                metadata = qresult["metadatas"][0][i]
                if metadata:
                    docs_found.append(SearchResult(source=metadata.get("source", "Unknown"), content=doc))
        return docs_found

    def __repr__(self):
        sources = self.collection.get().get("metadatas",[])
        c=Counter([item['source'] for item in sources])
        return f"<DB:{self._name} {c}>"

if __name__ == "__main__":
    db = DB("MyDB")
    db.feed("example.md",open("example.md").read())
    db.feed("README.md",open("README.md").read())
    
    agent = Agent(
        model="gemini-2.5-flash",
        system_prompt="Tu es un assistant qui répond uniquement à partir du contexte fourni.",
        tools=[db.find],
    )

    print(db)

    response = agent.run_sync("how to display the output of a command ?")
    print(response.output)
