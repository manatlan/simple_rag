# -*- coding: utf-8 -*-
import chromadb
from typing import List, Optional
import hashlib
from collections import Counter
from pydantic import BaseModel, Field

from .utils import split_markdown

class SearchResult(BaseModel):
    """Pydantic model for a structured search result."""
    source: str = Field(..., description="The source of the document chunk.")
    content: str = Field(..., description="The content of the document chunk.")


class DB:
    def __init__(self, path: str):
        self._name = path
        db = chromadb.PersistentClient(path=self._name)
        self.collection = db.get_or_create_collection("docs")

    def _get_embedding(self, text: str):
        # Let ChromaDB handle embedding generation
        return None

    def feed_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.feed(file_path, content)

    def feed(self, source: str, content: str, chunk_size: int = 1000, overlap: int = 200):
        chunks = split_markdown(content, chunk_size, overlap)
        metadatas = [{"source": source} for _ in chunks]

        if not chunks:
            return

        ids = [hashlib.md5(text.encode()).hexdigest() for text in chunks]
        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)


    def find(self, query: str, nb_docs: int = 2) -> List[SearchResult]:
        """recherche dans les documents disponibles, ceux qui te paraissent interessant pour la query 'query', retourne les documents"""
        qresult = self.collection.query(query_texts=[query], n_results=nb_docs)

        docs_found = []
        if qresult and "documents" in qresult and qresult["documents"]:
            for i, doc in enumerate(qresult["documents"][0]):
                metadata = qresult["metadatas"][0][i]
                if metadata:
                    docs_found.append(SearchResult(source=metadata.get("source", "Unknown"), content=doc))
        return docs_found

    def __repr__(self):
        sources = self.collection.get().get("metadatas", [])
        c = Counter(item['source'] for item in sources)
        return f"<DB:{self._name} {c}>"
