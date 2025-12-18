"""
Airflow DAG to pull data from YouTube based on topic and store in DuckDB.
"""

from airflow import DAG
from airflow.models import Variable

from datetime import datetime, timedelta
import duckdb
import requests
import logging
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

# YouTube API key - use Airflow Variable for security
YOUTUBE_API_KEY = Variable.get('youtube_api_key')

# DuckDB database path - use Airflow Variable with default
DUCKDB_PATH = Variable.get('duckdb_path', default_var='/opt/airflow/data/youtube_data.db')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
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
    schedule=timedelta(days=1),
    catchup=False,
    tags=['youtube', 'duckdb'],
)

@task
def search_videos(topic: str, max_results: int = 10):
    """Search YouTube for videos based on topic."""
    logger.info(f"Searching YouTube for topic: {topic}, max_results: {max_results}")
    try:
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
        logger.info(f"Found {len(videos)} videos for topic '{topic}'")
        return videos
    except Exception as e:
        logger.error(f"Error searching videos for topic '{topic}': {e}")
        raise

def get_transcript(video_id):
    """Get transcript for a YouTube video."""
    try:
        logger.info(f"Getting transcript for video {video_id}")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([item['text'] for item in transcript])
        logger.info(f"Successfully retrieved transcript for video {video_id}")
        return text
    except Exception as e:
        logger.warning(f"Error getting transcript for {video_id}: {e}")
        return ""

@task
def process_videos(videos: list):
    """Process videos: get transcripts and store in DuckDB."""
    logger.info(f"Processing {len(videos)} videos")
    try:
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

        processed_count = 0
        # Process each video
        for video in videos:
            video_id = video['video_id']
            transcript = get_transcript(video_id)

            # Insert or update
            con.execute("""
                INSERT OR REPLACE INTO videos (video_id, title, description, url, transcript)
                VALUES (?, ?, ?, ?, ?)
            """, (video_id, video['title'], video['description'], video['url'], transcript))
            processed_count += 1

        con.close()
        logger.info(f"Successfully processed {processed_count} videos")
    except Exception as e:
        logger.error(f"Error processing videos: {e}")
        raise

with dag:
    # Define flow
    video_list = search_videos(topic='machine learning', max_results=5)
    process_videos(video_list)
