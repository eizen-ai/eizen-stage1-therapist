"""
Redis Session Manager for TRT System
Handles session persistence with self-hosted Redis
"""

import redis
import json
import os
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RedisSessionManager:
    """Manages TRT therapy sessions in Redis"""

    def __init__(self, redis_url: str = None):
        """
        Initialize Redis connection

        Args:
            redis_url: Redis connection URL (from environment or parameter)
        """
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://:changeme@localhost:6379")

        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)

            # Test connection
            self.redis.ping()
            logger.info(f"✅ Redis connected successfully")

        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

        # Default TTL: 24 hours
        self.session_ttl = 86400

    def save_session_state(self, session_id: str, session_state) -> bool:
        """
        Save session state to Redis

        Args:
            session_id: Unique session identifier
            session_state: TRTSessionState object

        Returns:
            True if successful
        """
        try:
            key = f"trt:session:{session_id}:state"

            # Convert session state to dict
            data = {
                "session_id": session_id,
                "current_stage": session_state.current_stage,
                "current_substate": session_state.current_substate,
                "body_questions_asked": str(session_state.body_questions_asked),
                "stage_1_completion": json.dumps(session_state.stage_1_completion),
                "last_interaction": datetime.now().isoformat(),
                "created_at": getattr(session_state, 'created_at', datetime.now().isoformat())
            }

            # Save as hash
            self.redis.hset(key, mapping=data)

            # Set TTL (24 hours)
            self.redis.expire(key, self.session_ttl)

            # Add to active sessions index (sorted by timestamp)
            self.redis.zadd("trt:active_sessions", {session_id: datetime.now().timestamp()})

            logger.info(f"✅ Session saved: {session_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save session {session_id}: {e}")
            return False

    def load_session_state(self, session_id: str) -> Optional[Dict]:
        """
        Load session state from Redis

        Args:
            session_id: Unique session identifier

        Returns:
            Dict with session data or None if not found
        """
        try:
            key = f"trt:session:{session_id}:state"

            # Get hash data
            data = self.redis.hgetall(key)

            if not data:
                logger.info(f"ℹ️ Session not found: {session_id}")
                return None

            # Parse JSON fields
            if "stage_1_completion" in data:
                data["stage_1_completion"] = json.loads(data["stage_1_completion"])

            # Convert numeric fields
            if "body_questions_asked" in data:
                data["body_questions_asked"] = int(data["body_questions_asked"])

            logger.info(f"✅ Session loaded: {session_id}")
            return data

        except Exception as e:
            logger.error(f"❌ Failed to load session {session_id}: {e}")
            return None

    def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists in Redis

        Args:
            session_id: Unique session identifier

        Returns:
            True if session exists
        """
        try:
            return self.redis.exists(f"trt:session:{session_id}:state") > 0
        except Exception as e:
            logger.error(f"❌ Failed to check session existence: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session from Redis

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful
        """
        try:
            # Delete all keys for this session
            keys = [
                f"trt:session:{session_id}:state",
                f"trt:session:{session_id}:history",
                f"trt:session:{session_id}:meta"
            ]

            self.redis.delete(*keys)

            # Remove from active sessions index
            self.redis.zrem("trt:active_sessions", session_id)

            logger.info(f"✅ Session deleted: {session_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete session {session_id}: {e}")
            return False

    def add_conversation_exchange(self, session_id: str, exchange: Dict) -> bool:
        """
        Add conversation exchange to history

        Args:
            session_id: Unique session identifier
            exchange: Dict with turn, client_input, therapist_response, etc.

        Returns:
            True if successful
        """
        try:
            key = f"trt:session:{session_id}:history"

            # Add timestamp
            exchange["timestamp"] = datetime.now().isoformat()

            # Add to list (newest first)
            self.redis.lpush(key, json.dumps(exchange))

            # Keep only last 50 exchanges (trim old ones)
            self.redis.ltrim(key, 0, 49)

            # Set TTL
            self.redis.expire(key, self.session_ttl)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to save conversation exchange: {e}")
            return False

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Get conversation history

        Args:
            session_id: Unique session identifier
            limit: Maximum number of exchanges to return

        Returns:
            List of conversation exchanges (newest first)
        """
        try:
            key = f"trt:session:{session_id}:history"

            # Get last N exchanges
            history = self.redis.lrange(key, 0, limit - 1)

            # Parse JSON
            return [json.loads(exchange) for exchange in history]

        except Exception as e:
            logger.error(f"❌ Failed to get conversation history: {e}")
            return []

    def save_session_metadata(self, session_id: str, metadata: Dict) -> bool:
        """
        Save session metadata

        Args:
            session_id: Unique session identifier
            metadata: Dict with metadata (platform, app_version, etc.)

        Returns:
            True if successful
        """
        try:
            key = f"trt:session:{session_id}:meta"

            # Save as hash
            self.redis.hset(key, mapping=metadata)

            # Set TTL
            self.redis.expire(key, self.session_ttl)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {e}")
            return False

    def list_active_sessions(self, limit: int = 100) -> List[str]:
        """
        List active sessions (most recent first)

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session IDs
        """
        try:
            # Get from sorted set (most recent first)
            return self.redis.zrevrange("trt:active_sessions", 0, limit - 1)

        except Exception as e:
            logger.error(f"❌ Failed to list active sessions: {e}")
            return []

    def get_session_count(self) -> int:
        """
        Get total number of active sessions

        Returns:
            Number of active sessions
        """
        try:
            return self.redis.zcard("trt:active_sessions")
        except Exception as e:
            logger.error(f"❌ Failed to get session count: {e}")
            return 0

    def cleanup_inactive_sessions(self, hours: int = 24) -> int:
        """
        Remove sessions inactive for X hours

        Args:
            hours: Inactive threshold in hours

        Returns:
            Number of sessions cleaned up
        """
        try:
            import time
            cutoff = time.time() - (hours * 3600)

            # Get inactive sessions
            inactive = self.redis.zrangebyscore("trt:active_sessions", "-inf", cutoff)

            # Delete each
            count = 0
            for session_id in inactive:
                if self.delete_session(session_id):
                    count += 1

            if count > 0:
                logger.info(f"✅ Cleaned up {count} inactive sessions")

            return count

        except Exception as e:
            logger.error(f"❌ Failed to cleanup sessions: {e}")
            return 0

    def health_check(self) -> Dict:
        """
        Check Redis connection health

        Returns:
            Dict with health status
        """
        try:
            # Ping Redis
            self.redis.ping()

            # Get stats
            info = self.redis.info()

            return {
                "status": "healthy",
                "connected": True,
                "active_sessions": self.get_session_count(),
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human")
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
