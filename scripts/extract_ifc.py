import sys
import json
import os
from datetime import datetime

try:
    import ifcopenshell
    import ifcopenshell.util.element
except ImportError:
    print(json.dumps({
        "error": "ifcopenshell not installed. Run: pip install ifcopenshell",
        "elements": [], "properties": [], "quantities": [], "materials": []
    }))
    sys.exit(1)

ELEMENT_TYPES = [
    # IFC4 building elements
    "IfcWall", "IfcWallStandardCase",
    "IfcSlab", "IfcSlabStandardCase",
    "IfcBeam", "IfcBeamStandardCase",
    "IfcColumn", "IfcColumnStandardCase",
    "IfcRoof", "IfcChimney",
    "IfcStair", "IfcStairFlight",
    "IfcRamp", "IfcRampFlight",
    "IfcDoor", "IfcWindow",
    "IfcCovering", "IfcRailing",
    "IfcPlate", "IfcMember",
    "IfcFooting", "IfcPile",
    "IfcBuildingElementProxy",
    "IfcFurniture", "IfcFurnishingElement",
    "IfcSpace",
    # ✅ Removed IfcSpatialZone and IfcZone — no QTO, causes A/B coverage asymmetry
    "IfcTendon", "IfcTendonAnchor", "IfcTendonConduit",
    "IfcReinforcingBar", "IfcReinforcingMesh",
    # IFC4x3 infrastructure elements
    "IfcBearing", "IfcDeepFoundation",
    "IfcCourse", "IfcEarthworksElement",
    "IfcPavement", "IfcKerb",
    "IfcRail", "IfcTrackElement",
    "IfcSurfaceFeature",
    "IfcFacilityPart",
    "IfcCivilElement",
    "IfcSignal", "IfcSign",
]

# ✅ IFC4x3-aware spatial hierarchy
SPATIAL_TYPES_IFC4 = [
    "IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcSpace",
]
SPATIAL_TYPES_IFC4X3 = [
    "IfcProject", "IfcSite",
    "IfcFacility", "IfcFacilityPart", "IfcFacilityPartCommon",
    "IfcRoad", "IfcRailway", "IfcBridge",
    "IfcMarineFacility",
]

# Optional flags — keeps output lean by default
INCLUDE_PROPERTIES = "--include-properties" in sys.argv
INCLUDE_MATERIALS  = "--include-materials"  in sys.argv

def safe_value(v):
    if isinstance(v, (int, float, bool, str)) or v is None:
        return v if v is not None else ""
    return str(v)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 extract_ifc.py <path_to_ifc_file>"}))
        sys.exit(1)

    ifc_path = sys.argv[1]

    if not os.path.exists(ifc_path):
        print(json.dumps({"error": f"File not found: {ifc_path}"}))
        sys.exit(1)

    try:
        model = ifcopenshell.open(ifc_path)
    except Exception as e:
        print(json.dumps({"error": f"Failed to open IFC file: {str(e)}"}))
        sys.exit(1)

    schema = model.schema
    elements_rows, properties_rows, quantities_rows, materials_rows = [], [], [], []
    seen_gids = set()

    for ifc_type in ELEMENT_TYPES:
        try:
            type_elements = model.by_type(ifc_type)
        except Exception:
            continue

        for el in type_elements:
            gid = el.GlobalId
            if gid in seen_gids:
                continue
            seen_gids.add(gid)

            name  = el.Name or ""
            etype = el.is_a()

            # ✅ Extract IsExternal as flat field for zone assignment
            is_external = False
            try:
                all_psets = ifcopenshell.util.element.get_psets(el)
                for pset_name, props in all_psets.items():
                    if "IsExternal" in props:
                        is_external = bool(props["IsExternal"])
                        break
            except Exception:
                pass

            # ✅ Category instead of Type — matches Pipeline A + all
