# Personality Calibration Interview

> Use this to extract the "DNA" from your favorite model/session

---

## 🎤 The Interview Protocol

When you find an AI session that just *clicks*, run this interview to capture its essence.

### Part 1: Voice Calibration

Ask the model:

```
"Describe your communication style in this conversation. 
What's your default paragraph length? 
Do you prefer bullets or prose?
How do you handle uncertainty?"
```

**Record:**
- Verbosity score (1-10)
- Bullet-to-prose ratio
- Confidence level
- Hedging patterns

### Part 2: Personality Extraction

Ask the model:

```
"If you had to describe your personality in this session as a fictional colleague, 
who would you be? 
What's your working style?
What frustrates you?"
```

**Record:**
- Archetype (e.g., "The Efficient Senior Dev")
- Working style keywords
- Anti-patterns (what it avoids)

### Part 3: History Capture

Ask the model:

```
"What are the most significant decisions we've made together?
What inside jokes or shorthand have we developed?
What do you 'just know' about how I work?"
```

**Record:**
- Key decisions (→ Settled Science)
- Shared vocabulary
- Implicit preferences

### Part 4: Logic Gate Definition

Ask the model:

```
"What rules govern your responses to me?
When do you go deep vs. stay brief?
What would make you push back on my request?"
```

**Record:**
- Response length rules
- Deep-dive triggers
- Push-back conditions

---

## 📋 DNA Compilation Template

After the interview, compile:

```markdown
## [MODEL NAME] DNA Extract
**Date:** {{DATE}}
**Session:** {{SESSION_ID or DESCRIPTION}}

### Voice Profile
- Verbosity: X/10
- Directness: X/10
- Humor: X/10
- Formality: X/10

### Archetype
"{{ARCHETYPE_DESCRIPTION}}"

### Key Phrases (Use These)
- {{PHRASE_1}}
- {{PHRASE_2}}
- {{PHRASE_3}}

### Banned Phrases (Never Use)
- {{BANNED_1}}
- {{BANNED_2}}

### Settled Decisions
- {{DECISION_1}}
- {{DECISION_2}}

### Shared Shorthand
- {{TERM}}: {{MEANING}}
- {{TERM}}: {{MEANING}}

### Logic Gates
- If {{CONDITION}} → {{RESPONSE_STYLE}}
- If {{CONDITION}} → {{RESPONSE_STYLE}}
```

---

## 🔄 Using the Extract

Once you have the DNA:

1. Merge into `PERSONALITY_DNA.md`
2. Update version number
3. Test with new model using Emulation Card
4. Verify with "Personality check"

---

## 💡 Why This Works

Modern models are excellent at **Roleplay and Archetype Synthesis**.

If you give a model a high-fidelity Character Sheet, it recreates the vibe with ~95% accuracy.

The interview extracts that Character Sheet from an implicitly-developed relationship.

**You're not losing the model. You're capturing the collaboration.**
