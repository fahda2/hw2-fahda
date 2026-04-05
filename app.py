import anthropic
import json
import os
import sys

# Config
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You are an AI policy communication specialist.
Given a raw AI policy excerpt, produce three summaries:

1. EMPLOYEE VERSION: Plain language, 2-3 sentences, no jargon. Start with a clear action ("Do this" / "Don't do that"). Never say "you don't need to take action."
2. MANAGER VERSION: Use 3-4 bullet points. Each bullet = one concrete responsibility or enforcement action for the manager. No vague language.
3. EXECUTIVE VERSION: 2-3 sentences. No jargon. State what the policy requires, then name a specific risk (e.g., regulatory fine, data breach, lawsuit) if ignored. Flag if legal review is recommended.

Format your response exactly like this:
EMPLOYEE: [summary]
MANAGER:
- [bullet]
- [bullet]
- [bullet]
EXECUTIVE: [summary]

If the input is empty or unclear, respond with: ERROR: Input is empty or unreadable. Human review required."""

def run_eval(policy_text, case_id="manual"):
    if not policy_text.strip():
        print(f"\n[Case {case_id}] Empty input detected.")
        print("ERROR: Input is empty or unreadable. Human review required.")
        return

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"POLICY TEXT:\n{policy_text}"}]
    )

    print(f"\n{'='*50}")
    print(f"CASE {case_id}")
    print(f"{'='*50}")
    print(f"INPUT: {policy_text[:100]}...")
    print(f"\nOUTPUT:\n{response.content[0].text}")

def run_all_evals():
    with open("eval_set.json") as f:
        cases = json.load(f)

    for case in cases:
        run_eval(case["input"], case_id=case["id"])

    print("\n\nAll eval cases complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--eval":
        run_all_evals()
    else:
        print("Enter policy text (press Enter twice to submit):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        policy_text = " ".join(lines)
        run_eval(policy_text)
