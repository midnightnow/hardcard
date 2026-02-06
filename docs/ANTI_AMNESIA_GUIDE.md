# The Anti-Amnesia Guide
> **How to Stop LLMs From Forgetting Their Reasoning**

## The Problem: The "Amnesia Loop"
Large Language Models (LLMs) are brilliant but ephemeral. They hallucinate because they lose the **chain of custody** on their own reasoning. 
You spend 20 minutes prompting a diagnosis, and 5 minutes later, it forgets *why* it reached that conclusion.

## The Solution: Hardcard Anchoring
Hardcard provides a "Save Point" for logic. By hashing the reasoning chain, you create an immutable anchor that forces the model to realign with the truth.

### Step 1: Anchor the Breakthrough
When the AI makes a critical decision (e.g., a diagnosis, a code architecture choice), **anchor it immediately**.

```bash
hardcard anchor "Decision: Use Ed25519 for agent keys to ensure self-sovereignty."
```

### Step 2: The "Hardcard" Artifact
The system generates a JSON object (a "Hardcard"):
```json
{
  "t_stamp": 1738481303,
  "h_logic": "a1b2c3d4...",
  "p_prev": "00000000...",
  "content": "Decision: Use Ed25519 for agent keys..."
}
```

### Step 3: Rehydrate (The Cure)
When the LLM starts drifting or halluncinating, paste the **Verification Block** back into the context:

> "System Alert: Realign logic to Hardcard Anchor [a1b2c3d4]. Verified Truth: Use Ed25519."

**Result:** The model snaps back to the anchored reality. No more amnesia.

---
*Part of the Hardcard Sovereign Framework.*
