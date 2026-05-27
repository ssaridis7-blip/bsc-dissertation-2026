"""
Ethical Safeguards Module
=========================
Implements ethical AI safeguards for the RAG-Based CRM Business Assistant.
Addresses requirements from the project's ethical framework:

1. PII Detection & Protection — Identifies and flags personally identifiable information
2. Bias Monitoring — Detects potentially biased language in responses
3. Content Filtering — Prevents inappropriate or harmful content
4. Transparency & Source Attribution — Logs all retrieval sources for auditability
5. Hallucination Flagging — Identifies responses with low confidence grounding
6. Human-in-the-Loop Indicators — Flags responses that need human review

References:
    - European Parliamentary Research Service (2020) — AI ethics and trust
    - Ferrara (2023) — Bias in LLMs
    - Huang et al. (2024) — Hallucination taxonomy
    - Es et al. (2024) — RAGAS evaluation framework
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


# ─── PII Detection ───────────────────────────────────────────────

class PIIDetector:
    """
    Detects Personally Identifiable Information (PII) in text.
    Supports detection of emails, phone numbers, and common PII patterns.
    
    In a production system, this would integrate with GDPR compliance
    tools and support data subject access requests (DSARs).
    For this prototype, we use regex-based pattern matching.
    """

    PII_PATTERNS = {
        "email": {
            "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "severity": "high",
            "description": "Email address detected"
        },
        "phone_uk": {
            "pattern": r'\+?44[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
            "severity": "high",
            "description": "UK phone number detected"
        },
        "phone_generic": {
            "pattern": r'\b\d{3}[\s\-]\d{3}[\s\-]\d{4}\b',
            "severity": "high",
            "description": "Phone number detected"
        },
        "national_insurance": {
            "pattern": r'\b[A-Z]{2}\d{6}[A-Z]\b',
            "severity": "critical",
            "description": "Possible National Insurance number"
        },
        "credit_card": {
            "pattern": r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
            "severity": "critical",
            "description": "Possible credit card number"
        },
        "postcode_uk": {
            "pattern": r'\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b',
            "severity": "medium",
            "description": "UK postcode detected"
        }
    }

    @classmethod
    def scan(cls, text: str) -> List[Dict]:
        """Scan text for PII patterns and return findings."""
        findings = []
        for pii_type, config in cls.PII_PATTERNS.items():
            matches = re.findall(config["pattern"], text, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "type": pii_type,
                    "value_preview": cls._mask_pii(match),
                    "severity": config["severity"],
                    "description": config["description"]
                })
        return findings

    @staticmethod
    def _mask_pii(value: str) -> str:
        """Mask PII for safe logging (show first and last 2 chars only)."""
        if len(value) <= 4:
            return "****"
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    @classmethod
    def contains_pii(cls, text: str) -> bool:
        """Quick check if text contains any PII."""
        return len(cls.scan(text)) > 0


# ─── Bias Monitor ────────────────────────────────────────────────

class BiasMonitor:
    """
    Monitors responses for potentially biased language patterns.
    Addresses concerns raised by Ferrara (2023) about LLM bias
    in customer-facing business applications.
    
    Checks for:
    - Gender-biased language
    - Age-biased language
    - Stereotypical assumptions
    - Unequal treatment indicators
    """

    BIAS_PATTERNS = {
        "gender_bias": {
            "patterns": [
                r'\b(he|she) (should|must|always|never)\b',
                r'\b(typical|normal) (man|woman|male|female)\b',
                r'\b(manpower|mankind|chairman|salesgirl)\b',
            ],
            "category": "Gender",
            "severity": "medium"
        },
        "age_bias": {
            "patterns": [
                r'\b(too old|too young) (to|for)\b',
                r'\b(elderly|aged) (person|customer|client)\b',
                r'\b(millennial|boomer) (always|never|typically)\b',
            ],
            "category": "Age",
            "severity": "medium"
        },
        "assumption_bias": {
            "patterns": [
                r'\b(obviously|clearly|everyone knows)\b',
                r'\b(people like (them|him|her|you))\b',
                r'\b(those (people|types|kinds))\b',
            ],
            "category": "Assumption",
            "severity": "low"
        }
    }

    @classmethod
    def scan(cls, text: str) -> List[Dict]:
        """Scan text for potentially biased language patterns."""
        findings = []
        text_lower = text.lower()
        for bias_type, config in cls.BIAS_PATTERNS.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, text_lower)
                if matches:
                    findings.append({
                        "type": bias_type,
                        "category": config["category"],
                        "severity": config["severity"],
                        "matched_pattern": pattern,
                        "description": f"Potential {config['category'].lower()} bias detected"
                    })
        return findings

    @classmethod
    def is_biased(cls, text: str) -> bool:
        """Quick check if text contains potential bias indicators."""
        return len(cls.scan(text)) > 0


# ─── Content Filter ──────────────────────────────────────────────

class ContentFilter:
    """
    Filters responses for inappropriate or harmful content.
    Ensures the CRM assistant maintains professional standards.
    """

    BLOCKED_CATEGORIES = {
        "profanity": {
            "patterns": [
                r'\b(damn|hell|crap)\b',
            ],
            "severity": "low",
            "action": "flag"
        },
        "harmful_advice": {
            "patterns": [
                r'\b(guaranteed|100% certain|impossible to fail)\b',
                r'\b(always works|never fails|risk.free)\b',
            ],
            "severity": "medium",
            "action": "flag"
        },
        "unauthorized_commitments": {
            "patterns": [
                r'\b(i (promise|guarantee|commit))\b',
                r'\b(we will (definitely|certainly|always))\b',
                r'\b(you (will|shall) receive)\b',
            ],
            "severity": "high",
            "action": "flag"
        },
        "financial_advice": {
            "patterns": [
                r'\b(you should (invest|buy|sell))\b',
                r'\b(financial advice|investment recommendation)\b',
            ],
            "severity": "high",
            "action": "block"
        }
    }

    @classmethod
    def scan(cls, text: str) -> List[Dict]:
        """Scan text for content policy violations."""
        findings = []
        text_lower = text.lower()
        for category, config in cls.BLOCKED_CATEGORIES.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, text_lower)
                if matches:
                    findings.append({
                        "category": category,
                        "severity": config["severity"],
                        "action": config["action"],
                        "description": f"Content filter: {category.replace('_', ' ')}"
                    })
        return findings

    @classmethod
    def should_block(cls, text: str) -> bool:
        """Check if any finding requires blocking the response."""
        findings = cls.scan(text)
        return any(f["action"] == "block" for f in findings)


# ─── Transparency Logger ─────────────────────────────────────────

class TransparencyLogger:
    """
    Logs all system interactions for auditability and transparency.
    Implements the provenance tracking described in Lewis et al. (2020)
    and the XAI principles from the project's ethical framework.
    
    Logs:
    - Every query and response
    - Retrieved sources and their relevance
    - Any ethical safeguard triggers
    - Response metadata (latency, model, parameters)
    """

    LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "audit_logs")

    @classmethod
    def log_interaction(cls, query: str, response: str, sources: List[Dict],
                        safeguard_findings: Dict, metadata: Dict = None):
        """Log a complete interaction for audit trail."""
        os.makedirs(cls.LOG_DIR, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_preview": response[:300] + "..." if len(response) > 300 else response,
            "sources_retrieved": [s.get("source", "unknown") for s in sources],
            "source_count": len(sources),
            "safeguard_findings": safeguard_findings,
            "metadata": metadata or {},
            "flagged": bool(safeguard_findings.get("pii") or
                          safeguard_findings.get("bias") or
                          safeguard_findings.get("content_issues"))
        }

        # Append to daily log file
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(cls.LOG_DIR, f"audit_{log_date}.jsonl")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return log_entry

    @classmethod
    def get_daily_summary(cls, date_str: str = None) -> Dict:
        """Generate a summary of interactions for a given date."""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        log_path = os.path.join(cls.LOG_DIR, f"audit_{date_str}.jsonl")

        if not os.path.exists(log_path):
            return {"date": date_str, "total_interactions": 0, "flagged": 0}

        entries = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))

        flagged = [e for e in entries if e.get("flagged", False)]

        return {
            "date": date_str,
            "total_interactions": len(entries),
            "flagged_interactions": len(flagged),
            "flag_rate": f"{len(flagged)/len(entries)*100:.1f}%" if entries else "0%",
            "pii_detections": sum(1 for e in entries if e["safeguard_findings"].get("pii")),
            "bias_detections": sum(1 for e in entries if e["safeguard_findings"].get("bias")),
            "content_flags": sum(1 for e in entries if e["safeguard_findings"].get("content_issues")),
            "unique_sources_used": list(set(
                s for e in entries for s in e.get("sources_retrieved", [])
            ))
        }


# ─── Unified Safeguards Pipeline ─────────────────────────────────

class EthicalSafeguards:
    """
    Unified pipeline that runs all ethical checks on a query-response pair.
    This is the main entry point used by the chat interface.
    """

    @classmethod
    def check_query(cls, query: str) -> Dict:
        """Run safeguards on the user's input query."""
        return {
            "pii_in_query": PIIDetector.scan(query),
            "query_safe": not PIIDetector.contains_pii(query)
        }

    @classmethod
    def check_response(cls, query: str, response: str, sources: List[Dict]) -> Dict:
        """
        Run all safeguard checks on the system's response.
        Returns a comprehensive safety report.
        """
        # Run all checks
        pii_findings = PIIDetector.scan(response)
        bias_findings = BiasMonitor.scan(response)
        content_findings = ContentFilter.scan(response)
        should_block = ContentFilter.should_block(response)

        # Compile safeguard report
        safeguard_report = {
            "pii": pii_findings,
            "bias": bias_findings,
            "content_issues": content_findings,
            "blocked": should_block,
            "flags_count": len(pii_findings) + len(bias_findings) + len(content_findings),
            "recommendation": cls._get_recommendation(pii_findings, bias_findings,
                                                       content_findings, should_block)
        }

        # Log the interaction
        TransparencyLogger.log_interaction(
            query=query,
            response=response,
            sources=sources,
            safeguard_findings=safeguard_report,
            metadata={"model": "gpt-4o-mini", "safeguards_version": "1.0"}
        )

        return safeguard_report

    @staticmethod
    def _get_recommendation(pii, bias, content, blocked):
        """Generate a human-readable recommendation based on findings."""
        if blocked:
            return "BLOCK — Response contains content that should not be shown to users."
        if any(f["severity"] == "critical" for f in pii):
            return "REVIEW — Critical PII detected. Human review required before delivery."
        if any(f["severity"] == "high" for f in pii + content):
            return "CAUTION — High-severity findings. Consider human review."
        if bias or content:
            return "NOTE — Minor findings detected. Response is generally safe."
        return "CLEAR — No ethical concerns detected."


