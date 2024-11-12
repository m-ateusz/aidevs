import os
import requests


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
