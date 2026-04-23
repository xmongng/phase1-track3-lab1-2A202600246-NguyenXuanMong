# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpotqa_100_samples.json
- Mode: mock
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.9 | 0.99 | 0.09 |
| Avg attempts | 1 | 1.12 | 0.12 |
| Avg token estimate | 2117.02 | 2487.99 | 370.97 |
| Avg latency (ms) | 3375.48 | 4304.91 | 929.43 |

## Failure modes
```json
{
  "react": {
    "none": 90,
    "wrong_final_answer": 10
  },
  "reflexion": {
    "none": 99,
    "wrong_final_answer": 1
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- adaptive_max_attempts

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. By using an adaptive max attempts strategy, we give the agent more chances to recover if it's close to the right answer. The reflection memory is highly useful in preventing the agent from repeating the exact same spurious claims. However, failure modes like wrong_final_answer can still remain if the LLM evaluator is unable to parse complex context properly or if the model hallucinates.
