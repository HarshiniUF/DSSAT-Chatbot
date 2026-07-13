"""
Residue Agent - Handles residue and organic matter
"""

from utils.state import DSSATState
from utils.helpers import convert_date_to_dssat_date
from DSSATTools.DSSATTools.filex import Residue, ResidueEvent


class ResidueAgent:
    """
    Agent responsible for residues using DSSATTools.
    """
    
    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        config = state.get("config", {})
        residue_config = config.get("residues_and_organic", {}) or {}
        applications = residue_config.get("applications", []) or []
        
        if not applications or len(applications) == 0:
            state["messages"].append("ResidueAgent: No organic fertilizers")
            state["residue"] = None
        else:
            residue_events = []
            for idx, app in enumerate(applications, 1):
                rdate = convert_date_to_dssat_date(app.get("RDATE", state.get("pdate", "2025-03-15")))
                residue_event = ResidueEvent(
                    rdate=rdate,
                    rcod=app.get("RCOD", "RE003"),
                    ramt=float(app.get("RAMT", 100)),
                    resn=float(app.get("RESN", 0.5)),
                    resp=float(app.get("RESP", 0.2)),
                    resk=float(app.get("RESK", 0.1)),
                    rinp=float(app.get("RINP", 100)),
                    rdep=float(app.get("RDEP", 15)),
                    rmet=app.get("RMET", "RM001"),
                    rename=f"Residue_{idx}"
                )
                residue_events.append(residue_event)
            
            residue = Residue(table=residue_events)
            state["residue"] = residue
            state["messages"].append(f"ResidueAgent: Created Residue with {len(residue_events)} events")

        return state
