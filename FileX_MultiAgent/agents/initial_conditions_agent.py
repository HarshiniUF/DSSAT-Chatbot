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
        
        # Create soil layers
        layers = [
            InitialConditionsLayer(icbl=5, sh2o=0.25, snh4=1.0, sno3=5.0),
            InitialConditionsLayer(icbl=15, sh2o=0.25, snh4=1.0, sno3=5.0),
            InitialConditionsLayer(icbl=30, sh2o=0.25, snh4=1.0, sno3=5.0),
            InitialConditionsLayer(icbl=60, sh2o=0.25, snh4=1.0, sno3=5.0),
            InitialConditionsLayer(icbl=90, sh2o=0.25, snh4=1.0, sno3=5.0),
            InitialConditionsLayer(icbl=120, sh2o=0.25, snh4=1.0, sno3=5.0),
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
