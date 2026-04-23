# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpotqa_100_samples.json
- Mode: mock
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.91 | 0.99 | 0.08 |
| Avg attempts | 1 | 1.14 | 0.14 |
| Avg token estimate | 2113.43 | 2547.21 | 433.78 |
| Avg latency (ms) | 3612.23 | 4514.48 | 902.25 |

## Failure modes
```json
{
  "react": {
    "none": 91,
    "entity_drift": 4,
    "incomplete_multi_hop": 5
  },
  "reflexion": {
    "none": 99,
    "entity_drift": 1
  },
  "overall_failures": {
    "entity_drift": 5,
    "incomplete_multi_hop": 5
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
