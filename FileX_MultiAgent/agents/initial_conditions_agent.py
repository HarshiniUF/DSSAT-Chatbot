"""
Initial Conditions Agent - Handles initial soil conditions
"""

from utils.state import DSSATState
from utils.helpers import convert_date_to_dssat_date
from DSSATTools.DSSATTools.filex import InitialConditions, InitialConditionsLayer


class InitialConditionsAgent:
    """
    Agent responsible for creating InitialConditions object.
    """
    
    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        config = state.get("config", {})
        ic_config = config.get("initial_conditions", {})
        
        pdate = state.get("pdate", "2025-03-15")
        pdate_obj = convert_date_to_dssat_date(pdate)
        
        # Default depth gradient: moisture rising with depth (topsoil dries
        # out first) and mineral N falling with depth (mineralization/fert
        # concentrated near the surface). Used as a placeholder until real
        # per-layer values are wired in from the generated soil profile.
        default_gradient = [
            (5,   0.180, 3.0, 8.0),
            (15,  0.200, 2.0, 6.0),
            (30,  0.220, 1.5, 4.0),
            (60,  0.250, 1.0, 3.0),
            (90,  0.270, 0.8, 2.0),
            (120, 0.280, 0.5, 1.0),
        ]
        ic_layers = ic_config.get("layers", default_gradient)
        layers = [
            InitialConditionsLayer(icbl=icbl, sh2o=sh2o, snh4=snh4, sno3=sno3)
            for icbl, sh2o, snh4, sno3 in ic_layers
        ]
        
        # Create InitialConditions object
        initial_conditions = InitialConditions(
            pcr="MZ", #default change later
            icdat=pdate_obj,
            icrt=ic_config.get("ICRT", 100),
            icrn=ic_config.get("ICRN", 1),
            icre=ic_config.get("ICRE", 1),
            icres=ic_config.get("ICRES", 1000),
            icren=ic_config.get("ICREN", 0.5),
            icrip=ic_config.get("ICRIP", 100),
            icrid=ic_config.get("ICRID", 5),
            icname="Initial",
            table=layers
        )
        
        state["initial_conditions"] = initial_conditions
        state["messages"].append("InitialConditionsAgent: Created InitialConditions object")
        
        return state
