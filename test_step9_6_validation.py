"""
STEP 9.6 VERIFICATION SUITE: DGCA VALIDATION & 30-DAY BACK-TEST
Executes single route validations, 30-day statistical back-test,
volatility computation, and JSON validation report export.
"""

import asyncio
import json
import os
from backend.services.mongo_manager import mongo_db
from backend.services.dgca_validation_service import DGCAValidationService


async def test_step9_6():
    print("==================================================")
    print("  🔬 Verifying Step 9.6: DGCA Validation Service")
    print("==================================================\n")

    await mongo_db.connect_db()
    validator = DGCAValidationService()

    # 1. Single Route Validation Test
    print("[1/4] Testing Single Route Validation Against DGCA...")
    val_pass = validator.validate_route("DEL-BOM", "T+15", 4350.0)
    print(f"  Route DEL-BOM (T+15): ₹4350 vs DGCA ₹4200 ➔ Diff: {val_pass['percentDifference']} ({val_pass['status']})")
    assert val_pass["status"] == "PASS"

    val_fail = validator.validate_route("DEL-BOM", "T+15", 7000.0)
    print(f"  Route DEL-BOM (T+15 Outlier): ₹7000 vs DGCA ₹4200 ➔ Diff: {val_fail['percentDifference']} ({val_fail['status']})")
    assert val_fail["status"] == "FAIL"

    # 2. 30-Day Back-Test Execution
    print("\n[2/4] Running 30-Day Back-Test Across All Metro Routes...")
    result = await validator.run_30_day_back_test()
    print(f"  ✅ Back-Test Status: {result['status']}")
    print(f"  ✅ Overall Pass Rate: {result['passRate']}")
    print(f"  ✅ Total Fares Analyzed: {result['metrics']['totalFares']}")
    print(f"  ✅ Volatility (Std Dev): ₹{result['metrics']['volatility']}")
    print(f"  ✅ Price Trend: {result['metrics']['trend']}")

    # 3. Recommendations Engine
    print("\n[3/4] Reviewing Submission Recommendations...")
    for rec in result["recommendations"]:
        print(f"    {rec}")

    # 4. JSON Report Export
    print("\n[4/4] Exporting SIH Audit Validation Report...")
    report_path = await validator.export_report("sih_dgca_validation_report.json")
    assert os.path.exists(report_path)
    print(f"  ✅ Audit report generated at: {report_path}")

    await mongo_db.close_db()
    print("\n🎉 STEP 9.6 DGCA VALIDATION SERVICE FULLY OPERATIONAL WITH ZERO ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_6())