import requests
from bs4 import BeautifulSoup
from aidevs import answer_question_openai

def solve_form_task():
    # Fetch the page with the question
    url = ... # FIXME: redacted for git due to security reasons, subdomain is xyz

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract question from paragraph with id=human-question
    question = soup.find('p', id='human-question').text.strip()
    
    # Get answer using the local aidevs module
    answer = answer_question_openai(question, system_prompt='Answer using only one word or one number only!')
    print(f"Answer: {answer}")

    # Prepare form data
    form_data = {
        'username': 'tester',
        'password': '574e112a',
        'answer': answer
    }
    
    # Submit the form via POST
    response = requests.post(url, data=form_data)
    
    return response.text

if __name__ == "__main__":
    result = solve_form_task()
    print(result)

