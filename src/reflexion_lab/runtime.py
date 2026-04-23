import json
import time
from .llm import get_llm_response
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .utils import normalize_answer

FAILURE_MODE_BY_QID = {}

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> tuple[str, int, int]:
    start_time = time.time()
    
    # Construct prompt
    context_str = "\n".join([f"Source: {c.title}\nContent: {c.text}" for c in example.context])
    reflections_str = "\n".join(reflection_memory)
    
    prompt = f"""
Context:
{context_str}

Question: {example.question}

Previous Reflections:
{reflections_str if reflections_str else "None"}

Please provide your answer below:
"""
    
    response = get_llm_response(ACTOR_SYSTEM + "\n" + prompt)
    latency = int((time.time() - start_time) * 1000)
    
    return response["content"], response["total_tokens"], latency

def evaluator(example: QAExample, answer: str) -> tuple[JudgeResult, int, int]:
    start_time = time.time()
    
    prompt = f"""
Question: {example.question}
Gold Answer: {example.gold_answer}
Assistant Answer: {answer}

Evaluate the Assistant Answer against the Gold Answer.
"""
    
    response = get_llm_response(EVALUATOR_SYSTEM + "\n" + prompt)
    latency = int((time.time() - start_time) * 1000)
    
    try:
        # Clean potential markdown code blocks
        clean_content = response["content"].strip()
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:-3].strip()
        elif clean_content.startswith("```"):
            clean_content = clean_content[3:-3].strip()
            
        data = json.loads(clean_content)
        result = JudgeResult(**data)
    except Exception as e:
        # Fallback if LLM fails to provide valid JSON
        is_correct = normalize_answer(example.gold_answer) == normalize_answer(answer)
        result = JudgeResult(
            score=1 if is_correct else 0,
            reason=f"Auto-fallback evaluation. Parse error: {str(e)}",
            missing_evidence=[],
            spurious_claims=[]
        )
        
    return result, response["total_tokens"], latency

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> tuple[ReflectionEntry, int, int]:
    start_time = time.time()
    
    prompt = f"""
Question: {example.question}
Gold Answer: {example.gold_answer}
Failure Reason from Evaluator: {judge.reason}
Missing Evidence: {judge.missing_evidence}
Spurious Claims: {judge.spurious_claims}

Analyze this failure and provide a reflection for attempt {attempt_id}.
"""
    
    response = get_llm_response(REFLECTOR_SYSTEM + "\n" + prompt)
    latency = int((time.time() - start_time) * 1000)
    
    try:
        clean_content = response["content"].strip()
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:-3].strip()
        elif clean_content.startswith("```"):
            clean_content = clean_content[3:-3].strip()
            
        data = json.loads(clean_content)
        reflection = ReflectionEntry(attempt_id=attempt_id, **data)
    except Exception as e:
        reflection = ReflectionEntry(
            attempt_id=attempt_id,
            failure_reason=judge.reason,
            lesson="Failed to parse reflection JSON.",
            next_strategy="Try to be more careful and double check the context."
        )
        
    return reflection, response["total_tokens"], latency
