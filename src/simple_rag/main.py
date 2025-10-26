# -*- coding: utf-8 -*-
from pydantic_ai import Agent
import dotenv
from .rag_db import DB
import os

dotenv.load_dotenv()  # GEMINI_API_KEY

if __name__ == "__main__":
    db = DB("MyDB")

    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    db.feed_file(os.path.join(project_root, "example.md"))
    db.feed_file(os.path.join(project_root, "README.md"))

    agent = Agent(
        model="gemini-1.5-flash",
        system_prompt="Tu es un assistant qui répond uniquement à partir du contexte fourni.",
        tools=[db.find],
    )

    print(db)

    response = agent.run_sync("how to display the output of a command ?")
    print(response.output)
