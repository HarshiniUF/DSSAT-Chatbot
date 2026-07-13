# 🤖 DSSAT LangGraph Agents Architecture

This document provides a comprehensive analysis of the DSSAT Assistant agent system, including detailed pseudocodes at three levels of abstraction and architectural recommendations.

## 📋 Project Overview

The DSSAT LangGraph Assistant is a sophisticated multi-agent system that combines conversational AI with specialized DSSAT crop simulation capabilities. It processes farmer questions, determines if simulation is needed, designs experiments, validates them, generates DSSAT input files, and provides farmer-friendly explanations.

## 🏗️ Architecture Analysis

### Current System Structure

```
DSSAT Assistant System
├── Entry Points
│   ├── chat_assistant.py (Interactive + Single Q&A)
│   └── dssat_assistant.py (Direct experiment mode)
├── Agent Layer (/agents/)
│   ├── Core Agents
│   │   ├── conversation_agent.py (AU Router, AU Summarizer)
│   │   ├── experiment_agents.py (Q Classifier, A1 Designer, A2 Critic)
│   │   └── workflow_config.py (LangGraph workflow orchestration)
│   ├── Configuration
│   │   ├── schemas.py (TypedDict definitions)
│   │   ├── experiment_guidelines.json (Agent behavior rules)
│   │   └── knowledge_base.py (CSV database access)
│   └── Legacy/Empty Files (candidates for deletion)
├── Tools Layer
│   ├── dssat_tools/ (Regional knowledge, fertilizer codes)
│   └── tool_json_xfiles_09_17_25/ (MZX file generation)
├── Data Layer
│   ├── Soil/ (ICASA-compliant soil files)
│   ├── Weather/ (ICASA-compliant weather files)
│   └── CSV Knowledge Bases (fertilizers, varieties, etc.)
└── Configuration
    ├── provider_config.py (Multi-LLM provider support)
    ├── llm_config.py (LLM initialization)
    └── experiment_config.py (Simulation parameters)
```

## 🔄 Agent Workflow Flow

```
User Question → AU Router → [Direct Answer | Simulation Path]
                              ↓
                         Q Classifier → A1 Designer ⟷ A2 Critic
                              ↓              ↓           ↓
                         Intent Brief → Experiment → Approval/Feedback
                              ↓
                         MZX Generator → AU Summarizer → Final Answer
```

---

## 📝 Pseudocode Level 1: High-Level System Overview

```pseudocode
SYSTEM DSSATAssistant:
    INITIALIZE multi_provider_llm_system
    INITIALIZE conversation_memory
    INITIALIZE mzx_file_generator
    
    FUNCTION handle_user_question(question):
        // Step 1: Route the question
        decision = AU_ROUTER.analyze(question, conversation_history)
        
        IF decision == "direct_answer":
            response = AU_ROUTER.provide_direct_answer(question)
            RETURN response
        
        ELSE IF decision == "needs_simulation":
            // Step 2: Experiment Design Pipeline
            intent = Q_CLASSIFIER.extract_intent(question)
            experiment = A1_DESIGNER.create_experiment(intent, knowledge_base)
            
            // Step 3: Quality Validation Loop (max 4 iterations)
            REPEAT:
                assessment = A2_CRITIC.evaluate(experiment, standards)
                IF assessment.approved:
                    BREAK
                experiment = A1_DESIGNER.redesign(experiment, assessment.feedback)
            UNTIL iterations > 4 OR approved
            
            // Step 4: DSSAT File Generation & Summary
            mzx_files = MZX_GENERATOR.create_files(experiment)
            final_answer = AU_SUMMARIZER.explain_results(experiment, mzx_files)
            
            RETURN final_answer
    
    FUNCTION interactive_mode():
        memory = INITIALIZE_conversation_memory()
        WHILE user_wants_to_continue:
            question = GET_user_input()
            answer = handle_user_question(question, memory)
            DISPLAY(answer)
            memory.add_exchange(question, answer)
```

---

## 📝 Pseudocode Level 2: Detailed Agent Interactions

