from neo4j.time import DateTime, Date, Time, Duration
from typing import Any

def serialize_neo4j_value(value: Any) -> Any:
    """Convert Neo4j types to JSON-serializable Python types"""
    if isinstance(value, DateTime):
        return value.isoformat()
    elif isinstance(value, Date):
        return value.isoformat()
    elif isinstance(value, Time):
        return value.isoformat()
    elif isinstance(value, Duration):
        return str(value)
    elif isinstance(value, dict):
        return {k: serialize_neo4j_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [serialize_neo4j_value(item) for item in value]
    else:
        return value