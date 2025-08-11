# AnimeDekho API

This is a Flask-based API that scrapes video URLs from animedekho.co. It uses Playwright to navigate the website and extract video URLs from the network requests.

## API Endpoints

### Get Video URL

```
GET /api/video
```

**Query Parameters:**
- `title` (string, required): The anime title
- `season` (integer, required): The season number
- `episode` (integer, required): The episode number

**Example Request:**
```
GET /api/video?title=shinchan&season=1&episode=1
```

**Example Response:**
```json
{
  "success": true,
  "video_url": "https://play.zephyrflick.top/video/abc123def456",
  "message": "Video URL found successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No video URL found. Try different season/episode numbers.",
  "message": "No video URL found"
}
```

### Health Check

```
GET /health
```

Returns a JSON response indicating that the API is running.

### Home

```
GET /
```

Returns API documentation in JSON format.

## Deployment to Render

To deploy this API to Render, follow these steps:

1. Fork this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" and select "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - Name: `animedekho-api` (or any name you prefer)
   - Region: Select "Singapore" or "Mumbai" for better access to Indian websites
   - Branch: `main` (or your default branch)
   - Root Directory: Leave empty if this is the root of your repository
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && playwright install-deps && playwright install firefox`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
6. Click "Create Web Service"

### Important Note About Cloudflare Security

The website animedekho.co uses Cloudflare security which may block requests from certain regions or IP ranges. To minimize the chances of being blocked:

1. Deploy your service in Render's Mumbai or Singapore region
2. The API uses Firefox instead of Chromium as some websites are less likely to block Firefox
3. If you still encounter issues, you might need to:
   - Add delays between requests
   - Rotate user agents
   - Consider using a proxy service

## Local Development

To run the API locally:

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```
   playwright install-deps
   playwright install firefox
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the API at `http://localhost:5000`

## Testing the API

You can test the API using curl:

```bash
curl "http://localhost:5000/api/video?title=shinchan&season=1&episode=1"
```

Or by visiting in your browser:
```
http://localhost:5000/api/video?title=shinchan&season=1&episode=1