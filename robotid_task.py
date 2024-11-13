import os
from aidevs import generate_image, send_task, fetch_data

def main():
    api_key = os.getenv('AIDEVS_API_KEY')
    base_url = os.getenv('AIDEVS_BASE_URL')
    
    if not api_key:
        raise EnvironmentError("AIDEVS_API_KEY not found in environment variables")
    if not base_url:
        raise EnvironmentError("AIDEVS_BASE_URL not found in environment variables")

    try:
        # Fetch the robot description using the generic fetch_data function
        url = f"{base_url}/data/{api_key}/robotid.json"
        data = fetch_data(url)
        description = data["description"]
        print(f"Fetched description: {description}")
        # Generate image using DALL-E 2 with 256x256 resolution
        image_url = generate_image(
            prompt=description,
            size="256x256",
            model="dall-e-2"
        )

        # Generate image using DALL-E 3
        image_url = generate_image(description)
        print(f"Generated image URL: {image_url}")

        # Send the answer
        send_task("robotid", image_url)
        print("Task completed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 