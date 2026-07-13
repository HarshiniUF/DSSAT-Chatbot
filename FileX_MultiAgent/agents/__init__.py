"""
Agent modules
"""

# Wrapped in try/except so standalone scripts (generate_dataset.py,
# CultivarAgent) can import cleanly without needing the full DSSATTools
# stack installed.
try:
    from .planting_agent import PlantingAgent
    from .fertilizer_agent import FertilizerAgent
    from .irrigation_agent import IrrigationAgent
    from .residue_agent import ResidueAgent
    from .initial_conditions_agent import InitialConditionsAgent
    from .simulation_control_agent import SimulationControlAgent
    from .file_assembler_agent import FileAssemblerAgent

    __all__ = [
        'PlantingAgent',
        'FertilizerAgent',
        'IrrigationAgent',
        'ResidueAgent',
        'InitialConditionsAgent',
        'SimulationControlAgent',
        'FileAssemblerAgent',
    ]

except ImportError:
    __all__ = []
