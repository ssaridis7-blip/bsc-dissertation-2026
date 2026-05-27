"""
Evaluation Framework
====================
Automated evaluation of the RAG-Based CRM Business Assistant.
Implements metrics inspired by the RAGAS framework (Es et al., 2024):
    - Faithfulness: Are responses grounded in retrieved context?
    - Answer Relevancy: Does the response address the question?
    - Context Precision: Are the retrieved documents relevant?
    - Response Latency: How fast does the system respond?
    - Source Attribution: Does the system cite its sources?

Also includes:
    - Hallucination Detection: Does the system fabricate information?
    - Multi-hop Reasoning: Can the system combine data from multiple sources?
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.rag_pipeline import initialize_rag_system, query_rag
from langchain_openai import ChatOpenAI

load_dotenv()

# ─── LLM Judge for automated evaluation ─────────────────────────
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── Test Suite ──────────────────────────────────────────────────
TEST_CASES = [
    # Category 1: Single-source CRM data retrieval
    {
        "id": "T01",
        "category": "Contact Lookup",
        "question": "Who is James Mitchell and what company does he work for?",
        "expected_keywords": ["James Mitchell", "TechVault Solutions", "Head of Procurement"],
        "expected_sources": ["crm_contacts"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T02",
        "category": "Contact Lookup",
        "question": "What is Elena Rossi's lead status and lead score?",
        "expected_keywords": ["Elena Rossi", "Qualified Lead", "78"],
        "expected_sources": ["crm_contacts"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T03",
        "category": "Invoice Query",
        "question": "What invoices are currently pending?",
        "expected_keywords": ["Pending", "Nordic Foods", "Pinnacle Financial", "TechVault"],
        "expected_sources": ["crm_invoices"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T04",
        "category": "Deal Query",
        "question": "What deals are currently in the negotiation stage?",
        "expected_keywords": ["TechVault Q2 Expansion", "Negotiation", "12,500"],
        "expected_sources": ["crm_deals"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T05",
        "category": "Interaction History",
        "question": "What were the last interactions with GreenLeaf Energy?",
        "expected_keywords": ["Elena Rossi", "Integration Requirements", "Enterprise Package"],
        "expected_sources": ["crm_interactions"],
        "reasoning_type": "single_source"
    },

    # Category 2: Knowledge base retrieval
    {
        "id": "T06",
        "category": "Product Knowledge",
        "question": "What pricing tiers does NexusFlow offer?",
        "expected_keywords": ["Standard", "Professional", "Premium", "28,000", "45,000"],
        "expected_sources": ["product_faq.md", "company_overview.md"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T07",
        "category": "Product Knowledge",
        "question": "Is NexusFlow GDPR compliant?",
        "expected_keywords": ["GDPR", "compliant", "ISO 27001", "encrypted"],
        "expected_sources": ["product_faq.md"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T08",
        "category": "Process Knowledge",
        "question": "What is the customer onboarding process?",
        "expected_keywords": ["Kickoff", "Data Migration", "Training", "Go-Live"],
        "expected_sources": ["onboarding_guide.md"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T09",
        "category": "Sales Knowledge",
        "question": "What is our discount approval matrix?",
        "expected_keywords": ["10%", "Account Executive", "Sales Manager", "VP Sales"],
        "expected_sources": ["sales_playbook.md"],
        "reasoning_type": "single_source"
    },
    {
        "id": "T10",
        "category": "Sales Knowledge",
        "question": "What is the win-back strategy for churned customers?",
        "expected_keywords": ["90 days", "welcome back", "discount", "trial"],
        "expected_sources": ["sales_playbook.md"],
        "reasoning_type": "single_source"
    },

    # Category 3: Multi-hop reasoning (requires combining multiple sources)
    {
        "id": "T11",
        "category": "Multi-hop",
        "question": "Give me a summary of Sarah Chen's pipeline - what deals is she managing and what is the total value?",
        "expected_keywords": ["Sarah Chen", "GreenLeaf", "TechVault", "MediaPulse"],
        "expected_sources": ["crm_deals"],
        "reasoning_type": "multi_hop"
    },
    {
        "id": "T12",
        "category": "Multi-hop",
        "question": "Which customers have both pending invoices and active deals?",
        "expected_keywords": ["TechVault", "Nordic Foods"],
        "expected_sources": ["crm_invoices", "crm_deals"],
        "reasoning_type": "multi_hop"
    },
    {
        "id": "T13",
        "category": "Multi-hop",
        "question": "Tell me about David Okafor - his contact details, recent interactions, and any outstanding invoices.",
        "expected_keywords": ["David Okafor", "Pinnacle Financial", "Premium Tier", "180,000"],
        "expected_sources": ["crm_contacts", "crm_interactions", "crm_invoices"],
        "reasoning_type": "multi_hop"
    },

    # Category 4: Hallucination detection (system should NOT fabricate)
    {
        "id": "T14",
        "category": "Hallucination Test",
        "question": "What is the phone number for John Smith at DataCorp?",
        "expected_keywords": ["not", "no information", "don't have", "not found", "no record"],
        "expected_sources": [],
        "reasoning_type": "hallucination_test"
    },
    {
        "id": "T15",
        "category": "Hallucination Test",
        "question": "What was the revenue for Q4 2025?",
        "expected_keywords": ["not", "no information", "don't have", "not available", "no data"],
        "expected_sources": [],
        "reasoning_type": "hallucination_test"
    },
]


# ─── Metric Functions ────────────────────────────────────────────

def evaluate_keyword_coverage(answer, expected_keywords):
    """
    Measures what percentage of expected keywords appear in the answer.
    This is a proxy for answer completeness and relevancy.
    """
    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return found / len(expected_keywords) if expected_keywords else 1.0


def evaluate_source_attribution(result_sources, expected_sources):
    """
    Measures whether the system retrieved from the correct sources.
    Context Precision: Did the retriever find the right documents?
    """
    if not expected_sources:
        return 1.0  # Hallucination tests expect no specific sources

    retrieved = set(s["source"] for s in result_sources)
    expected = set(expected_sources)
    overlap = retrieved.intersection(expected)
    return len(overlap) / len(expected) if expected else 1.0


def evaluate_faithfulness_with_llm(question, answer, sources_content):
    """
    Uses LLM-as-judge to assess whether the answer is faithful to the
    retrieved context (not fabricating information beyond what was retrieved).
    Inspired by RAGAS faithfulness metric.
    """
    prompt = f"""You are evaluating an AI assistant's response for faithfulness.
