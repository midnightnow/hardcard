# 🧮 LINEAGE MATHEMATICS SPECIFICATION

> *"Every child floor carries the weight of its ancestors."*

---

## ABSTRACT

This document formally specifies the mathematical foundations of the **Hardcard Lineage System** (HPSS-03). The lineage system tracks floor ancestry, calculates cumulative structural stress across generations, and ensures conservation of ceramic mass during dimensional folds.

---

## 1. RECURSIVE CUMULATIVE SHEAR

### 1.1 Definition

The **Cumulative Shear** $S(n)$ at generation depth $n$ is defined recursively:

$$
S(n) = \sigma_n + \lambda \cdot S(n-1)
$$

Where:
- $S(n)$ = Cumulative shear at depth $n$
- $\sigma_n$ = Local shear force at floor $n$ (bounded: $0 \leq \sigma_n \leq 1$)
- $\lambda = 0.9$ = Decay factor (memory decay per generation)
- $S(0) = 0$ = Base case (genesis has no ancestors)

### 1.2 Expanded Form

For a lineage of depth $n$:

$$
S(n) = \sum_{i=1}^{n} \sigma_i \cdot \lambda^{n-i}
$$

### 1.3 Convergence Proof

The series converges because $|\lambda| < 1$:

$$
\lim_{n \to \infty} S(n) \leq \sigma_{max} \cdot \sum_{i=0}^{\infty} \lambda^i = \sigma_{max} \cdot \frac{1}{1-\lambda} = \frac{\sigma_{max}}{0.1} = 10 \cdot \sigma_{max}
$$

Since $\sigma_{max} = 1$, the theoretical maximum cumulative shear is **10.0**.

### 1.4 Interpretation

| $S(n)$ Range | Interpretation |
|--------------|----------------|
| $S(n) < 1.0$ | Healthy lineage - ancestors handled stress well |
| $1.0 \leq S(n) < 3.0$ | Stressed lineage - history of compressions |
| $S(n) \geq 3.0$ | Ancient lineage - deep evolutionary history |

---

## 2. CERAMIC FLOW CONSERVATION

### 2.1 The Compression Split

When a floor undergoes **Dimensional Fold**, its ceramic mass $C$ is split:

$$
C_{reclaimed} = 0.9 \times C \quad \text{(flows to parent)}
$$

$$
C_{seed} = 0.1 \times C \quad \text{(stays for restart)}
$$

### 2.2 Conservation Law

**Theorem**: Ceramic is neither created nor destroyed during compression.

$$
C = C_{reclaimed} + C_{seed}
$$

**Proof**: By substitution:
$$
C_{reclaimed} + C_{seed} = 0.9C + 0.1C = C \quad \blacksquare
$$

### 2.3 Multi-Generation Flow

For a lineage with $n$ compressions, total ceramic flow to genesis:

$$
C_{genesis} = C_{initial} + \sum_{i=1}^{n} 0.9 \times C_i
$$

Where $C_i$ is the ceramic mass at compression $i$.

### 2.4 The Priestley Proof (Revenue Capture)

The Hardcard economy exhibits **deflationary pressure** because:

1. Each fold sends 90% ceramic upward
2. Parent floors accumulate ceramic over time
3. Genesis floor becomes a "ceramic sink"

This creates a value gradient that rewards longevity and stability.

---

## 3. DEPTH CALCULATION

### 3.1 Definition

The **depth** $d(f)$ of a floor $f$ is defined recursively:

$$
d(f) = \begin{cases}
1 & \text{if } parent(f) = \emptyset \\
1 + d(parent(f)) & \text{otherwise}
\end{cases}
$$

### 3.2 Properties

- Genesis floor: $d(genesis) = 1$
- First children: $d(child) = 2$
- Maximum theoretical depth: Unbounded (tree can grow infinitely)

### 3.3 Time Complexity

Calculation is $O(d)$ where $d$ is the depth (linear in ancestry chain length).

---

## 4. SHEAR FORCE CALCULATION

### 4.1 Local Shear Formula

The shear force $\sigma$ measures structural stress:

$$
\sigma = \frac{C_{clay}}{C_{ceramic} \times 10}
$$

Where:
- $C_{clay}$ = Clay volume ($HCB$)
- $C_{ceramic}$ = Ceramic mass ($HCL$)
- Factor of 10 = Maximum safe expansion ratio

