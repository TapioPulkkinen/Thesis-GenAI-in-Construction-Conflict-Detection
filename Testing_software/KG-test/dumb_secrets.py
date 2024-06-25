
"""NOTE THAT IS NOT A CORRECT WAY TO STORE SECRETS LIKE API KEYS. THIS IS IMPLEMENT FOR TESTING PURPOSES ONLY"""

class DummyKeys:
    OPENAI_API_KEY = "sk-..."

class Neo4jSecrets:

    first_instance = {
        "NEO4J_URI": "neo4j+s://XXXXXXXX.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "pass"
    }

    second_instance = {
        "NEO4J_URI": "neo4j+s://XXXXXXXX.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "pass"
    }