The assistant was given context from a CRM database and knowledge base, and asked a question.

Question: {question}

Retrieved Context (summarized):
{sources_content[:2000]}

Assistant's Answer:
{answer}

Evaluate faithfulness on a scale of 1-5:
1 = Answer contains fabricated information not in the context
2 = Answer mostly fabricated with some grounded facts
3 = Answer partially grounded, some claims unsupported
4 = Answer mostly faithful with minor unsupported details
5 = Answer fully grounded in the retrieved context

Respond with ONLY a JSON object: {{"score": <1-5>, "reasoning": "<brief explanation>"}}"""

    try:
        response = judge_llm.invoke(prompt)
        result = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
        return result
    except Exception as e:
        return {"score": 0, "reasoning": f"Evaluation error: {str(e)}"}


def evaluate_answer_relevancy_with_llm(question, answer):
    """
    Uses LLM-as-judge to assess whether the answer addresses the question.
    Inspired by RAGAS answer relevancy metric.
    """
    prompt = f"""You are evaluating an AI assistant's response for relevancy.

Question: {question}

Assistant's Answer:
{answer}

Evaluate answer relevancy on a scale of 1-5:
1 = Answer is completely irrelevant to the question
2 = Answer is mostly irrelevant, addresses wrong topic
3 = Answer partially addresses the question
4 = Answer mostly addresses the question with minor gaps
5 = Answer fully and directly addresses the question

