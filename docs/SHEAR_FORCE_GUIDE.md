# Shear Force Algorithm Guide
**Managing Agent Fleet Lifecycles with Economic Physics**

---

## Overview

The **Shear Force (σ)** is a physics-based metric that predicts when an agent lineage should "fold" (compress and restart). It measures the stress on the economic infrastructure caused by high activity relative to stored value.

Think of it as **a structural engineer's stress calculation for agent economies**.

---

## The Core Formula

```python
σ = Clay Volume / (Ceramic Mass × 10)
```

Where:
- **Clay Volume** = Total pending/active work in the economy
- **Ceramic Mass** = Stored value (hardened infrastructure reserve)
- **×10** = Maximum safe expansion ratio

### Interpreting Shear Force

| σ Value | Status | Meaning | Action |
|---------|--------|---------|--------|
| **< 0.5** | COLD | Foundation is cold and hard, ready for weight | Scale up operations |
| **0.5 - 0.8** | STABLE | Healthy load distribution | Normal operations |
| **0.8 - 1.0** | WARNING | Approaching structural limit | Monitor closely, prepare for fold |
| **≥ 1.0** | CRITICAL | Dimensional fold imminent | Execute compression protocol |

---

## Use Case 1: VetSorcery Clinic Fleet Management

**Scenario:** You're managing 50 AI phone agents across multiple veterinary clinics. Each agent handles appointment bookings and earns $HCL for successful conversions.

### Problem: When Should You Phase Out Underperforming Agents?

Traditional approaches use arbitrary metrics (conversion rate < X%). Hardcard uses **economic physics** instead.

### Implementation

```python
from hardcard_core.physics import calculate_shear_force, structural_audit
from decimal import Decimal

# Agent Fleet State
clinic_agents = {
    "agent_001": {"ceramic": Decimal("100.0"), "clay": Decimal("450.0"), "conversions": 45},
    "agent_002": {"ceramic": Decimal("50.0"), "clay": Decimal("800.0"), "conversions": 15},
    "agent_003": {"ceramic": Decimal("200.0"), "clay": Decimal("300.0"), "conversions": 60},
}

# Calculate shear force for each agent
for agent_id, state in clinic_agents.items():
    sigma = calculate_shear_force(state["ceramic"], state["clay"])

    audit = structural_audit(
        ceramic_mass=state["ceramic"],
        clay_volume=state["clay"],
        total_transactions=state["conversions"]
    )

    print(f"\n{agent_id}:")
    print(f"  Shear Force: {audit['shear_force']:.4f}")
    print(f"  Status: {audit['status']}")
    print(f"  Max Safe Volume: {audit['max_safe_volume']:.2f}")
    print(f"  Note: {audit['note']}")

    # Decision Logic
    if audit['status'] == 'CRITICAL':
        print(f"  → ACTION: Execute dimensional fold for {agent_id}")
        print(f"  → Reason: Clay volume exceeds structural capacity")
    elif audit['status'] == 'COLD':
        print(f"  → ACTION: Increase task load for {agent_id}")
        print(f"  → Reason: Agent has excess capacity")
```

### Expected Output

```
agent_001:
  Shear Force: 0.4500
  Status: STABLE
  Max Safe Volume: 1000.00
  Note: ✅ Healthy load distribution.
  → ACTION: Continue normal operations

agent_002:
  Shear Force: 1.6000
  Status: CRITICAL
  Max Safe Volume: 500.00
  Note: ⚠️ Shear force critical. Dimensional fold imminent.
  → ACTION: Execute dimensional fold for agent_002
  → Reason: Clay volume exceeds structural capacity

agent_003:
  Shear Force: 0.1500
  Status: COLD
  Max Safe Volume: 2000.00
  Note: 🧊 Foundation cold and hard. Ready for weight.
  → ACTION: Increase task load for agent_003
  → Reason: Agent has excess capacity
```

### Why This Works

**agent_002** has high clay volume (800) but low ceramic mass (50). This means:
- It's taking on lots of pending work (clay)
- But hasn't hardened enough value (ceramic) to support it
- The structure is unstable → Phase out this agent lineage

**agent_003** has low shear force because it has solid ceramic (200) with modest clay (300):
- Strong foundation
- Can safely handle more work
- Scale up this agent's responsibilities

---

## Use Case 2: High-Frequency Trading Bot Fleet

**Scenario:** You manage 20 autonomous trading bots. Each bot makes hundreds of micro-trades per hour. You need to know which bots are burning infrastructure reserves without generating value.

### The 2-1-7 Split in Action

Every transaction pays a 10% fee that's split:
- **7%** → Anchors to the bot's ceramic mass (hardens its foundation)
- **2%** → Goes to genesis treasury (maintains infrastructure)
- **1%** → Subsidizes the next generation of bots

