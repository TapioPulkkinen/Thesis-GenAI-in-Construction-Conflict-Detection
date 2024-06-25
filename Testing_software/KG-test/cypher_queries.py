

class ModelCypherQueries:
    node_properties_query = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    RETURN {labels: nodeLabels, properties: properties} AS output
    """

    rel_properties_query = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
    WITH label AS nodeLabels, collect({property:property, type:type}) AS properties
    RETURN {type: nodeLabels, properties: properties} AS output
    """

    rel_query = """
    CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE type = "RELATIONSHIP" AND elementType = "node"
    UNWIND other AS other_node
    RETURN {start: label, type: property, end: toString(other_node)} AS output
    """


class OwnCypherQueries:
    clear_db = """
    CALL apoc.periodic.iterate(
    "MATCH (n) RETURN n",
    "DETACH DELETE n",
    {batchSize: 10000, parallel: true}
    )
    """

    return_all = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m) 
    RETURN n, r, m
    """

    clear_db_cypher_only = """
    MATCH (n)
    DETACH DELETE n
    """