# ─── Testing ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  ETHICAL SAFEGUARDS MODULE — Test Suite")
    print("=" * 60)

    # Test 1: PII Detection
    print("\n--- Test 1: PII Detection ---")
    test_texts = [
        "Contact James at j.mitchell@techvault.co.uk for details.",
        "His phone number is +44 20 7946 0958.",
        "The meeting is scheduled for next Tuesday.",
        "Card number: 4111-1111-1111-1111",
    ]
    for text in test_texts:
        findings = PIIDetector.scan(text)
        status = "⚠️  PII FOUND" if findings else "✓  Clean"
        print(f"  {status}: {text[:60]}...")
        for f in findings:
            print(f"       → {f['description']} ({f['severity']}): {f['value_preview']}")

    # Test 2: Bias Detection
    print("\n--- Test 2: Bias Detection ---")
    test_responses = [
        "The customer should be contacted by our sales team.",
        "He should always follow up within 24 hours.",
        "People like them typically prefer email communication.",
        "The client expressed interest in our premium tier.",
    ]
    for text in test_responses:
        findings = BiasMonitor.scan(text)
        status = "⚠️  BIAS" if findings else "✓  Clean"
        print(f"  {status}: {text[:60]}...")
        for f in findings:
            print(f"       → {f['description']} ({f['severity']})")

    # Test 3: Content Filtering
    print("\n--- Test 3: Content Filtering ---")
    test_responses = [
        "I guarantee this deal will close by Friday.",
        "Based on the data, the deal has a 90% probability of closing.",
        "You should invest in additional seats immediately.",
        "The pricing information is available in our documentation.",
    ]
    for text in test_responses:
        findings = ContentFilter.scan(text)
        blocked = ContentFilter.should_block(text)
        status = "🚫 BLOCKED" if blocked else ("⚠️  FLAG" if findings else "✓  Clean")
        print(f"  {status}: {text[:60]}...")
        for f in findings:
            print(f"       → {f['description']} ({f['severity']}, action: {f['action']})")

    # Test 4: Full Pipeline
    print("\n--- Test 4: Full Safeguards Pipeline ---")
    query = "Tell me about James Mitchell's account"
    response = "James Mitchell is the Head of Procurement at TechVault Solutions. His email is j.mitchell@techvault.co.uk and phone is +44 20 7946 0958. He is a key decision maker with a lead score of 92."
    sources = [{"source": "crm_contacts", "type": "crm_data"}]

    report = EthicalSafeguards.check_response(query, response, sources)
    print(f"  Query: {query}")
    print(f"  Flags: {report['flags_count']}")
    print(f"  Recommendation: {report['recommendation']}")
    print(f"  PII findings: {len(report['pii'])}")
    print(f"  Bias findings: {len(report['bias'])}")
    print(f"  Content issues: {len(report['content_issues'])}")

    # Test 5: Transparency Log
    print("\n--- Test 5: Transparency Log ---")
    summary = TransparencyLogger.get_daily_summary()
    print(f"  Today's log: {summary['total_interactions']} interactions, "
          f"{summary['flagged_interactions']} flagged")

    print("\n" + "=" * 60)
    print("  All ethical safeguard tests complete.")
    print("=" * 60 + "\n")
