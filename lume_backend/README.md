# Lume Media Research API

A clean, provider-based FastAPI microservice for media research. Built with dependency injection for easy testing and provider swapping.

## Architecture Overview

```
lume_backend/
├── models/
│   └── schemas.py          # Pydantic models (MediaLink, SearchResult)
├── providers/
│   ├── base.py             # Abstract BaseProvider interface
│   └── mock_provider.py    # MockProvider implementation
├── routers/
│   └── media.py            # FastAPI endpoints
├── main.py                 # Application factory
└── requirements.txt
```

## Key Features

- **Provider Pattern**: Abstract base class allows swapping implementations
- **Dependency Injection**: Clean separation of concerns
- **Pydantic Models**: Type-safe request/response validation
- **Comprehensive Error Handling**: 404, 503, and 500 error responses

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py

# Or with uvicorn
uvicorn main:app --reload --port 8000
```

## API Endpoints

### `GET /resolve/{query}`
Returns the top result for a media query.

```bash
curl http://localhost:8000/resolve/inception
```

**Response:**
```json
{
  "title": "Inception (2010) 1080p BluRay",
  "url": "https://mock-cdn.example.com/movies/inception-2010.mkv",
  "size": 8542781952,
  "seeds": 2450
}
```

### `GET /resolve/search/{query}?limit=10`
Returns all matching results.

```bash
curl "http://localhost:8000/resolve/search/movie?limit=5"
```

**Response:**
```json
{
  "query": "movie",
  "results": [...],
  "total_results": 5,
  "provider_name": "MockProvider"
}
```

### `GET /resolve/health/provider`
Check provider health.

## Swapping Providers

To add a new provider:

1. Create a new class inheriting from `BaseProvider`
2. Implement `search()` and `health_check()` methods
3. Update `get_provider()` dependency in `routers/media.py`

Example:

```python
class TMDBProvider(BaseProvider):
    async def search(self, query: str) -> List[MediaLink]:
        # Implementation
        pass
    
    async def health_check(self) -> bool:
        # Implementation
        pass

# In routers/media.py
def get_provider() -> BaseProvider:
    return TMDBProvider()  # Swap here!
```

## Testing

Use query=`empty` to test 404 handling:
```bash
curl http://localhost:8000/resolve/empty
```

Use query=`all` to get all mock data:
```bash
curl http://localhost:8000/resolve/all
```


## Production Run

Use multiple workers in production to handle concurrent clients:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

Keep `--reload` for development only.

## Documentation

Once running, view interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