```pseudocode
// ============================================================================
// AGENT: AU Router (Conversational Interface & Decision Maker)
// ============================================================================
AGENT AU_Router:
    PURPOSE: "Friendly farmer interface with intelligent routing"
    
    FUNCTION analyze_question(question, conversation_history):
        context = EXTRACT_conversation_context(conversation_history)
        
        // Decision matrix for routing
        simulation_indicators = [
            "compare", "vs", "better", "optimal", "when should", 
            "how much", "what if", "which variety", "timing"
        ]
        
        direct_answer_indicators = [
            "what is", "how does", "explain", "definition", "benefits"
        ]
        
        // LLM-powered decision with fallback logic
        TRY:
            llm_decision = LLM.classify(question, context, examples)
            confidence = CALCULATE_confidence(llm_decision, indicators)
        CATCH llm_error:
            confidence = KEYWORD_FALLBACK_classification(question, indicators)
        
        IF confidence.simulation > 0.6:
            RETURN "needs_simulation", IMPROVE_question_clarity(question)
        ELSE:
            RETURN "direct_answer", GENERATE_direct_response(question, knowledge_base)
    
    FUNCTION provide_direct_answer(question):
        context = LOAD_knowledge_csvs(["fertilizer_database.csv", "enhanced_knowledge_base.csv"])
        
        // RAG-style knowledge retrieval
        relevant_info = SEMANTIC_SEARCH(question, context)
        
        response = LLM.generate_response(
            template="You are AU, a friendly DSSAT agricultural assistant...",
            question=question,
            context=relevant_info,
            personality="enthusiastic, farmer-focused, practical"
        )
        
        RETURN response

// ============================================================================
// AGENT: Q Classifier (Intent Extraction Specialist)
// ============================================================================
AGENT Q_Classifier:
    PURPOSE: "Extract structured experiment intent from natural language"
    
    FUNCTION extract_intent(question):
        // Multi-layered classification approach
        entities = EXTRACT_entities(question)  // Fertilizers, varieties, numbers, dates
        
        // Primary classification with confidence scoring
        focus_patterns = {
            "fertilizer_type": ["DAP", "CAN", "MAP", "vs", "compare"],
            "fertilizer_rate": ["kg/ha", "much", "rate", "application"],
            "fertilizer_timing": ["when", "timing", "topdress", "split"],
            "planting_date": ["plant", "sow", "date", "season"],
            "crop_variety": ["variety", "hybrid", "cultivar", "H614", "H622"]
        }
        
        focus_scores = {}
        FOR each pattern_type, keywords IN focus_patterns:
            score = CALCULATE_match_score(question, keywords)
            focus_scores[pattern_type] = score
        
        primary_focus = ARGMAX(focus_scores)
        
        // Structure classification
        structure_type = DETERMINE_structure(question, primary_focus)
        // Options: comparison, rate_response, timing, calendar, variety
        
        // Extract specific options and numeric targets
        options = EXTRACT_options(question, entities)
        numeric_targets = EXTRACT_numeric_values(question, entities)
        
        RETURN IntentBrief(
            focus_variable=primary_focus,
            experiment_structure=structure_type,
            options=options,
            numeric_targets=numeric_targets,
            confidence=MAX(focus_scores.values())
        )

// ============================================================================
// AGENT: A1 Designer (Experiment Design Specialist)
// ============================================================================
AGENT A1_Designer:
    PURPOSE: "Agricultural experiment design with Trans Nzoia expertise"
    
    FUNCTION create_experiment(intent, knowledge_context):
        // Load regional and agricultural knowledge
        regional_data = LOAD_regional_profile("Trans Nzoia")
        fertilizer_catalog = LOAD_fertilizer_database()
        variety_catalog = LOAD_crop_varieties()
        
        // Design constraints validation
        planting_window = VALIDATE_planting_dates(regional_data.season_dates)
        treatment_limits = GET_treatment_constraints()  // 3-5 treatments max
        
        // LLM-guided experiment design with knowledge grounding
        design_prompt = CONSTRUCT_design_prompt(
            farmer_question=intent.question,
            intent_structure=intent,
            available_fertilizers=fertilizer_catalog,
            available_varieties=variety_catalog,
            regional_practices=regional_data,
            design_rules=LOAD_experiment_guidelines()
        )
        
        TRY:
            experiment = LLM.design_experiment(design_prompt)
            experiment = VALIDATE_and_enhance(experiment, knowledge_context)
        CATCH design_error:
            experiment = FALLBACK_experiment_generator(intent, knowledge_context)
        
        // Ensure all treatments have required fields for DSSAT compatibility
        FOR each treatment IN experiment.treatments:
            treatment = APPLY_core_defaults(treatment, regional_data)
            treatment = ENSURE_fertilizer_requirements(treatment)  // basal_rate >= 50 for non-control
        
        RETURN experiment
    
    FUNCTION fallback_experiment_generator(intent, context):
        treatments = []
        
        // Always include control treatment
        control = CREATE_control_treatment(context)
        treatments.append(control)
        
        // Generate treatments based on focus variable
        SWITCH intent.focus_variable:
            CASE "fertilizer_type":
                treatments.extend(GENERATE_fertilizer_comparison(intent.options, context))
            CASE "fertilizer_rate":
                treatments.extend(GENERATE_rate_response(intent.numeric_targets, context))
            CASE "fertilizer_timing":
                treatments.extend(GENERATE_timing_comparison(context))
            CASE "planting_date":
                treatments.extend(GENERATE_planting_calendar(context))
            CASE "crop_variety":
                treatments.extend(GENERATE_variety_comparison(intent.options, context))
        
        RETURN ASSEMBLE_experiment(intent, treatments, context)

// ============================================================================
// AGENT: A2 Critic (Quality Assurance & Scientific Rigor)
// ============================================================================
AGENT A2_Critic:
    PURPOSE: "Scientific validation and agricultural best practices enforcement"
    
    FUNCTION evaluate_experiment(experiment, regional_standards):
        assessment = INITIALIZE_assessment()
        
        // Multi-criteria evaluation framework
        criteria = {
            "agricultural_realism": VALIDATE_agricultural_practices(experiment),
            "statistical_rigor": VALIDATE_experimental_design(experiment),
            "dssat_compatibility": VALIDATE_dssat_requirements(experiment),
            "regional_appropriateness": VALIDATE_regional_fit(experiment, regional_standards),
            "treatment_differentiation": VALIDATE_treatment_contrast(experiment)
        }
        
        // Detailed evaluation with scoring
        FOR criterion, validator IN criteria:
            result = validator.assess(experiment)
            assessment.scores[criterion] = result.score
            assessment.issues.extend(result.issues)
            assessment.suggestions.extend(result.suggestions)
        
        // Critical flaw detection
        critical_flaws = IDENTIFY_critical_issues(assessment.issues)
        overall_score = CALCULATE_weighted_score(assessment.scores)
        
        // Approval decision logic
        approval_threshold = 7.0
        has_critical_issues = len(critical_flaws) > 0
        
        IF overall_score >= approval_threshold AND NOT has_critical_issues:
            assessment.approved = True
            assessment.feedback = GENERATE_positive_feedback(assessment)
        ELSE:
            assessment.approved = False
            assessment.feedback = GENERATE_improvement_suggestions(assessment, critical_flaws)
        
        RETURN assessment
    
    FUNCTION validate_agricultural_practices(experiment):
        issues = []
        suggestions = []
        
        // Check fertilizer program realism
        FOR treatment IN experiment.treatments:
            IF treatment.has_fertilizer:
                rate = treatment.basal_rate
                timing = treatment.application_timing
                
                IF rate < 50 OR rate > 300:
                    issues.append(f"Unrealistic fertilizer rate: {rate} kg/ha")
                
                IF timing NOT IN ["At planting", "2-6 weeks after planting"]:
                    issues.append(f"Unusual timing: {timing}")
        
        // Check planting date realism for Trans Nzoia
        valid_window = ("2025-03-01", "2025-05-31")  // Long rains season
        FOR treatment IN experiment.treatments:
            IF treatment.planting_date NOT IN valid_window:
                issues.append(f"Planting date {treatment.planting_date} outside optimal window")
        
        RETURN ValidationResult(issues, suggestions, CALCULATE_score(issues))

// ============================================================================
// AGENT: AU Summarizer (Results Communication Specialist)
// ============================================================================
AGENT AU_Summarizer:
    PURPOSE: "Farmer-friendly explanation of simulation results"
    
    FUNCTION explain_results(experiment, generated_files):
        // Extract key experiment details
        experiment_summary = SUMMARIZE_experiment(experiment)
        technical_details = EXTRACT_technical_info(generated_files)
        
        // Generate farmer-friendly explanation
        response_structure = {
            "enthusiasm": "Express excitement about helping the farmer",
            "simulation_explanation": "What we simulated and why it matters",
            "treatment_breakdown": "Clear explanation of each treatment",
            "practical_value": "How this helps farmer decision-making",
            "next_steps": "What happens with the DSSAT files",
            "technical_summary": "File generation details for reference"
        }
        
        farmer_response = LLM.generate_explanation(
            template=LOAD_summarizer_template(),
            experiment=experiment_summary,
            files=technical_details,
            personality="enthusiastic, educational, practical",
            audience="farmers and agricultural practitioners"
        )
        
        RETURN farmer_response
```

