import json
from agent_prompts import prompts

# ===== CONFIG =====
INPUT_FILE = "policy_dataset.jsonl"      # your current dataset
OUTPUT_FILE = "updated_policy_dataset.jsonl"

NEW_INSTRUCTION = "..."
# ===== PROCESS =====
with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    for line in infile:
        item = json.loads(line)

        # Replace instruction
        item["instruction"] = NEW_INSTRUCTION

        # Write updated entry
        outfile.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"Updated dataset saved to: {OUTPUT_FILE}")
