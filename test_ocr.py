from aidevs import extract_text_from_image
import os

def test_ocr(image_path: str):
    """
    Test OCR functionality on an existing image file
    
    Parameters:
    - image_path (str): Path to the image file to test
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
        
    print(f"Testing OCR on image: {image_path}")
    
    try:
        # Test EasyOCR
        # print("\nTesting EasyOCR:")
        # text_easyocr = extract_text_from_image(
        #     image_path, 
        #     method="easyocr",
        #     language=("en", "pl")
        # )
        # print(f"EasyOCR result:\n{text_easyocr}")
        
        # Test Tesseract
        print("\nTesting Tesseract:")
        text_tesseract = extract_text_from_image(
            image_path, 
            method="tesseract",
            language="pol+eng"
        )
        print(f"Tesseract result:\n{text_tesseract}")
        
    except Exception as e:
        print(f"Error during OCR test: {str(e)}")

if __name__ == "__main__":
    # Replace this with your image path
    image_path = "./temp_data/2024-11-12_report-13.png"
    test_ocr(image_path) 