import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from aidevs import get_embedding, send_task, answer_question_local
from tabulate import tabulate

def evaluate_relevance(content: str, query: str) -> float:
    """
    Use LLM to evaluate how relevant the document is to the query.
    Returns a score between 0 and 1.
    """
    prompt = """Oceń jak dobrze ten dokument pasuje do pytania.
    Zwróć tylko liczbę z zakresu 0-1, gdzie:
    1 = dokument jest w 100% związany z pytaniem
    0 = dokument nie ma nic wspólnego z pytaniem
    
    Pytanie: {query}
    
    Dokument: {content}
    
    Wynik (0-1):"""
    
    response = answer_question_local(
        prompt.format(query=query, content=content),
        model='gemma2:27b',
        stream=False
    )
    
    try:
        print(f"LLM score: {response}")
        score = float(response.strip())
        return min(max(score, 0), 1)  # Ensure score is between 0 and 1
    except:
        return 0.0

def search_documents(query: str) -> str:
    """Search documents in Qdrant and return date from best matching document"""
    
    # Get embedding for query
    query_embedding = get_embedding(query)
    
    # Initialize Qdrant client
    api_key = os.getenv('QDRANT_API_KEY')
    qdrant_url = os.getenv('QDRANT_URL')
    
    if not api_key:
        raise ValueError("QDRANT_API_KEY environment variable not set")
    if not qdrant_url:
        raise ValueError("QDRANT_URL environment variable not set")
    
    client = QdrantClient(
        qdrant_url,
        api_key=api_key
    )
    
    # Search for 5 most similar documents
    search_result = client.search(
        collection_name="factory_documents",
        query_vector=query_embedding,
        limit=5
    )
    
    if not search_result:
        raise ValueError("No matching documents found")
    
    # Evaluate each document's relevance
    evaluated_results = []
    for match in search_result:
        llm_score = evaluate_relevance(match.payload['content'], query)
        combined_score = (match.score + llm_score) / 2  # Average of vector similarity and LLM score
        evaluated_results.append((match, combined_score))
    
    # Sort by combined score
    evaluated_results.sort(key=lambda x: x[1], reverse=True)
    
    # Prepare table data
    table_data = []
    headers = ["Rank", "Date", "Weapon Name", "Vector Score", "LLM Score", "Combined Score"]
    
    for i, (match, combined_score) in enumerate(evaluated_results, 1):
        date = match.payload['date'].split('T')[0]  # Convert to YYYY-MM-DD
        llm_score = (combined_score * 2) - match.score  # Extract LLM score from combined score
        table_data.append([
            i,
            date,
            match.payload['weapon_name'],
            f"{match.score:.4f}",
            f"{llm_score:.4f}",
            f"{combined_score:.4f}"
        ])
    
    # Print table
    print("\nSearch Results:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Print content of best match
    best_match = evaluated_results[0][0]
    print(f"\nBest matching document content:")
    print("-" * 80)
    print(best_match.payload['content'][:80])
    print("-" * 80)
    
    return best_match.payload['date']

def main():
    """Main function to search for document about weapon prototype theft"""
    query = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
    
    try:
        date = search_documents(query)
        print(f"\nBest matching date: {date}")
        
        # Convert ISO date to YYYY-MM-DD format
        formatted_date = date.split('T')[0]
        # Send answer to task
        send_task("wektory", formatted_date)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 