"""
AU Agents
- au_router: Conversational decision + question improvement
- au_summarizer: User-facing wrap-up of simulation results
"""

import json
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from llm_config import LLMConfig
from typing import Optional
from agents.experiment_agents import get_database_context
from experiment_config import get_max_critic_iterations

# Import state serializer
try:
    from .state_serializer import sanitize_state
except ImportError:
    def sanitize_state(state):
        return state

# Will be initialized from main
llm = None

def initialize_conversation_llm(api_key: Optional[str] = None, model: Optional[str] = None, provider: str = "groq"):
    """Initialize the LLM for conversation agent with flexible provider support"""
    global llm
    
    # Create LLM config and instance  
    config = LLMConfig(api_key=api_key, model=model)
    llm = config.create_llm(temperature=0.3)  # Slightly higher temp for conversation
    
    print(f"💬 Initialized Conversation LLM: {config.get_info()}")
    return llm


class ConversationMemory:
    """Simple memory for conversation context"""
    def __init__(self):
        self.conversation_history = []
        self.user_context = {}
    
    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        # Keep last 10 messages to avoid token overflow
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_context(self) -> str:
        if not self.conversation_history:
            return "No previous conversation"
        
        context = "Previous conversation:\n"
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            context += f"{msg['role']}: {msg['content']}\n"
        return context
    
    def to_dict(self) -> Dict:
        """Convert to serializable dict"""
        return {
            "conversation_history": self.conversation_history,
            "user_context": self.user_context
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from serializable dict"""
        memory = cls()
        memory.conversation_history = data.get("conversation_history", [])
        memory.user_context = data.get("user_context", {})
        return memory


def au_router(state: Dict) -> Dict:
    """AU Router: decide direct vs simulation and improve the question"""
    
    question = state["user_question"]
    memory_data = state.get("conversation_memory", {})
    
    # Convert dict back to ConversationMemory if needed
    if isinstance(memory_data, dict):
        memory = ConversationMemory.from_dict(memory_data)
    else:
        memory = ConversationMemory()
    
    print(f"💬 **AU Router:**")
    print(f"   User: {question}")
    
    # Get conversation context
    context = memory.get_context()
    
    # Decision prompt: Does this need simulation?
    decision_prompt = ChatPromptTemplate.from_template("""
    You are AU - Agent User, a friendly DSSAT agricultural assistant.
    
    User Question: "{question}"
    
    Context from previous conversation:
    {context}
    
    DECISION TASK: Determine if this question needs DSSAT simulation or can be answered directly.
    
    Questions that NEED SIMULATION (respond "simulation"):
    - ANY question asking about YIELD IMPACT of a specific change (e.g., "how much yield if I add 50 kg N?")
    - Comparing SPECIFIC fertilizer rates, timings, or application methods
    - Determining optimal planting dates by testing multiple options
    - "What if" scenarios asking for QUANTITATIVE results (numbers, yield amounts)
    - Questions asking "how much yield", "what will be the yield", "yield increase"
    - Percentage or absolute amount changes asking for yield response
    - ANY question asking to COMPARE multiple specific scenarios
    - Questions explicitly requesting simulation, modeling, or testing
    
    Questions for DIRECT ANSWER (respond "direct"):
    - General agricultural knowledge and best practices
    - Explaining what DSSAT is or how crop modeling works
    - Questions asking for TYPICAL or RECOMMENDED values without yield quantification
    - Qualitative questions (e.g., "is more nitrogen generally better?")
    - Simple definitions or clarification questions
    - Questions about crop biology, soil science, or farming practices
    - "Why" and "How" questions about processes (not predictions)
    
    KEY RULES FOR CLARITY:
    
    1. If the question asks "how much yield" → SIMULATION
    2. If the question asks "what if I change X, what happens to yield" → SIMULATION  
    3. If the question asks "compare yield at X vs Y" → SIMULATION
    4. If the question asks "what is recommended/typical X" → DIRECT
    5. If the question asks "why does X happen" → DIRECT
    6. If the question asks for a SPECIFIC NUMBER or QUANTITATIVE prediction → SIMULATION
    
    EXAMPLES:
    
    ✅ SIMULATION:
    - "what if i increase nitrogen by 50 kg per hectare, how much additional yield we will get?"
    - "how much yield will I get if I plant on March 15?"
    - "compare yields at 60, 90, 120 kg N/ha"
    - "what is the yield difference between planting March 1 vs April 1?"
    - "if I increase fertilizer by 50%, what will be the yield impact?"
    
    ✅ DIRECT:
    - "what is the optimum nitrogen rate for Trans Nzoia?" (asking for recommendation)
    - "what is DSSAT?"
    - "why is nitrogen important for maize?"
    - "what are good fertilizer practices?"
    - "is it better to apply fertilizer at planting or later?" (general principle)
    
    When in doubt: If the user wants a SPECIFIC YIELD NUMBER or COMPARISON → simulation
    
    Respond with just "simulation" or "direct"
    """)
    
    decision_result = llm.invoke(decision_prompt.format_messages(
        question=question,
        context=context
    ))
    
    decision = decision_result.content.strip().lower()
    
    if "simulation" in decision:
        print(f"   🧠 AU Decision: Needs simulation")
        print(f"   💭 AU Response: Let me use the power of DSSAT to answer your question...")
        
        memory.add_message("user", question)
        memory.add_message("assistant", "Let me use DSSAT simulation to analyze this for you...")
        
        return sanitize_state({
            **state,
            "needs_simulation": True,
            "conversation_memory": memory.to_dict(),
            "au_initial_response": "Let me use the power of DSSAT to answer your question. I'll design and run a simulation to give you the best answer."
        })
    
    else:
        print(f"   🧠 AU Decision: Can answer directly")

        # The workflow routes direct questions through weather.forecast before
        # calling direct_answer_node. This keeps live provider calls out of the
        # router and avoids fetching weather for simulation questions.
        return sanitize_state({
            **state,
            "needs_simulation": False,
            "conversation_memory": memory.to_dict(),
            "final_answer": ""
        })


def _format_context_list(items: List[Dict[str, Any]], formatter) -> str:
    if not items:
        return "No matching entries found"
    lines = [formatter(item) for item in items[:5]]
    return "\n".join(lines)


# def answer_directly(question: str, context: str, memory: ConversationMemory) -> str:
#     """Answer questions that don't need simulation"""

#     db_context = get_database_context(question)

#     fert_info = _format_context_list(
#         db_context.get("fertilizers", []),
#         lambda item: f"- {item.get('name', 'Unknown')}: {item.get('composition', 'N/A')} ({item.get('notes') or 'No notes provided'})"
#     )

#     variety_info = _format_context_list(
#         db_context.get("varieties", []),
#         lambda item: f"- {item.get('name', 'Unknown')} ({item.get('maturity', 'N/A')} maturity, yield {item.get('yield', 'N/A')})"
#     )

#     irrigation_info = _format_context_list(
#         db_context.get("irrigation", []),
#         lambda item: f"- {item.get('name', 'Unknown')} ({item.get('method', 'N/A')} method, notes: {item.get('notes', 'No notes provided')})"
#     )

#     regional_details = db_context.get("regional_info", {})
#     region_info = (
#         f"Region: {regional_details.get('region', 'Trans Nzoia')}\n"
#         f"Altitude: {regional_details.get('altitude', 'N/A')}\n"
#         f"Rainfall: {regional_details.get('rainfall', 'N/A')}\n"
#         f"Temperature: {regional_details.get('temperature', 'N/A')}\n"
#         f"Soil: {regional_details.get('soil', 'N/A')}"
#     ) if regional_details else "Regional data not available"

#     direct_prompt = ChatPromptTemplate.from_template("""
# You are AU - Agent User, a friendly and knowledgeable DSSAT agricultural assistant.

# User Question: "{question}"

# Previous conversation context:
# {context}

# Relevant Fertilizer Insights:
# {fertilizer_info}

# Relevant Variety Options:
# {variety_info}

# Relevant Irrigation Options:
# {irrigation_info}

# Regional Snapshot:
# {regional_info}

# Provide a clear, encouraging answer grounded in the information above and your agronomic knowledge. 
# IMPORTANT: Always provide the full name for agricultural acronyms the first time you use them 
# (e.g., "DAP (Diammonium Phosphate)" or "CAN (Calcium Ammonium Nitrate)"). 

# Cite specific fertilizers, varieties, or irrigation methods (include IDs when available) and explain why they fit the situation. If the question would benefit from a DSSAT simulation, invite the user to let you run one for precise, data-backed guidance.
# Keep the tone practical, concise, and farmer-friendly.
# Keep the tone practical, concise, and farmer-friendly.
# """)
    
#     result = llm.invoke(direct_prompt.format_messages(
#         question=question,
#         context=context,
#         fertilizer_info=fert_info,
#         variety_info=variety_info,
#         irrigation_info=irrigation_info,
#         regional_info=region_info
#     ))
    
#     answer = result.content.strip()
#     memory.add_message("user", question)
#     memory.add_message("assistant", answer)
    
#     return answer
# old
# new
def answer_directly(
    question: str,
    context: str,
    memory: ConversationMemory,
    forecast_context: str = "",
) -> str:
    """Answers questions directly, prioritizing local data if found, 
    otherwise using expert LLM knowledge silently."""

    try:
        db_context = get_database_context(question)
    except Exception:
        db_context = {}

    fert_list = db_context.get("fertilizers", [])
    variety_list = db_context.get("varieties", [])
    irrigation_list = db_context.get("irrigation", [])
    regional_details = db_context.get("regional_info", {})

    # Load farmer context from Input_config_test.json
    farmer_context = _load_farmer_context()
    
    # Format data if it exists
    fert_info = _format_context_list(
        fert_list,
        lambda item: f"- {item.get('name', 'Unknown')}: {item.get('composition', 'N/A')}"
    ) if fert_list else ""

    variety_info = _format_context_list(
        variety_list,
        lambda item: f"- {item.get('name', 'Unknown')} ({item.get('maturity', 'N/A')} maturity)"
    ) if variety_list else ""

    # Regional details fallback to Kitale/Trans Nzoia logic internally
    region_name = regional_details.get('region', 'Trans Nzoia (Highlands)')
    region_info = (
        f"Region: {region_name}\n"
        f"Soil: {regional_details.get('soil', 'N/A')}\n"
        f"Altitude: {regional_details.get('altitude', 'N/A')}"
    )

    # UPDATED PROMPT: Include comprehensive farmer context
    direct_prompt = ChatPromptTemplate.from_template("""
    You are AU - Agent User, a friendly and knowledgeable agricultural assistant helping a farmer.
    
    User Question: "{question}"
    
    --- 
    FARMER & LOCATION CONTEXT (Must consider before answering):
    {farmer_context}
    ---
    
    --- 
    ADDITIONAL CONTEXTUAL DATA:
    {fertilizer_info}
    {variety_info}
    {regional_info}
    ---

    ---
    LIVE WEATHER CONTEXT (use only when it is relevant and available):
    {forecast_context}
    ---

    CRITICAL INSTRUCTIONS:
    1. **Crop Consideration**: If a crop is mentioned in the question, use that crop. Otherwise, use the crop from the farmer's context above.
    2. **Location-Specific**: Tailor your answer to the farmer's location (country, latitude/longitude, agroecological zone).
    3. **Temporal Context**: Consider the year/season mentioned in farmer's context for timing recommendations.
    4. **Scale & Resources**: Consider the scale of production and access to local resources when making recommendations.
    5. **Representative Farmer**: Assume this is an average farmer in this region - don't recommend expensive or hard-to-access solutions unless specifically appropriate.
    6. **Practical Recommendations**: Provide actionable advice that fits the agroecological zone and local conditions.
    7. **Forecast Integrity**: Never invent forecast values. Distinguish the operational daily forecast from the lower-resolution seasonal ensemble guidance, and communicate uncertainty.
    
    RESPONSE GUIDELINES:
    - **Be CONCISE and RELEVANT**: Keep answers focused and to the point - no unnecessary elaboration.
    - Provide exactly what's needed to answer the question - could be 2 points, could be 7, or short paragraphs.
    - Adapt your format (paragraphs, bullet points, numbered lists) based on what suits the question best.
    - **Stay on topic**: Answer ONLY what was asked - avoid tangential information or deviations.
    - Prioritize actionable, practical advice over theoretical explanations.
    - Provide a clear, confident, and professional agronomic answer.
    - DO NOT mention whether information came from a database or "general knowledge." 
    - DO NOT say "I don't have data" or "The database is empty."
    - Simply provide the best possible guidance for the farmer's specific context.
    - Always provide the full name for agricultural acronyms (e.g., "CAN (Calcium Ammonium Nitrate)").
    - Keep the tone practical and farmer-friendly.
    - Reference the farmer's context (location, crop, conditions) naturally in your answer.
    
    RESPONSE FORMAT:
    1. Provide your main answer (as brief or detailed as the question requires - stay relevant)
    2. **Always end with a brief "Note" or "Follow-up"** offering DSSAT simulation if it would provide more precise, data-backed guidance
    3. Example closing: "Note: If you'd like precise yield predictions or want to compare different strategies, I can run a DSSAT simulation for you!"
    """)

    result = llm.invoke(direct_prompt.format_messages(
        question=question,
        farmer_context=farmer_context,
        fertilizer_info=fert_info,
        variety_info=variety_info,
        regional_info=region_info,
        forecast_context=forecast_context or "No live forecast context is available for this question."
    ))
    
    answer = result.content.strip()
    
    memory.add_message("user", question)
    memory.add_message("assistant", answer)
    
    return answer


def direct_answer_node(state: Dict) -> Dict:
    """Generate the direct response after optional forecast enrichment."""
    memory_data = state.get("conversation_memory", {})
    memory = ConversationMemory.from_dict(memory_data) if isinstance(memory_data, dict) else ConversationMemory()
    answer = answer_directly(
        state["user_question"],
        memory.get_context(),
        memory,
        state.get("forecast_context_text", ""),
    )
    print(f"   💭 AU Response: {answer[:100]}...")
    return sanitize_state({
        **state,
        "needs_simulation": False,
        "conversation_memory": memory.to_dict(),
        "final_answer": answer,
    })


def _load_farmer_context() -> str:
    """Load farmer context from Input_config_test.json - dynamically extracts whatever is present"""
    import json
    import os
    
    config_path = os.path.join(os.path.dirname(__file__), "..", "Input_config_test.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        context_parts = []
        context_parts.append("**Farmer Configuration (from Input_config_test.json):**\n")
        
        # 1. Location information (if present)
        location = config.get("Location", {})
        if location:
            loc_parts = []
            if "Country" in location:
                loc_parts.append(f"Country: {location['Country']}")
            if "Latitude" in location and "Longitude" in location:
                loc_parts.append(f"Coordinates: Lat {location['Latitude']}, Lon {location['Longitude']}")
                # Derive agroecological zone if coordinates exist
                aez = _determine_agroecological_zone(
                    location.get('Latitude'), 
                    location.get('Longitude'), 
                    location.get('Country', '')
                )
                if aez:
                    loc_parts.append(f"Agroecological Zone: {aez}")
            
            if loc_parts:
                context_parts.append("- Location: " + ", ".join(loc_parts))
        
        # 2. Crop/Cultivar information (if present)
        cultivar = config.get("cultivar", {})
        if cultivar and "CR" in cultivar:
            crop_code = cultivar["CR"]
            # Just provide the code - LLM understands agricultural crop codes
            context_parts.append(f"- Primary Crop Code: {crop_code}")
        
        # 3. Year/Temporal information (if present)
        year_info = config.get("Year", {})
        if year_info and "start_year" in year_info:
            context_parts.append(f"- Season/Year: {year_info['start_year']}")
        
        # 4. Planting details (if present)
        planting = config.get("planting_details", {})
        if planting:
            planting_info = []
            if "PDATE" in planting:
                planting_info.append(f"Planting date: {planting['PDATE']}")
            if "PPOP" in planting:
                planting_info.append(f"Population: {planting['PPOP']} plants/m²")
            if "PLME" in planting:
                planting_info.append(f"Method: {planting['PLME']}")
            if planting_info:
                context_parts.append("- Planting: " + ", ".join(planting_info))
        
        # 5. Irrigation information (if present)
        irrigation = config.get("irrigation_and_water_management", {})
        if irrigation and "applications" in irrigation and irrigation["applications"]:
            irr_count = len(irrigation["applications"])
            context_parts.append(f"- Irrigation: {irr_count} application(s) planned")
        
        # 6. Fertilizer information (if present)
        fertilizers = config.get("fertilizers_inorganic", [])
        if fertilizers:
            context_parts.append(f"- Fertilizer Plan: {len(fertilizers)} application(s) configured")
        
        # 7. Organic/Residues information (if present)
        residues = config.get("residues_and_organic", {})
        if residues and "applications" in residues and residues["applications"]:
            res_count = len(residues["applications"])
            context_parts.append(f"- Organic Matter: {res_count} application(s) planned")
        
        # 8. Determine farm scale from available data
        scale = _determine_farm_scale(config)
        if scale:
            context_parts.append(f"- Farm Type: {scale}")
        
        # 9. Determine resource access if location is available
        if location:
            resource_access = _determine_resource_access(location, scale)
            if resource_access:
                context_parts.append(f"- Resource Access: {resource_access}")
        
        # Build contextual considerations
        context_parts.append("\n**Important Considerations for Your Answer:**")
        
        if location.get("Country"):
            context_parts.append(f"- Tailor recommendations to {location['Country']} farming practices")
        
        if cultivar.get("CR"):
            context_parts.append(f"- Focus on crop code '{cultivar['CR']}' cultivation unless user specifies different crop")
        
        if location.get("Latitude") and location.get("Longitude"):
            context_parts.append("- Consider the local agroecological conditions and climate")
        
        if scale:
            context_parts.append(f"- Recommendations must be practical for {scale.lower()} context")
        
        context_parts.append("- Assume this represents an average/typical farmer in this region")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        # Minimal fallback if file can't be read
        return "**Farmer Configuration:** Unable to load Input_config_test.json. Providing general agricultural guidance."


def _determine_agroecological_zone(lat, lon, country: str) -> str:
    """Simply return coordinates - let LLM determine agroecological zone naturally"""
    if not lat or not lon:
        return ""
    
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return ""
    
    # Just return the coordinates - LLM can determine the agroecological zone
    # based on its knowledge of geography, climate zones, and agriculture
    return f"Coordinates indicate local agroecological conditions"


def _get_crop_name(crop_code: str) -> str:
    """Simply return the crop code - let LLM interpret it naturally"""
    if not crop_code:
        return ""
    # Return just the code - LLM knows agricultural codes (MZ, WH, etc.)
    return crop_code.upper()


def _determine_farm_scale(config: dict) -> str:
    """Extract farm indicators - let LLM interpret the scale naturally"""
    if not config:
        return ""
    
    indicators = []
    
    planting = config.get("planting_details", {})
    if planting and planting.get("PPOP"):
        indicators.append(f"Planting density: {planting['PPOP']} plants/m²")
    
    if config.get("irrigation_and_water_management", {}).get("applications"):
        indicators.append("Has irrigation planned")
    
    if config.get("fertilizers_inorganic", []):
        indicators.append("Has fertilizer plan")
    
    # Return indicators, let LLM interpret the farm scale
    return ", ".join(indicators) if indicators else ""


def _determine_resource_access(location: dict, scale: str) -> str:
    """Return location info - let LLM determine resource access naturally"""
    if not location:
        return ""
    
    country = location.get("Country", "")
    if not country:
        return ""
    
    # Just return the country - LLM knows about agricultural resources by country
    return f"Agricultural context in {country}"

def au_summarizer(state: Dict) -> Dict:
    """AU Summarizer: explain simulation output to the user"""
    
    question = state["user_question"]
    experiment = state.get("proposed_experiment", {})
    approved = state.get("approved", False)
    iterations = state.get("iteration_count", 0)
    files = state.get("generated_files", [])
    memory_data = state.get("conversation_memory", {})
    
    # Convert dict back to ConversationMemory if needed
    if isinstance(memory_data, dict):
        memory = ConversationMemory.from_dict(memory_data)
    else:
        memory = ConversationMemory()
    
    print(f"💬 **AU Summarizer:**")
    
    summary_prompt = ChatPromptTemplate.from_template("""
    You are AU - Agent User, a friendly DSSAT agricultural assistant.

    Original User Question: "{question}"

    SIMULATION COMPLETED:
    - Experiment Purpose: {purpose}
    - Variable Tested: {variable}
    - Number of Treatments: {num_treatments}
    - Treatments: {treatments}
    - Approved by Critic: {approved}
    - Design Iterations: {iterations}
    - Generated FileX (.SNX) files, one per treatment:
{files_text}

    TASK: Explain to the user in a friendly, conversational way:
    1. What simulation was designed and why
    2. How this answers their question
    3. That the FileX (.SNX) file(s) listed above were generated and are ready to run
       with the DSSAT-CSM model (do not invent a different file format or folder
       structure — reference the exact filenames given above)
    4. Practical interpretation for farmers

    Be enthusiastic about helping them and explain the value of the simulation approach.
    """)

    treatments_text = ""
    treatments = experiment.get('treatments', [])
    for t in treatments:
        treatments_text += f"- {t.get('description', 'N/A')}\n"

    files_text = "\n".join(f"    - {f}" for f in files) if files else "    - (none — generation failed or was skipped)"

    result = llm.invoke(summary_prompt.format_messages(
        question=question,
        purpose=experiment.get('experiment_purpose', 'N/A'),
        variable=experiment.get('variable_tested', 'N/A'),
        num_treatments=len(treatments),
        treatments=treatments_text,
        approved=approved,
        iterations=iterations,
        files_text=files_text
    ))

    summary = result.content.strip()

    # Deterministically append the real file list regardless of what the LLM
    # chose to mention, so the user always sees accurate output paths.
    if files:
        file_list_block = "\n\n📁 **Generated FileX file(s):**\n" + "\n".join(f"- `{f}`" for f in files)
        summary = summary + file_list_block

    memory.add_message("assistant", summary)
    
    print(f"   💭 AU Final Response: {summary[:100]}...")
    print()
    
    # Check if there's a nitrogen adjustment summary to append
    nitrogen_summary = state.get("nitrogen_adjustment_summary", "")
    if nitrogen_summary:
        final_answer = summary + "\n\n" + nitrogen_summary
    else:
        final_answer = summary
    
    return sanitize_state({
        **state,
        "final_answer": final_answer,
        "conversation_memory": memory.to_dict()
    })