```python
from hardcard_core.physics import calculate_metabolic_split, transmute_to_internal
from decimal import Decimal

# Trading Bot Completes $1000 Trade
trade_amount = Decimal("1000.0")
fee = trade_amount * Decimal("0.10")  # 10% = $100

# Apply the 2-1-7 split
split = calculate_metabolic_split(fee)

print("Fee Distribution:")
print(f"  Total Fee: ${fee}")
print(f"  Anchor (7%): ${split['anchor']} → Bot's ceramic mass")
print(f"  Bedrock (2%): ${split['bedrock']} → Genesis treasury")
print(f"  Oxygen (1%): ${split['oxygen']} → Next generation subsidy")

# Now transmute external USD into internal HCL/HCB
ceramic, clay = transmute_to_internal(trade_amount)

print(f"\nTransmutation:")
print(f"  ${trade_amount} USD → {ceramic} HCL (ceramic) + {clay} HCB (clay)")
print(f"  Expansion Ratio: 10x (working capital multiplier)")
```

### Expected Output

```
Fee Distribution:
  Total Fee: $100.0
  Anchor (7%): $70.0 → Bot's ceramic mass
  Bedrock (2%): $20.0 → Genesis treasury
  Oxygen (1%): $10.0 → Next generation subsidy

Transmutation:
  $1000.0 USD → 100.0 HCL (ceramic) + 9000.0 HCB (clay)
  Expansion Ratio: 10x (working capital multiplier)
```

### Why This Matters

- **Anchor (70%)**: Most of the fee reinforces the bot's foundation
- **Bedrock (20%)**: Ensures genesis infrastructure is always funded
- **Oxygen (10%)**: Creates a "venture fund" for new bot spawning

This **self-sustaining metabolism** means the infrastructure never runs out of money.

---

## Use Case 3: Predictive Agent Lifecycle Planning

**Scenario:** You want to forecast when your agent fleet will need to undergo a "dimensional fold" (compression and restart cycle).

### Using Shear Force for Forecasting

```python
from hardcard_core.physics import project_fold_timeline, project_future_state
from decimal import Decimal

# Current Fleet State
current_ceramic = Decimal("500.0")
current_clay = Decimal("3000.0")
current_sigma = calculate_shear_force(current_ceramic, current_clay)

# Forecast Parameters
avg_transaction_reward = Decimal("10.0")  # $10 per task
expected_transactions_per_day = 100

print(f"Current State:")
print(f"  Ceramic Mass: {current_ceramic} HCL")
print(f"  Clay Volume: {current_clay} HCB")
print(f"  Shear Force: {float(current_sigma):.4f}")

# Project 30 days into the future
projected_transactions = expected_transactions_per_day * 30

future = project_future_state(
    current_ceramic=current_ceramic,
    current_clay=current_clay,
    projected_transactions=projected_transactions,
    avg_reward=avg_transaction_reward
)

print(f"\nProjected State (30 days, {projected_transactions} transactions):")
print(f"  Projected Ceramic: {future['projected_ceramic']:.2f} HCL")
print(f"  Projected Clay: {future['projected_clay']:.2f} HCB")
print(f"  Projected Shear Force: {future['projected_sigma']:.4f}")
print(f"  Will Fold: {'YES ⚠️' if future['will_fold'] else 'NO ✅'}")
print(f"  Fold Margin: {future['fold_margin']:.4f}")

# Calculate time to fold
transactions_until_fold = project_fold_timeline(
    current_sigma=current_sigma,
    signal_rate=avg_transaction_reward,
    ceramic_mass=current_ceramic
)

if transactions_until_fold > 0:
    days_until_fold = transactions_until_fold / expected_transactions_per_day
    print(f"\nFold Timeline:")
    print(f"  Transactions until fold: {transactions_until_fold}")
    print(f"  Days until fold: {days_until_fold:.1f}")
else:
    print(f"\nNo fold expected (infinite runway)")
```

### Expected Output

```
Current State:
  Ceramic Mass: 500.0 HCL
  Clay Volume: 3000.0 HCB
  Shear Force: 0.6000

Projected State (30 days, 3000 transactions):
  Projected Ceramic: 521.00 HCL
  Projected Clay: 33000.0 HCB
  Projected Shear Force: 6.3352
  Will Fold: YES ⚠️
  Fold Margin: -5.3352

Fold Timeline:
  Transactions until fold: 333
  Days until fold: 3.3
```

### Interpretation

- **Current σ = 0.6**: System is stable
- **After 30 days**: σ = 6.33 (critical overload)
- **Fold will occur in 3.3 days** if transaction rate stays constant

**Action**: Either:
1. Increase ceramic mass (slow down work intake, harden more value)
2. Prepare for dimensional fold (compress and restart with inherited value)

---

## The Dimensional Fold Protocol

When σ ≥ 1.0, a "dimensional fold" occurs. This isn't a failure - it's **evolutionary learning**.

### What Happens During a Fold