---

## 📝 Pseudocode Level 3: Implementation-Level Detail

```pseudocode
// ============================================================================
// DETAILED IMPLEMENTATION: AU Router Agent
// ============================================================================
CLASS AU_Router_Agent:
    ATTRIBUTES:
        llm: LangChain_LLM_Instance
        memory: ConversationMemory
        knowledge_loader: CSV_Knowledge_Loader
    
    METHOD analyze_question(question: str, conversation_memory: dict) -> dict:
        // Step 1: Conversation context extraction
        context_history = []
        IF conversation_memory.conversation_history:
            FOR message IN conversation_memory.conversation_history[-5:]:  // Last 5 messages
                context_history.append(f"{message.role}: {message.content}")
        
        context_string = "\n".join(context_history) IF context_history ELSE "No previous conversation"
        
        // Step 2: Decision prompt construction with examples
        decision_prompt = ChatPromptTemplate.from_template("""
        You are AU - Agent User, a friendly DSSAT agricultural assistant.
        
        User Question: "{question}"
        
        Context from previous conversation:
        {context}
        
        DECISION TASK: Determine if this question needs DSSAT simulation or can be answered directly.
        
        Questions that NEED SIMULATION (respond "simulation"):
        - Comparing fertilizer types/rates/timing (e.g., "DAP vs CAN", "100kg vs 150kg")
        - Optimal planting dates ("When should I plant?")
        - Yield predictions under different conditions
        - "What if" scenarios requiring crop modeling
        - Questions asking "what is better" between options
        
        Questions for DIRECT ANSWER (respond "direct"):
        - General knowledge ("What is DSSAT?", "What are benefits of fertilizer?")
        - Definitions and explanations
        - How-to information without specific optimization
        
        Respond with either "simulation" or "direct" followed by your reasoning.
        """)
        
        // Step 3: LLM inference with error handling
        TRY:
            llm_response = self.llm.invoke(
                decision_prompt.format_messages(
                    question=question,
                    context=context_string
                )
            )
            
            response_content = llm_response.content.strip().lower()
            
            // Extract decision from LLM response
            IF "simulation" IN response_content:
                needs_simulation = True
            ELIF "direct" IN response_content:
                needs_simulation = False
            ELSE:
                // Fallback to keyword analysis
                needs_simulation = self._fallback_classification(question)
            
        CATCH LLM_Error as e:
            PRINT(f"LLM classification failed: {e}, using fallback")
            needs_simulation = self._fallback_classification(question)
        
        // Step 4: Response generation based on decision
        IF needs_simulation:
            au_response = "Let me use the power of DSSAT to answer your question..."
            improved_question = self._improve_question_clarity(question)
            
            RETURN {
                "needs_simulation": True,
                "au_initial_response": au_response,
                "clarified_question": improved_question,
                "conversation_memory": conversation_memory
            }
        
        ELSE:
            direct_answer = self._provide_direct_answer(question)
            
            RETURN {
                "needs_simulation": False,
                "final_answer": direct_answer,
                "conversation_memory": conversation_memory
            }
    
    METHOD _fallback_classification(question: str) -> bool:
        // Keyword-based classification when LLM fails
        question_lower = question.lower()
        
        simulation_keywords = [
            "compare", "vs", "versus", "better", "best", "optimal", "should i use",
            "which", "when should", "how much", "rate", "timing", "split",
            "topdressing", "variety", "hybrid", "planting date"
        ]
        
        direct_keywords = [
            "what is", "what are", "how does", "explain", "definition",
            "benefits", "advantages", "disadvantages", "meaning of"
        ]
        
        simulation_score = SUM(1 FOR keyword IN simulation_keywords IF keyword IN question_lower)
        direct_score = SUM(1 FOR keyword IN direct_keywords IF keyword IN question_lower)
        
        RETURN simulation_score > direct_score
    
    METHOD _provide_direct_answer(question: str) -> str:
        // Load knowledge bases for RAG-style retrieval
        knowledge_files = [
            "knowledge_base.csv",
            "enhanced_knowledge_base.csv", 
            "fertilizer_database.csv"
        ]
        
        context_data = []
        FOR file IN knowledge_files:
            TRY:
                df = pd.read_csv(file)
                relevant_rows = self._semantic_search(question, df)
                context_data.extend(relevant_rows)
            CATCH FileNotFoundError:
                CONTINUE
        
        // Construct response prompt
        answer_prompt = ChatPromptTemplate.from_template("""
        You are AU, a friendly DSSAT agricultural assistant. Answer the user's question 
        using the provided knowledge base context.
        
        User Question: {question}
        
        Relevant Context:
        {context}
        
        Instructions:
        - Be enthusiastic and farmer-focused
        - Provide practical, actionable advice
        - Use simple language that farmers can understand
        - If you mention specific fertilizers or varieties, include their benefits
        - Offer to run a simulation if they want more detailed analysis
        
        Answer:
        """)
        
        context_string = "\n".join([str(item) for item in context_data[:10]])  // Limit context size
        
        response = self.llm.invoke(
            answer_prompt.format_messages(
                question=question,
                context=context_string
            )
        )
        
        RETURN response.content

// ============================================================================
// DETAILED IMPLEMENTATION: Q Classifier Agent  
// ============================================================================
CLASS Q_Classifier_Agent:
    ATTRIBUTES:
        llm: LangChain_LLM_Instance
        entity_patterns: Dict[str, List[str]]
    
    METHOD extract_intent(question: str, conversation_state: dict) -> dict:
        // Step 1: Entity extraction using regex patterns
        entities = self._extract_entities(question)
        
        // Step 2: Multi-layered focus classification
        focus_variable = self._classify_focus_variable(question, entities)
        experiment_structure = self._determine_structure(question, focus_variable)
        
        // Step 3: Option and target extraction
        options = self._extract_options(question, entities)
        numeric_targets = self._extract_numeric_targets(question)
        
        // Step 4: Confidence calculation
        confidence = self._calculate_confidence(question, focus_variable, entities)
        
        intent_brief = {
            "question": question,
            "focus_variable": focus_variable,
            "experiment_structure": experiment_structure,
            "target_crop": entities.get("crop", "Maize"),
            "location_hint": entities.get("location", "Trans Nzoia"),
            "options": options,
            "numeric_targets": numeric_targets,
            "confidence": confidence
        }
        
        PRINT(f"Focus variable: {focus_variable}")
        PRINT(f"Structure: {experiment_structure}")
        PRINT(f"Options: {options}")
        
        RETURN {
            **conversation_state,
            "question_type": focus_variable,
            "intent_brief": intent_brief,
            "extracted_entities": entities
        }
    
    METHOD _extract_entities(question: str) -> dict:
        entities = {}
        
        // Fertilizer name extraction
        fertilizer_patterns = {
            "DAP": r"\b(dap|diammonium phosphate)\b",
            "CAN": r"\b(can|calcium ammonium nitrate)\b",
            "MAP": r"\b(map|monoammonium phosphate)\b",
            "Urea": r"\burea\b",
            "NPK": r"\bnpk\s*\d+-\d+-\d+\b"
        }
        
        fertilizer_mentions = []
        FOR name, pattern IN fertilizer_patterns.items():
            IF re.search(pattern, question, re.IGNORECASE):
                fertilizer_mentions.append(name)
        
        entities["fertilizer_mentions"] = fertilizer_mentions
        
        // Variety extraction
        variety_patterns = {
            "H614": r"\bh614\b",
            "H622": r"\bh622\b", 
            "PAN": r"\bpan\d+\b"
        }
        
        variety_mentions = []
        FOR name, pattern IN variety_patterns.items():
            IF re.search(pattern, question, re.IGNORECASE):
                variety_mentions.append(name)
        
        entities["variety_mentions"] = variety_mentions
        
        // Numeric value extraction
        numeric_pattern = r"(\d+(?:\.\d+)?)\s*(kg|kg/ha|weeks?|days?|tons?)"
        numeric_matches = re.findall(numeric_pattern, question, re.IGNORECASE)
        
        entities["numeric_values"] = [
            {"value": float(match[0]), "unit": match[1]}
            FOR match IN numeric_matches
        ]
        
        RETURN entities
    
    METHOD _classify_focus_variable(question: str, entities: dict) -> str:
        question_lower = question.lower()
        
        // Pattern-based classification with scoring
        focus_patterns = {
            "fertilizer_type": {
                "keywords": ["vs", "compare", "better", "which fertilizer", "dap or can"],
                "entity_requirement": lambda e: len(e.get("fertilizer_mentions", [])) >= 2,
                "weight": 2.0
            },
            "fertilizer_rate": {
                "keywords": ["how much", "rate", "kg/ha", "application rate", "amount"],
                "entity_requirement": lambda e: len(e.get("numeric_values", [])) > 0,
                "weight": 1.5
            },
            "fertilizer_timing": {
                "keywords": ["when", "timing", "topdress", "split", "basal", "weeks after"],
                "entity_requirement": lambda e: True,
                "weight": 1.5
            },
            "planting_date": {
                "keywords": ["plant", "planting", "sow", "seeding", "date"],
                "entity_requirement": lambda e: True,
                "weight": 1.0
            },
            "crop_variety": {
                "keywords": ["variety", "hybrid", "cultivar", "h614", "h622"],
                "entity_requirement": lambda e: len(e.get("variety_mentions", [])) > 0,
                "weight": 2.0
            }
        }
        
        scores = {}
        FOR focus_type, config IN focus_patterns.items():
            keyword_score = SUM(1 FOR keyword IN config["keywords"] IF keyword IN question_lower)
            entity_bonus = 1 IF config["entity_requirement"](entities) ELSE 0
            
            scores[focus_type] = (keyword_score + entity_bonus) * config["weight"]
        
        // Return focus with highest score, fallback to fertilizer_type
        IF MAX(scores.values()) > 0:
            RETURN ARGMAX(scores)
        ELSE:
            RETURN "fertilizer_type"  // Default fallback

// ============================================================================
// DETAILED IMPLEMENTATION: A1 Designer Agent
// ============================================================================  
CLASS A1_Designer_Agent:
    ATTRIBUTES:
        llm: LangChain_LLM_Instance
        knowledge_loader: Knowledge_Context_Builder
        guidelines: Dict[str, Any]
    
    METHOD create_experiment(conversation_state: dict) -> dict:
        intent = conversation_state.get("intent_brief", {})
        entities = conversation_state.get("extracted_entities", {})
        
        // Step 1: Build comprehensive knowledge context
        knowledge_context = self._build_knowledge_context(intent, entities)
        
        // Step 2: LLM-guided experiment design
        experiment = self._design_with_llm(intent, knowledge_context)
        
        // Step 3: Fallback generation if LLM fails
        IF NOT experiment OR NOT experiment.get("treatments"):
            experiment = self._generate_fallback_experiment(intent, knowledge_context)
        
        // Step 4: Post-processing and validation
        experiment = self._post_process_experiment(experiment, knowledge_context)
        
        iteration_count = conversation_state.get("iteration_count", 0) + 1
        
        RETURN {
            **conversation_state,
            "proposed_experiment": experiment,
            "design_context": {
                "intent": intent,
                "knowledge": knowledge_context
            },
            "iteration_count": iteration_count
        }
    
    METHOD _build_knowledge_context(intent: dict, entities: dict) -> dict:
        // Load regional profile
        region_name = intent.get("location_hint", "Trans Nzoia")
        regional_profile = self.knowledge_loader.load_regional_data(region_name)
        
        // Load fertilizer catalog based on mentions
        fertilizer_mentions = entities.get("fertilizer_mentions", [])
        fertilizer_catalog = self.knowledge_loader.load_fertilizer_data(fertilizer_mentions)
        
        // Load variety catalog
        variety_mentions = entities.get("variety_mentions", [])
        variety_catalog = self.knowledge_loader.load_variety_data(variety_mentions)
        
        // Determine planting window
        current_date = datetime.now()
        planting_window = self._calculate_planting_window(regional_profile, current_date)
        
        // Load standard agricultural practices
        standard_practice = self._get_standard_practice(intent.get("focus_variable"))
        
        RETURN {
            "region": regional_profile,
            "fertilizers": fertilizer_catalog,
            "varieties": variety_catalog,
            "planting_window": planting_window,
            "standard_practice": standard_practice,
            "guidelines": self.guidelines
        }
    
    METHOD _design_with_llm(intent: dict, context: dict) -> dict:
        // Construct comprehensive design prompt
        design_prompt = ChatPromptTemplate.from_template("""
        You are an agronomic experiment designer creating DSSAT-compatible treatments.

        FARMER QUESTION: {question}
        INTENT BRIEF: {intent_json}

        AVAILABLE KNOWLEDGE:
        - Regional profile: {regional_profile}
        - Candidate fertilizers: {fertilizer_catalog}
        - Candidate varieties: {variety_catalog}
        - Standard practice: {standard_practice}

        DESIGN CONSTRAINTS:
        - Treatments between {min_treatments} and {max_treatments}
        - Include a realistic control baseline with NO fertilizer (basal_rate: 0, basal_fertilizer: "None")
        - All non-control treatments MUST have basal fertilizer application (basal_rate ≥ 50 kg/ha)
        - Keep planting date within regional window ({planting_window})
        - Use fertilizer IDs and variety IDs from knowledge where possible
        
        CRITICAL FERTILIZER REQUIREMENTS:
        - Every non-control treatment must include "basal_fertilizer" and "basal_rate" fields
        - basal_rate must be ≥ 50 kg/ha for non-control treatments  
        - basal_fertilizer must be specific name (DAP, CAN, MAP, etc.), never "None" for non-control
        - Control treatment should have basal_rate: 0 and basal_fertilizer: "None"

        Output JSON matching this schema exactly:
        {{
            "experiment_purpose": "clear objective",
            "variable_tested": "{focus_variable}",
            "treatments": [
                {{
                    "id": "S01",
                    "description": "treatment summary", 
                    "modifications": {{
                        "crop_variety": "name",
                        "variety_id": "ID",
                        "basal_fertilizer": "specific fertilizer name or None for control",
                        "basal_rate": "numeric value (0 for control, ≥50 for others)",
                        "fertilizer": "name or None",
                        "fertilizer_rate": "value + kg/ha",
                        "application_timing": "timing description",
                        "planting_date": "YYYY-MM-DD"
                    }}
                }}
            ],
            "expected_answer": "specific insight"
        }}

        Make sure treatments isolate the primary variable while keeping other management consistent.
        Return JSON only, no explanations.
        """)
        
        TRY:
            response = self.llm.invoke(
                design_prompt.format_messages(
                    question=intent.get("question"),
                    intent_json=json.dumps(intent, indent=2),
                    regional_profile=json.dumps({
                        k: v for k, v in context.get("region", {}).items() 
                        if isinstance(v, (str, int, float))
                    }, indent=2),
                    fertilizer_catalog=json.dumps(context.get("fertilizers", []), indent=2),
                    variety_catalog=json.dumps(context.get("varieties", []), indent=2),
                    standard_practice=json.dumps(context.get("standard_practice", {}), indent=2),
                    min_treatments=get_min_treatments(),
                    max_treatments=get_max_treatments(),
                    planting_window=f"{context.get('planting_window', {}).get('start')} to {context.get('planting_window', {}).get('end')}",
                    focus_variable=intent.get("focus_variable")
                )
            )
            
            // Extract JSON from LLM response
            content = response.content.strip()
            start = content.find("{")
            end = content.rfind("}") + 1
            
            IF start != -1 AND end != 0:
                experiment = json.loads(content[start:end])
                RETURN experiment
            ELSE:
                RAISE ValueError("No valid JSON found in LLM response")
                
        CATCH Exception as e:
            PRINT(f"LLM experiment design failed: {e}")
            RETURN None
    
    METHOD _generate_fallback_experiment(intent: dict, context: dict) -> dict:
        // Deterministic experiment generation when LLM fails
        focus_variable = intent.get("focus_variable", "fertilizer_type")
        
        treatments = []
        
        // Always start with control treatment
        control_treatment = {
            "id": "S01",
            "description": "Control - No fertilizer",
            "modifications": {
                "basal_fertilizer": "None",
                "basal_rate": 0,
                "fertilizer": "None",
                "fertilizer_rate": "0 kg/ha",
                "application_timing": "None"
            }
        }
        treatments.append(control_treatment)
        
        // Generate treatments based on focus variable
        SWITCH focus_variable:
            CASE "fertilizer_type":
                treatments.extend(self._generate_fertilizer_comparison(intent, context))
            CASE "fertilizer_rate":
                treatments.extend(self._generate_rate_response(intent, context))
            CASE "fertilizer_timing":
                treatments.extend(self._generate_timing_comparison(intent, context))
            CASE "planting_date":
                treatments.extend(self._generate_planting_calendar(intent, context))
            CASE "crop_variety":
                treatments.extend(self._generate_variety_comparison(intent, context))
        
        RETURN {
            "experiment_purpose": f"Compare {focus_variable} effects on crop yield",
            "variable_tested": focus_variable,
            "treatments": treatments,
            "expected_answer": f"Determine optimal {focus_variable} strategy"
        }
```

