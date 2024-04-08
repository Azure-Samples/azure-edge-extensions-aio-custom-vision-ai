import logging
import requests
import time
import os
import azure.functions as func
from .search_client import create_search_client

def main(myblob: func.InputStream):
  logging.info(f"Python blob trigger function processed blob \n"
         f"Name: {myblob.name}\n"
         f"Blob Size: {myblob.length} bytes")
  # Extract text data from the video file
  text_data = extract_text(myblob)

  # Create a search client
  search_client = create_search_client(os.environ["INDEX_NAME"])

  # Index the text data
  search_client.upload_documents([{"id": myblob.name, "text": text_data}])

def extract_text(video_path):
  # Set up the Video Indexer API parameters
  location = os.environ["VIDEO_INDEXER_LOCATION"]
  account_id = os.environ["VIDEO_INDEXER_ACCOUNT_ID"]
  api_key = os.environ["VIDEO_INDEXER_API_KEY"]

  # Upload the video to Video Indexer
  upload_url = f"https://{location}.api.videoindexer.ai/Accounts/{account_id}/Videos?accessToken={api_key}&name=test&description=test"
  with open(video_path, "rb") as video_file:
    requests.post(upload_url, files={"file": video_file})

  # Wait for Video Indexer to index the video
  time.sleep(60)  # Adjust this value based on the length of your video

  # Get the indexed data
  index_url = f"https://{location}.api.videoindexer.ai/Accounts/{account_id}/Videos/test/Index?accessToken={api_key}"
  response = requests.get(index_url)
  data = response.json()

  # Extract the transcriptions
  transcriptions = [caption["text"] for caption in data["videos"][0]["insights"]["transcript"]]

  return " ".join(transcriptions)