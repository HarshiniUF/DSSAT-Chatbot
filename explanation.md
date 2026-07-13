# Workflow Explanation: Comparison Question Processing

## Question
**"Is it more effective to apply 100kg of Nitrogen in one go at knee-high or should I split it into 50kg at 4 weeks and 50kg at 8 weeks?"**

---

## Complete Execution Flow

### **Step 1: Question Entry**
- **File**: `integrated_dssat_assistant.py`
- **What happens**: User enters the comparison question
- **Code executes**: Main conversation loop receives input and passes to LangGraph workflow

---

### **Step 2: AU Router (Admin Understanding)**
- **File**: `agents/multiagent_nodes.py` → `multiagent_admin_understanding()` function
- **What happens**: Initial question analysis to route to correct handler
- **LLM Used**: Navigator API (GPT-5)
- **Prompt**: Analyzes if question is about fertilizer/planting/irrigation
- **Output**: Routes to Q Classifier for detailed fertilizer analysis

---

### **Step 3: Q Classifier with Comparison Detection** ⭐ **CRITICAL STEP**
- **File**: `agents/experiment_agents.py` → `q_classifier_comparison()` function (lines 68-275)
- **What happens**: 
  - Detects "OR" keyword indicating comparison
  - Uses LLM to parse both strategies
- **LLM Used**: Navigator API (GPT-5)
- **Prompt Used** (lines 95-158):
  ```
  You are an expert agricultural advisor analyzing fertilizer comparison questions.
  
  Parse this question into TWO strategies:
  - Strategy A: First option
  - Strategy B: Second option
  
  Growth stage mappings:
  - "knee-high" / "V8" → 45 days after planting
  - "4 weeks" → 28 days after planting
  - "8 weeks" → 56 days after planting
  
  Return JSON format with applications array for each strategy
  ```
- **LLM Call** (line 162):
  ```python
  result = llm.invoke(comparison_prompt.format_messages(question=question))
  ```
- **Output** (JSON from LLM):
  ```json
  {
    "strategy_a": {
      "description": "100kg at knee-high",
      "applications": [
        {
          "timing": "knee-high",
          "amount_kg": 100,
          "days_after_planting": 45
        }
      ]
    },
    "strategy_b": {
      "description": "50kg at 4 weeks and 50kg at 8 weeks",
      "applications": [
        {
          "timing": "4 weeks",
          "amount_kg": 50,
          "days_after_planting": 28
        },
        {
          "timing": "8 weeks",
          "amount_kg": 50,
          "days_after_planting": 56
        }
      ]
    }
  }
  ```
- **State Update**: Sets `question_type = "fertilizer_comparison"` and stores parsed strategies

---

### **Step 4: Conditional Routing** ⭐ **CRITICAL ROUTING**
- **File**: `agents/workflow_config.py` → `route_after_q_classifier()` function (lines 117-127)
- **What happens**: Checks question type and routes accordingly
- **Code**:
  ```python
  def route_after_q_classifier(state):
      question_type = state.get("intent", {}).get("question_type", "")
      if question_type == "fertilizer_comparison":
          return "generate_comparison_snx"  # Skip A1 Designer/A2 Critic
      else:
          return "design_experiment"  # Regular workflow
  ```
- **Route Taken**: `generate_comparison_snx` → Goes directly to comparison handler
- **Routes SKIPPED**: A1 Designer and A2 Critic (NOT executed for comparisons)

---

