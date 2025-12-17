# YouTube Data Pipeline

An Apache Airflow pipeline that pulls YouTube video data based on a specified topic, retrieves video transcripts, and persists the data in DuckDB for efficient querying and analysis.

## Features

- **Topic-based Search**: Search YouTube videos using customizable topics
- **Comprehensive Data Collection**: Collect video URLs, titles, descriptions, and transcripts
- **Transcript Extraction**: Automatically fetch video transcripts where available
- **Persistent Storage**: Store all data in DuckDB for fast querying and analysis
- **Simple Architecture**: Direct API calls without complex middleware

## Tech Stack

- **Apache Airflow**: Workflow orchestration and scheduling
- **DuckDB**: High-performance analytical database
- **YouTube Data API v3**: For video search and metadata
- **YouTube Transcript API**: For transcript extraction
- **Python**: Core programming language

## Project Structure

```bash
antigravity-mcp-airflow-duckdb-pipeline-pull-data-from-youtube/
├── dags/
│   └── youtube_pipeline.py          # Main Airflow DAG
├── README.md                        # This file
└── .gitignore                      # Git ignore rules
```

### Key Components

1. **Airflow DAG (`dags/youtube_pipeline.py`)**:
   - Orchestrates the data pipeline workflow
   - Contains two main tasks: search and process videos
   - Handles topic input and data persistence

2. **DuckDB Database**:
   - Stores video metadata and transcripts
   - Optimized for analytical queries
   - File-based database for easy deployment

## DAG Architecture and Workflow

### DAG Structure

```python
youtube_data_pipeline (DAG)
├── search_task (PythonOperator)
│   └── Searches YouTube for videos
└── process_task (PythonOperator)
    └── Retrieves transcripts and stores in DuckDB
```

### How the DAG Works

1. **Initialization**:
   - Sets up database connection to DuckDB
   - Creates `videos` table if it doesn't exist
   - Configures API authentication

2. **Search Phase** (`search_task`):
   - Takes topic input (default: "machine learning")
   - Calls YouTube Search API
   - Returns list of video metadata (ID, title, description, URL)

3. **Processing Phase** (`process_task`):
   - Receives video list from search task
   - For each video:
     - Fetches transcript using YouTube Transcript API
     - Stores complete data in DuckDB
   - Handles errors gracefully (e.g., videos without transcripts)

4. **Data Persistence**:
   - All data stored in DuckDB with schema:

     ```sql
     CREATE TABLE videos (
         video_id VARCHAR PRIMARY KEY,
         title VARCHAR,
         description VARCHAR,
         url VARCHAR,
         transcript VARCHAR,
         created_at TIMESTAMP
     );
     ```

### Scheduling and Execution

- **Schedule**: Configurable (default: daily)
- **Retries**: 1 retry with 5-minute delay on failure
- **Dependencies**: Sequential execution (search → process)

## Data Analysis with DuckDB

### Why DuckDB?

- **Performance**: Fast analytical queries on structured data
- **Simplicity**: File-based database, no server required
- **SQL Support**: Standard SQL for complex queries
- **Python Integration**: Native Python API for data manipulation

### Sample Analysis Queries

```sql
-- Count videos by topic
SELECT COUNT(*) as video_count
FROM videos
WHERE description ILIKE '%machine learning%';

-- Find videos with longest transcripts
SELECT title, LENGTH(transcript) as transcript_length
FROM videos
ORDER BY transcript_length DESC
LIMIT 10;

-- Search transcripts for specific keywords
SELECT title, url
FROM videos
WHERE transcript ILIKE '%neural network%';

-- Analyze content trends
SELECT
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as videos_added
FROM videos
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;
```

### Python Analysis Example

```python
import duckdb

# Connect to database
con = duckdb.connect('youtube_data.db')

# Load data into pandas
df = con.execute("SELECT * FROM videos").fetchdf()

# Analyze transcript lengths
df['transcript_length'] = df['transcript'].str.len()
print(df.groupby('topic')['transcript_length'].describe())
```

## Prerequisites

