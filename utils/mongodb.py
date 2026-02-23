# utils/mongodb.py

from datetime import datetime, timezone
from config import Config


def get_mongo_client():
    """Return MongoClient or None if URI not configured / connection fails."""
    if not Config.MONGODB_URI:
        return None
    try:
        from pymongo import MongoClient
        client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Force a connection check
        client.admin.command('ping')
        return client
    except Exception:
        return None


def log_usage(event, **fields):
    """Log a usage event to MongoDB. Fire-and-forget, silent on failure.

    Args:
        event: Event name (e.g. 'data_load', 'chart_render', 'dashboard_export')
        **fields: Event-specific fields (e.g. source_type='upload', file_ext='csv')
    """
    try:
        client = get_mongo_client()
        if client is None:
            return

        db = client[Config.MONGODB_DATABASE]
        collection = db[Config.MONGODB_COLLECTION_LOGS]

        document = {
            "event": event,
            "timestamp": datetime.now(timezone.utc),
            "language": Config.APP_LANGUAGE,
            "git_commit": Config.GIT_COMMIT,
        }
        document.update(fields)

        collection.insert_one(document)
        client.close()
    except Exception:
        pass


def save_feedback(category, message, language):
    """Save feedback document to MongoDB.

    Returns:
        tuple: (success: bool, error: str | None)
    """
    try:
        client = get_mongo_client()
        if client is None:
            return False, "Database connection is not available."

        db = client[Config.MONGODB_DATABASE]
        collection = db[Config.MONGODB_COLLECTION_FEEDBACK]

        document = {
            "category": category,
            "message": message,
            "language": language,
            "timestamp": datetime.now(timezone.utc),
            "git_commit": Config.GIT_COMMIT,
        }

        collection.insert_one(document)
        client.close()
        return True, None

    except Exception as e:
        return False, str(e)
