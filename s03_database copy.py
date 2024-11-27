import os
from aidevs import answer_question_openai, send_task, answer_question_local
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

def extract_data_with_llm(json_response: dict, extraction_prompt: str) -> list:
    """
    Use local LLM to extract data from JSON response based on the prompt
    """
    prompt = f"""
    Given this JSON response:
    {json.dumps(json_response, indent=2)}
    
    {extraction_prompt}
    
    Return only the extracted data as comma separated values, nothing else, only data without keys, do not write a program, just process the data.
    """
    
    result = answer_question_local(prompt)
    print(f"{result=}")
    return result

def get_database_structure():
    """
    Get the database structure including tables and their schemas
    """
    # Get list of tables
    result = query_database("show tables")
    
    # Extract table names using LLM
    tables = extract_data_with_llm(
        result,
        "Extract all table names from this response. Return them as a Python list of strings."
    )
    print(f"{tables=}")
    
    # Get structure for each table
    structure = {}
    for table_name in tables.split(','):
        create_table = query_database(f"show create table {table_name}")
        # Extract create table statement using LLM
        table_structure = extract_data_with_llm(
            create_table,
            "Extract only the CREATE TABLE statement from this response object. Return it as a single string, without any additional text or formatting."
        )
        print(f"{table_structure=}")
        if table_structure:
            structure[table_name] = table_structure
        print(f"Structure for {table_name}: {structure[table_name]}")
    print(f"{structure=}")
    
    return structure

def main():
    # Get database structure
    db_structure = get_database_structure()
    
    # Create prompt for the LLM to generate the SQL query
    prompt = f"""
    Given these table structures:
    {db_structure}
    
    
    Write an SQL query to find the flag for a capture the flag game with the hint: 'Wszystko jest w porządku, także dane'. The whole flag looks like '{"{{FLG:<somestring>}}"}'
    Return only the query, nothing else. DO NOT embed the query in code coloring!
    """
    #  It should be sorted by weight (as number), ignore ids.
    # Get SQL query from LLM
    sql_query = answer_question_openai(prompt, max_tokens=100,
                                       model="gpt-4o", system_prompt="You are a SQL expert. You write only simple SQL queries, nothing else. No formatting, no comments, no explanations, only the query. Use table names, no aliases.")
    print(f"Generated SQL query: {sql_query}")
    
    # Execute the query
    result = query_database(sql_query)
    
    # Extract DC_IDs using LLM
    dc_ids = extract_data_with_llm(
        result,
        """Extract the value of this response. Return it as text."""
    )
    
    # Send answer to the task using default URL
    send_task("database", dc_ids)

if __name__ == "__main__":
    main() 