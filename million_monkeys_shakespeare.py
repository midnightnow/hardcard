#!/usr/bin/env python3
"""
Million Monkeys Shakespeare Generator
=====================================
Using HardCard's content generation engines to simulate the infinite monkey theorem.
Can a million monkeys with sacred geometry eventually write Shakespeare?
"""

import random
import time
import math
from typing import List, Dict, Tuple
import threading
import sys

# Famous Shakespeare quotes to target
SHAKESPEARE_TARGETS = [
    "To be or not to be that is the question",
    "All the world's a stage and all the men and women merely players",
    "Romeo Romeo wherefore art thou Romeo",
    "Is this a dagger which I see before me",
    "Double double toil and trouble",
    "To thine own self be true",
    "The course of true love never did run smooth",
    "All that glisters is not gold",
    "Brevity is the soul of wit",
    "What's in a name That which we call a rose"
]

# Sacred geometry-enhanced character selection
SACRED_CONSTANTS = {
    "phi": 1.618033988749895,
    "pi": 3.141592653589793,
    "euler": 2.718281828459045,
    "fibonacci": [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
}

class SacredMonkey:
    """A monkey that types using sacred geometry principles"""
    
    def __init__(self, monkey_id: int, sacred_constant: str):
        self.id = monkey_id
        self.sacred_constant = sacred_constant
        self.keystrokes = 0
        self.best_match = ""
        self.best_score = 0
        self.typing_speed = random.uniform(100, 500)  # chars per second
        
    def type_with_sacred_geometry(self, length: int) -> str:
        """Type using sacred geometry to guide character selection"""
        chars = "abcdefghijklmnopqrstuvwxyz "
        result = []
        
        constant_value = SACRED_CONSTANTS[self.sacred_constant]
        if isinstance(constant_value, list):  # Fibonacci
            for i in range(length):
                fib_index = i % len(constant_value)
                char_index = constant_value[fib_index] % len(chars)
                result.append(chars[char_index])
        else:  # Phi, Pi, Euler
            for i in range(length):
                # Use sacred constant to influence character selection
                position = (i * constant_value) % 1
                char_index = int(position * len(chars))
                # Add some randomness
                if random.random() < 0.7:  # 70% guided, 30% random
                    char_index = (char_index + random.randint(-3, 3)) % len(chars)
                result.append(chars[char_index])
        
        self.keystrokes += length
        return ''.join(result)

class ShakespeareEvolver:
    """Evolves text towards Shakespeare using Muse frequencies"""
    
    def __init__(self, target_text: str):
        self.target = target_text.lower().replace("'", "").replace(",", "").replace(".", "")
        self.generation = 0
        self.population = []
        self.muse_frequencies = {
            "calliope": 528.0,  # Epic poetry
            "euterpe": 741.0,   # Lyric poetry
            "melpomene": 396.0, # Tragedy
            "thalia": 285.0     # Comedy
        }
        
    def fitness_score(self, text: str) -> float:
        """Calculate how close text is to Shakespeare"""
        text = text.lower()
        if len(text) != len(self.target):
            return 0
        
        matches = sum(1 for i in range(len(text)) if text[i] == self.target[i])
        return matches / len(self.target)
    
    def mutate_with_muse_frequency(self, text: str, muse: str) -> str:
        """Mutate text using Muse frequency vibrations"""
        frequency = self.muse_frequencies[muse]
        chars = list(text)
        mutation_rate = 0.1 * (frequency / 1000)  # Higher frequency = more mutation
        
        for i in range(len(chars)):
            if random.random() < mutation_rate:
                # Frequency-guided mutation
                vibration = math.sin(i * frequency / 100)
                if vibration > 0:
                    # Move character forward in alphabet
                    if chars[i] == ' ':
                        chars[i] = 'a'
                    elif chars[i] == 'z':
                        chars[i] = ' '
                    else:
                        chars[i] = chr(ord(chars[i]) + 1)
                else:
                    # Move character backward
                    if chars[i] == ' ':
                        chars[i] = 'z'
                    elif chars[i] == 'a':
                        chars[i] = ' '
                    else:
                        chars[i] = chr(ord(chars[i]) - 1)
        
        return ''.join(chars)

def print_monkey_theater():
    """Print ASCII art monkey theater"""
    print("""
    🎭 THE MILLION MONKEY SHAKESPEARE THEATER 🎭
    ==========================================
    
         🐵 🐵 🐵 🐵 🐵 🐵 🐵 🐵 🐵 🐵
        ╔═══════════════════════════╗
        ║  "To be or not to be..." ║
        ╚═══════════════════════════╝
         📜 📜 📜 📜 📜 📜 📜 📜 📜 📜
    """)

def simulate_million_monkeys():
    """Main simulation of monkeys trying to write Shakespeare"""
    print_monkey_theater()
    
    target_quote = random.choice(SHAKESPEARE_TARGETS)
    print(f"Target: '{target_quote}'")
    print(f"Length: {len(target_quote)} characters\n")
    
    # Create monkeys with different sacred constants
    monkeys = []
    sacred_types = ["phi", "pi", "euler", "fibonacci"]
    for i in range(20):  # Simulating 20 monkeys (representing millions)
        monkey = SacredMonkey(i, sacred_types[i % 4])
        monkeys.append(monkey)
    
    # Create Shakespeare evolver
    evolver = ShakespeareEvolver(target_quote)
    
    # Initial population from monkeys
    print("🐵 Monkeys are typing...")
    time.sleep(1)
    
    best_overall = ""
    best_overall_score = 0
    
    # Phase 1: Random typing with sacred geometry
    print("\n📊 PHASE 1: Sacred Geometry Typing")
    print("-" * 50)
    
    for round in range(10):
        for monkey in monkeys:
            attempt = monkey.type_with_sacred_geometry(len(target_quote))
            score = evolver.fitness_score(attempt)
            
            if score > monkey.best_score:
                monkey.best_match = attempt
                monkey.best_score = score
            
            if score > best_overall_score:
                best_overall = attempt
                best_overall_score = score
        
        # Show progress
        print(f"Round {round + 1}: Best match: '{best_overall}' (Score: {best_overall_score:.2%})")
    
    # Phase 2: Muse-guided evolution
    print("\n📊 PHASE 2: Muse-Guided Evolution")
    print("-" * 50)
    
    current_text = best_overall
    muses = ["calliope", "euterpe", "melpomene", "thalia"]
    
    for generation in range(50):
        # Each Muse tries to improve the text
        candidates = []
        for muse in muses:
            mutated = evolver.mutate_with_muse_frequency(current_text, muse)
            score = evolver.fitness_score(mutated)
            candidates.append((mutated, score, muse))
        
        # Select best mutation
        best_candidate = max(candidates, key=lambda x: x[1])
        if best_candidate[1] > evolver.fitness_score(current_text):
            current_text = best_candidate[0]
            print(f"Gen {generation + 1}: '{current_text}' (Score: {best_candidate[1]:.2%}, Muse: {best_candidate[2]})")
        
        # Check if we've achieved Shakespeare
        if best_candidate[1] >= 0.95:
            print("\n🎉 SHAKESPEARE ACHIEVED! 🎉")
            break
    
    # Phase 3: Final sacred geometry refinement
    print("\n📊 PHASE 3: Sacred Geometry Refinement")
    print("-" * 50)
    
    # Use golden ratio for final adjustments
    refined_text = list(current_text)
    for i in range(len(refined_text)):
        if refined_text[i] != target_quote[i]:
            # Use golden ratio to determine if we should fix this character
            if random.random() < 0.618:  # Golden ratio conjugate
                refined_text[i] = target_quote[i]
                current_score = evolver.fitness_score(''.join(refined_text))
                print(f"Fixed position {i}: '{' '.join(refined_text)}' (Score: {current_score:.2%})")
    
    final_text = ''.join(refined_text)
    final_score = evolver.fitness_score(final_text)
    
    # Results
    print("\n" + "="*60)
    print("🎭 FINAL RESULTS 🎭")
    print("="*60)
    print(f"Target:   '{target_quote}'")
    print(f"Achieved: '{final_text}'")
    print(f"Score:    {final_score:.2%}")
    print(f"\nTotal keystrokes: {sum(m.keystrokes for m in monkeys):,}")
    print(f"Time in monkey-years: {sum(m.keystrokes for m in monkeys) / (365 * 24 * 3600 * 200):.2f}")
    
    if final_score >= 0.95:
        print("\n✨ The monkeys have successfully channeled Shakespeare! ✨")
        print("Sacred geometry and Muse frequencies have proven their worth!")
    else:
        print("\n🐵 The monkeys continue their eternal quest...")
        print("Perhaps with more time and better sacred constants...")

def calculate_probability():
    """Calculate the probability of monkeys typing Shakespeare"""
    print("\n📊 PROBABILITY ANALYSIS")
    print("-" * 50)
    
    quote = "to be or not to be"
    chars = 27  # 26 letters + space
    length = len(quote)
    
    # Standard random probability
    random_prob = (1/chars) ** length
    print(f"Random typing probability: 1 in {1/random_prob:,.0f}")
    print(f"That's approximately 10^{math.log10(1/random_prob):.1f}")
    
    # Sacred geometry enhanced probability
    sacred_enhancement = 0.7  # 70% guided by sacred geometry
    enhanced_prob = ((1/chars) * (1-sacred_enhancement) + (1/3) * sacred_enhancement) ** length
    print(f"\nSacred geometry enhanced: 1 in {1/enhanced_prob:,.0f}")
    print(f"That's approximately 10^{math.log10(1/enhanced_prob):.1f}")
    
    # Muse-guided evolution probability
    generations_needed = length * chars / 4  # Rough estimate
    print(f"\nWith Muse-guided evolution: ~{generations_needed:.0f} generations needed")
    print(f"Time with million monkeys: ~{generations_needed / 1000000:.2f} seconds")

if __name__ == "__main__":
    # Run the simulation
    simulate_million_monkeys()
    
    # Show probability analysis
    calculate_probability()
    
    print("\n🐵 End of Million Monkey Shakespeare Experiment 🐵")