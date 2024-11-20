import os
from aidevs import send_task, answer_question_local

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

def get_database_structure():
    """
    Get the database structure including tables and their schemas
    """
    # Get list of tables
    result = query_database("show tables")
    tables = [item['Tables_in_banan'] for item in result['reply']]
    print(f"Tables: {tables}")
    # Get structure for each table
    structure = {}
    for table_name in tables:
        create_table = query_database(f"show create table {table_name}")
        structure[table_name] = create_table['reply'][0]  # Assuming CREATE TABLE statement is in second column
        print(f"{structure[table_name]=}")        
    return structure

def main():
    # Get database structure
    db_structure = get_database_structure()
    
    # Create prompt for the LLM to generate the SQL query
    prompt = f"""
    Given these table structures:
    {db_structure}
    
    Write an SQL query to find active datacenter IDs (DC_ID) that are managed by employees who are on leave (is_active=0).
    Only return the SQL query, nothing else.
    """
    
    # Get SQL query from LLM
    sql_query = answer_question_local(prompt)
    print(f"Generated SQL query: {sql_query}")
    
    # Execute the query
    result = query_database(sql_query)
    
    # Extract DC_IDs from result
    dc_ids = [row['dc_id'] for row in result['reply']]  # Assuming DC_ID is the first column
    
    # Send answer to the task using default URL
    send_task("database", dc_ids)

if __name__ == "__main__":
    main() 