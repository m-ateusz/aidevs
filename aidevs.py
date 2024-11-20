import base64
import os
from typing import Optional, Dict, Any
import requests
from joblib import Memory
from openai import OpenAI
import json
import zipfile

# Set up a caching directory
memory = Memory("_cache_dir", verbose=1)


def send_task(task: str, answer, url: str = None, payload_name: str = 'answer'):
    """
    Wysyła zadanie do serwera API z podaną nazwą zadania i odpowiedzią.
    
    Parameters:
        task (str): nazwa zadania.
        answer: Obiekt odpowiedzi, która ma być wysłana.
        url (str): Optional URL override. If None, uses default from environment.
        payload_name (str): Name of the payload field (default: 'answer')
    """
    api_key = os.getenv('AIDEVS_API_KEY')
    if not api_key:
        raise EnvironmentError("Nie znaleziono klucza API w zmiennych środowiskowych.")

    base_url = os.getenv('AIDEVS_BASE_URL')
    if not base_url:
        raise EnvironmentError("AIDEVS_BASE_URL not found in environment variables")

    # Use provided URL or construct from base URL
    report_url = url or f"{base_url}/report"

    payload = {
        "task": task,
        "apikey": api_key,
        payload_name: answer
    }

    post_response = requests.post(report_url, json=payload)
    print(post_response.text)
    if post_response.status_code == 200:
        print("POST request successful!")
    else:
        print(f"POST request failed. Status code: {post_response.status_code}")
    return post_response.json()
    

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
        model: str = "gpt-4o-mini",
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
def answer_question_openai(
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


@memory.cache
def answer_question_local(
        question: str,
        model: str = 'llama3.1:8b',
        stream: bool = False
    ) -> str:
    """
    Wykonuje zapytanie do lokalnego modelu LLM poprzez API Ollama.
    
    Parameters:
    - question (str): Tekst pytania
    - model (str): Nazwa modelu do użycia (default: 'llama3.1:8b')
    - stream (bool): Czy używać streamowania odpowiedzi (default: False)
    
    Returns:
    - str: Odpowiedź z modelu
    
    Raises:
    - Exception: Jeśli wystąpi błąd w komunikacji z API
    """
    url = "http://localhost:11434/api/generate"
    
    data = {
        'model': model,
        'prompt': question,
        'stream': stream
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        response_json = json.loads(response.text)
        return response_json['response']
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with local LLM API: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing API response: {str(e)}")


def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    model: str = "dall-e-3"
) -> str:
    """
    Generates an image using OpenAI's DALL-E model and returns the URL.
    
    Parameters:
    - prompt (str): The description of the image to generate
    - size (str): Size of the image (default: "1024x1024")
    - quality (str): Quality of the image (default: "standard")
    - model (str): The model to use (default: "dall-e-3")
    
    Returns:
    - str: URL of the generated image
    """
    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        return response.data[0].url
    except Exception as e:
        raise Exception(f"Error generating image: {str(e)}")


def fetch_data(url: str) -> Dict[str, Any]:
    """
    Fetches JSON data from a given URL and returns it as a dictionary.
    
    Parameters:
    - url (str): The URL to fetch data from
    
    Returns:
    - Dict[str, Any]: The JSON response as a dictionary
    
    Raises:
    - Exception: If the request fails or returns non-200 status code
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    return response.json()

def fetch_text(url: str) -> str:
    """
    Fetches text data from a given URL and returns it as a string.
    
    Parameters:
    - url (str): The URL to fetch text from
    
    Returns:
    - str: The text response
    
    Raises:
    - Exception: If the request fails or returns non-200 status code
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch text: {response.status_code}")
    return response.text


def download_and_extract_zip(zip_url: str, output_folder: str = "temp_data") -> str:
    """
    Downloads a ZIP file from a URL and extracts its contents to a specified folder.
    
    Parameters:
    - zip_url (str): URL of the ZIP file to download
    - output_folder (str): Folder where contents should be extracted (default: "temp_data")
    
    Returns:
    - str: Path to the output folder containing extracted files
    
    Raises:
    - Exception: If download or extraction fails
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    zip_path = os.path.join(output_folder, "downloaded.zip")
    
    try:
        # Download the ZIP file
        response = requests.get(zip_url)
        response.raise_for_status()
        
        with open(zip_path, "wb") as f:
            f.write(response.content)
            
        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
            
        return output_folder
        
    except Exception as e:
        raise Exception(f"Error processing ZIP file: {str(e)}")
    finally:
        # Clean up the ZIP file
        if os.path.exists(zip_path):
            os.remove(zip_path)


def transcribe_audio_file(
    audio_path: str,
    language: str = None,
    model_name: str = "base",
    whisper_model = None
) -> str:
    """
    Transcribes an audio file using OpenAI's Whisper model.
    
    Parameters:
    - audio_path (str): Path to the audio file
    - language (str): Optional language code (e.g., 'pl' for Polish)
    - model_name (str): Whisper model size to use if no model provided
    - whisper_model: Optional pre-loaded Whisper model instance
    
    Returns:
    - str: Transcribed text
    
    Raises:
    - Exception: If transcription fails
    """
    try:
        import whisper
        
        # Use provided model or load new one
        model = whisper_model or whisper.load_model(model_name)
        
        # Transcribe the audio
        result = model.transcribe(
            audio_path,
            language=language
        )
        
        return result['text'].strip()
        
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")


def process_audio_batch(
    audio_folder: str,
    file_extensions: list[str] = ['.mp3', '.m4a', '.wav'],
    **transcribe_kwargs
) -> list[str]:
    """
    Processes multiple audio files in a folder and returns their transcriptions.
    
    Parameters:
    - audio_folder (str): Path to folder containing audio files
    - file_extensions (list[str]): List of audio file extensions to process
    - **transcribe_kwargs: Additional arguments passed to transcribe_audio_file
    
    Returns:
    - list[str]: List of transcribed texts
    
    Raises:
    - Exception: If processing fails
    """
    transcripts = []
    
    try:
        for file_name in os.listdir(audio_folder):
            if any(file_name.lower().endswith(ext) for ext in file_extensions):
                audio_path = os.path.join(audio_folder, file_name)
                transcript = transcribe_audio_file(audio_path, **transcribe_kwargs)
                transcripts.append(transcript)
                
        return transcripts
        
    except Exception as e:
        raise Exception(f"Error processing audio batch: {str(e)}")


def categorize_content(
    content: str,
    system_prompt: str = """Categorize if the text contains information about:
    1. People or traces of human presence
    2. Hardware repairs or issues
    Return either "people", "hardware", or "none" if neither category applies.
    Only return the single word category.""",
    model: str = "gpt-4"
) -> str:
    """
    Categorizes content using OpenAI's model to determine if it contains
    information about people or hardware repairs.
    
    Parameters:
    - content (str): The text content to analyze
    - system_prompt (str): Instructions for the categorization
    - model (str): The model to use for categorization
    
    Returns:
    - str: Category ("people", "hardware", or "none")
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error categorizing content: {str(e)}")
        return "none"


def extract_text_from_image(
    image_path: str,
    method: str = "easyocr",
    language: str = "en"
) -> str:
    """
    Extracts text from an image file using specified OCR method.
    
    Parameters:
    - image_path (str): Path to the image file
    - method (str): OCR method to use - either "easyocr" or "tesseract"
    - language (str): Language code for OCR (default: "en")
    
    Returns:
    - str: Extracted text from the image
    
    Raises:
    - ImportError: If required OCR package is not installed
    - Exception: If OCR processing fails
    """
    try:
        if method.lower() == "easyocr":
            import easyocr
            reader = easyocr.Reader([language])
            result = reader.readtext(image_path)
            # Combine all detected text blocks
            return " ".join([text[1] for text in result])
            
        elif method.lower() == "tesseract":
            import pytesseract
            from PIL import Image
            
            # Open the image
            image = Image.open(image_path)
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            return text.strip()
            
        else:
            raise ValueError(f"Unsupported OCR method: {method}")
            
    except ImportError as e:
        installation_guide = {
            "easyocr": "pip install easyocr",
            "tesseract": "pip install pytesseract\nAnd install Tesseract OCR engine: https://github.com/UB-Mannheim/tesseract/wiki"
        }
        method_name = method.lower()
        raise ImportError(
            f"Required package for {method} not installed. "
            f"Please install using:\n{installation_guide.get(method_name, '')}"
        )
    except Exception as e:
        raise Exception(f"Error performing OCR: {str(e)}")


def run_ocr(image_path: str) -> str:
    """
    Runs OCR on an image file and returns the extracted text.
    
    Parameters:
    - image_path (str): Path to the image file to process
    
    Returns:
    - str: Extracted text from the image
    """
    try:
        import easyocr
        
        # Initialize EasyOCR reader with English and Polish language support
        reader = easyocr.Reader(['en', 'pl'])
        
        # Read text from image
        result = reader.readtext(image_path)
        
        # Combine all detected text blocks with spaces
        extracted_text = ' '.join([text[1] for text in result])
        
        return extracted_text.strip()
        
    except Exception as e:
        print(f"Error performing OCR: {str(e)}")
        return ""


@memory.cache
def get_embedding(text: str) -> list[float]:
    """Get embedding for text using local Gemma model"""
    url = "http://localhost:11434/api/embeddings"
    
    data = {
        'model': 'gemma2:27b',
        'prompt': text
    }
    
    response = requests.post(url, json=data)
    return response.json()['embedding']


client = OpenAI()
