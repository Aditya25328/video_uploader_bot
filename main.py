import os
import sys
import asyncio
import aiohttp
from instaloader import Instaloader, Post
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()
FLIC_TOKEN = os.getenv('FLIC_TOKEN')

if not FLIC_TOKEN:
    raise Exception("FLIC_TOKEN is not set in the environment. Check your .env file or environment variables.")

def extract_shortcode(url: str) -> str:
    """
    Extract the shortcode from an Instagram reel URL.
    """
    try:
        # Look for 'reel/' or 'reels/' in the URL
        if 'reel/' in url:
            shortcode = url.split('reel/')[1].split('/')[0]
        elif 'reels/' in url:
            shortcode = url.split('reels/')[1].split('/')[0]
        else:
            raise ValueError("Invalid Instagram URL format.")
        return shortcode
    except IndexError:
        raise ValueError("Unable to extract shortcode. Check the URL format.")

async def download_from_instagram(url: str) -> None:
    """
    Download an Instagram reel given its URL and save it to the 'videos' directory.
    """
    il = Instaloader()
    shortcode = extract_shortcode(url)
    post = Post.from_shortcode(il.context, shortcode)

    os.makedirs('videos', exist_ok=True)

    il.download_post(post, target='videos')

    for file in os.listdir('videos'):
        if not file.endswith('.mp4') and not file.endswith('.txt'):
            os.remove(os.path.join('videos', file))

async def generate_upload_url() -> dict:
    """
    Generate a pre-signed upload URL from the API.
    Returns the URL and hash as a dictionary.
    """
    endpoint = 'https://api.socialverseapp.com/posts/generate-upload-url'
    headers = {
        'Flic-Token': FLIC_TOKEN,
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to generate upload URL: {response.status}, {await response.text()}")

async def upload_video_to_url(upload_url: str, file_path: str) -> None:
    """
    Upload the video file to the server using the pre-signed URL.
    """
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            async with session.put(upload_url, data=file) as response:
                if response.status != 200:
                    raise Exception(f"Failed to upload video: {response.status}, {await response.text()}")

async def create_post(hash_value: str, title: str, category_id: int = 69) -> None:
    """
    Create a post on the Socialverse platform using the video hash.
    """
    endpoint = 'https://api.socialverseapp.com/posts'
    headers = {
        'Flic-Token': FLIC_TOKEN,
        'Content-Type': 'application/json'
    }
    body = {
        "title": title,
        "hash": hash_value,
        "is_available_in_public_feed": False,
        "category_id": category_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=body) as response:
            if response.status != 200:
                raise Exception(f"Failed to create post: {response.status}, {await response.text()}")

async def process_reel(url: str) -> None:
    """
    End-to-end process: download, upload, and create a post for an Instagram reel.
    """
    print(f"Processing URL: {url}")
    await download_from_instagram(url)

    video_files = [file for file in os.listdir('videos') if file.endswith('.mp4')]
    if not video_files:
        raise Exception("No video file found in 'videos' directory.")
    video_file_path = os.path.join('videos', video_files[0])

    upload_data = await generate_upload_url()
    upload_url = upload_data['url']
    hash_value = upload_data['hash']

    await upload_video_to_url(upload_url, video_file_path)

    title_file = [file for file in os.listdir('videos') if file.endswith('.txt')]
    if not title_file:
        raise Exception("No title file found in 'videos' directory.")
    
    # Read the title file with UTF-8 encoding
    with open(os.path.join('videos', title_file[0]), 'r', encoding='utf-8') as f:
        title = f.read()

    await create_post(hash_value, title)

    print(f"Process completed successfully for {url}: Video uploaded and post created.")


async def main():
    if len(sys.argv) < 2:
        print("Add a url for the instagram with the script during initialization. python main.py <>")
        sys.exit(1)

    urls = sys.argv[1:]
    for url in urls:
        try:
            await process_reel(url)
        except Exception as e:
            print(f"Error processing {url}: {e}", file=sys.stderr)
        finally:
            if os.path.exists('videos'):
                shutil.rmtree('videos')

if __name__ == "__main__":
    asyncio.run(main())
