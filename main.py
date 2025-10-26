# -*- coding: utf-8 -*-
from pydantic_ai import Agent
import dotenv
from src.simple_rag.rag_db import DB
import os

dotenv.load_dotenv()  # GEMINI_API_KEY

if __name__ == "__main__":
    db = DB("MyDB")

    # db.feed_file( "example.md")
    # db.feed_file( "README.md")

    agent = Agent(
        model="gemini-2.5-flash",
        system_prompt="Tu es un assistant qui répond uniquement à partir du contexte fourni.",
        tools=[db.find],
    )

    print(db)

    response = agent.run_sync("how to display the output of a command ?")
    print(response.output)
