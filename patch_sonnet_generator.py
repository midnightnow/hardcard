#!/usr/bin/env python3
"""
Custom Sonnet Generator for Patch the Dog
=========================================
Creates a beautiful Shakespearean sonnet about Patch, Heidi's loyal brown companion
"""

def generate_patch_sonnet():
    """Generate a custom sonnet for Patch the dog"""
    
    sonnet_lines = [
        "Small Patch, who looks like collie brown and white,",
        "But Pomeranian and Chihuahua's blend,",
        "Brown spots around each eye shine bright,",
        "A tiny mix, Heidi's dearest friend.",
        "",
        "Through morning walks on tiny fluffy feet,",
        "Her spotted shadow, small but filled with sass,",
        "Part pom's soft fur, part chi's spirit sweet,",
        "His patchwork coat worn with such class.",
        "",
        "When moonlight casts its silver on the ground,",
        "His little form glows soft and fair,",
        "A pocket pup, the best that can be found,",
        "With brown-ringed eyes and patches everywhere.",
        "",
        "  Though collie-looking, he's a different breed,",
        "  Small Patch loves Heidi, fills her every need."
    ]
    
    return "\n".join(sonnet_lines)

def main():
    print("\n" + "🐕" * 25)
    print("A SONNET FOR PATCH THE DOG".center(50))
    print("Pomeranian x Chihuahua Mix | Collie Lookalike | Brown-Ringed Eyes | Pocket Pup")
    print("🐕" * 25 + "\n")
    
    sonnet = generate_patch_sonnet()
    print(sonnet)
    
    print("\n" + "🐕" * 25)
    print("Through sun and moon, through play and rest,")
    print("Patch loves his Heidi - faithful, blessed")
    print("🐕" * 25 + "\n")

if __name__ == "__main__":
    main()