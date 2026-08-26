"""
Merges two single-treatment FileX (.SNX) texts -- both produced by the
existing FileX_MultiAgent pipeline exactly as today -- into one DSSAT-native
multi-treatment X-file, instead of the caller writing two separate files.

Treatment 1's text is the base (kept as-is except for one new row appended to
*TREATMENTS). Treatment 2's text is only used as a value source: the data
rows from whichever section the question actually varies (fertilizer today;
planting/irrigation follow the same pattern) are pulled out, renumbered from
level 1 to level 2, and spliced into that same section in the base text.
Every other section is untouched, since treatment 2's field/cultivar/planting/
irrigation guidelines are locked to treatment 1's anyway.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

# focus_variable (from intent_brief) -> which *TREATMENTS factor-level column
# gets bumped to 2, and which section header holds that factor's data rows.
# Only "fertilizer" is wired up upstream today; planting/irrigation are here
# for when q_classifier/a1_designer grow those focus_variables.
SECTION_CONFIG: Dict[str, Dict[str, str]] = {
    "fertilizer": {"header_prefix": "*FERTILIZERS", "treatment_col": "MF"},
    "planting": {"header_prefix": "*PLANTING DETAILS", "treatment_col": "MP"},
    "irrigation": {"header_prefix": "*IRRIGATION AND WATER MANAGEMENT", "treatment_col": "MI"},
}


def target_section_from_focus_variable(focus_variable: str) -> str:
    fv = (focus_variable or "").lower()
    for section in SECTION_CONFIG:
        if fv.startswith(section):
            return section
    return "fertilizer"  # the only focus_variable q_classifier/a1_designer emit today


def _split_blocks(text: str) -> List[List[str]]:
    """Split FileX text into top-level '*SECTION' blocks. Each block is a list
    of lines: [header_line, *body_lines]."""
    blocks: List[List[str]] = []
    for line in text.splitlines():
        if line.startswith("*"):
            blocks.append([line])
        elif blocks:
            blocks[-1].append(line)
    return blocks


def _find_block(blocks: List[List[str]], header_prefix: str) -> int:
    for i, block in enumerate(blocks):
        if block[0].strip().upper().startswith(header_prefix.upper()):
            return i
    raise ValueError(f"Section '{header_prefix}' not found in generated FileX text.")


def _subtables(body_lines: List[str]) -> List[Dict[str, Any]]:
    """Group a section's body lines by each '@...' column-header line found,
    in order -- most sections have one sub-table, *IRRIGATION AND WATER
    MANAGEMENT has two ('@I EFIR...' and '@I IDATE IROP IRVAL...')."""
    groups: List[Dict[str, Any]] = []
    current = None
    for idx, line in enumerate(body_lines):
        if line.startswith("@"):
            current = {"header_idx": idx, "data_idxs": []}
            groups.append(current)
        elif current is not None and line.strip():
            current["data_idxs"].append(idx)
    return groups


def _header_fields(header_line: str) -> List[Dict[str, Any]]:
    """Return [{"name", "start", "width"}, ...] for each column of a DSSAT
    '@...' header line, in order.

    DSSATTools right-justifies every field to its OWN pars_fmt width (e.g.
    FAMN is ">5.1f", 5 characters) and joins fields with a single space --
    so a field's true width is not its header label's character count (e.g.
    "FAMN" is only 4 characters). The label-length shortcut coincidentally
    matches for narrow values (e.g. "18.0" is 4 chars) but silently
    truncates wider ones (e.g. "112.0" is 5 chars), so widths are instead
    derived from the gap to the END of the PREVIOUS field:
        width = this_token_end - previous_token_end - 1  (the "-1" is the
                                                            single join space)
        start = previous_token_end + 1
    which recovers the true reserved slot, including whatever padding space
    the header label itself needed. The first column (the row/level-number
    column, e.g. '@F') is a base case: DSSATTools always writes it as a
    literal single digit in a fixed slot the same width as its own '@X'
    header token, so it uses the token's own span directly.
    """
    spans = [m.span() for m in re.finditer(r"\S+", header_line)]
    fields = []
    prev_end = None
    for i, (s, e) in enumerate(spans):
        name = header_line[s:e].lstrip("@").split(".")[0]
        if i == 0:
            start = s
        else:
            start = prev_end + 1
        fields.append({"name": name, "start": start, "width": e - start})
        prev_end = e
    return fields


def _find_field(header_line: str, field_name: str) -> Dict[str, Any]:
    for field in _header_fields(header_line):
        if field["name"] == field_name.upper():
            return field
    raise ValueError(f"Field '{field_name}' not found in header: {header_line!r}")


def _read_row_field(header_line: str, data_line: str, field_name: str) -> str:
    """Read one column's raw value out of a fixed-width DSSAT row."""
    field = _find_field(header_line, field_name)
    start, end = field["start"], field["start"] + field["width"]
    return data_line[start:end].strip() if start < len(data_line) else ""


def _replace_row_field(header_line: str, data_line: str, field_name: str, new_value: str,
                        *, left_justify: bool = False) -> str:
    """Replace one column's value in a fixed-width DSSAT row, so column
    alignment (and every other field on the row) is left exactly as-is.

    DSSATTools right-justifies numeric fields but left-justifies name/
    description fields (e.g. TNAME uses pars_fmt ".<25") -- pass
    left_justify=True for those so the replacement matches that convention."""
    field = _find_field(header_line, field_name)
    start, width = field["start"], field["width"]
    end = start + width
    padded = list(data_line.ljust(max(len(data_line), end)))
    if left_justify:
        value_slice = new_value.ljust(width)[:width]
    else:
        value_slice = new_value.rjust(width)[-width:]
    padded[start:end] = list(value_slice)
    return "".join(padded)


