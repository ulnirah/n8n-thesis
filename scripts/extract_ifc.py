#!/usr/bin/env python3
"""
extract_ifc.py — IfcOpenShell IFC extractor for n8n Pipeline B
Thesis: Uncertainty-Aware Risk Screening from Imperfect BIM
Author: Annisa (EMJM NORISK, UPC Barcelona)

Usage:
    python3 extract_ifc.py <path_to_ifc_file>

Output:
    JSON to stdout — n8n captures this via Execute Command node (2.3).
"""

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
    # IFC4X3 infrastructure elements (by_type includes subtypes)
    "IfcBearing", "IfcDeepFoundation",
    "IfcCourse", "IfcEarthworksElement",
    "IfcPavement", "IfcKerb",
    "IfcRail", "IfcTrackElement",
    "IfcSurfaceFeature",
    "IfcFacilityPart",
    "IfcCivilElement",
    "IfcSignal", "IfcSign",
]

# Spatial container types differ between IFC4 and IFC4X3
SPATIAL_TYPES_IFC4 = [
    "IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcSpace",
]
SPATIAL_TYPES_IFC4X3 = [
    "IfcProject", "IfcSite",
    "IfcFacility", "IfcFacilityPart", "IfcFacilityPartCommon",
    "IfcRoad", "IfcRailway", "IfcBridge",
    "IfcMarineFacility",
]


def resolve_material_name(material):
    """Return a readable material name string for any IFC material assignment type."""
    if material is None:
        return ""
    mat_class = material.is_a() if hasattr(material, "is_a") else ""

    if mat_class == "IfcMaterial":
        return material.Name or ""

    if mat_class == "IfcMaterialList":
        return ", ".join(
            m.Name for m in (material.Materials or [])
            if hasattr(m, "Name") and m.Name
        )

    if mat_class in ("IfcMaterialLayerSet", "IfcMaterialLayerSetUsage"):
        layer_set = material.ForLayerSet if mat_class == "IfcMaterialLayerSetUsage" else material
        return ", ".join(
            l.Material.Name for l in (layer_set.MaterialLayers or [])
            if hasattr(l, "Material") and l.Material and l.Material.Name
        )

    if mat_class == "IfcMaterialProfileSet":
        return ", ".join(
            p.Material.Name for p in (material.MaterialProfiles or [])
            if hasattr(p, "Material") and p.Material and p.Material.Name
        )

    if mat_class == "IfcMaterialConstituentSet":
        return ", ".join(
            c.Material.Name for c in (material.MaterialConstituents or [])
            if hasattr(c, "Material") and c.Material and c.Material.Name
        )

    return getattr(material, "Name", None) or ""


def safe_value(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        return v
    if isinstance(v, (list, tuple)):
        return ", ".join(str(i) for i in v)
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

            mat_name = resolve_material_name(ifcopenshell.util.element.get_material(el))
            if mat_name:
                materials_rows.append({
                    "GlobalId": gid, "Name": name, "Type": etype,
                    "Material": mat_name,
                })

    # Schema-aware spatial query — IFC4X3 uses road/rail/bridge/facility hierarchy
    is_ifc4x3 = schema.upper().startswith("IFC4X3")
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
