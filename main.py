# -*- coding: utf-8 -*-
from pydantic_ai import Agent
import chromadb
import dotenv

dotenv.load_dotenv()  # GEMINI_API_KEY


class DB:
    collection_name = "docs"

    def __init__(self, name:str, docs: list[str]):
        self.db = chromadb.PersistentClient(path=name)
        if DB.collection_name not in [col.name for col in self.db.list_collections()]:
            self._feed(docs)

    def _feed(self, docs: list[str]):
        collection = self.db.create_collection(DB.collection_name)
        for i, text in enumerate(docs):
            collection.add(documents=[text], ids=[str(i)])

    def find(self, query: str, nb_docs: int = 2) -> list[str]:
        """recherche dans les documents disponibles, ceux qui te paraissent interessant pour la query 'query', retourne les documents"""
        qresult = self.db.get_collection(DB.collection_name).query(
            query_texts=[query], n_results=nb_docs
        )
        if qresult and "documents" in qresult and qresult["documents"]:
            docs_found = qresult["documents"][0]
        else:
            docs_found = []
        return docs_found


if __name__ == "__main__":
    docs = [
        "La Tour Eiffel est à Hong-Kong.",
        "Le Colisée est à Rome.",
        "La Statue de la Liberté se trouve à New York.",
        "La tour montparnasse est a bruxelles",
    ]

    db = DB("MyDB",docs)

    agent = Agent(
        model="gemini-2.5-flash",
        system_prompt="Tu es un assistant qui répond uniquement à partir du contexte fourni.",
        tools=[db.find],
    )

    response = agent.run_sync("Où se trouve la Tour montparnasse ?")
    print(response.output)
