#!/usr/bin/env python3
"""
Custom Sonnet Generator for Heidi Adams
=======================================
Creates a beautiful Shakespearean sonnet about Heidi Adams with tropical flower imagery
"""

def generate_heidi_sonnet():
    """Generate a custom sonnet for Heidi Adams"""
    
    sonnet_lines = [
        "Sweet Heidi Adams, like a tropic bloom,",
        "Whose fragrance drifts on gentle evening air,", 
        "Unassuming beauty in exotic room,",
        "With elegant grace beyond compare.",
        "",
        "Well-traveled soul with sophisticated heart,", 
        "From distant shores her wisdom flows,",
        "Each cultured word a perfect art,",
        "Like jasmine scent that softly glows.",
        "",
        "Her kindness blooms in every glance,",
        "Natural beauty, poised and refined,",
        "In her presence, hearts advance,",
        "To peaceful joy, so well-defined.",
        "",
        "  Like flowers fair that charm from far,",
        "  Sweet Heidi shines, our guiding star."
    ]
    
    return "\n".join(sonnet_lines)

def main():
    print("\n" + "🌺" * 25)
    print("A SONNET FOR HEIDI ADAMS".center(50))
    print("Tropical Flower Imagery | Golden Ratio Inspired")
    print("🌺" * 25 + "\n")
    
    sonnet = generate_heidi_sonnet()
    print(sonnet)
    
    print("\n" + "🌺" * 25)
    print("Like a tropical flower's sweet perfume,")
    print("Heidi's grace fills every room")
    print("🌺" * 25 + "\n")

if __name__ == "__main__":
    main()