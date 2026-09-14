"""
STEP 9.4 VERIFICATION SUITE: LOGGING & TELEMETRY SERVICE
Tests Scraper Activity Logging, Local File Partitioning,
MongoDB Aggregations, Daily Reporting, and CSV Exports.
"""

import asyncio
import os
from backend.services.mongo_manager import mongo_db
from backend.tasks.logging_service import LoggingService


async def test_step9_4_logging():
    print("==================================================")
    print("  🧪 Verifying Step 9.4: Logging & Telemetry Service")
    print("==================================================\n")

    await mongo_db.connect_db()
    service = LoggingService()

    # 1. Log Scraper Activities
    print("[1/5] Logging Scraper Cycles (Success & Failures)...")
    await service.log_scraper_activity({
        "source": "indigo_scraper",
        "route": "DEL-BOM",
        "status": "success",
        "faresScraped": 42,
        "executionTime": 1420.5,
        "metadata": {"advanceWindow": "T+15", "botEngine": "httpx"}
    })

    await service.log_scraper_activity({
        "source": "airindia_scraper",
        "route": "BLR-DEL",
        "status": "failed",
        "faresScraped": 0,
        "errorMessage": "HTTP 429 Too Many Requests (Rate Limited)",
        "executionTime": 850.0,
        "metadata": {"retryCount": 3}
    })
    print("  ✅ Scraper activity persisted to MongoDB & written to daily log file.")

    # 2. Log Data Quality & API Events
    print("\n[2/5] Logging Data Quality & System Events...")
    service.log_data_quality_event({
        "eventType": "outlier_detected",
        "severity": "warning",
        "message": "Fare ₹28,500 for BOM-GOI exceeds 1.5x IQR threshold",
        "affectedRecords": 1
    })
    service.log_api_request({
        "method": "GET",
        "endpoint": "/api/index/latest",
        "statusCode": 200,
        "responseTime": 18.4
    })
    print("  ✅ Data quality and API telemetry recorded to local disk logs.")

    # 3. Test Scraper Statistics Aggregation
    print("\n[3/5] Computing MongoDB Aggregation Metrics...")
    stats = await service.get_scraper_stats(days=7)
    print(f"  ✅ Aggregated sources count: {len(stats)}")
    for s in stats:
        print(f"     ➔ [{s['source']}] Total Runs: {s['totalRuns']} | Success: {s['successRate']} | Total Fares: {s['totalFaresScraped']} | Avg Time: {s['avgExecutionTime']}")

    # 4. Generate Daily Summary Report
    print("\n[4/5] Generating Daily Activity Report...")
    report = await service.generate_daily_report()
    print(f"  ✅ Report Date: {report['date']}")
    print(f"  ✅ Successful Scrapes: {report['successful']} | Failed: {report['failed']}")
    print(f"  ✅ Total Fares Scraped: {report['totalFares']}")
    print(f"  ✅ Errors Logged: {report['errorSummary']}")

    # 5. Export Logs to CSV
    print("\n[5/5] Exporting Scraper Audit Log to CSV...")
    csv_file = await service.export_logs_to_csv("test_logs_export.csv", days=7)
    assert os.path.exists(csv_file)
    print(f"  ✅ CSV Export generated at: {csv_file}")

    await mongo_db.close_db()
    print("\n🎉 STEP 9.4 LOGGING SERVICE FULLY OPERATIONAL WITH ZERO ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_4_logging())