- Python 3.8+
- Apache Airflow 2.x
- YouTube Data API v3 key (get from [Google Cloud Console](https://console.developers.google.com/))

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/denis911/antigravity-mcp-airflow-duckdb-pipeline-pull-data-from-youtube.git
   cd antigravity-mcp-airflow-duckdb-pipeline-pull-data-from-youtube
   ```

2. Install Python dependencies:

   ```bash
   pip install apache-airflow duckdb requests youtube-transcript-api
   ```

3. Set up YouTube API key:

   ```bash
   export YOUTUBE_API_KEY="your_youtube_api_key_here"
   ```

4. Initialize Airflow (if not already done):

   ```bash
   airflow db init
   ```

## Local Setup and Running

### 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv airflow_env
source airflow_env/bin/activate  # On Windows: airflow_env\Scripts\activate

# Install dependencies
pip install apache-airflow duckdb requests youtube-transcript-api
```

### 2. Airflow Initialization

```bash
# Set AIRFLOW_HOME (optional, defaults to ~/airflow)
export AIRFLOW_HOME=./airflow_home

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

### 3. Configure YouTube API

Get your API key from [Google Cloud Console](https://console.developers.google.com/):

1. Create a new project or select existing one
2. Enable YouTube Data API v3
3. Create credentials (API Key)
4. Set environment variable:

   ```bash
   export YOUTUBE_API_KEY="your_actual_api_key_here"
   ```

### 4. Setup DAG Directory

```bash
# Copy DAG to Airflow dags folder
cp dags/youtube_pipeline.py $AIRFLOW_HOME/dags/

# Or set AIRFLOW__CORE__DAGS_FOLDER to current directory
export AIRFLOW__CORE__DAGS_FOLDER=./dags
```

### 5. Run Airflow

```bash
# Start scheduler (runs DAGs)
airflow scheduler

# In another terminal, start webserver
airflow webserver --port 8080
```

### 6. Access Airflow UI

Open http://localhost:8080 in your browser and login with:
- Username: admin
- Password: (whatever you set during user creation)

### 7. Run the Pipeline

1. In Airflow UI, find `youtube_data_pipeline` DAG
2. Click the toggle to enable it
3. Click "Trigger DAG" to run immediately
4. Monitor progress in the UI

### 8. Check Results

```bash
# Connect to DuckDB and query results
python -c "
import duckdb
con = duckdb.connect('./data/youtube_data.db')
result = con.execute('SELECT COUNT(*) as total_videos FROM videos').fetchone()
print(f'Total videos collected: {result[0]}')
con.close()
"
```

## Usage

1. Place the DAG file in your Airflow dags folder
2. Update the topic in the DAG (currently set to 'machine learning')
3. Start Airflow:

   ```bash
   airflow scheduler &
   airflow webserver &
   ```

4. Trigger the DAG from the Airflow UI or CLI

## Configuration

### Environment Variables

- `YOUTUBE_API_KEY`: Required for YouTube API access
- `DUCKDB_PATH`: Path to DuckDB database (default: /opt/airflow/data/youtube_data.db)

### DAG Parameters

- `topic`: Search topic (default: 'machine learning')
- `max_results`: Number of videos to process (default: 5)
- `schedule_interval`: How often to run the pipeline

## Monitoring and Maintenance

### Airflow UI

- Monitor DAG runs and task status
- View logs for debugging
- Manually trigger runs for testing

### Database Maintenance

```sql
-- Check data volume
SELECT COUNT(*) FROM videos;

-- Remove old data if needed
DELETE FROM videos WHERE created_at < '2023-01-01';

-- Optimize database
VACUUM;
```

### API Quotas

- Monitor YouTube API quota usage
- Handle rate limits gracefully
- Consider upgrading API quotas for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure YOUTUBE_API_KEY is set correctly
2. **Transcript Not Available**: Some videos don't have transcripts
3. **Database Connection**: Check DuckDB file permissions
4. **Airflow Not Starting**: Verify Python path and dependencies

### Logs

Check Airflow logs in the UI or log files for detailed error messages.

## Future Enhancements

- **Multi-topic support**: Process multiple topics in single DAG run
- **Incremental updates**: Only fetch new videos since last run
- **Advanced analytics**: Sentiment analysis on transcripts
- **Dashboard integration**: Connect with BI tools like Tableau
- **Notification system**: Alert on pipeline failures or new content

## Disclaimer

This project is for educational and research purposes. Please respect YouTube's Terms of Service and API usage limits.
