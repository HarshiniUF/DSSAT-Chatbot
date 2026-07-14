"""
Schemas and type aliases for agent state and experiment structures.
These are lightweight (TypedDict/Literal) to avoid runtime deps.
"""

from typing import TypedDict, Literal, List, Dict, Any

# Routing and classification
Route = Literal["direct", "simulation"]
QuestionType = Literal["planting_date", "fertilizer_timing", "fertilizer_type", "fertilizer_rate", "irrigation_method", "irrigation_timing", "irrigation_comparison"]


class Treatment(TypedDict, total=False):
    id: str
    description: str
    # Optional explicit modifications to apply in MZX generation
    modifications: Dict[str, Any]
    # Back-compat: Some legacy flows may still use a single 'parameter'
    parameter: Any


class Experiment(TypedDict):
    experiment_purpose: str
    variable_tested: str
    treatments: List[Treatment]
    expected_answer: str


class ConversationState(TypedDict, total=False):
    # Inputs
    user_question: str
    conversation_memory: Any

    # Routing
    needs_simulation: bool
    au_initial_response: str
    route: Route
    clarified_question: str

    # Simulation-specific
    question_type: QuestionType
    proposed_experiment: Experiment
    critic_feedback: str
    approved: bool
    mzx_instructions: List[Dict[str, Any]]
    generated_files: List[str]
    iteration_count: int
    forecast_context: Dict[str, Any]
    forecast_context_text: str

    # Finalization
    final_answer: str
