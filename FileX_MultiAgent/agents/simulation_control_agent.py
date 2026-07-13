"""
Simulation Control Agent - Handles simulation parameters
"""

from utils.state import DSSATState
from utils.helpers import convert_date_to_dssat_date
from DSSATTools.DSSATTools.filex import (
    SimulationControls, SCGeneral, SCOptions, SCMethods,
    SCManagement, SCOutputs, AMPlanting, AMIrrigation,
    AMNitrogen, AMResidues, AMHarvest
)


class SimulationControlAgent:
    """
    Agent responsible for simulation controls using DSSATTools.
    """
    
    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        pdate = state.get("pdate", "2025-03-15")
        pdate_obj = convert_date_to_dssat_date(pdate)
        irrig = state.get("irrig")

        # Always 1 year for dynamic advisory
        nyears = 1

        # SDATE is always January 1st of the chosen growing season year
        growing_season_year = state["config"]["crop_growing_season"]
        sdate_str = f"{growing_season_year}-01-01"
        sdate_obj = convert_date_to_dssat_date(sdate_str)

        # Create simulation control components
        general = SCGeneral(
            sdate=sdate_obj,
            nyers=nyears,
            nreps=1,
            start="S",
            rseed=2150,
            sname="Maize Simulation",
            smodel="MZCER"
        )
        
        options = SCOptions(
            water="Y",
            nitro="Y",
            symbi="N",
            phosp="N",
            potas="N",
            dises="N",
            chem="N",
            till="N",
            co2="M"
        )
        
        methods = SCMethods(
            wther="M",
            incon="M",
            light="E",
            evapo="F",
            infil="S",
            photo="L",
            hydro="R",
            nswit="1",
            mesom="P",
            mesev="S",
            mesol="2"
        )
        
        management = SCManagement(
            plant="R",
            irrig=irrig,
            ferti="R",
            resid="D",
            harvs="M"
        )
        
        outputs = SCOutputs(
            fname="N",
            ovvew="Y",
            sumry="Y",
            fropt=1,
            grout="Y",
            caout="N",
            waout="Y",
            niout="Y",
            miout="N",
            diout="N",
            vbose="Y",
            chout="N",
            opout="N",
            fmopt="A"
        )
        
        # Automatic management sections
        planting = AMPlanting(
            pfrst=pdate_obj,
            plast=pdate_obj,
            ph2ol=40,
            ph2ou=100,
            ph2od=30,
            pstmx=40,
            pstmn=10
        )
        
        # Automatic-irrigation thresholds only matter when IRRIG is set to
        # automatic ("A"). When irrigation is off ("N") or on a reported
        # schedule ("R"), leave this block empty instead of writing values
        # that imply an active auto-irrigation plan that never runs.
        if irrig == "A":
            irrigation_am = AMIrrigation(
                imdep=30,
                ithrl=70,
                ithru=100,
                iroff="GS000",
                imeth="IR001",
                iramt=10,
                ireff=1.0
            )
        else:
            irrigation_am = AMIrrigation(
                imdep=None, ithrl=None, ithru=None,
                iroff=None, imeth=None, iramt=None, ireff=None
            )
        
        nitrogen = AMNitrogen(
            nmdep=30,
            nmthr=50,
            namnt=25,
            ncode="FE001",
            naoff="GS000"
        )
        
        residues = AMResidues(
            ripcn=100,
            rtime=1,
            ridep=20
        )
        
        # HARVS="M" (harvest at physiological maturity) means this window is
        # only a bound, not the actual trigger -- leave it open-ended rather
        # than pinning it to the planting date. hfrst=None -> no lower bound;
        # hlast is capped at the end of the simulated growing season year.
        harvest_end_str = f"{growing_season_year}-12-31"
        harvest = AMHarvest(
            hfrst=None,
            hlast=convert_date_to_dssat_date(harvest_end_str),
            hpcnp=100,
            hpcnr=0
        )
        
        # Create SimulationControls object
        simulation_controls = SimulationControls(
            general=general,
            options=options,
            methods=methods,
            management=management,
            outputs=outputs,
            planting=planting,
            irrigation=irrigation_am,
            nitrogen=nitrogen,
            residues=residues,
            harvest=harvest
        )
        
        state["simulation_controls"] = simulation_controls
        state["messages"].append("SimulationControlAgent: Created SimulationControls object")
        
        return state
