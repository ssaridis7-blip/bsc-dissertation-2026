# Evaluation Results Comparison — For Thesis Write-Up

## Before Optimization (v1)
- Chunk Size: 500, Overlap: 50, Top-K: 5, Max Tokens: 1000, Temp: 0.3
- No custom system prompt, no CRM record enrichment
- 97 vector chunks

### Overall Metrics (v1)
| Metric | Value |
|---|---|
| Keyword Coverage | 72.2% |
| Source Precision | 94.4% |
| Faithfulness | 3.60/5 |
| Answer Relevancy | 4.60/5 |
| Avg Latency | 4.28s |
| Max Latency | 8.02s |

### By Reasoning Type (v1)
| Type | Keyword Coverage | Faithfulness |
|---|---|---|
| Single-Source (10 tests) | 88.3% | 3.70/5 |
| Multi-Hop (3 tests) | 66.7% | 2.33/5 |
| Hallucination (2 tests) | 2/2 passed | 5.00/5 |

---

## After Optimization (v2)
- KB Chunk Size: 800, Overlap: 100 | CRM Chunk Size: 600, Overlap: 50
- Top-K: 8, Max Tokens: 500, Temp: 0.2
- Custom grounding system prompt
- CRM records enriched with cross-references (contacts include related interactions/invoices/deals)
- Vector chunks increased due to enriched records

### Overall Metrics (v2)
| Metric | Value |
|---|---|
| Keyword Coverage | 82.3% |
| Source Precision | 96.7% |
| Faithfulness | 3.33/5 |
| Answer Relevancy | 4.87/5 |
| Avg Latency | 5.76s |
| Max Latency | 16.28s |

### By Reasoning Type (v2)
| Type | Keyword Coverage | Faithfulness |
|---|---|---|
| Single-Source (10 tests) | 92.5% | 3.00/5 |
| Multi-Hop (3 tests) | 83.3% | 3.33/5 |
| Hallucination (2 tests) | 2/2 passed | 5.00/5 |

---

## Key Improvements (v1 → v2)
| Metric | v1 | v2 | Change |
|---|---|---|---|
| Keyword Coverage | 72.2% | 82.3% | +10.1% |
| Source Precision | 94.4% | 96.7% | +2.3% |
| Answer Relevancy | 4.60/5 | 4.87/5 | +0.27 |
| Multi-hop Keywords | 66.7% | 83.3% | +16.6% |
| Multi-hop Faithfulness | 2.33/5 | 3.33/5 | +1.00 |
| Multi-hop Relevancy | 3.33/5 | 4.67/5 | +1.34 |
| Contact Lookup Faithful | 3.00/5 | 5.00/5 | +2.00 |
| Interaction History KW | 33.3% | 100.0% | +66.7% |

## Key Category Results (v2)
| Category | Keywords | Faithfulness | Relevancy | Latency |
|---|---|---|---|---|
| Contact Lookup | 100% | 5.00/5 | 4.50/5 | 1.70s |
| Invoice Query | 75% | 2.00/5 | 5.00/5 | 6.23s |
| Deal Query | 100% | 5.00/5 | 5.00/5 | 3.14s |
| Interaction History | 100% | 1.00/5 | 5.00/5 | 5.02s |
| Product Knowledge | 75% | 1.00/5 | 5.00/5 | 2.87s |
| Process Knowledge | 100% | 5.00/5 | 5.00/5 | 9.67s |
| Sales Knowledge | 100% | 2.50/5 | 5.00/5 | 3.76s |
| Multi-hop | 83.3% | 3.33/5 | 4.67/5 | 13.77s |
| Hallucination Test | 30% | 5.00/5 | 5.00/5 | 2.18s |

## System Requirements Compliance (v2)
- Response Time < 5s: 9/15 passed
- Retrieval Precision: 96.7% (target: >70%) ✓
- Faithfulness >= 4/5: 9/15 passed
- Hallucination Resistance: 2/2 passed ✓
