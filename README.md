# Antigravity YouTube Data Pipeline

An Apache Airflow pipeline that pulls YouTube video data based on a specified topic, retrieves video transcripts, and persists the data in DuckDB for efficient querying and analysis.

## Features

- **Topic-based Search**: Search YouTube videos using customizable topics
- **Comprehensive Data Collection**: Collect video URLs, titles, descriptions, and transcripts
- **Transcript Extraction**: Automatically fetch video transcripts where available
- **Persistent Storage**: Store all data in DuckDB for fast querying and analysis
- **MCP Integration**: Uses Context7 MCP server for YouTube API interactions

## Tech Stack

- **Apache Airflow**: Workflow orchestration and scheduling
- **DuckDB**: High-performance analytical database
- **YouTube Data API v3**: For video search and metadata
- **YouTube Transcript API**: For transcript extraction
- **Python**: Core programming language
- **MCP (Model Context Protocol)**: Context7 server for API interactions

## Project Structure

```
antigravity-mcp-airflow-duckdb-pipeline-pull-data-from-youtube/
├── dags/
│   └── youtube_pipeline.py          # Main Airflow DAG
├── C:\Users\d_local\Documents\Cline\MCP\youtube-server/  # Context7 MCP Server
│   ├── src/youtube-server/
│   │   └── index.ts                 # MCP server implementation
│   ├── package.json                 # Node.js dependencies
│   ├── tsconfig.json               # TypeScript configuration
│   └── build/                      # Compiled JavaScript (after build)
├── README.md                        # This file
├── .gitignore                      # Git ignore rules
└── requirements.txt               # Python dependencies (to be created)
```

### Key Components

1. **Airflow DAG (`dags/youtube_pipeline.py`)**:
   - Orchestrates the data pipeline workflow
   - Contains two main tasks: search and process videos
   - Handles topic input and data persistence

2. **Context7 MCP Server**:
   - Custom MCP server for YouTube API interactions
   - Provides `search_videos` and `get_transcript` tools
   - Enables modular API access through MCP protocol

3. **DuckDB Database**:
   - Stores video metadata and transcripts
   - Optimized for analytical queries
   - File-based database for easy deployment

## How Context7 MCP Server Works

The Context7 MCP server acts as an intermediary between your applications and the YouTube API:

### Server Architecture
- **Framework**: Built using Model Context Protocol (MCP) SDK
- **Language**: TypeScript/Node.js for robust API handling
- **Tools Provided**:
  - `search_videos`: Searches YouTube for videos based on topics
  - `get_transcript`: Extracts transcripts from individual videos

### API Integration
1. **Authentication**: Uses YouTube Data API v3 with API key authentication
2. **Search Functionality**: Calls YouTube Search API to find relevant videos
3. **Transcript Extraction**: Uses YouTube Transcript API for caption retrieval
4. **Error Handling**: Graceful handling of API limits and unavailable transcripts

### Usage in Data Pipeline
The MCP server provides a standardized interface for YouTube data access:
- **Modularity**: Separates API logic from pipeline orchestration
- **Reusability**: Can be used by multiple applications
- **Maintainability**: Centralized API key management and error handling

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
- Node.js (for MCP server)

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

## MCP Server Setup

The project uses a custom MCP server (Context7) for YouTube API interactions.

1. Build the MCP server:
   ```bash
   cd C:\Users\d_local\Documents\Cline\MCP\youtube-server
   npm install
   npm run build
   ```

2. Add to MCP settings (cline_mcp_settings.json):
   ```json
   {
     "mcpServers": {
       "Context7": {
         "command": "node",
         "args": ["C:\\Users\\d_local\\Documents\\Cline\\MCP\\youtube-server\\build\\index.js"],
         "env": {
           "YOUTUBE_API_KEY": "your_youtube_api_key_here"
         }
       }
     }
   }
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This project is for educational and research purposes. Please respect YouTube's Terms of Service and API usage limits.
