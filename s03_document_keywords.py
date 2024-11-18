import os
import json
from pathlib import Path
from typing import List, Dict
from aidevs import answer_question_local, answer_question_openai, send_task

def load_facts(facts_dir: str) -> str:
    """
    Loads all facts from text files in the facts directory.
    
    Parameters:
    - facts_dir (str): Path to the directory containing fact files
    
    Returns:
    - str: Concatenated facts as a single string
    """
    facts = []
    facts_path = Path(facts_dir)
    
    for file in facts_path.glob("*.txt"):
        print(f"Loading facts from {file}")
        with open(file, 'r', encoding='utf-8') as f:
            facts.append(f.read().strip())
            
    return " ".join(facts)

def load_factory_reports(reports_dir: str) -> Dict[str, str]:
    """
    Loads factory report files.
    
    Parameters:
    - reports_dir (str): Path to the directory containing report files
    
    Returns:
    - Dict[str, str]: Dictionary mapping filenames to their contents
    """
    reports = {}
    reports_path = Path(reports_dir)
    
    for file in reports_path.glob("*.txt"):
        print(f"Loading report from {file}")
        
        with open(file, 'r', encoding='utf-8') as f:
            reports[file.name] = f"Nazwa pliku: {file.name}\n{f.read().strip()}"
            
    return reports

def generate_fact_keywords(facts_dir: str) -> Dict[str, List[str]]:
    """
    Generates keywords for each fact file.
    
    Parameters:
    - facts_dir (str): Path to the directory containing fact files
    
    Returns:
    - Dict[str, List[str]]: Dictionary mapping fact files to their keywords
    """
    fact_keywords = {}
    facts_path = Path(facts_dir)
    
    system_prompt = """
    Analyze the following fact and generate keywords in Polish in singluar nominative form that describe:
    - What is this fact about: person name
    - Key entities mentioned
    - Important attributes or characteristics
    - Any specific technical terms
    Return only personname followed by keywords separated by commas, no other text.
    """
    
    for file in facts_path.glob("*.txt"):
        print(f"Generating keywords for fact: {file}")
        with open(file, 'r', encoding='utf-8') as f:
            fact_content = f.read().strip()
            
        response = answer_question_openai(
            question=f"Generate fact name andkeywords for:\n{fact_content}",
            system_prompt=system_prompt,
            max_tokens=100
        )
        
        fact_keywords[file.name] = [kw.strip() for kw in response.split(',')]
        
    return fact_keywords

def generate_keywords(text: str, fact_keywords: Dict[str, List[str]]) -> List[str]:
    """
    Generates keywords for a given text using fact keywords as context.
    
    Parameters:
    - text (str): The text to generate keywords for
    - fact_keywords (Dict[str, List[str]]): Keywords extracted from facts
    
    Returns:
    - List[str]: List of keywords
    """
    # Create a context string from fact keywords
    context = "\n".join([
        f"Fact {idx + 1} keywords: {', '.join(keywords)}"
        for idx, keywords in enumerate(fact_keywords.values())
    ])
    
    system_prompt = f"""
    Using the following fact keywords as context:
    {context}
    
    Generate keywords for the document that describe:
    - Names and their characteristics (occupation, skills, languages)
    - Sector names if mentioned
    - Technical terms and technologies
    - Detection-related keywords if relevant
    - Include keywords for detected persons
    - Always include keyword for the sector name
    
    Generate keywords in Polish in singular form.
    Return only keywords separated by commas, no other text.
    """
    
    response = answer_question_openai(
        question=f"If person in mentioned include all keywords for this person. Include information of the sector name! Generate keywords for:\n{text}",
        system_prompt=system_prompt,
        max_tokens=100
    )
    
    keywords = [kw.strip() for kw in response.split(',')]
    print(f"{keywords=}")
    return keywords

def main():
    # Load environment variables
    base_dir = "data/dane_z_fabryki"
    facts_dir = os.path.join(base_dir, "facts")
    
    # Generate keywords for facts first
    fact_keywords = generate_fact_keywords(facts_dir)
    print("Fact keywords generated:", fact_keywords)

    # Load reports
    reports = load_factory_reports(base_dir)
    
    # Generate keywords for each report using fact keywords as context
    result = {}
    for filename, content in reports.items():
        keywords = generate_keywords(content, fact_keywords)
        result[filename] = ", ".join(keywords)
    
    # Send results to API
    print(f"{result=}")
    send_task("dokumenty", result)

if __name__ == "__main__":
    main() 