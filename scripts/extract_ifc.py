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
    "IfcSpace", "IfcSpatialZone", "IfcZone",
    "IfcTendon", "IfcTendonAnchor", "IfcTendonConduit",
    "IfcReinforcingBar", "IfcReinforcingMesh",
    # IFC4X3 infrastructure elements (by_type includes subtypes, so base classes catch all)
    "IfcBearing", "IfcDeepFoundation",
    "IfcCourse", "IfcEarthworksElement",
    "IfcPavement", "IfcKerb",
    "IfcRail", "IfcTrackElement",
    "IfcSurfaceFeature",
    "IfcFacilityPart",
    "IfcCivilElement",
    "IfcSignal", "IfcSign",
]

# IFC4X3 spatial container types (different from IFC4 building hierarchy)
SPATIAL_TYPES_IFC4 = [
    "IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcSpace",
]
SPATIAL_TYPES_IFC4X3 = [
    "IfcProject", "IfcSite",
    "IfcFacility", "IfcFacilityPart", "IfcFacilityPartCommon",
    "IfcRoad", "IfcRailway", "IfcBridge",
    "IfcMarineFacility",
]

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

            elements_rows.append({
                "GlobalId":    gid,
                "Name":        name,
                "Type":        etype,
                "Description": el.Description or "",
                "ObjectType":  getattr(el, "ObjectType", "") or "",
                "Tag":         getattr(el, "Tag", "") or "",
            })

            for pset_name, props in ifcopenshell.util.element.get_psets(el).items():
                for prop_name, prop_val in props.items():
                    if prop_name == "id":
                        continue
                    properties_rows.append({
                        "GlobalId": gid, "Name": name, "Type": etype,
                        "PropertySet": pset_name, "Property": prop_name, "Value": prop_val,
                    })

            for qset_name, qs in ifcopenshell.util.element.get_psets(el, qtos_only=True).items():
                for q_name, q_val in qs.items():
                    if q_name == "id":
                        continue
                    quantities_rows.append({
                        "GlobalId": gid, "Name": name, "Type": etype,
                        "QuantitySet": qset_name, "Quantity": q_name, "Value": q_val,
                    })

            material = ifcopenshell.util.element.get_material(el)
            if material:
                materials_rows.append({
                    "GlobalId": gid, "Name": name, "Type": etype,
                    "Material": material.Name if hasattr(material, "Name") else str(material),
                })

    # Pick spatial types based on schema — IFC4X3 uses facility/road/rail/bridge hierarchy
    is_ifc4x3 = schema.upper().startswith("IFC4X3") or schema.upper() == "IFC4X3_ADD2"
    spatial_query_types = SPATIAL_TYPES_IFC4X3 if is_ifc4x3 else SPATIAL_TYPES_IFC4

    spatial_rows = []
    seen_spatial_gids = set()
    for entity_type in spatial_query_types:
        try:
            for elem in model.by_type(entity_type):
                if elem.GlobalId in seen_spatial_gids:
                    continue
                seen_spatial_gids.add(elem.GlobalId)
                parent_gid, parent_name = "", ""
                if hasattr(elem, "Decomposes") and elem.Decomposes:
                    parent = elem.Decomposes[0].RelatingObject
                    parent_gid  = parent.GlobalId
                    parent_name = parent.Name or ""
                spatial_rows.append({
                    "GlobalId":       elem.GlobalId,
                    "Name":           elem.Name or "",
                    "Type":           elem.is_a(),
                    "ParentGlobalId": parent_gid,
                    "ParentName":     parent_name,
                })
        except Exception:
            continue

    def safe_value(v):
        if isinstance(v, (int, float, bool, str)) or v is None:
            return v if v is not None else ""
        return str(v)

    for row in properties_rows:
        row["Value"] = safe_value(row["Value"])
    for row in quantities_rows:
        row["Value"] = safe_value(row["Value"])

    print(json.dumps({
        "elements":   elements_rows,
        "properties": properties_rows,
        "quantities": quantities_rows,
        "materials":  materials_rows,
        "spatial":    spatial_rows,
        "metadata": {
            "source_file":          os.path.basename(ifc_path),
            "schema":               schema,
            "extraction_timestamp": datetime.now().isoformat(),
            "pipeline":             "ifcopenshell",
            "counts": {
                "elements":         len(elements_rows),
                "properties":       len(properties_rows),
                "quantities":       len(quantities_rows),
                "materials":        len(materials_rows),
                "spatial_entities": len(spatial_rows),
            },
        },
    }))

if __name__ == "__main__":
    main()
