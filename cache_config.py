from flask_caching import Cache

# Initialize cache without app
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour in seconds
    'CACHE_KEY_PREFIX': 'zoom_mock_'  # Add a prefix to avoid conflicts
})

# Remove the init_cache function since we'll initialize directly in app.py 