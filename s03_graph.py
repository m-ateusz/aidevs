import os
from aidevs import send_task, answer_question_local
import json

def get_db_url():
    """Get database URL from base URL"""
    base_url = os.getenv('AIDEVS_BASE_URL')
    if not base_url:
        raise EnvironmentError("AIDEVS_BASE_URL not found in environment variables")
    return f"{base_url}/apidb"

DB_URL = get_db_url()

def query_database(query: str) -> dict:
    """
    Execute a query against the database API
    """
    return send_task("database", query, url=DB_URL, payload_name="query")

from neo4j import GraphDatabase

# Function to create a session and insert data into the Neo4j database
class GraphDatabaseHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_nodes_and_edges(self, nodes, edges):
        with self.driver.session() as session:
            # Create nodes
            for node in nodes:
                session.execute_write(self._create_node, node["id"], node["username"], node["access_level"], node["is_active"], node["lastlog"])
            
            # Create edges
            for edge in edges:
                session.execute_write(self._create_edge, edge["user1_id"], edge["user2_id"])
    
    def find_shortest_path(self, start_name, end_name):
        with self.driver.session() as session:
            result = session.execute_read(self._shortest_path_query, start_name, end_name)
            return result
    
    @staticmethod
    def _shortest_path_query(tx, start_name, end_name):
        query = """
        MATCH p = shortestPath((a:Node {username: $start_name})-[:CONNECTED_TO*]-(b:Node {username: $end_name}))
        RETURN [n IN nodes(p) | n.username] AS path
        """
        result = tx.run(query, start_name=start_name, end_name=end_name)
        record = result.single()
        if record:
            return record["path"]
        return None
    
    @staticmethod
    def _create_node(tx, id, username, access_level, is_active, lastlog):
        query = """
        MERGE (n:Node {id: $id})
        SET n.username = $username
        SET n.access_level = $access_level
        SET n.is_active = $is_active
        SET n.lastlog = $lastlog
        """
        tx.run(query, id=id, username=username, access_level=access_level, is_active=is_active, lastlog=lastlog)
    
    @staticmethod
    def _create_edge(tx, from_id, to_id):
        query = """
        MATCH (a:Node {id: $from_id}), (b:Node {id: $to_id})
        MERGE (a)-[:CONNECTED_TO]->(b)
        """
        tx.run(query, from_id=from_id, to_id=to_id)


def main():
    # nodes = query_database("select * from users")['reply']
    # edges = query_database("select * from connections")['reply']

    # Connection details for Neo4j
    uri = "neo4j+s://<redacted>.databases.neo4j.io"
    user = "neo4j"  # Default user
    password = "<redacted>"  # Replace with your password
    handler = GraphDatabaseHandler(uri, user, password)
    try:
        # handler.create_nodes_and_edges(nodes, edges)
        # print("Graph data successfully stored in Neo4j!")

        result = handler.find_shortest_path("Rafał", "Barbara")
        answer = ", ".join(result)
        print(answer)
        # Send answer to the task using default URL
        print(send_task("connections", answer))
    finally:
        handler.close()

if __name__ == "__main__":
    main() 