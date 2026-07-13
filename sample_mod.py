import ast
import operator
import openai
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_core.tools import tool
import requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}
_ALLOWED_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(node):
    """Evaluate a numeric-only expression AST, rejecting anything else."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Only numeric arithmetic expressions are allowed")

# ==================== LLM ====================
class ChatGPTLLM:
    def __init__(self, model="gpt-5", temperature=0):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt):
        response = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()

LLM = ChatGPTLLM(model="gpt-5", temperature=0)

# ==================== TOOLS ====================
@tool
def calculator(expression: str) -> str:
    """Calculate math expression"""
    try:
        result = _safe_eval(ast.parse(expression, mode="eval"))
        return str(result)
    except Exception:
        return "Error"

@tool
def internet_search(query: str) -> str:
    """Search the internet for information"""
    try:
        # Using DuckDuckGo Instant Answer API (free, no API key needed)
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Get abstract or related topics
        result = data.get('AbstractText', '')
        
        if not result:
            # Try to get related topics
            topics = data.get('RelatedTopics', [])
            if topics and len(topics) > 0:
                result = topics[0].get('Text', 'No results found')
        
        if not result:
            result = "No results found. Try rephrasing your query."
        
        return result[:500]  # Limit to 500 chars
    except Exception as e:
        return f"Search failed: {str(e)}"

# ==================== STATE ====================
class State(TypedDict):
    question: str
    answer: str
    count: int

# ==================== NODES ====================
def answer_question(state: State):
    print(f"\n--- Step {state['count']}: Answering ---")
    print(f"Question: {state['question']}")
    
    # Ask LLM if it needs tools
    prompt = f"""Question: {state['question']}

Do you need to:
1. Use calculator (for math)
2. Search internet (for current info/facts)
3. Answer directly (you know the answer)

Reply with ONLY: "calculator" OR "search" OR "direct"
"""
    
    decision = LLM.invoke(prompt).lower().strip()
    print(f"LLM Decision: {decision}")
    
    return {
        "question": state["question"],
        "answer": decision,
        "count": state["count"] + 1
    }

def use_calculator(state: State):
    print(f"\n--- Step {state['count']}: Using Calculator ---")
    
    # Ask LLM to extract the math expression
    prompt = f"Extract only the math expression from: {state['question']}\nReply with just the expression like: 25*4"
    expression = LLM.invoke(prompt)
    print(f"Expression: {expression}")
    
    # Use calculator tool
    result = calculator.invoke(expression)
    print(f"Calculator result: {result}")
    
    # Generate final answer
    final_prompt = f"Question: {state['question']}\nCalculation result: {result}\nProvide a complete answer:"
    final_answer = LLM.invoke(final_prompt)
    
    return {
        "question": state["question"],
        "answer": final_answer,
        "count": state["count"] + 1
    }

def use_search(state: State):
    print(f"\n--- Step {state['count']}: Searching Internet ---")
    
    # Search the internet
    search_result = internet_search.invoke(state["question"])
    print(f"Search result: {search_result[:200]}...")
    
    # Generate answer using search results
    prompt = f"""Question: {state['question']}

Search results: {search_result}

Based on the search results, provide a clear answer:"""
    
    answer = LLM.invoke(prompt)
    
    return {
        "question": state["question"],
        "answer": answer,
        "count": state["count"] + 1
    }

def answer_direct(state: State):
    print(f"\n--- Step {state['count']}: Direct Answer ---")
    
    # LLM answers directly
    prompt = f"Answer this question: {state['question']}"
    answer = LLM.invoke(prompt)
    
    return {
        "question": state["question"],
        "answer": answer,
        "count": state["count"] + 1
    }

def finish(state: State):
    print(f"\n--- Step {state['count']}: Finished ---")
    print(f"Final Answer: {state['answer']}")
    return state

# ==================== ROUTING ====================
def route_to_tool(state: State):
    decision = state["answer"]
    
    if "calculator" in decision or "calc" in decision:
        print("→ Going to calculator")
        return "calculator"
    elif "search" in decision:
        print("→ Going to search")
        return "search"
    else:
        print("→ Going to direct answer")
        return "direct"

# ==================== BUILD GRAPH ====================
workflow = StateGraph(State)

workflow.add_node("answer", answer_question)
workflow.add_node("calculator", use_calculator)
workflow.add_node("search", use_search)
workflow.add_node("direct", answer_direct)
workflow.add_node("finish", finish)

workflow.set_entry_point("answer")

workflow.add_conditional_edges(
    "answer",
    route_to_tool,
    {
        "calculator": "calculator",
        "search": "search",
        "direct": "direct"
    }
)

workflow.add_edge("calculator", "finish")
workflow.add_edge("search", "finish")
workflow.add_edge("direct", "finish")
workflow.add_edge("finish", END)

app = workflow.compile()

# ==================== RUN ====================
print("="*50)
print("TEST 1: Math Question")
print("="*50)
result1 = app.invoke({
    "question": "What is 25 times 4?",
    "answer": "",
    "count": 1
})
print(f"\nFINAL: {result1['answer']}\n")

print("\n" + "="*50)
print("TEST 2: Internet Search Question")
print("="*50)
result2 = app.invoke({
    "question": "Who is the president of France? And what is today's date?",
    "answer": "",
    "count": 1
})
print(f"\nFINAL: {result2['answer']}\n")

print("\n" + "="*50)
print("TEST 3: Direct Answer Question")
print("="*50)
result3 = app.invoke({
    "question": "What is photosynthesis?",
    "answer": "",
    "count": 1
})
print(f"\nFINAL: {result3['answer']}\n")
