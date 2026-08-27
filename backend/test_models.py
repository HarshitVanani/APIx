from datetime import datetime
from models.schema import FareRecord, CabinClass

sample = FareRecord(
    source="indigo",
    route_from="DEL",
    route_to="BOM",
    departure_date=datetime.now(),
    fare_price=4500.0,
    tax=500.0,
    fees=250.0,
    total_price=5250.0,
    advance_window=7,
    cabin_class=CabinClass.ECONOMY,
    airline="IndiGo"
)

print("\n--- TEST RESULT ---")
print("Pydantic Schema Validation Passed!")
print(sample.model_dump())