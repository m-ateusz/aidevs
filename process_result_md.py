import os
from aidevs import answer_question_openai, send_task, fetch_text

def read_markdown_file(filename: str = "result.md") -> str:
    """Read and return contents of the markdown file"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error reading markdown file: {str(e)}")

def fetch_questions() -> dict:
    """Fetch and parse questions from the API endpoint"""
    api_key = os.getenv('AIDEVS_API_KEY')
    if not api_key:
        raise EnvironmentError("AIDEVS_API_KEY not found in environment variables")
    
    base_url = os.getenv('AIDEVS_BASE_URL')
    if not base_url:
        raise EnvironmentError("AIDEVS_BASE_URL not found in environment variables")
    
    url = f"{base_url}/data/{api_key}/arxiv.txt"
    
    try:
        response = fetch_text(url)
        print(f"{response=}")
        questions = {}
        # Split response into lines and process each non-empty line
        for line in response.splitlines():
            line = line.strip()
            if line and '=' in line:
                qid, question = line.split('=', 1)
                questions[qid.strip()] = question.strip()
        return questions
    except Exception as e:
        raise Exception(f"Error fetching questions: {str(e)}")

def process_questions(questions: dict, context: str) -> dict:
    """Process each question using OpenAI with the markdown context"""
    system_prompt = f"""Oto cały kontekst:
    {context} 
    Na podstawie podanego kontekstu, najpierw podaj wszystkie istotne dla danego pytania informacje, 
    a następnie odpowiedz na pytanie. Odpowiedź na pytanie nie może być pełnym zdaniem, tylko krótka i związana z pytaniem.
    Możesz się domyślać niektórych faktów na podstawie metadanych dokumentu, np. lokalizacji, dat etc. Zwróć uwagę o co jesteś pytany.
    Fotografie zapewne zostały wykonane w mieście autora.
    """
    
    answers = {}
    for qid, question in questions.items():
        answer = answer_question_openai(
            question=question,
            system_prompt=system_prompt,
            max_tokens=1000,
            model='gpt-4o-mini'
        )
        answers[qid] = answer
        print(f"{qid=}\n{question=}\n{answer=}\n")
    
    return answers

def main():
    try:
        # Read markdown content
        context = read_markdown_file()
        
        # Fetch questions
        questions = fetch_questions()
        
        # Process questions and get answers
        answers = process_questions(questions, context)
        
        # Send results to the API
        send_task("arxiv", answers)
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main() 