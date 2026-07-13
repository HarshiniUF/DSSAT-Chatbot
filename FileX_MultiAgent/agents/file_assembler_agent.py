"""
File Assembler Agent - Assembles final FileX output
"""

from utils.state import DSSATState
from DSSATTools.DSSATTools.filex import create_filex


class FileAssemblerAgent:
    """
    Final agent that assembles all sections into complete FileX using DSSATTools.
    """
    
    @staticmethod
    def process(state: DSSATState) -> DSSATState:
        # Use DSSATTools create_filex function to generate the complete FileX
        try:
            print("----------ginalll------",state['cultivar'])
            complete_filex = create_filex(
                field=state["field"],
                cultivar=state["cultivar"],
                planting=state["planting"],
                simulation_controls=state["simulation_controls"],
                initial_conditions=state.get("initial_conditions"),
                fertilizer=state.get("fertilizer"),
                irrigation=state.get("irrigation"),
            )
            print(complete_filex,"---------- complete filex")
            state["complete_filex"] = complete_filex
            state["messages"].append("FileAssemblerAgent: Generated complete FileX using DSSATTools")
        except Exception as e:
            state["errors"].append(f"FileAssemblerAgent: Failed to create FileX. Error: {e}")
            state["complete_filex"] = ""
        
        return state