## 📁 Files Analysis & Cleanup Recommendations

### ✅ Core Files (Keep)
- `__init__.py` - Package initialization and exports
- `conversation_agent.py` - AU Router and AU Summarizer agents
- `experiment_agents.py` - Q Classifier, A1 Designer, A2 Critic agents  
- `workflow_config.py` - LangGraph workflow orchestration
- `schemas.py` - Type definitions and schemas
- `experiment_guidelines.json` - Agent behavior configuration
- `knowledge_base.py` - CSV database access utilities

### ❌ Files to Delete (Empty/Redundant)
- `smart_agents.py` - Empty file
- `smart_agents_clean.py` - Empty file  
- `domain_router.py` - Empty file
- `smart_domain_router.py` - Empty file
- `smart_dssat_agents.py` - Empty file
- `specialized_workflow.py` - Empty file

### 🔧 Recommended Cleanup Commands

```bash
cd /mnt/ssd/DSSAT_LangGraph_with_tools/agents
rm smart_agents.py smart_agents_clean.py domain_router.py smart_domain_router.py smart_dssat_agents.py specialized_workflow.py
```

## 🎯 Architecture Strengths

1. **Modular Design**: Clean separation of concerns between routing, classification, design, validation, and generation
2. **Knowledge-Driven**: Extensive use of CSV knowledge bases for agricultural expertise
3. **LangGraph Integration**: Proper state management and workflow orchestration
4. **Multi-Provider LLM**: Flexible LLM provider system (OpenRouter, Groq, etc.)
5. **DSSAT Compliance**: Generated files are fully compatible with DSSAT simulation software
6. **Farmer-Friendly**: Conversational interface with practical, actionable advice

## 🚀 Key Technical Features

- **Conversation Memory**: Maintains context across multi-turn conversations  
- **Fallback Mechanisms**: Robust error handling with keyword-based classification fallbacks
- **Agricultural Validation**: A2 Critic ensures experiments follow best practices
- **Iterative Improvement**: A1/A2 feedback loop (up to 4 iterations) for quality assurance
- **ICASA Compliance**: Soil and weather file generation follows international standards
- **Multi-Question Support**: Handles fertilizer type/rate/timing, planting dates, varieties

This architecture successfully combines conversational AI with domain expertise to provide farmers with scientifically-grounded, simulation-backed agricultural recommendations.
