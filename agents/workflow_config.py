"""
DSSAT LangGraph Workflow Configuration
Defines the state, workflow structure, and routing logic.
Node IDs are namespaced for readability (au.*, analysis.*, experiments.*, tools.*).
"""

from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from experiment_config import get_max_critic_iterations

# ============================================================================
# State Types and Edge Decision Functions
# ============================================================================

class ConversationState(TypedDict):
    """Enhanced state definition for conversation + experiment workflow"""
    user_question: str
    needs_simulation: bool
    conversation_memory: Any
    au_initial_response: str
    final_answer: str
    
    # Simulation-specific fields
    question_type: str 


     
    intent_brief: Dict
    extracted_entities: Dict
    proposed_experiment: Dict
    design_context: Dict
    critic_feedback: str
    critic_assessment: Dict
    approved: bool
    mzx_instructions: List[Dict]
    generated_files: List[str]
    iteration_count: int


def should_iterate(state: ConversationState) -> str:
    """Decide if we need another iteration or proceed to .ccX generation
    
    NEW LOGIC (Feb 2026):
    - Generate SNX files if score >= MIN_SCORE_FOR_SNX_GENERATION (even if not approved)
    - This allows exploratory simulations for imperfect but reasonable designs
    - Only redesign if score is very low (< MIN_SCORE_FOR_SNX_GENERATION)
    - Always generate after max iterations to avoid infinite loops
    """
    from experiment_config import MIN_SCORE_FOR_SNX_GENERATION
    
    score = state.get("critic_assessment", {}).get("overall_score", 0.0)
    approved = state.get("approved", False)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = get_max_critic_iterations()
    
    # Always generate after max iterations
    if iteration_count >= max_iterations:
        print(f"   → Max iterations ({max_iterations}) reached, proceeding to SNX generation")
        return "generate_mzx"
    
    # Generate if approved (ideal case)
    if approved:
        print(f"   → Experiment approved, proceeding to SNX generation")
        return "generate_mzx"
    
    # Generate if score is acceptable for exploratory analysis
    if score >= MIN_SCORE_FOR_SNX_GENERATION:
        print(f"   → Design score {score}/10 >= {MIN_SCORE_FOR_SNX_GENERATION}, allowing exploratory SNX generation")
        return "generate_mzx"
    
    # Only redesign if score is too low
    print(f"   → Design score {score}/10 < {MIN_SCORE_FOR_SNX_GENERATION}, requesting redesign (iteration {iteration_count + 1}/{max_iterations})")
    return "redesign"


def should_simulate(state: ConversationState) -> str:
    """Decide if we need simulation or can answer directly"""
    
    if state.get("needs_simulation", False):
        return "analyze_question"
    else:
        return "direct_answer"


def create_conversation_workflow(au_router, q_classifier, a1_designer,
                               a2_critic, ccx_generator, au_summarizer):
    """Create and configure the LangGraph conversation + experiment workflow"""
    
    workflow = StateGraph(ConversationState)
    
    # Add nodes (namespaced for clarity)
    workflow.add_node("au.router", au_router)
    workflow.add_node("direct_answer", lambda state: state)  # Direct answer already handled by AU
    workflow.add_node("analysis.q_classifier", q_classifier)
    workflow.add_node("experiments.a1_designer", a1_designer)
    workflow.add_node("experiments.a2_critic", a2_critic)
    workflow.add_node("tools.ccx_generator", ccx_generator)
    workflow.add_node("au.summarizer", au_summarizer)
    
    # Add edges - Start with AU router
    workflow.add_edge(START, "au.router")
    
    # Conditional routing from AU router
    workflow.add_conditional_edges(
        "au.router",
        should_simulate,
        {
            "analyze_question": "analysis.q_classifier",
            "direct_answer": END  # Direct answers end immediately
        }
    )
    
    # NEW: Conditional routing after Q Classifier
    # For comparison workflows, skip A1/A2 and go directly to SNX generation
    def route_after_q_classifier(state):
        """Route comparison workflows directly to SNX generation"""
        intent = state.get("intent") or state.get("intent_brief", {})
        question_type = intent.get("question_type", "")
        
        if question_type == "fertilizer_comparison":
            print(f"   → Routing comparison workflow directly to SNX generation (skipping A1/A2)")
            return "generate_comparison_snx"
        else:
            return "design_experiment"
    
    # Simulation workflow with conditional routing
    workflow.add_conditional_edges(
        "analysis.q_classifier",
        route_after_q_classifier,
        {
            "design_experiment": "experiments.a1_designer",
            "generate_comparison_snx": "tools.ccx_generator"  # Skip design loop for comparisons
        }
    )
    
    workflow.add_edge("experiments.a1_designer", "experiments.a2_critic")
    
    # Conditional edge for feedback loop
    workflow.add_conditional_edges(
        "experiments.a2_critic",
        should_iterate,
        {
            "generate_mzx": "tools.ccx_generator",
            "redesign": "experiments.a1_designer"
        }
    )
    
    # After .ccX generation, summarize for user
    workflow.add_edge("tools.ccx_generator", "au.summarizer")
    workflow.add_edge("au.summarizer", END)
    
    # Disable checkpointer to avoid serialization issues with DSSATTools objects
    # (Cultivar, Planting, Fertilizer are not msgpack-serializable)
    return workflow.compile(checkpointer=False)
