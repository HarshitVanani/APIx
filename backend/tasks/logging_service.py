"""
STEP 9.4: COMPREHENSIVE LOGGING SERVICE
Track all scraper activities, errors, and performance metrics.
Provides dual-channel persistence: MongoDB ('scraper_logs') + Structured Local Log Files.
SIH 2026 - APIx Project
"""

import csv
import json
import logging
import os
import random
import string
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Ensure backend root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.mongo_manager import mongo_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LoggingService")


class LoggingService:
    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            self.log_dir = os.path.abspath(os.path.join(BACKEND_DIR, "..", "logs"))
        else:
            self.log_dir = os.path.abspath(log_dir)

        self._initialize_log_directory()
        self.session_id = self.generate_session_id()

    def _initialize_log_directory(self) -> None:
        """Initialize local log directory if it does not exist."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            logger.info(f"Created log directory: {self.log_dir}")

    def generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"SESSION_{int(time.time() * 1000)}_{random_suffix}"

    # ============ SCRAPER ACTIVITY LOGGING ============

    async def log_scraper_activity(self, activity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Log Scraper Activity to MongoDB and local JSONL fallback.
        activity_data keys:
          - source: str (e.g. 'indigo_scraper')
          - route: str (e.g. 'DEL-BOM')
          - status: str ('success', 'partial', 'failed', 'timeout')
          - faresScraped: int
          - errorMessage: Optional[str]
          - executionTime: float (ms)
          - metadata: dict
        """
        source = activity_data.get("source", "unknown_source")
        route = activity_data.get("route", "")
        status = activity_data.get("status", "success")
        fares_scraped = int(activity_data.get("faresScraped", 0))
        error_message = activity_data.get("errorMessage")
        execution_time = float(activity_data.get("executionTime", 0.0))
        metadata = activity_data.get("metadata", {})

        now_utc = datetime.now(timezone.utc)
        meta_payload = {
            **metadata,
            "sessionId": self.session_id,
            "timestamp": now_utc.isoformat(),
        }

        log_doc = {
            "date": now_utc,
            "source": source,
            "route": route,
            "status": status,
            "faresScraped": fares_scraped,
            "errorMessage": error_message,
            "executionTime": execution_time,
            "metadata": meta_payload,
        }

        db = mongo_db.db
        if db is not None:
            try:
                res = await db["scraper_logs"].insert_one(log_doc)
                log_doc["_id"] = res.inserted_id
            except Exception as err:
                logger.error(f"Error logging to MongoDB: {err}")
                self.write_to_local_log(activity_data)
        else:
            self.write_to_local_log(activity_data)

        # Write to local file stream
        self.write_to_local_log(activity_data)
        return log_doc

    def write_to_local_log(self, activity_data: Dict[str, Any]) -> None:
        """Write logs to local date-partitioned log file."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"scraper_{date_str}.log")

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessionId": self.session_id,
            **activity_data,
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, default=str) + "\n")
        except Exception as err:
            logger.error(f"Failed to write to local log file: {err}")

    # ============ SCRAPER STATISTICS AGGREGATION ============

    async def get_scraper_stats(self, source: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """Aggregate scraper metrics from MongoDB over the specified timeframe."""
        db = mongo_db.db
        if db is None:
            return []

        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        match_query: Dict[str, Any] = {"date": {"$gte": start_date}}
        if source:
            match_query["source"] = source

        pipeline = [
            {"$match": match_query},
            {
                "$group": {
                    "_id": "$source",
                    "totalRuns": {"$sum": 1},
                    "successfulRuns": {
                        "$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                    },
                    "failedRuns": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                    },
                    "partialRuns": {
                        "$sum": {"$cond": [{"$eq": ["$status", "partial"]}, 1, 0]}
                    },
                    "totalFaresScraped": {"$sum": "$faresScraped"},
                    "avgExecutionTime": {"$avg": "$executionTime"},
                    "maxExecutionTime": {"$max": "$executionTime"},
                    "minExecutionTime": {"$min": "$executionTime"},
                }
            }
        ]

        cursor = db["scraper_logs"].aggregate(pipeline)
        raw_stats = await cursor.to_list(length=100)

        results = []
        for stat in raw_stats:
            total_runs = stat.get("totalRuns", 0)
            successful_runs = stat.get("successfulRuns", 0)
            total_fares = stat.get("totalFaresScraped", 0)
            avg_exec = stat.get("avgExecutionTime") or 0.0
            max_exec = stat.get("maxExecutionTime") or 0.0
            min_exec = stat.get("minExecutionTime") or 0.0

            success_rate = f"{(successful_runs / total_runs * 100):.2f}%" if total_runs > 0 else "0.00%"
            avg_fares = f"{(total_fares / total_runs):.0f}" if total_runs > 0 else "0"

            results.append({
                "source": stat.get("_id"),
                "totalRuns": total_runs,
                "successfulRuns": successful_runs,
                "failedRuns": stat.get("failedRuns", 0),
                "partialRuns": stat.get("partialRuns", 0),
                "successRate": success_rate,
                "totalFaresScraped": total_fares,
                "avgFaresPerRun": avg_fares,
                "avgExecutionTime": f"{avg_exec:.2f}ms",
                "maxExecutionTime": f"{max_exec:.2f}ms",
                "minExecutionTime": f"{min_exec:.2f}ms",
            })

        return results

    # ============ DATA QUALITY & SYSTEM AUDIT EVENTS ============

    def log_data_quality_event(self, event_data: Dict[str, Any]) -> None:
        """Log Data Quality events (duplicates, outliers, missing components) to disk."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "eventType": event_data.get("eventType"),
            "severity": event_data.get("severity", "info"),
            "message": event_data.get("message", ""),
            "affectedRecords": event_data.get("affectedRecords", 0),
            "metadata": {
                **event_data.get("metadata", {}),
                "sessionId": self.session_id,
            },
        }
        log_file = os.path.join(self.log_dir, "data_quality.log")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, default=str) + "\n")
        except Exception as err:
            logger.error(f"Failed to log data quality event: {err}")

    def log_api_request(self, request_data: Dict[str, Any]) -> None:
        """Log API HTTP requests for latency & traffic audits."""
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessionId": self.session_id,
            "method": request_data.get("method", "GET"),
            "endpoint": request_data.get("endpoint", ""),
            "statusCode": request_data.get("statusCode", 200),
            "responseTime": request_data.get("responseTime", 0),
            "userId": request_data.get("userId", "anonymous"),
        }
        log_file = os.path.join(self.log_dir, "api_requests.log")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_payload, default=str) + "\n")
        except Exception as err:
            logger.error(f"Failed to log API request: {err}")

    def log_system_event(self, event_data: Dict[str, Any]) -> None:
        """Log System lifecycle events (DB connections, cache, errors)."""
        level = event_data.get("level", "info").lower()
        message = event_data.get("message", "")
        error = event_data.get("error")

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessionId": self.session_id,
            "eventType": event_data.get("eventType", "system"),
            "level": level,
            "message": message,
            "error": str(error) if error is not None else None,
            "metadata": event_data.get("metadata", {}),
        }

        log_file = os.path.join(self.log_dir, "system_events.log")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, default=str) + "\n")
        except Exception as err:
            logger.error(f"Failed to log system event: {err}")

        if level in ("critical", "error"):
            logger.error(f"[{level.upper()}] {message} | {error}")

    # ============ LOG RETRIEVAL & REPORTS ============

    def get_logs_tail(self, filename: str, lines: int = 50) -> List[Dict[str, Any]]:
        """Read the last N lines of a specified log file."""
        log_file = os.path.join(self.log_dir, filename)
        if not os.path.exists(log_file):
            return []

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                raw_lines = [line.strip() for line in f if line.strip()]

            tail = raw_lines[-lines:]
            parsed = []
            for item in tail:
                try:
                    parsed.append(json.loads(item))
                except Exception:
                    parsed.append({"raw": item})
            return parsed
        except Exception as err:
            logger.error(f"Error reading {filename}: {err}")
            return []

    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate a summary of the current day's scraping activity."""
        db = mongo_db.db
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)

        logs: List[Dict[str, Any]] = []
        if db is not None:
            cursor = db["scraper_logs"].find({"date": {"$gte": today_start, "$lt": tomorrow_start}})
            logs = await cursor.to_list(length=10000)

        total_scrapes = len(logs)
        successful = sum(1 for l in logs if l.get("status") == "success")
        failed = sum(1 for l in logs if l.get("status") == "failed")
        partial = sum(1 for l in logs if l.get("status") == "partial")
        total_fares = sum(l.get("faresScraped", 0) for l in logs)

        avg_time = (sum(l.get("executionTime", 0) for l in logs) / total_scrapes) if total_scrapes > 0 else 0.0
        unique_sources = sorted(list({l.get("source") for l in logs if l.get("source")}))

        errors: Dict[str, int] = {}
        for l in logs:
            err = l.get("errorMessage")
            if err:
                errors[err] = errors.get(err, 0) + 1

        return {
            "date": today_start.strftime("%Y-%m-%d"),
            "totalScrapes": total_scrapes,
            "successful": successful,
            "failed": failed,
            "partial": partial,
            "totalFares": total_fares,
            "avgExecutionTime": f"{avg_time:.2f}ms",
            "uniqueSources": unique_sources,
            "errorSummary": errors,
        }

    # ============ EXPORT & HOUSEKEEPING ============

    async def export_logs_to_csv(self, filename: str = "logs_export.csv", days: int = 7) -> str:
        """Export logs from the last N days into CSV format."""
        db = mongo_db.db
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        logs: List[Dict[str, Any]] = []
        if db is not None:
            cursor = db["scraper_logs"].find({"date": {"$gte": start_date}}).sort("date", 1)
            logs = await cursor.to_list(length=100000)

        filepath = os.path.join(self.log_dir, filename)
        header = ["Date", "Source", "Route", "Status", "Fares Scraped", "Execution Time (ms)", "Error Message"]

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            for l in logs:
                d_val = l.get("date")
                d_str = d_val.isoformat() if isinstance(d_val, datetime) else str(d_val)
                writer.writerow([
                    d_str,
                    l.get("source", ""),
                    l.get("route", ""),
                    l.get("status", ""),
                    l.get("faresScraped", 0),
                    l.get("executionTime", 0.0),
                    l.get("errorMessage", ""),
                ])

        return filepath

    async def clear_old_logs(self, days_to_keep: int = 30) -> None:
        """Prune old log records from MongoDB and delete old log files from disk."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

        db = mongo_db.db
        if db is not None:
            del_res = await db["scraper_logs"].delete_many({"date": {"$lt": cutoff_date}})
            logger.info(f"Deleted {del_res.deleted_count} old MongoDB log records.")

        if os.path.exists(self.log_dir):
            for filename in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, filename)
                if os.path.isfile(file_path):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
                    if file_mtime < cutoff_date:
                        try:
                            os.remove(file_path)
                            logger.info(f"Deleted old log file: {filename}")
                        except Exception as err:
                            logger.error(f"Failed to delete {filename}: {err}")


logging_service = LoggingService()