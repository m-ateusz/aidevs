import base64
import os
from typing import Optional
import requests
from joblib import Memory
from openai import OpenAI

# Set up a caching directory
memory = Memory("_cache_dir", verbose=1)


def send_task(task: str, answer, url: str = 'https://centrala.ag3nts.org/report'):
    """
    Wysyła zadanie do serwera API z podaną nazwą zadania i odpowiedzią.
    
    Parameters:
        task (str): nazwa zadania.
        answer: Obiekt odpowiedzi, która ma być wysłana.
        api_url (str): URL endpointu, domyślnie 'https://centrala.ag3nts.org/report'
    """
    
    # Pobranie klucza API ze zmiennej środowiskowej
    api_key = os.getenv('AIDEVS_API_KEY')
    if not api_key:
        raise EnvironmentError("Nie znaleziono klucza API w zmiennych środowiskowych.")

    # Przygotowanie payloadu
    payload: dict[str, str] = {
        "task": task,
        "apikey": api_key,
        "answer": answer  # Odpowiedź przekazana jako string
    }

    # Wykonanie żądania POST
    post_response = requests.post(url, json=payload)
    print(post_response.text)
    if post_response.status_code == 200:
        print("POST request successful!")
    else:
        print(f"POST request failed. Status code: {post_response.status_code}")
    

def encode_image(image_path:str) -> str:
    """
    Encodes an image file to a base64 string.
    
    Parameters:
    - image_path (str): Path to the image file to be encoded.
    
    Returns:
    - str: Base64-encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def generate_image_completion(
        prompt: str,
        image_filenames: list[str],
        system_prompt: str = "",
        model: str = "gpt-4-vision-preview",
        max_tokens: int = 500
) -> str:
    """
    Sends a prompt with images to the OpenAI model and returns the response.

    Parameters:
    - prompt (str): User prompt describing the task or question for the images.
    - image_filenames (list[str]): List of paths to image files to include in the prompt.
    - system_prompt (str): Additional instructions or context for the system. Default is an empty string.
    - model (str): The model name to use for the OpenAI API call. Default is "gpt-4-vision-preview".
    - max_tokens (int): The maximum number of tokens to generate in the response. Default is 500.

    Returns:
    - str: The text response from the OpenAI API, containing the model's reply.

    Raises:
    - Exception: If there's an error in the API call or processing the response.
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ] + [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(filename)}"
                    }
                }
                for filename in image_filenames
            ]
        }
    ]

    # Query the OpenAI model
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )

    # Return the response
    return response.choices[0]


@memory.cache
def answer_question(
        question: str,
        system_prompt: Optional[str] = None,
        max_tokens:int = 5,
        model:str='gpt-4o-mini'
    ) -> str:
    """
    Zwraca odpowiedź na pojedyncze pytanie `question` z modelu GPT-4.
    
    Parameters:
    - question: Treść pytania.
    - system_prompt: Opcjonalny prompt systemowy (np. dodatkowy kontekst).
    - max_tokens: Maksymalna liczba tokenów w odpowiedzi.
    - model: Nazwa modelu OpenAI do użycia.
    
    Returns:
    - str: Odpowiedź na pytanie.
    """
    try:

        # Konfiguracja promptu systemowego, jeśli podany
        messages = [{"role": "user", "content": question}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        # Wykonaj zapytanie do modelu
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


client = OpenAI()