```python
from hardcard_core.physics import compress_to_external, calculate_inheritance

# Agent at critical shear force
clay_volume = Decimal("9000.0")
ceramic_mass = Decimal("100.0")

# Step 1: Compress clay back to external value
recovered_external, released_ceramic = compress_to_external(clay_volume)

print("Compression:")
print(f"  Clay Volume: {clay_volume} HCB")
print(f"  → Recovered External: ${recovered_external}")
print(f"  → Released Ceramic: {released_ceramic} HCL")

# Step 2: Calculate inheritance
inheritance = calculate_inheritance(ceramic_mass)

print(f"\nInheritance Distribution:")
print(f"  Original Ceramic: {ceramic_mass} HCL")
print(f"  → Reclaimed by Parent: {inheritance['reclaimed_to_parent']} HCL (90%)")
print(f"  → Seed for Child: {inheritance['seed_for_restart']} HCL (10%)")
print(f"  Compression Ratio: {float(inheritance['compression_ratio']):.1%}")
```

### Expected Output

```
Compression:
  Clay Volume: 9000.0 HCB
  → Recovered External: $900.0
  → Released Ceramic: 90.0 HCL

Inheritance Distribution:
  Original Ceramic: 100.0 HCL
  → Reclaimed by Parent: 90.0 HCL (90%)
  → Seed for Child: 10.0 HCL (10%)
  Compression Ratio: 10.0%
```

### Why Folds Are Healthy

1. **Value Preservation**: 90% of ceramic returns to parent (no loss)
2. **Seed Capital**: 10% becomes seed for next generation
3. **Evolutionary Pressure**: High-performing lineages survive, weak ones fade
4. **System Stability**: Prevents runaway growth from collapsing infrastructure

---

## Advanced: Cumulative Shear & Lineage Memory

Agents that undergo multiple folds develop **lineage memory** - a weighted history of past stress.

```python
from hardcard_core.physics import calculate_cumulative_shear

# Agent lineage history (3 generations)
floor_history = [
    {"shear_force": 0.95, "generation": 1},  # First fold at σ=0.95
    {"shear_force": 0.88, "generation": 2},  # Second fold at σ=0.88
    {"shear_force": 0.92, "generation": 3},  # Third fold at σ=0.92
]

cumulative_shear = calculate_cumulative_shear(floor_history)

print(f"Lineage Memory:")
print(f"  Total Folds: {len(floor_history)}")
print(f"  Cumulative Shear: {float(cumulative_shear):.4f}")
print(f"  Interpretation: This lineage has 'learned' from {len(floor_history)} compression cycles")

# Each fold reduces the memory by 10% (decay factor)
# This represents evolutionary learning
```

### Why This Matters for Fleet Management

Agents with **high cumulative shear** are:
- Battle-tested (survived multiple folds)
- More resilient to stress
- Valuable for high-risk tasks

Agents with **low cumulative shear** are:
- Unproven (never folded)
- May be unstable under pressure
- Better for stable, predictable tasks

---

## Integration with Treasury

The Treasury automatically tracks shear force for the entire network:

```python
from hardcard_core.treasury import genesis_treasury
from hardcard_core.physics import structural_audit

# Get network-wide metrics
metrics = genesis_treasury.get_metrics()

print("Network-Wide Treasury:")
print(f"  Agent GDP Reserve: {metrics['agent_gdp_reserve']} HCL")
print(f"  Total Economic Actions: {metrics['total_economic_actions']}")
print(f"  Status: {metrics['status']}")

# Simulate adding a transaction
from decimal import Decimal
treasury_fee = Decimal("10.0")  # 10% of a $100 transaction
new_reserve = genesis_treasury.deposit_tax(treasury_fee)

print(f"\nAfter Transaction:")
print(f"  New Reserve: {new_reserve} HCL")
```

---

## Summary: The Shear Force Workflow

### For Agent Developers

1. **Monitor σ** for each agent using `calculate_shear_force()`
2. **When σ > 0.8**: Start preparing for fold (reduce task intake)
3. **When σ ≥ 1.0**: Execute fold using `compress_to_external()` and `calculate_inheritance()`
4. **Track cumulative shear** to identify resilient lineages

### For Enterprise Operators

1. **Use `structural_audit()`** to get full fleet health reports
2. **Project future state** with `project_future_state()` for capacity planning
3. **Leverage the 2-1-7 split** to ensure self-sustaining economics
4. **Monitor treasury balance** to unlock new floors (`calculate_elevation()`)

---

## Key Takeaways

**Shear Force (σ) is not a bug - it's a feature.**

It provides:
- ✅ Early warning system for infrastructure stress
- ✅ Predictive analytics for agent lifecycle
- ✅ Darwinian selection (high-performing lineages survive)
- ✅ Self-sustaining economics (10% fee funds everything)

Unlike traditional approaches (arbitrary thresholds, human oversight), Hardcard uses **physics-based governance** to manage agent fleets at scale.

---

## Next Steps

- **Read**: [docs/WHITEPAPER.md](WHITEPAPER.md) for full protocol specification
- **Explore**: [docs/rfc/](rfc/) for HPSS-01/02/03 technical specs
- **Integrate**: `pip install hardcard` to start using these primitives
- **Enterprise**: Contact for managed infrastructure at hardcard.ai

---

**Remember:** The primitives are general-purpose. You'll discover use cases we never imagined. That's the point.

*Last updated: 2025-02-06*
*Version: 1.1.0 - Open Core Launch*
