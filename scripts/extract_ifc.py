#!/usr/bin/env python3
"""
extract_ifc.py — IfcOpenShell IFC extractor for n8n Pipeline C
Thesis: Uncertainty-Aware Risk Screening from Imperfect BIM
Author: Annisa (EMJM NORISK, UPC Barcelona)

Usage:
    python3 extract_ifc.py <path_to_ifc_file>

Output:
    JSON to stdout with keys: elements, properties, quantities, materials, metadata
    n8n captures this via Execute Command node.

Based on the working extraction script tested locally via Claude Code.
Uses ifcopenshell.util.element utilities (get_psets, get_material).
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


# Element types to extract — covers buildings, bridges, and infra
ELEMENT_TYPES = [
    # Building elements
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
    # Spatial elements
    "IfcSpace", "IfcSpatialZone", "IfcZone",
    # Bridge / infra types (IFC4.3)
    "IfcBearing", "IfcDeepFoundation",
    "IfcCourse", "IfcEarthworksElement",
    "IfcPavement", "IfcRail", "IfcSurfaceFeature",
    "IfcTendon", "IfcTendonAnchor", "IfcTendonConduit",
    "IfcReinforcingBar", "IfcReinforcingMesh",
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

    elements_rows = []
    properties_rows = []
    quantities_rows = []
    materials_rows = []
    seen_gids = set()

    for ifc_type in ELEMENT_TYPES:
        try:
            type_elements = model.by_type(ifc_type)
        except Exception:
            continue

        for el in type_elements:
            gid = el.GlobalId

            # Deduplicate (inheritance: IfcWallStandardCase is also IfcWall)
            if gid in seen_gids:
                continue
            seen_gids.add(gid)

            name = el.Name or ""
            etype = el.is_a()

            # ── Elements ──
            elements_rows.append({
                "GlobalId": gid,
                "Name": name,
                "Type": etype,
                "Description": el.Description or "",
                "ObjectType": getattr(el, "ObjectType", "") or "",
                "Tag": getattr(el, "Tag", "") or "",
            })

            # ── Properties (using get_psets utility) ──
            psets = ifcopenshell.util.element.get_psets(el)
            for pset_name, props in psets.items():
                for prop_name, prop_val in props.items():
                    if prop_name == "id":
                        continue
                    properties_rows.append({
                        "GlobalId": gid,
                        "Name": name,
                        "Type": etype,
                        "PropertySet": pset_name,
                        "Property": prop_name,
                        "Value": prop_val,
                    })

            # ── Quantities (using get_psets with qtos_only) ──
            qsets = ifcopenshell.util.element.get_psets(el, qtos_only=True)
            for qset_name, qs in qsets.items():
                for q_name, q_val in qs.items():
                    if q_name == "id":
                        continue
                    quantities_rows.append({
                        "GlobalId": gid,
                        "Name": name,
                        "Type": etype,
                        "QuantitySet": qset_name,
                        "Quantity": q_name,
                        "Value": q_val,
                    })

            # ── Materials (using get_material utility) ──
            material = ifcopenshell.util.element.get_material(el)
            if material:
                mat_name = material.Name if hasattr(material, "Name") else str(material)
                materials_rows.append({
                    "GlobalId": gid,
                    "Name": name,
                    "Type": etype,
                    "Material": mat_name,
                })

    # ── Spatial hierarchy (Project > Site > Building > Storey) ──
    spatial_rows = []
    for entity_type in ["IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey"]:
        try:
            for elem in model.by_type(entity_type):
                parent_gid = ""
                parent_name = ""
                if hasattr(elem, "Decomposes") and elem.Decomposes:
                    for rel in elem.Decomposes:
                        parent = rel.RelatingObject
                        parent_gid = parent.GlobalId
                        parent_name = parent.Name or ""
                        break
                spatial_rows.append({
                    "GlobalId": elem.GlobalId,
                    "Name": elem.Name or "",
                    "Type": elem.is_a(),
                    "ParentGlobalId": parent_gid,
                    "ParentName": parent_name,
                })
        except Exception:
            continue

    # ── Ensure all values are JSON-serializable ──
    def safe_value(v):
        if v is None:
            return ""
        if isinstance(v, (int, float, bool, str)):
            return v
        return str(v)

    for row in properties_rows:
        row["Value"] = safe_value(row["Value"])
    for row in quantities_rows:
        row["Value"] = safe_value(row["Value"])

    metadata = {
        "source_file": os.path.basename(ifc_path),
        "schema": schema,
        "extraction_timestamp": datetime.now().isoformat(),
        "pipeline": "ifcopenshell",
        "counts": {
            "elements": len(elements_rows),
            "properties": len(properties_rows),
            "quantities": len(quantities_rows),
            "materials": len(materials_rows),
            "spatial_entities": len(spatial_rows),
        },
    }

    output = {
        "elements": elements_rows,
        "properties": properties_rows,
        "quantities": quantities_rows,
        "materials": materials_rows,
        "spatial": spatial_rows,
        "metadata": metadata,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
