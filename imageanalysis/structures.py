"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import spec2nexus as s2n
from spec2nexus import spec

# ==================================================================================

class Project:

    def __init__(
        self, 
        project_path: str, 
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:
        
        # Path variables
        self.path = project_path
        self.spec_path = spec_path
        self.instrument_path = instrument_path
        self.detector_path = detector_path

        self.spec_data = spec.SpecDataFile(spec_path)
        self.scan_numbers = self.spec_data.getScanNumbers()

# ==================================================================================

class Scan:

    def __init__(self) -> None:
        pass

# ==================================================================================