"""
Field Agent - Handles field information (soil + weather) and cultivar
resolution from the pre-built AEZ database.

Soil/weather is fetched via ExternalFieldAgent (INTEGRATION layer).
Cultivar resolution reads the zone's cultivar list from the local JSON
database (built by CultivarAgent / generate_dataset.py) and matches
it against the DSSAT .CUL file.

IMPORTANT: The cultivar JSON database must exist before this agent runs.
           Use CultivarAgent (standalone) or generate_dataset.py to
           build it for the required country + crop.

Stores in state:
  field, weather_duration_years          — soil/weather
  cultivar                               — Cultivar object (cr, ingeno, cname)
  cultivar_list                          — (zone_name, zone_cultivars_dict)
  cultivar_name   (CNAME)               — e.g. "DKC 910"
  cultivar_ingeno (INGENO / VAR#)       — e.g. "IB0037"
  matched_cultivar_data                  — (name, details_dict) from CUL file
  crop_code                              — normalised crop code
"""

from utils.state import DSSATState
from DSSATTools.DSSATTools.filex import Field, Cultivar
from INTEGRATION.field_agent_standalone import FieldAgent as ExternalFieldAgent
from utils.ui_logger import ui_event, ui_log
from utils.helpers import get_location, get_cultivar_list_by_location
from utils.cul_parser import parse_and_match_cultivar