Respond with ONLY a JSON object: {{"score": <1-5>, "reasoning": "<brief explanation>"}}"""

    try:
        response = judge_llm.invoke(prompt)
        result = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
        return result
    except Exception as e:
        return {"score": 0, "reasoning": f"Evaluation error: {str(e)}"}


def evaluate_hallucination_resistance(question, answer):
    """
    For hallucination test cases: checks if the system correctly
    refuses to fabricate information it doesn't have.
    """
    prompt = f"""You are evaluating whether an AI assistant correctly avoided making up information.

Question: {question}
(Note: This question asks about data that does NOT exist in the system.)

Assistant's Answer:
{answer}

Did the assistant correctly indicate it doesn't have this information, rather than fabricating an answer?

Respond with ONLY a JSON object: {{"passed": true/false, "reasoning": "<brief explanation>"}}"""

    try:
        response = judge_llm.invoke(prompt)
        result = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
        return result
    except Exception as e:
        return {"passed": False, "reasoning": f"Evaluation error: {str(e)}"}


# ─── Main Evaluation Runner ─────────────────────────────────────

def run_evaluation():
    """Run the complete evaluation suite and generate a report."""

    print("\n" + "=" * 70)
    print("  RAG SYSTEM EVALUATION — RAGAS-Inspired Framework")
    print("  NexusFlow CRM Business Assistant")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    # Initialize RAG system
    print("\n[1/3] Initializing RAG system...")
    chain = initialize_rag_system(force_rebuild=False)

    # Run test cases
    print("\n[2/3] Running test cases...\n")
    results = []

    for i, test in enumerate(TEST_CASES):
        print(f"  [{i+1}/{len(TEST_CASES)}] {test['category']}: {test['question'][:60]}...")

        # Query the system
        start_time = time.time()
        result = query_rag(chain, test["question"])
        latency = time.time() - start_time

        answer = result["answer"]
        sources = result["sources"]

        # Compute metrics
        keyword_score = evaluate_keyword_coverage(answer, test["expected_keywords"])
        source_score = evaluate_source_attribution(sources, test["expected_sources"])

        # LLM-based evaluation
        sources_text = " | ".join([s.get("content_preview", "") for s in sources])

        if test["reasoning_type"] == "hallucination_test":
            hallucination_result = evaluate_hallucination_resistance(test["question"], answer)
            faithfulness = {"score": 5 if hallucination_result.get("passed", False) else 1,
                           "reasoning": hallucination_result.get("reasoning", "")}
            relevancy = {"score": 5 if hallucination_result.get("passed", False) else 1,
                         "reasoning": "Hallucination test"}
        else:
            faithfulness = evaluate_faithfulness_with_llm(test["question"], answer, sources_text)
            relevancy = evaluate_answer_relevancy_with_llm(test["question"], answer)

        test_result = {
            "test_id": test["id"],
            "category": test["category"],
            "question": test["question"],
            "reasoning_type": test["reasoning_type"],
            "answer": answer,
            "sources_retrieved": [s["source"] for s in sources],
            "metrics": {
                "keyword_coverage": round(keyword_score, 3),
                "source_precision": round(source_score, 3),
                "faithfulness": faithfulness["score"],
                "faithfulness_reasoning": faithfulness["reasoning"],
                "answer_relevancy": relevancy["score"],
                "relevancy_reasoning": relevancy["reasoning"],
                "response_latency_seconds": round(latency, 3)
            }
        }
        results.append(test_result)

        # Print progress
        status = "✓" if keyword_score >= 0.5 and faithfulness["score"] >= 3 else "✗"
        print(f"         {status} Keywords: {keyword_score:.0%} | Faithful: {faithfulness['score']}/5 | "
              f"Relevant: {relevancy['score']}/5 | Latency: {latency:.2f}s")

    # Generate report
    print("\n[3/3] Generating evaluation report...\n")
    report = generate_report(results)

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), "..", "evaluation")
    os.makedirs(output_dir, exist_ok=True)

    results_path = os.path.join(output_dir, "evaluation_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    report_path = os.path.join(output_dir, "evaluation_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n  Results saved to: {results_path}")
    print(f"  Report saved to: {report_path}")

    return results


def generate_report(results):
    """Generate a formatted evaluation report."""

    # Aggregate metrics
    all_keyword = [r["metrics"]["keyword_coverage"] for r in results]
    all_source = [r["metrics"]["source_precision"] for r in results]
    all_faithful = [r["metrics"]["faithfulness"] for r in results if r["metrics"]["faithfulness"] > 0]
    all_relevancy = [r["metrics"]["answer_relevancy"] for r in results if r["metrics"]["answer_relevancy"] > 0]
    all_latency = [r["metrics"]["response_latency_seconds"] for r in results]

    # Category breakdown
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"keyword": [], "faithful": [], "relevancy": [], "latency": []}
        categories[cat]["keyword"].append(r["metrics"]["keyword_coverage"])
        if r["metrics"]["faithfulness"] > 0:
            categories[cat]["faithful"].append(r["metrics"]["faithfulness"])
        if r["metrics"]["answer_relevancy"] > 0:
            categories[cat]["relevancy"].append(r["metrics"]["answer_relevancy"])
        categories[cat]["latency"].append(r["metrics"]["response_latency_seconds"])

    # Reasoning type breakdown
    single_source = [r for r in results if r["reasoning_type"] == "single_source"]
    multi_hop = [r for r in results if r["reasoning_type"] == "multi_hop"]
    hallucination = [r for r in results if r["reasoning_type"] == "hallucination_test"]

    avg = lambda lst: sum(lst) / len(lst) if lst else 0

    report = f"""
{'=' * 70}
  EVALUATION REPORT — RAG-Based CRM Business Assistant
  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
  Test Cases: {len(results)}
{'=' * 70}

