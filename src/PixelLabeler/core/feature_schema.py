from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class FeatureDimension:
    id: str
    label: str
    options: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeatureSchema:
    version: int
    dimensions: tuple[FeatureDimension, ...]

    def dimension_ids(self) -> tuple[str, ...]:
        return tuple(d.id for d in self.dimensions)

    def default_values(self) -> dict[str, str]:
        return {d.id: d.options[0] for d in self.dimensions}


def load_feature_schema(path: Path) -> FeatureSchema:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return parse_feature_schema(raw)


def parse_feature_schema(raw: Mapping[str, Any]) -> FeatureSchema:
    try:
        version = int(raw["version"])
        dims_raw = raw["dimensions"]
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError("Invalid feature schema: missing version or dimensions") from e

    if not isinstance(dims_raw, list) or not dims_raw:
        raise ValueError("Invalid feature schema: dimensions must be a non-empty list")

    dimensions: list[FeatureDimension] = []
    for item in dims_raw:
        if not isinstance(item, dict):
            raise ValueError("Invalid feature schema: dimension entry must be an object")
        dim_id = str(item["id"]).strip()
        label = str(item["label"]).strip()
        options_raw = item.get("options", [])
        if not dim_id or not label:
            raise ValueError("Invalid feature schema: id and label must be non-empty strings")
        if not isinstance(options_raw, list) or not options_raw:
            raise ValueError(f"Invalid feature schema: options for {dim_id!r} must be a non-empty list")
        options = tuple(str(o) for o in options_raw)
        dimensions.append(FeatureDimension(id=dim_id, label=label, options=options))

    return FeatureSchema(version=version, dimensions=tuple(dimensions))


def normalize_label_values(schema: FeatureSchema, values: Mapping[str, Any]) -> dict[str, str]:
    """Map raw label dict to schema ids; invalid/missing keys fall back to first option."""
    out: dict[str, str] = {}
    by_id = {d.id: d for d in schema.dimensions}
    for dim in schema.dimensions:
        raw_val = values.get(dim.id)
        chosen = str(raw_val) if raw_val is not None else dim.options[0]
        if chosen not in by_id[dim.id].options:
            chosen = dim.options[0]
        out[dim.id] = chosen
    return out


def label_file_payload(schema: FeatureSchema, values: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "version": schema.version,
        "dimensions": normalize_label_values(schema, values),
    }


def parse_label_file(raw: Mapping[str, Any]) -> dict[str, str]:
    try:
        dims = raw["dimensions"]
    except (KeyError, TypeError) as e:
        raise ValueError("Invalid label file: missing dimensions") from e
    if not isinstance(dims, dict):
        raise ValueError("Invalid label file: dimensions must be an object")
    return {str(k): str(v) for k, v in dims.items()}