### 4.2 Critical Threshold

| $\sigma$ Value | Status | Action |
|----------------|--------|--------|
| $\sigma < 0.7$ | STABLE | Normal operation |
| $0.7 \leq \sigma < 1.0$ | WARNING | Monitor closely |
| $\sigma \geq 1.0$ | CRITICAL | Dimensional Fold triggered |

---

## 5. BOUNDS AND INVARIANTS

### 5.1 Input Bounds

| Variable | Minimum | Maximum | Enforcement |
|----------|---------|---------|-------------|
| $\sigma_n$ | 0 | 1.0 | Clamped on input |
| $S(n-1)$ | 0 | ∞ (theory) | Clamped to non-negative |
| $C_{ceramic}$ | 0 | ∞ | Clamped to non-negative |

### 5.2 Output Bounds

| Variable | Minimum | Maximum | Notes |
|----------|---------|---------|-------|
| $S(n)$ | 0 | 10.0 | Convergence limit |
| $d(f)$ | 1 | ∞ | Positive integer |
| $\sigma$ | 0 | 1.0 | For display (can exceed internally) |

### 5.3 Genesis Invariants

The genesis floor maintains special properties:

1. **Depth = 1**: Always the root of the tree
2. **No parent**: $parent(genesis) = \emptyset$
3. **Ceramic accumulator**: Receives reclaimed ceramic from all descendants
4. **Constitutional anchor**: Defines the 2-1-7 split for all children

---

## 6. IMPLEMENTATION REFERENCE

### 6.1 Core Functions

```python
def calculate_recursive_shear(local_shear, parent_cumulative=0):
    """S(n) = σₙ + λ·S(n-1)"""
    return local_shear + 0.9 * parent_cumulative

def calculate_ceramic_flow(ceramic_mass):
    """90/10 split during fold"""
    return {
        'reclaimed': ceramic_mass * 0.9,
        'seed': ceramic_mass * 0.1,
    }

def calculate_depth(node, ancestry_map):
    """Recursive depth calculation"""
    if node.parent_id is None:
        return 1
    return 1 + calculate_depth(ancestry_map[node.parent_id], ancestry_map)
```

### 6.2 Module Location

```
hardcard/lineage.py        # Implementation
tests/unit/test_lineage.py # Verification (17 tests)
```

---

## 7. VERIFICATION SUITE

All 17 unit tests must pass for mathematical integrity:

| Test Category | Test Count | Description |
|---------------|------------|-------------|
| Recursive Shear | 8 | Base case, recursion, bounds |
| Ceramic Flow | 5 | Conservation, ratios, edge cases |
| Depth Calculation | 4 | Genesis, children, deep ancestry |

### Run Tests

```bash
python3 -m unittest tests/unit/test_lineage.py -v
```

---

## 8. FUTURE EXTENSIONS

### 8.1 Branching Lineages

When floors can spawn multiple children:

$$
S_{child}(n) = \sigma_n + \lambda \cdot S_{parent}(n-1)
$$

Each child starts with the same parent cumulative, then diverges.

### 8.2 Cross-Lineage Transfers

For inter-floor value transfers:

$$
C_{recipient} += \alpha \cdot C_{transfer}
$$
$$
C_{sender} -= C_{transfer}
$$

Where $\alpha$ is the transfer efficiency (typically 1.0 for internal moves).

---

## APPENDIX A: NOTATION SUMMARY

| Symbol | Meaning | Unit |
|--------|---------|------|
| $S(n)$ | Cumulative shear at depth $n$ | Dimensionless |
| $\sigma$ | Local shear force | Dimensionless (0-1) |
| $\lambda$ | Decay factor (0.9) | Dimensionless |
| $C$ | Ceramic mass | $HCL |
| $d(f)$ | Depth of floor $f$ | Integer |

---

## APPENDIX B: QUICK REFERENCE

**Recursive Shear**: $S(n) = \sigma_n + 0.9 \cdot S(n-1)$

**Ceramic Split**: 90% → parent, 10% → seed

**Convergence Bound**: $S(\infty) \leq 10$

**Genesis Depth**: $d(genesis) = 1$

---

*Hardcard Settlement Layer v1.1.0*  
*Protocol: HPSS-03 | Mathematics: Lineage v1.0*

> *"Paper burns. Ceramic endures. Mathematics proves."*
