from neo4j import GraphDatabase, exceptions
from typing import Any, Dict, List, Optional
from cypher_queries import ModelCypherQueries, OwnCypherQueries


class Neo4jConnector:

    def __init__(self, uri, user, password, database="neo4j", read_only=False):
        self._read_only = read_only
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._database = database
        self.schema: str = ""
        self.structured_schema: Dict[str, Any] = {}

        # Verify connection
        try:
            self._driver.verify_connectivity()
        except exceptions.ServiceUnavailable:
            raise ValueError("Could not connect to Neo4j database. Please ensure that the url is correct")
        except exceptions.AuthError:
            raise ValueError("Could not connect to Neo4j database. Please ensure that the username and password are correct")
        # Set schema
        try:
            self.refresh_schema()
        except exceptions.ClientError:
            raise ValueError("Could not use APOC procedures. "
                             "Please ensure the APOC plugin is installed in Neo4j and that "
                             "'apoc.meta.data()' is allowed in Neo4j configuration ")

    def close(self):
        """Close the Neo4j connection."""
        if not self._is_connection_open():
            self._driver.close()
            self._driver = None

    def _is_connection_open(self):
        """Check if the Neo4j connection is open."""
        try:
            self._driver.verify_connectivity()
            return True if self._driver is not None else False
        except:
            return False

    def get_schema(self) -> str:
        """Returns the schema of the Graph"""
        return self.schema

    @staticmethod
    def _execute_read_only_query(tx, cypher_query: str, params: Optional[Dict] = {}):
        result = tx.run(cypher_query, params)
        return [r.data() for r in result]

    def query(self, cypher_query: str, params: dict = {}) -> List[Dict[str, Any]]:
        """Query Neo4j database."""

        with self._driver.session(database=self._database) as session:
            try:
                if self._read_only:
                    result = session.read_transaction(self._execute_read_only_query, cypher_query, params)
                    return result
                else:
                    result = session.run(cypher_query, params)
                    return [r.data() for r in result]

            # Catch Cypher syntax errors
            except exceptions.CypherSyntaxError as e:
                return [{"code": "invalid_cypher",
                        "message": f"Invalid Cypher statement due to an error: {str(e)}"}]

            except exceptions.ClientError as e:
                # Catch access mode errors
                if e.code == "Neo.ClientError.Statement.AccessMode":
                    return [{"code": "error",
                            "message": "Couldn't execute the query due to the read only access to Neo4j"}]
                else:
                    return [{"code": "error", "message": str(e)}]

    def get_structured_schema(self) -> Dict[str, Any]:
        """Returns the structured schema of the Graph"""
        return self.structured_schema

    def refresh_schema(self) -> None:
        """
        Refreshes the Neo4j graph schema information.
        """
        node_properties = [el["output"] for el in self.query(ModelCypherQueries.node_properties_query)]
        rel_properties = [el["output"] for el in self.query(ModelCypherQueries.rel_properties_query)]
        relationships = [el["output"] for el in self.query(ModelCypherQueries.rel_query)]

        self.structured_schema = {
            "node_props": {el["labels"]: el["properties"] for el in node_properties},
            "rel_props": {el["type"]: el["properties"] for el in rel_properties},
            "relationships": relationships}

        # Format node properties
        formatted_node_props = []
        for el in node_properties:
            props_str = ", ".join([f"{prop['property']}: {prop['type']}" for prop in el["properties"]])
            formatted_node_props.append(f"{el['labels']} {{{props_str}}}")

        # Format relationship properties
        formatted_rel_props = []
        for el in rel_properties:
            props_str = ", ".join([f"{prop['property']}: {prop['type']}" for prop in el["properties"]])
            formatted_rel_props.append(f"{el['type']} {{{props_str}}}")

        # Format relationships
        formatted_rels = [f"(:{el['start']})-[:{el['type']}]->(:{el['end']})" for el in relationships]

        self.schema = "\n".join([
                "Node properties are the following:",
                ",".join(formatted_node_props),
                "Relationship properties are the following:",
                ",".join(formatted_rel_props),
                "The relationships are the following:",
                ",".join(formatted_rels)])

    def process_json(self, data_json, batch_size=1000):
        """Process the JSON data to add nodes and relationships to the Neo4j database in batches."""
        unique_nodes = set()
        relationships = data_json['relationships']

        # Temporarily store nodes and relationships to batch insert later
        nodes_to_add = []
        relationships_to_add = []

        # Collect all unique nodes and relationships
        for relationship in relationships:
            from_node = relationship['from_node']
            to_node = relationship['to_node']

            if (from_node['text'], from_node['type']) not in unique_nodes:
                nodes_to_add.append(from_node)
                unique_nodes.add((from_node['text'], from_node['type']))

            if (to_node['text'], to_node['type']) not in unique_nodes:
                nodes_to_add.append(to_node)
                unique_nodes.add((to_node['text'], to_node['type']))

            relationships_to_add.append(relationship)

        # Process nodes and relationships in batches
        with self._driver.session(database=self._database) as session:
            for i in range(0, len(nodes_to_add), batch_size):
                batch_nodes = nodes_to_add[i:i + batch_size]
                session.write_transaction(self._add_nodes_batch, batch_nodes)

            for i in range(0, len(relationships_to_add), batch_size):
                batch_relationships = relationships_to_add[i:i + batch_size]
                session.write_transaction(self._add_relationships_batch, batch_relationships)

    def _add_nodes_batch(self, tx, nodes):
        """Add a batch of nodes using a single transaction."""
        for node in nodes:
            cypher_query = """
            CALL apoc.merge.node(
                [$type], 
                {text: $text}
            )
            """
            tx.run(cypher_query, node)

    def _add_relationships_batch(self, tx, relationships):
        """Add a batch of relationships using a single transaction."""
        for rel in relationships:
            cypher_query = """
            MATCH (a {text: $from_text}), (b {text: $to_text})
            CALL apoc.merge.relationship(
                a, 
                $rel_type, 
                {}, 
                {},
                b
            )
            YIELD rel
            RETURN rel
            """
            tx.run(cypher_query, {
                "from_text": rel["from_node"]["text"],
                "to_text": rel["to_node"]["text"],
                "rel_type": rel["type"]
            })

    def add_node(self, node_data):
        """Add a new node to the Neo4j database using APOC."""
        print("Adding node")
        cypher_query = """
        CALL apoc.merge.node(
            [apoc.util.sanitize($type)], 
            {text: $text}
        )
        """
        params = {"type": node_data["type"], "text": node_data["text"]}
        self.query(cypher_query, params)

    def add_relationship(self, rel_json):
        """Add a new relationship to the Neo4j database using APOC."""
        print("Adding rel")
        cypher_query = """
        MATCH (a {text: $from_text}), (b {text: $to_text})
        CALL apoc.merge.relationship(
            a, 
            apoc.util.sanitize($rel_type), 
            {}, 
            {},
            b
        )
        YIELD rel
        RETURN rel
        """
        params = {
            "from_text": rel_json["from_node"]["text"],
            "to_text": rel_json["to_node"]["text"],
            "rel_type": rel_json["type"]
        }
        self.query(cypher_query, params)

    def clear_database(self):
        """Clear the entire Neo4j database."""

        with self._driver.session(database=self._database) as session:
            try:
                data = session.run(query=OwnCypherQueries.clear_db)
                print("Database cleared successfully!\n")
                return []
            except exceptions.CypherSyntaxError as e:
                raise ValueError(f"Generated Cypher Statement is not valid for clearing database\n{e}")
            except Exception as e:
                raise Exception(f"This happened while clearing db: {e}")