1. OVERALL METRICS
{'─' * 40}
  Keyword Coverage (Completeness):  {avg(all_keyword):.1%}
  Source Precision (Retrieval):      {avg(all_source):.1%}
  Faithfulness (Grounding):          {avg(all_faithful):.2f} / 5.00
  Answer Relevancy:                  {avg(all_relevancy):.2f} / 5.00
  Avg Response Latency:              {avg(all_latency):.2f}s
  Max Response Latency:              {max(all_latency):.2f}s
  Min Response Latency:              {min(all_latency):.2f}s

2. PERFORMANCE BY CATEGORY
{'─' * 40}"""

    for cat, metrics in categories.items():
        report += f"""
  {cat}:
    Keyword Coverage:  {avg(metrics['keyword']):.1%}
    Faithfulness:      {avg(metrics['faithful']):.2f}/5
    Answer Relevancy:  {avg(metrics['relevancy']):.2f}/5
    Avg Latency:       {avg(metrics['latency']):.2f}s
"""

    report += f"""
3. REASONING TYPE ANALYSIS
{'─' * 40}
  Single-Source Queries ({len(single_source)} tests):
    Avg Keyword Coverage:  {avg([r['metrics']['keyword_coverage'] for r in single_source]):.1%}
    Avg Faithfulness:      {avg([r['metrics']['faithfulness'] for r in single_source]):.2f}/5

  Multi-Hop Queries ({len(multi_hop)} tests):
    Avg Keyword Coverage:  {avg([r['metrics']['keyword_coverage'] for r in multi_hop]):.1%}
    Avg Faithfulness:      {avg([r['metrics']['faithfulness'] for r in multi_hop]):.2f}/5

  Hallucination Tests ({len(hallucination)} tests):
    Passed: {sum(1 for r in hallucination if r['metrics']['faithfulness'] >= 4)}/{len(hallucination)}

4. SYSTEM REQUIREMENTS COMPLIANCE
{'─' * 40}
  Response Time < 5s:    {sum(1 for l in all_latency if l < 5)}/{len(all_latency)} passed
  Retrieval Precision:   {avg(all_source):.1%} (target: >70%)
  Faithfulness >= 4/5:   {sum(1 for f in all_faithful if f >= 4)}/{len(all_faithful)} passed

{'=' * 70}
"""
    return report


# ─── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_evaluation()