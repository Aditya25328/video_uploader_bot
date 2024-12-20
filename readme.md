﻿# video_uploader_bot
# Instagram Reel Downloader and Uploader

This script provides an end-to-end solution for downloading Instagram reels, uploading them to a server using pre-signed URLs, and creating posts on the Socialverse platform. It is designed to automate the process while ensuring proper error handling and modularity.

## Features
- **Download Instagram Reels**: Extracts and downloads reels using their URL.
- **Upload Video**: Uploads the downloaded video to a server via a pre-signed URL.
- **Create Posts**: Automatically creates a post on Socialverse using the uploaded video's hash.
- **Error Handling**: Provides clear error messages and ensures proper cleanup.

---

## Prerequisites
1. **Python Version**: Ensure Python 3.8+ is installed on your system.
2. **Libraries**:
    - `instaloader`
    - `aiohttp`
    - `python-dotenv`
    - `shutil` (part of Python standard library)
3. **Environment Variables**:
    - A `.env` file containing the `FLIC_TOKEN` (required for API authentication).

---

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add the following:
    ```
    FLIC_TOKEN=<your_flic_token>
    ```

---

## Usage

### Command Format
Run the script with the following command:
```bash
python script.py <instagram_reel_url>
```

### Example
```bash
python script.py https://www.instagram.com/reel/example_shortcode/
```

You can process multiple URLs by providing them as space-separated arguments:
```bash
python script.py <url1> <url2> <url3>
```

---

## Script Workflow

### 1. **Download Reel**
- **Description**: Extracts the shortcode from the provided Instagram URL and downloads the reel.
- **Implementation**:
  - Extracts the shortcode using the `parse_instagram_url` function.
  - Uses `Instaloader` to fetch and save the reel to a `videos` directory.

### 2. **Generate Pre-Signed URL**
- **Description**: Communicates with the API to generate a pre-signed URL for uploading the video.
- **Implementation**:
  - Sends a GET request to the `/generate-upload-url` API endpoint.
  - Parses the response to retrieve the upload URL and video hash.

### 3. **Upload Video**
- **Description**: Uploads the downloaded video to the server.
- **Implementation**:
  - Sends a PUT request with the video file to the pre-signed URL.
  - Ensures upload success by checking the server response.

### 4. **Create Post**
- **Description**: Creates a post on the Socialverse platform using the video's hash and title.
- **Implementation**:
  - Reads the title from the accompanying `.txt` file in the `videos` directory.
  - Sends a POST request to the `/posts` API endpoint with the required details (title, hash, category).

---

## Directory Structure

After downloading a reel, the following structure is created in the `videos` directory:
```
/videos
├── <shortcode>.mp4   # The downloaded video
├── <shortcode>.txt   # Title file accompanying the video
```

The directory is cleaned up after processing.

---

## Error Handling
- **Missing Environment Variable**: Checks if `FLIC_TOKEN` is set and raises an exception if not.
- **Invalid URL Format**: Validates the Instagram URL format and raises an error if invalid.
- **No Video Files Found**: Ensures a valid video file is downloaded; otherwise, an exception is raised.
- **Upload or Post Failure**: Captures HTTP errors and provides detailed messages.

---

## Key Functions

### 1. `load_environment_variables()`
- Loads the `FLIC_TOKEN` from the `.env` file.
- Raises an exception if the token is missing.

### 2. `parse_instagram_url(reel_url)`
- Extracts the shortcode from the provided Instagram reel URL.
- Validates URL format.

### 3. `fetch_upload_url()`
- Sends a GET request to generate a pre-signed upload URL.
- Returns the upload URL and video hash.

### 4. `upload_file(upload_url, file_path)`
- Uploads the video file to the pre-signed URL.
- Handles upload success or failure.

### 5. `submit_post(hash_value, title, category=25)`
- Sends a POST request to create a Socialverse post with the uploaded video's details.

### 6. `process_reel_video(reel_url)`
- Orchestrates the full workflow: download reel, generate upload URL, upload video, and create a post.

---

## Cleanup
- The script cleans up the `videos` directory after processing each reel to save disk space and avoid conflicts.

---

## API Endpoints

### 1. Generate Upload URL
- **Endpoint**: `https://api.socialverseapp.com/posts/generate-upload-url`
- **Method**: `GET`
- **Headers**:
  - `Flic-Token`: Authentication token

### 2. Create Post
- **Endpoint**: `https://api.socialverseapp.com/posts`
- **Method**: `POST`
- **Headers**:
  - `Flic-Token`: Authentication token
  - `Content-Type`: `application/json`
- **Body**:
  ```json
  {
    "title": "<video_title>",
    "hash": "<video_hash>",
    "is_available_in_public_feed": false,
    "category_id": 25
  }
  ```

---

## Additional Notes
- Ensure proper permissions to access Instagram content.
- Handle API rate limits if uploading a large number of videos.
- Ensure `FLIC_TOKEN` remains secure and is not hardcoded in the script.

---


---

## Contribution
Feel free to submit issues or pull requests for improvements. Contributions are welcome!

