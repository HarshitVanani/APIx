from datetime import datetime
from services.index_calculator import APIxCalculationEngine
from services.dgca_service import DGCAService

engine = APIxCalculationEngine(DGCAService.get_route_weights())

mock_fares = [
    {"route_from": "DEL", "route_to": "BOM", "total_price": 5200.0, "departure_date": datetime.now()},
    {"route_from": "DEL", "route_to": "BOM", "total_price": 4900.0, "departure_date": datetime.now()},
    {"route_from": "BLR", "route_to": "DEL", "total_price": 5600.0, "departure_date": datetime.now()},
    {"route_from": "BOM", "route_to": "BLR", "total_price": 3800.0, "departure_date": datetime.now()},
    {"route_from": "DEL", "route_to": "CCU", "total_price": 5100.0, "departure_date": datetime.now()},
]

result = engine.calculate_daily_index(mock_fares, datetime.now())

print("\n==========================================")
print("  STEP 6 ENGINE EXECUTION VERIFICATION   ")
print("==========================================")
print(f"APIx Index Value : {result['index_value']}")
print(f"Quality Score    : {result['data_quality_score']}")
print(f"95% CI Range     : ₹{result['lower_ci']} to ₹{result['upper_ci']}")
print(f"Standard Error   : ₹{result['std_error']}")
print(f"Routes Covered   : {result['routes_included']}")
print("==========================================\n")