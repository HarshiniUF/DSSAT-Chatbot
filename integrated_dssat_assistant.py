#!/usr/bin/env python3
"""
Integrated DSSAT Assistant - Chatbot + Multiagent System
Combines conversational AI with X-file generation capabilities
"""

import sys
import os
from typing import Dict, Optional
import uuid

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Import chatbot components
from agents import (
    au_router,
    au_summarizer,
    q_classifier,
    a1_designer,
    a2_critic,
    initialize_llm,
    initialize_conversation_llm,
    ConversationMemory,
    create_conversation_workflow
)

# Import multiagent wrapper
from agents.multiagent_nodes import multiagent_xfile_node

# Import configuration
from provider_config import get_active_config
from experiment_config import get_max_critic_iterations

class IntegratedDSSATAssistant:
    """
    Integrated DSSAT Assistant combining:
    - Conversational AI (chatbot decision making)
    - Multiagent X-file generation system
    """
    
    def __init__(self):
        # Get active provider configuration (GPT-5)
        config = get_active_config()
        print(f"[*] Starting Integrated DSSAT Assistant with {config.model.upper()}")
        
        # Initialize LLMs with GPT-5
        initialize_llm(
            api_key=config.api_key,
            model=config.model,
            provider=config.provider
        )
        initialize_conversation_llm(
            api_key=config.api_key,
            model=config.model,
            provider=config.provider
        )
        
        # Stable session/thread id for graph memory
        self.session_id = f"chat-{uuid.uuid4().hex[:8]}"
        
        # Create workflow with all components
        self.workflow = create_conversation_workflow(
            au_router,
            q_classifier,
            a1_designer,
            a2_critic,
            multiagent_xfile_node,  # Use multiagent wrapper instead of MZX generator
            au_summarizer
        )
    
    def _generate_config_json(self, json_path: str, user_request: str, directives: list):
        """Generate configuration JSON file from fertilizer directives."""
        import json
        from datetime import datetime
        
        config = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "modification_type": "fertilizer",
            "directives": []
        }
        
        # Convert directives to JSON-serializable format
        for directive in directives:
            directive_copy = dict(directive)
            config["directives"].append(directive_copy)
        
        # Write JSON file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, default=str)
    
    def chat(self, user_input: str, memory: ConversationMemory = None):
        # Initialize memory if not provided
        if memory is None:
            memory = ConversationMemory()

        # ALWAYS run the full LangGraph + agents workflow so that
        # conversation_agent, experiment_agents, multiagent_nodes,
        # and xFileGenerator are responsible for experiment design
        # and SNX file generation.

        print("\n[Full Workflow] Running DSSAT simulation workflow (agents + xFileGenerator)...")

        # Create initial state for the workflow
        initial_state = {
            "user_question": user_input,
            "needs_simulation": False,
            "conversation_memory": memory.to_dict(),
            "au_initial_response": "",
            "final_answer": "",
            "question_type": "",
            "intent_brief": {},
            "extracted_entities": {},
            "proposed_experiment": {},
            "design_context": {},
            "critic_feedback": "",
            "critic_assessment": {},
            "approved": False,
            "mzx_instructions": [],
            "generated_files": [],
            "iteration_count": 0,
            "forecast_context": {},
            "forecast_context_text": ""
        }

        config = {"configurable": {"thread_id": self.session_id}}

        try:
            final_state = None
            for state in self.workflow.stream(initial_state, config):
                final_state = state

            if final_state:
                last_state = list(final_state.values())[0]
                final_answer = last_state.get("final_answer", "I'm not sure how to help.")

                print("\n🤖 **Assistant Response:**")
                print(final_answer)

                # Update memory and return
                updated_memory_data = last_state.get("conversation_memory", {})
                updated_memory = ConversationMemory.from_dict(updated_memory_data) if isinstance(updated_memory_data, dict) else memory

                return final_answer, updated_memory

        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {e}"
            print(f"❌ {error_msg}")
            return error_msg, memory
                    

               
    
    def _show_technical_summary(self, state: Dict):
        """Show technical simulation details"""
        experiment = state.get('proposed_experiment', {})
        
        if experiment:
            print(f"\n📋 **Technical Details:**")
            print(f"   Question Type: {state.get('question_type', 'Unknown')}")
            print(f"   Variable Tested: {experiment.get('variable_tested', 'N/A')}")
            print(f"   Iterations: {state.get('iteration_count', 0)}")
            print(f"   Approved: {state.get('approved', False)}")
            
            files = state.get('generated_files', [])
            if files:
                print(f"   Generated X Files: {len(files)} files")
                for f in files:
                    print(f"     • {f}")
                
                # Show generation summary
                summary = state.get('generation_summary', '')
                if summary:
                    print(f"   Summary: {summary}")


def interactive_chat():
    """Interactive chat mode with memory"""
    assistant = IntegratedDSSATAssistant()
    memory = ConversationMemory()
    
    print("🌾 Welcome to DSSAT Integrated Assistant!")
    print("I combine conversational AI with powerful X-file generation.")
    print("Ask me anything about farming, and I'll help you out!")
    print("=" * 60)
    
    while True:
        print("\n💡 You can ask me about:")
        print("  • Fertilizer recommendations")
        print("  • Planting dates and timing")
        print("  • Crop management practices")
        print("  • General agricultural questions")
        print("  • DSSAT-related questions")
        
        user_input = input("\n🌾 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
            print("🤖 Assistant: Goodbye! Happy farming! 🌱")
            break
            
        if not user_input:
            continue
        
        print()
        response, memory = assistant.chat(user_input, memory)
        print()


def single_question_mode(question: str):
    """Handle single question from command line"""
    assistant = IntegratedDSSATAssistant()
    print(f"🔬 Question: {question}")
    print()
    response, _ = assistant.chat(question)
    return response


if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        # Single question from command line
        question = " ".join(sys.argv[1:])
        single_question_mode(question)
    else:
        # Interactive chat mode
        interactive_chat()