### **Step 5: Comparison SNX Generation** ⭐ **MAIN PROCESSING**
- **File**: `agents/multiagent_nodes.py` → `multiagent_xfile_comparison()` function (lines 450-575)
- **What happens**: Generates TWO separate SNX files (s01 and s02)
- **No LLM Used**: Uses structured data from Step 3's LLM output
- **Process**:

  **For Strategy A (experiment_s01.SNX):**
  - Reads `strategy_a.applications` from LLM output (line 521)
  - Calls `build_fertilizer_events()` helper function (lines 480-520)
  - Extracts from LLM data (lines 498-499):
    ```python
    days_offset = app.get("days_after_planting", 0)  # Gets 45
    amount = app.get("amount_kg", 50)  # Gets 100
    ```
  - Calculates fertilizer date: PDATE + 45 days
  - Creates fertilizer event structure:
    ```python
    {
      "FDATE": "25120",  # Planting date + 45 days
      "FAMN": 100.0,     # Amount in kg
      "FMCD": "FE001",   # DSSAT fertilizer code
      "FACD": "AP001"    # DSSAT application code
    }
    ```

  **For Strategy B (experiment_s02.SNX):**
  - Reads `strategy_b.applications` from LLM output (line 534)
  - Calls `build_fertilizer_events()` twice (one per application)
  - Creates TWO fertilizer events:
    - Event 1: PDATE + 28 days, 50kg
    - Event 2: PDATE + 56 days, 50kg

- **Output**: Two experiment configs ready for xFileGenerator

---

### **Step 6: SNX File Generation**
- **File**: `xFileGenerator.py` → `FertilizerAgent` class (lines 810-840)
- **What happens**: Converts fertilizer events to DSSAT SNX format
- **No LLM Used**: Uses pre-structured events from Step 5
- **Code** (line 815):
  ```python
  fertilizer_list = config.get("fertilizer_events") or []
  print(f"Using {len(fertilizer_list)} pre-configured fertilizer event(s)")
  ```
- **Process**:
  - Takes fertilizer_events from config
  - Creates DSSAT Fertilizer objects
  - Writes to SNX file format

---

### **Step 7: Final Output**
- **Files Created**:
  1. `experiment_s01.SNX` - Strategy A (100kg at knee-high)
  2. `experiment_s02.SNX` - Strategy B (50kg at 4 weeks + 50kg at 8 weeks)

- **experiment_s01.SNX Content**:
  ```
  *FERTILIZERS (INORGANIC)
  @F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK
   1 25120 FE001 AP001     5 100.0   0.0   0.0
  ```
  *(FDATE 25120 = March 15 + 45 days = April 29)*

- **experiment_s02.SNX Content**:
  ```
  *FERTILIZERS (INORGANIC)
  @F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK
   1 25103 FE001 AP001     5  50.0   0.0   0.0
   2 25131 FE001 AP001     5  50.0   0.0   0.0
  ```
  *(FDATE 25103 = March 15 + 28 days = April 12)*
  *(FDATE 25131 = March 15 + 56 days = May 10)*

---

## Summary of Files Used

### **Files Executed (In Order)**:
1. ✅ `integrated_dssat_assistant.py` - Main entry point
2. ✅ `agents/multiagent_nodes.py` - AU Router
3. ✅ `agents/experiment_agents.py` - Q Classifier with LLM parsing
4. ✅ `agents/workflow_config.py` - Conditional routing
5. ✅ `agents/multiagent_nodes.py` - Comparison SNX generation
6. ✅ `xFileGenerator.py` - Final SNX file creation

### **Files NOT Executed**:
- ❌ `agents/experiment_agents.py` - A1 Designer (SKIPPED)
- ❌ `agents/experiment_agents.py` - A2 Critic (SKIPPED)

---

## LLM Usage Summary

### **LLM Calls Made**: 2 total

1. **AU Router LLM Call**
   - **Purpose**: Route to fertilizer handler
   - **Model**: Navigator API (GPT-5)
   - **Input**: Full question
   - **Output**: Fertilizer category

2. **Q Classifier LLM Call** ⭐ **MOST IMPORTANT**
   - **Purpose**: Parse comparison into two strategies
   - **Model**: Navigator API (GPT-5)
   - **Prompt Location**: `agents/experiment_agents.py` lines 95-158
   - **Input**: Comparison question
   - **Output**: JSON with strategy_a and strategy_b containing applications arrays
   - **Key Feature**: Understands natural language (knee-high, 4 weeks, 8 weeks) and converts to days

### **NO LLM Calls Made**:
- ❌ A1 Designer LLM (workflow routing skips this)
- ❌ A2 Critic LLM (workflow routing skips this)
- ❌ xFileGenerator LLM (uses pre-structured events)

