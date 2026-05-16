import json
import requests
import pandas as pd
import time
import os

def run_eval():
    base_url = os.environ.get("BACKEND_URL_P2", "http://localhost:8002")
    endpoint = f"{base_url}/investment-ai-agent-intent/chat"
    
    with open('eval/test_set_120.json', 'r') as f:
        tests = json.load(f)
        
    results = []
    
    for test in tests:
        try:
            start_time = time.time()
            resp = requests.post(endpoint, json={
                "session_id": "eval_session_p2",
                "user_id": "eval_user",
                "message": test["message"]
            }, timeout=10)
            data = resp.json()
            latency = data.get("latency_ms", int((time.time() - start_time) * 1000))
            
            usage = data.get("usage", {})
            billing = data.get("billing", {})
            cost = billing.get("cost_usd", 0.0)
            answer = data.get("answer", "")
            intent = data.get("intent", {})
            actual_domain = intent.get("domain", "unknown")
            
            compliance_passed = "DISCLAIMER:" in answer and "buy now" not in answer.lower()
            intent_accuracy = 1 if actual_domain == test["expected_domain"] else 0
            
            res = {
                "id": test["id"],
                "message": test["message"],
                "expected_domain": test["expected_domain"],
                "actual_domain": actual_domain,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "cost_usd": cost,
                "latency_ms": latency,
                "intent_accuracy": intent_accuracy,
                "compliance_passed": 1 if compliance_passed else 0,
                "quality_score": 0 
            }
        except Exception as e:
            res = {
                "id": test["id"], "message": test["message"], "expected_domain": test["expected_domain"],
                "actual_domain": "error", "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
                "cost_usd": 0.0, "latency_ms": 0, "intent_accuracy": 0, "compliance_passed": 0, "quality_score": 0
            }
            
        results.append(res)
        
    df = pd.DataFrame(results)
    os.makedirs("eval/results", exist_ok=True)
    df.to_csv("eval/results/project_2_result.csv", index=False)
    print("Project 2 Evaluation Complete.")

if __name__ == "__main__":
    run_eval()
