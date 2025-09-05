from typing import Any, Dict


def fetch_spain_stats(cnae: str, region: str) -> Dict[str, Any]:
    return {
        "region": region,
        "cnae": cnae,
        "note": "Replace with INE API calls",
        "sources": ["https://www.ine.es/dyngs/DAB/index.htm?cid=1099"],
    }