def _add_treatment_row(base_blocks: List[List[str]], treatment_col: str) -> None:
    """Rename treatment 1 to DSSATBaseline and append treatment 2
    (DSSATTreatment) to *TREATMENTS in-place: a copy of row 1 with @N -> 2
    and only the mapped factor-level column (MF/MP/MI) bumped to 2."""
    t_body = base_blocks[_find_block(base_blocks, "*TREATMENTS")]
    t_group = _subtables(t_body)[0]
    header_line = t_body[t_group["header_idx"]]
    row1_idx = t_group["data_idxs"][0]
    row1_line = _replace_row_field(header_line, t_body[row1_idx], "TNAME", "DSSATBaseline",
                                    left_justify=True)
    t_body[row1_idx] = row1_line
    row2_line = _replace_row_field(header_line, row1_line, "N", "2")
    row2_line = _replace_row_field(header_line, row2_line, treatment_col, "2")
    row2_line = _replace_row_field(header_line, row2_line, "TNAME", "DSSATTreatment",
                                    left_justify=True)
    insert_at = t_group["data_idxs"][-1] + 1
    t_body[insert_at:insert_at] = [row2_line]


def scale_fertilizer_treatment(base_text: str, new_total_n_kg_ha: float) -> str:
    """Build treatment 2's *FERTILIZERS block by reusing treatment 1's own
    schedule (same FDATE/FMCD/FACD/FDEP/FERNAME, same number of events) and
    only rescaling each event's FAMN so the events sum to new_total_n_kg_ha --
    instead of asking FertilizerAgent to design an independent schedule for
    treatment 2. This keeps FileX_MultiAgent (fertilizer_agent.py) completely
    untouched and out of the loop for treatment 2 -- the two treatments then
    differ in exactly one thing, the total N rate, matching the locked
    field/cultivar/planting/irrigation guidelines they already share."""
    cfg = SECTION_CONFIG["fertilizer"]
    blocks = _split_blocks(base_text)
    _add_treatment_row(blocks, cfg["treatment_col"])

    f_body = blocks[_find_block(blocks, cfg["header_prefix"])]
    f_group = _subtables(f_body)[0]
    header_line = f_body[f_group["header_idx"]]
    row1_idxs = list(f_group["data_idxs"])

    old_values = [float(_read_row_field(header_line, f_body[i], "FAMN")) for i in row1_idxs]
    old_total = sum(old_values)
    scale = (new_total_n_kg_ha / old_total) if old_total else 0.0

    scaled = [round(v * scale, 1) for v in old_values]
    # Round each event individually, then push any rounding remainder onto
    # the last event so the events sum to EXACTLY new_total_n_kg_ha.
    if scaled:
        scaled[-1] = round(scaled[-1] + (round(new_total_n_kg_ha, 1) - sum(scaled)), 1)

    new_rows = []
    for i, new_famn in zip(row1_idxs, scaled):
        row2 = _replace_row_field(header_line, f_body[i], "F", "2")
        row2 = _replace_row_field(header_line, row2, "FAMN", f"{new_famn:.1f}")
        new_rows.append(row2)

    insert_at = f_group["data_idxs"][-1] + 1
    f_body[insert_at:insert_at] = new_rows

    return "\n".join(line for block in blocks for line in block)


def build_combined_filex(base_text: str, variant_text: str, target_section: str) -> str:
    """base_text = treatment 1's full generated FileX (kept as the file's
    identity/experiment code). variant_text = treatment 2's full generated
    FileX, generated with guidelines locked to treatment 1 so only
    target_section actually differs between the two."""
    if target_section not in SECTION_CONFIG:
        raise ValueError(f"Unknown target_section '{target_section}', expected one of {list(SECTION_CONFIG)}")
    cfg = SECTION_CONFIG[target_section]

    base_blocks = _split_blocks(base_text)
    variant_blocks = _split_blocks(variant_text)

    # 1. Append treatment 2's row to *TREATMENTS: copy of row 1, @N -> 2, and
    #    only the mapped factor-level column (MF/MP/MI) bumped to 2.
    _add_treatment_row(base_blocks, cfg["treatment_col"])

    # 2. Pull the target section's data rows out of treatment 2's file,
    #    renumber their leading column from 1 -> 2, and splice them into the
    #    same section in the base file, right after its existing rows.
    v_body = variant_blocks[_find_block(variant_blocks, cfg["header_prefix"])]
    b_body = base_blocks[_find_block(base_blocks, cfg["header_prefix"])]
    v_groups = _subtables(v_body)
    b_groups = _subtables(b_body)

    offset = 0
    for b_group, v_group in zip(b_groups, v_groups):
        sub_header_line = b_body[b_group["header_idx"]]
        leading_field = sub_header_line.split()[0].lstrip("@")  # e.g. "@F" -> "F"
        new_rows = [
            _replace_row_field(sub_header_line, v_body[i], leading_field, "2")
            for i in v_group["data_idxs"]
        ]
        insert_at = b_group["data_idxs"][-1] + offset + 1
        b_body[insert_at:insert_at] = new_rows
        offset += len(new_rows)

    return "\n".join(line for block in base_blocks for line in block)
