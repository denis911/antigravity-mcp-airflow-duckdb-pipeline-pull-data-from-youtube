"""
Airflow DAG to pull data from YouTube based on topic and store in DuckDB.
"""

from airflow import DAG

from datetime import datetime, timedelta
import duckdb
import requests
import os
from youtube_transcript_api import YouTubeTranscriptApi

# YouTube API key - should be set as environment variable or Airflow Variable
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")

# DuckDB database path
DUCKDB_PATH = '/opt/airflow/data/youtube_data.db'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

from airflow.decorators import task

dag = DAG(
    'youtube_data_pipeline',
    default_args=default_args,
    description='Pull YouTube data for a topic and store in DuckDB',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['youtube', 'duckdb'],
)

@task
def search_videos(topic: str, max_results: int = 10):
    """Search YouTube for videos based on topic."""
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': topic,
        'type': 'video',
        'maxResults': max_results,
        'key': YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    videos = []
    for item in data['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        url = f'https://www.youtube.com/watch?v={video_id}'
        videos.append({
            'video_id': video_id,
            'title': title,
            'description': description,
            'url': url
        })
    return videos

def get_transcript(video_id):
    """Get transcript for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([item['text'] for item in transcript])
        return text
    except Exception as e:
        print(f"Error getting transcript for {video_id}: {e}")
        return ""

@task
def process_videos(videos: list):
    """Process videos: get transcripts and store in DuckDB."""
    # Connect to DuckDB
    con = duckdb.connect(DUCKDB_PATH)
    
    # Create table if not exists
    con.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id VARCHAR PRIMARY KEY,
            title VARCHAR,
            description VARCHAR,
            url VARCHAR,
            transcript VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Process each video
    for video in videos:
        video_id = video['video_id']
        transcript = get_transcript(video_id)
        
        # Insert or update
        con.execute("""
            INSERT OR REPLACE INTO videos (video_id, title, description, url, transcript)
            VALUES (?, ?, ?, ?, ?)
        """, (video_id, video['title'], video['description'], video['url'], transcript))
    
    con.close()
    print(f"Processed {len(videos)} videos")

with dag:
    # Define flow
    video_list = search_videos(topic='machine learning', max_results=5)
    process_videos(video_list)
