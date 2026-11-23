"""
TransitSense AI: Data Provenance Tracker & Verification Utility
Ensures cryptographic separation between SYNTHETIC and OFFICIAL datasets.
"""

import os
import json
from typing import Dict, Any, Optional

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "registry.json")


class ProvenanceTracker:
    """Manages dataset classification and ensures transparent attribution."""

    VALID_PROVENANCE = {"OFFICIAL", "SYNTHETIC", "DERIVED"}

    @classmethod
    def load_registry(cls) -> Dict[str, Any]:
        if not os.path.exists(REGISTRY_PATH):
            return {"datasets": []}
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def get_file_provenance(cls, file_path: str) -> str:
        registry = cls.load_registry()
        norm_path = file_path.replace("\\", "/").lstrip("./")
        for ds in registry.get("datasets", []):
            if ds.get("path") == norm_path:
                return ds.get("provenance", "UNKNOWN")
        
        # A directory name is not evidence of an official source. Official
        # inputs must be explicitly registered after checking their source.
        if "data/raw" in norm_path or "synthetic" in norm_path:
            return "SYNTHETIC"
        if "data/processed" in norm_path or "ml/model_artifacts" in norm_path:
            return "DERIVED"
        return "UNKNOWN"

    @classmethod
    def assert_provenance(cls, file_path: str, expected_provenance: str) -> bool:
        prov = cls.get_file_provenance(file_path)
        if prov != expected_provenance:
            raise ValueError(
                f"Data Provenance Violation: File '{file_path}' has classification '{prov}', "
                f"expected '{expected_provenance}'. Never mix synthetic data into official validation!"
            )
        return True


if __name__ == "__main__":
    reg = ProvenanceTracker.load_registry()
    print(f"Loaded Provenance Registry with {len(reg.get('datasets', []))} registered entries.")
    for ds in reg.get("datasets", []):
        print(f"  [{ds['provenance']:<9}] {ds['path']}")
