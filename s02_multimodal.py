import os
from aidevs import (
    answer_question_local,
    download_and_extract_zip, 
    generate_image_completion,
    answer_question_openai,
    send_task
)
from aidevs_text_extractor import TextExtractor

def process_file(filepath: str, filename: str) -> tuple[str, str]:
    """
    Process a single file and determine its category.
    Returns tuple of (filename, category) where category is 'people', 'hardware' or None
    """
    print(f"\nProcessing file: {filename}")
    
    try:
        # Create appropriate extractor and get content
        extractor = TextExtractor.create(filepath)
        content = extractor.extract(filepath)
        print(f"Extracted content: {content[:1000]}...")
        
    except ValueError as e:
        print(f"Skipping unsupported file: {e}")
        return filename, None
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return filename, None

    # Use answer_question_openai to categorize content
    system_prompt = """You are a content classifier. Analyze the text and determine if it contains:
    1. Information about detecting people or human presence (but not in the past).
    2. Information about physical hardware repairs or hardware-related issues
    
    Important distinctions:
    - Hardware refers to physical equipment, machinery, and devices
    - Software issues, code problems, or digital systems should be categorized as 'none'
    - If the text mentions both hardware and software, only categorize as 'hardware' if there are physical hardware repairs/issues
    - If humans are mentioned, but no physical presence is detected, categorize as 'none'
    - If no activity is detected, categorize as 'none'
    
    Respond with exactly one word: 'people', 'hardware', or 'none'."""
    
    print("Categorizing content...")
    category = answer_question_openai(
        question=f"{system_prompt}\n\nContent to analyze:\n{content}",
        max_tokens=1,
        model="gpt-4o-mini"
    )
    print(f"Category determined: {category}")
    
    return filename, category if category in ['people', 'hardware'] else None

def main():
    # Get base URL from environment
    base_url = os.getenv('AIDEVS_BASE_URL')
    if not base_url:
        raise EnvironmentError("AIDEVS_BASE_URL not found in environment variables")
    
    # Download and extract the ZIP file

    # Not needed, we're using local files
    # zip_url = f"{base_url}/dane/pliki_z_fabryki.zip"
    # print(f"\nDownloading and extracting ZIP from: {zip_url}")
    # output_dir = download_and_extract_zip(zip_url)
    # print(f"Files extracted to: {output_dir}")
    output_dir = "./temp_data"

    # Initialize result categories
    categories = {
        "people": [],
        "hardware": []
    }
    
    # Process only files in the root directory
    print("\nStarting file processing...")
    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    sorted_files = sorted(files)
    
    print(f"\nProcessing root directory: {output_dir}")
    print(f"Found {len(sorted_files)} files to process")
    
    for filename in sorted_files:
        filepath = os.path.join(output_dir, filename)
        filename, category = process_file(filepath, filename)
        
        if category in categories:
            categories[category].append(filename)
            print(f"Added {filename} to category: {category}")
    
    # Sort filenames in each category
    for category in categories:
        categories[category].sort()
    
    print("\nFinal categorization:")
    print(f"People category: {categories['people']}")
    print(f"Hardware category: {categories['hardware']}")
    
    # Send results
    print("\nSending results to server...")
    send_task("kategorie", categories)
    print("Task completed!")

if __name__ == "__main__":
    main() 