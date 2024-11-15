import requests
from bs4 import BeautifulSoup
import os
import re
from typing import Optional
from urllib.parse import urljoin
import tempfile
from aidevs_text_extractor import TextExtractor
from aidevs import generate_image_completion

def download_file(url: str, temp_dir: str) -> Optional[str]:
    """Downloads a file from URL to temporary directory"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Extract filename from URL or generate one
        filename = url.split('/')[-1]
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def process_media_element(element, base_url: str, temp_dir: str) -> str:
    """Process audio or image element and return extracted text"""
    
    # Get surrounding paragraph if exists
    surrounding_p = element.find_parent('p')
    context = surrounding_p.get_text(strip=True) if surrounding_p else ""
    
    if element.name == 'audio':
        src = element.get('src')
        if not src:
            return "[Audio file not found]"
            
        full_url = urljoin(base_url, src)
        audio_path = download_file(full_url, temp_dir)
        if not audio_path:
            return "[Failed to download audio]"
            
        try:
            extractor = TextExtractor.create(audio_path)
            transcription = extractor.extract(audio_path)
            return f"[Audio Transcription: {transcription}]"
        except Exception as e:
            return f"[Audio transcription failed: {str(e)}]"
            
    elif element.name == 'img':
        src = element.get('src')
        if not src:
            return "[Image not found]"
            
        full_url = urljoin(base_url, src)
        img_path = download_file(full_url, temp_dir)
        if not img_path:
            return "[Failed to download image]"
            
        try:
            # Get image description using GPT-4 Vision
            prompt = f"Please describe this image in detail. Context: {context}"
            description = generate_image_completion(
                prompt=prompt,
                image_filenames=[img_path],
                model="gpt-4o",
                system_prompt="Provide a detailed (try name things, especially recognized Named Entities and objects) description of the image that would be meaningful mentioned context.",
                max_tokens=300
            )
            return f"[Image Description: {description}]"
        except Exception as e:
            return f"[Image description failed: {str(e)}]"
            
    return ""

def html_to_markdown(html_content: str, base_url: str) -> str:
    """Convert HTML to Markdown, processing media elements"""
    
    # Create temporary directory for downloaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Process all media elements
        for element in soup.find_all(['audio', 'img']):
            replacement_text = process_media_element(element, base_url, temp_dir)
            element.replace_with(replacement_text)
        
        # Basic HTML to Markdown conversion
        markdown = ""
        
        # Process headings
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                markdown += f"{'#' * i} {heading.get_text().strip()}\n\n"
                heading.decompose()
        
        # Process paragraphs
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                markdown += f"{text}\n\n"
        
        return markdown.strip()

def main():
    # Get base URL from environment variable
    base_url = os.getenv('AIDEVS_BASE_URL')
    if not base_url:
        raise EnvironmentError("AIDEVS_BASE_URL not found in environment variables")
    
    url = f"{base_url}/dane/arxiv-draft.html"
    
    try:
        # Fetch HTML content
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert to Markdown
        markdown_content = html_to_markdown(response.text, base_url)
        
        # Save to file
        with open('result.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print("Successfully processed and saved to result.md")
        
    except Exception as e:
        print(f"Error processing page: {str(e)}")

if __name__ == "__main__":
    main() 