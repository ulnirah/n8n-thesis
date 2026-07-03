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
    "IfcElementAssembly",
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

            # ✅ Category instead of Type — matches Pipeline A + all downstream nodes
            elements_rows.append({
                "GlobalId":    gid,
                "Name":        name,
                "Category":    etype,
                "Description": el.Description or "",
                "ObjectType":  getattr(el, "ObjectType", "") or "",
                "Tag":         getattr(el, "Tag", "") or "",
                "is_external": is_external,
            })

            # ✅ Properties only if flag set — avoids memory issues on large models
            if INCLUDE_PROPERTIES:
                try:
                    for pset_name, props in ifcopenshell.util.element.get_psets(el).items():
                        for prop_name, prop_val in props.items():
                            if prop_name == "id":
                                continue
                            properties_rows.append({
                                "GlobalId":    gid,
                                "Name":        name,
                                "Category":    etype,
                                "PropertySet": pset_name,
                                "Property":    prop_name,
                                "Value":       safe_value(prop_val),
                            })
                except Exception as e:
                    # 🔍 DEBUG — remove after diagnosing
                    print(f"PROPERTIES ERROR on {gid} ({etype}): {e}", file=sys.stderr)

            # ✅ Always extract quantities — needed for QTO comparison in Node 3
            try:
                for qset_name, qs in ifcopenshell.util.element.get_psets(
                    el, qtos_only=True
                ).items():
                    for q_name, q_val in qs.items():
                        if q_name == "id":
                            continue
                        quantities_rows.append({
                            "GlobalId":    gid,
                            "Name":        name,
                            "Category":    etype,
                            "QuantitySet": qset_name,
                            "Quantity":    q_name,
                            "Value":       safe_value(q_val),
                        })
            except Exception as e:
                # 🔍 DEBUG — remove after diagnosing
                print(f"QUANTITIES ERROR on {gid} ({etype}): {e}", file=sys.stderr)

            # ✅ Materials only if flag set
            if INCLUDE_MATERIALS:
                try:
                    material = ifcopenshell.util.element.get_material(el)
                    if material:
                        materials_rows.append({
                            "GlobalId": gid,
                            "Name":     name,
                            "Category": etype,
                            "Material": material.Name if hasattr(material, "Name") else str(material),
                        })
                except Exception:
                    pass

    # ✅ Schema-aware spatial extraction
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

    print(json.dumps({
        "elements":   elements_rows,
        "quantities": quantities_rows,
        "properties": properties_rows,
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