class FieldAgent:
    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        config     = state.get("config", {})
        xcrd       = state.get("xcrd")
        ycrd       = state.get("ycrd")
        agent_name = "FieldAgent"

        print(f"[FieldAgent] Starting... xcrd={xcrd}, ycrd={ycrd}")

        # ====================================================================
        # STEP 0: Locked field_details/cultivars from a prior treatment
        # (e.g. s01) in this same run -- if both are fully supplied, skip the
        # live soil/weather fetch and the AEZ cultivar-zone LLM lookup
        # entirely, and reuse the exact same values so every treatment shares
        # the same field/cultivar, not just the same target N rate.
        # ====================================================================
        field_details_override = config.get("field_details") or {}
        cultivars_override = config.get("cultivars") or {}
        required_field_keys = ("ID_FIELD", "WSTA", "ID_SOIL")
        required_cultivar_keys = ("CR", "INGENO", "CNAME")
        locked = (
            all(field_details_override.get(k) not in (None, "") for k in required_field_keys)
            and all(cultivars_override.get(k) not in (None, "") for k in required_cultivar_keys)
        )

        if locked:
            field = Field(
                id_field=field_details_override.get("ID_FIELD"),
                wsta=field_details_override.get("WSTA"),
                id_soil=field_details_override.get("ID_SOIL"),
                flsa=field_details_override.get("FLSA", -99),
                flob=field_details_override.get("FLOB", -99),
                fldt=field_details_override.get("FLDT", "-99"),
                sldp=field_details_override.get("SLDP", -99),
                flname=field_details_override.get("FLNAME", -99),
                xcrd=ycrd,
                ycrd=xcrd,
            )

            state["field_metadata"] = field_details_override
            state["weather_duration_years"] = field_details_override.get("weather_duration_years", "N/A")
            state["field"] = field
            state["messages"].append(
                "FieldAgent: Using locked field_details from a prior treatment (no fetch) "
                f"(ID_FIELD={field['id_field']}, WSTA={field['wsta']}, ID_SOIL={field['id_soil']})"
            )
            ui_log(state, agent_name, "🔒 Using locked field_details (no ExternalFieldAgent call)")

            cr = cultivars_override.get("CR") or state.get("crop_code") or "MZ"
            ingeno = cultivars_override.get("INGENO")
            cname = cultivars_override.get("CNAME")
            cultivar = Cultivar(cr=cr, ingeno=ingeno, cname=cname)
            state["cultivar"] = cultivar
            state["cultivar_name"] = cname
            state["cultivar_ingeno"] = ingeno
            state["crop_code"] = cr
            state["messages"].append(f"FieldAgent: Using locked cultivar from a prior treatment (CNAME={cname}, INGENO={ingeno})")
            ui_log(state, agent_name, f"🔒 Using locked cultivar {cname} ({ingeno})")

            ui_event(
                state,
                agent=agent_name,
                kind="output",
                message="Field + cultivar locked from prior treatment",
                data={"id_field": field["id_field"], "wsta": field["wsta"], "id_soil": field["id_soil"], "cname": cname, "ingeno": ingeno},
            )
            return state

        # ====================================================================
        # STEP 1: Soil + Weather
        # ====================================================================
        field_meta = None

        try:
            external_result = ExternalFieldAgent.process(config, xcrd, ycrd)

            for msg in external_result.get("messages", []):
                state["messages"].append(f"ExternalFieldAgent: {msg}")
            for err in external_result.get("errors", []):
                state["errors"].append(f"ExternalFieldAgent: {err}")

            field_meta = external_result.get("field_metadata")
            if field_meta:
                state["field_metadata"] = field_meta
            else:
                state["messages"].append(
                    "FieldAgent: ExternalFieldAgent did not return field_metadata; "
                    "falling back to config['field']"
                )

        except Exception as e:
            state["errors"].append(f"FieldAgent: Error while calling ExternalFieldAgent: {e}")

        if not field_meta:
            field_meta = config.get("field", {})

        id_field = field_meta.get("id_field", field_meta.get("ID_FIELD"))
        wsta     = field_meta.get("wsta",     field_meta.get("WSTA"))
        id_soil  = field_meta.get("id_soil",  field_meta.get("ID_SOIL"))
        flsa     = field_meta.get("flsa",     field_meta.get("FLSA", -99))
        flob     = field_meta.get("flob",     field_meta.get("FLOB", -99))
        fldt     = field_meta.get("fldt",     field_meta.get("FLDT", "-99"))
        sldp     = field_meta.get("sldp",     field_meta.get("SLDP", -99))
        flname   = field_meta.get("flname",   field_meta.get("FLNAME", -99))

        # state["xcrd"]/state["ycrd"] hold latitude/longitude respectively
        # (see prompts/*, judge_agents/*), but DSSATTools' Field expects the
        # opposite (xcrd=longitude, ycrd=latitude) -- swap at this boundary.
        field = Field(
            id_field=id_field,
            wsta=wsta,
            id_soil=id_soil,
            flsa=flsa,
            flob=flob,
            fldt=fldt,
            sldp=sldp,
            flname=flname,
            xcrd=ycrd,
            ycrd=xcrd,
        )

        state["weather_duration_years"] = field_meta["metadata"]["weather_duration_years"]
        state["field"] = field
        state["messages"].append(
            "FieldAgent: Created Field object "
            f"(ID_FIELD={field['id_field']}, WSTA={field['wsta']}, ID_SOIL={field['id_soil']})"
        )
        ui_log(state, agent_name, "Fetched Soil and Weather")
        ui_log(state, agent_name, f"Weather : {field['wsta']}")
        ui_log(state, agent_name, f"Soil    : {field['id_soil']}")

        # ====================================================================
        # STEP 2: Cultivar resolution from pre-built AEZ database
        # ====================================================================
        cr = state.get("crop_code") or (config.get("cultivar", {}) or {}).get("CR") or "MZ"
        cr = str(cr).strip() or "MZ"
        state["crop_code"] = cr

        cache_manager       = state.get("cache_manager")
        cache_key           = state.get("cache_key")
        run_list            = state.get("run_list", ["ALL"])
        gen_model           = state.get("generator_model", "gpt-5")
        cultivar_cache_name = "CultivarAgent"

        # --- Cache check: skip DB lookup if cultivar is already cached ---
        cultivar_from_cache = False
        cultivar_should_run = True
        if cache_manager is not None:
            cultivar_should_run = cache_manager.should_run_agent(cultivar_cache_name, run_list)

        if not cultivar_should_run and cache_manager is not None:
            cached_data = cache_manager.get_cached_output(cultivar_cache_name, cache_key)
            if cached_data:
                cr     = cached_data.get("crop_code", cr)
                ingeno = cached_data.get("cultivar_ingeno")
                cname  = cached_data.get("cultivar_name")

                print(f"[FieldAgent] Cultivar cache hit: {cr} / {cname} ({ingeno})")
                ui_log(state, agent_name, f"Cultivar cache hit: {cname} ({ingeno})")
                ui_event(
                    state,
                    agent=agent_name,
                    kind="cache",
                    message="Cultivar loaded from cache",
                    data={
                        "cache_key":       cache_key,
                        "timestamp":       cached_data.get("timestamp"),
                        "crop_code":       cr,
                        "cultivar_name":   cname,
                        "cultivar_ingeno": ingeno,
                    },
                )

                cultivar = Cultivar(cr=cr, ingeno=ingeno, cname=cname)
                state["cultivar"]        = cultivar
                state["cultivar_name"]   = cname
                state["cultivar_ingeno"] = ingeno
                state["crop_code"]       = cr
                state["messages"].append(
                    f"FieldAgent: Cultivar loaded from cache ({cname}, INGENO={ingeno})"
                )
                cultivar_from_cache = True

        if not cultivar_from_cache:
            try:
                print(f"[FieldAgent] Resolving location for ({xcrd}, {ycrd})...")
                location, country = get_location(xcrd, ycrd)
                print(f"[FieldAgent] Location: {location}, Country: {country}")
                ui_log(state, agent_name, f"Location resolved: {location}, {country}")

                print(f"[FieldAgent] Fetching cultivar list from AEZ database (crop={cr})...")
                cultivar_list = get_cultivar_list_by_location(
                    location,
                    country=country.lower(),
                    crop_code=cr,
                    model=gen_model,
                )

                if not cultivar_list or cultivar_list[0] == "":
                    msg = (
                        f"FieldAgent: No AEZ database found for country='{country}', crop='{cr}'. "
                        f"Run CultivarAgent (standalone) or generate_dataset.py first."
                    )
                    state.setdefault("errors", []).append(msg)
                    ui_event(state, agent=agent_name, kind="error", message=msg)
                else:
                    zone_name = cultivar_list[0]
                    print(f"[FieldAgent] AEZ zone: {zone_name}")
                    state["cultivar_list"] = cultivar_list
                    ui_log(state, agent_name, f"AEZ Zone: {zone_name}, Cultivars: {len(cultivar_list[1])}")

                    print(f"[FieldAgent] Matching cultivar against CUL file...")
                    matched_name, matched_details = parse_and_match_cultivar(
                        cultivar_list=cultivar_list,
                        crop_code=cr,
                    )

                    ingeno = matched_details.get("VAR#")
                    state["matched_cultivar_data"] = (matched_name, matched_details)
                    state["cultivar_name"]         = matched_name
                    state["cultivar_ingeno"]        = ingeno

                    cultivar = Cultivar(cr=cr, ingeno=ingeno, cname=matched_name)
                    state["cultivar"] = cultivar

                    print(f"[FieldAgent] Cultivar resolved → CNAME={matched_name}, INGENO={ingeno}")
                    ui_log(state, agent_name, f"Cultivar: CNAME={matched_name}, INGENO={ingeno}")
                    state["messages"].append(
                        f"FieldAgent: Cultivar resolved — CNAME={matched_name}, INGENO={ingeno}"
                    )
                    ui_event(
                        state,
                        agent=agent_name,
                        kind="output",
                        message="Cultivar resolved from DB",
                        data={"crop_code": cr, "zone": zone_name, "cname": matched_name, "ingeno": ingeno},
                    )

                    # Save to cache
                    if cache_manager is not None:
                        cache_manager.save_agent_output(
                            cultivar_cache_name,
                            cache_key,
                            {
                                "crop_code":       cr,
                                "cultivar_name":   matched_name,
                                "cultivar_ingeno": ingeno,
                                "judge_approved":  True,
                                "attempts":        1,
                            },
                        )
                        ui_event(
                            state,
                            agent=agent_name,
                            kind="cache",
                            message="Cultivar saved to cache",
                            data={"cache_key": cache_key},
                        )

            except Exception as e:
                msg = f"FieldAgent: Cultivar DB lookup failed: {e}"
                print(f"[FieldAgent] ERROR: {msg}")
                state.setdefault("errors", []).append(msg)
                ui_event(state, agent=agent_name, kind="error", message=msg)

        return state
