import os
import sys
import asyncio
import aiohttp
import shutil
from instaloader import Instaloader, Post
from dotenv import load_dotenv

# Load environment variables
def load_environment_variables():
    load_dotenv()
    token = os.getenv('FLIC_TOKEN')
    if not token:
        raise RuntimeError("Environment variable 'FLIC_TOKEN' is missing. Ensure it's set in the .env file.")
    return token

FLIC_TOKEN = load_environment_variables()

# Helper Functions
def parse_instagram_url(reel_url):
    """Extract shortcode from Instagram URL."""
    try:
        if 'reel/' in reel_url:
            return reel_url.split('reel/')[1].split('/')[0]
        elif 'reels/' in reel_url:
            return reel_url.split('reels/')[1].split('/')[0]
        else:
            raise ValueError("Unsupported Instagram URL format.")
    except IndexError:
        raise ValueError("Failed to parse the shortcode. Verify the URL format.")

async def fetch_upload_url():
    """Request a pre-signed upload URL from the API."""
    api_endpoint = 'https://api.socialverseapp.com/posts/generate-upload-url'
    headers = {'Flic-Token': FLIC_TOKEN, 'Content-Type': 'application/json'}

    async with aiohttp.ClientSession() as session:
        async with session.get(api_endpoint, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            error_message = await response.text()
            raise RuntimeError(f"Error fetching upload URL: {response.status}, {error_message}")

async def upload_file(upload_url, file_path):
    """Upload the video to the server."""
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as file:
            async with session.put(upload_url, data=file) as response:
                if response.status != 200:
                    error_message = await response.text()
                    raise RuntimeError(f"Video upload failed: {response.status}, {error_message}")

async def submit_post(hash_value, title, category=25):
    """Create a new post on Socialverse."""
    api_endpoint = 'https://api.socialverseapp.com/posts'
    payload = {
        "title": title,
        "hash": hash_value,
        "is_available_in_public_feed": False,
        "category_id": category
    }
    headers = {'Flic-Token': FLIC_TOKEN, 'Content-Type': 'application/json'}

    async with aiohttp.ClientSession() as session:
        async with session.post(api_endpoint, headers=headers, json=payload) as response:
            if response.status != 200:
                error_message = await response.text()
                raise RuntimeError(f"Post creation failed: {response.status}, {error_message}")

# Main Workflow
async def process_reel_video(reel_url):
    """Orchestrates the end-to-end process for downloading and uploading a reel."""
    print(f"Starting process for: {reel_url}")

    # Download reel
    loader = Instaloader()
    shortcode = parse_instagram_url(reel_url)
    post = Post.from_shortcode(loader.context, shortcode)
    os.makedirs('videos', exist_ok=True)
    loader.download_post(post, target='videos')

    # Cleanup unnecessary files
    for file in os.listdir('videos'):
        if not file.endswith('.mp4') and not file.endswith('.txt'):
            os.remove(os.path.join('videos', file))

    video_files = [file for file in os.listdir('videos') if file.endswith('.mp4')]
    if not video_files:
        raise RuntimeError("No video files found after download.")
    video_path = os.path.join('videos', video_files[0])

    # Fetch upload URL and upload video
    upload_info = await fetch_upload_url()
    await upload_file(upload_info['url'], video_path)

    # Read title and create post
    title_files = [file for file in os.listdir('videos') if file.endswith('.txt')]
    if not title_files:
        raise RuntimeError("No title file found in downloaded content.")

    with open(os.path.join('videos', title_files[0]), 'r', encoding='utf-8') as title_file:
        title_content = title_file.read()

    await submit_post(upload_info['hash'], title_content)
    print(f"Completed process for: {reel_url}")

# Script Entry Point
async def run():
    if len(sys.argv) < 2:
        print("Usage: python script.py <instagram_reel_url>")
        sys.exit(1)

    urls_to_process = sys.argv[1:]
    for reel_url in urls_to_process:
        try:
            await process_reel_video(reel_url)
        except Exception as error:
            print(f"Error processing {reel_url}: {error}", file=sys.stderr)
        finally:
            if os.path.exists('videos'):
                shutil.rmtree('videos')

if __name__ == "__main__":
    asyncio.run(run())