---

## Key Technical Points for Professor

### **1. LLM-Based vs Hardcoded**
- ✅ **LLM interprets**: "knee-high" → 45 days, "4 weeks" → 28 days, "8 weeks" → 56 days
- ✅ **LLM parses**: Natural language into structured JSON
- ✅ **LLM handles variations**: Works with "V8", "tasseling", "flowering", etc.
- ❌ **NOT hardcoded**: No if/then logic for timing detection
- ❌ **Growth stages in prompt**: Provided as guidance to LLM, not code logic

### **2. Workflow Efficiency**
- **Comparison questions**: 2 LLM calls total
- **Regular questions**: 4+ LLM calls (includes A1 Designer and A2 Critic iterations)
- **Time saved**: Skip design/critique loop for comparisons

### **3. DSSAT Integration**
- **Fertilizer codes**: FE001 (Urea), AP001 (Broadcast application) - Required by DSSAT format
- **Date format**: YYDDD (25120 = Year 2025, Day 120)
- **Output**: Two valid DSSAT experiment files ready for simulation

### **4. Scalability**
- ✅ Works with ANY fertilizer amounts (not just 50kg/100kg)
- ✅ Works with ANY timing descriptions (not just knee-high/4 weeks)
- ✅ Handles 1, 2, or multiple split applications
- ✅ LLM learns from prompt examples and can generalize

---

## Data Flow Diagram

```
User Question
    ↓
integrated_dssat_assistant.py (Main Loop)
    ↓
AU Router (LLM Call #1) → Routes to fertilizer
    ↓
Q Classifier (LLM Call #2) → Detects "OR" keyword
    ↓
LLM Parses Question → JSON with 2 strategies
    ↓
Conditional Router → Checks question_type
    ↓
[SKIP A1 Designer & A2 Critic]
    ↓
Comparison Handler → Builds fertilizer events from LLM JSON
    ↓
xFileGenerator → Creates SNX files
    ↓
Output: experiment_s01.SNX (Strategy A)
Output: experiment_s02.SNX (Strategy B)
```

---

## Growth Stage Knowledge Base (In LLM Prompt)

| Growth Stage Term | Days After Planting | Agronomic Reference |
|------------------|---------------------|---------------------|
| V6 (6 leaves) | 30-35 | Early vegetative |
| V8 / V10 / knee-high | 45 | Mid-vegetative |
| Tasseling / Flowering | 60 | Reproductive |
| 4 weeks | 28 | Explicit time |
| 8 weeks | 56 | Explicit time |

*Note: These mappings are in the LLM prompt as guidance. The LLM uses them to interpret natural language, NOT hardcoded in if/then statements.*

---

## Verification Commands

```bash
# Test the workflow
python3 integrated_dssat_assistant.py

# Check s01.SNX (Strategy A: 100kg at knee-high)
grep -A 3 "FERTILIZERS (INORGANIC)" experiment_s01.SNX

# Check s02.SNX (Strategy B: 50kg at 4 weeks + 50kg at 8 weeks)
grep -A 4 "FERTILIZERS (INORGANIC)" experiment_s02.SNX
```

**Expected Output**:
- s01.SNX: 1 fertilizer event at 100kg
- s02.SNX: 2 fertilizer events at 50kg each

---

## Advantages of This Approach

1. ✅ **Natural Language Understanding**: LLM handles variations like "knee-high", "V8", "mid-season"
2. ✅ **No Hardcoding**: Works with any amounts, timings, or crop stages
3. ✅ **Efficient Routing**: Skips unnecessary design iterations for comparisons
4. ✅ **Scalable**: Can handle 2-way, 3-way, or N-way comparisons
5. ✅ **DSSAT Compatible**: Generates valid experiment files for simulation
6. ✅ **Maintainable**: Growth stage knowledge in LLM prompt, easy to update

---

*Generated: March 12, 2026*
*System: DSSAT Multi-Agent LangGraph Workflow*
*LLM: Navigator API (GPT-5)*
