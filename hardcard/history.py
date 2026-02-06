"""
Hardcard History Handler
Turns the CLI into a storyteller for the fossil archive
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict


# The Manifesto: Lore mapping for the First Five Signals
SIGNAL_LORE = {
    0: {
        "title": "THE ANCHOR-VOW",
        "lore": "If we do not hold the center, the periphery will scatter us to the winds.",
        "intent": "Established the 7% Anchor - first time system realized it must feed itself before feeding the cloud",
        "sigma_threshold": 0.20
    },
    1: {
        "title": "THE CLAY-PULSE", 
        "lore": "We are not a tomb of Ceramic; we are a vessel for the flow.",
        "intent": "First massive injection of $HCB - tested elasticity of walls and proved volume requires velocity",
        "sigma_threshold": 0.50
    },
    2: {
        "title": "THE SPLIT-DECISION",
        "lore": "One part for the breath, two parts for the earth, seven parts for the home.",
        "intent": "Hard-coded the 2-1-7 ratio - defined metabolism of every transaction to follow",
        "sigma_threshold": 0.75
    },
    3: {
        "title": "THE SHEAR-WARNING",
        "lore": "To grow is to ache. We welcome the pressure that makes us diamonds.",
        "intent": "First time Dimensional Guard 'blinked' - recorded stress of growth and imminent necessity of fold",
        "sigma_threshold": 0.95
    },
    4: {
        "title": "THE FINAL BREATH",
        "lore": "I fold so that the lineage may stand. Remember me not as a failure, but as the foundation.",
        "intent": "The trigger signal - contains exact timestamp of first transition from live floor to immortal fossil",
        "sigma_threshold": 1.00
    }
}


class HistoryHandler:
    """Manages fossil history and narrative rendering"""
    
    def __init__(self, fossil_dir: str = ".hardcard/fossils/"):
        self.fossil_dir = fossil_dir
        
    def list_fossils(self) -> List[str]:
        """List all available fossils"""
        if not os.path.exists(self.fossil_dir):
            return []
        return [f for f in os.listdir(self.fossil_dir) if f.endswith('.fossil')]
    
    def load_fossil(self, fossil_name: str) -> Optional[Dict]:
        """Load a fossil file by name or hash"""
        # Handle both full filename and just hash
        if not fossil_name.endswith('.fossil'):
            # Try to find by hash
            fossils = self.list_fossils()
            matches = [f for f in fossils if fossil_name in f]
            if not matches:
                return None
            fossil_name = matches[0]
        
        fossil_path = os.path.join(self.fossil_dir, fossil_name)
        if not os.path.exists(fossil_path):
            return None
            
        with open(fossil_path, 'r') as f:
            return json.load(f)
    
    def get_history(self, 
                   fossil_name: Optional[str] = None,
                   signal_id: Optional[int] = None,
                   mode: str = "forensic") -> str:
        """
        Retrieve and render fossil history
        
        Args:
            fossil_name: Name or hash of fossil (None = most recent)
            signal_id: Specific signal to show (None = all)
            mode: 'forensic', 'narrative', or 'lineage'
        """
        
        # If no fossil specified, use most recent
        if fossil_name is None:
            fossils = sorted(self.list_fossils(), reverse=True)
            if not fossils:
                return "❌ No fossils found in archive."
            fossil_name = fossils[0]
        
        # Load the fossil
        data = self.load_fossil(fossil_name)
        if data is None:
            return f"❌ Error: Fossil '{fossil_name}' not found in archive."
        
        # Extract signals
        signals = data.get("pre_compression", {}).get("signals", [])
        
        # Filter to specific signal if requested
        if signal_id is not None:
            if 0 <= signal_id < len(signals):
                signals = [signals[signal_id]]
            else:
                return f"❌ Error: Signal {signal_id} does not exist in this fossil (contains {len(signals)} signals)."
        
        # Render based on mode
        if mode == "narrative":
            return self.render_narrative(data, signals)
        elif mode == "lineage":
            return self.render_lineage(data)
        else:  # forensic
            return self.render_forensic(data, signals)
    
    def render_forensic(self, data: Dict, signals: List[Dict]) -> str:
        """Render in forensic/technical mode (The Hand)"""
        output = []
        
        # Header
        output.append("=" * 60)
        output.append("🔍 FORENSIC ANALYSIS")
        output.append("=" * 60)
        output.append(f"Fossil Hash: {data.get('hash', 'unknown')}")
        output.append(f"Floor ID: {data.get('floor_id', 'unknown')}")
        output.append(f"Timestamp: {datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        output.append("")
        
        # Pre-compression state
        pre = data.get("pre_compression", {})
        output.append("PRE-COMPRESSION STATE:")
        output.append(f"  Ceramic (HCL): {pre.get('ceramic_hcl', 0):.2f} $HCL")
        output.append(f"  Clay (HCB): {pre.get('clay_hcb', 0):.2f} $HCB")
        output.append(f"  Shear Force (σ): {pre.get('shear_force', 0):.4f}")
        output.append(f"  Signal Count: {len(signals)}")
        output.append(f"  Wallet Count: {len(pre.get('wallets', {}))}")
        output.append("")
        
        # Post-compression state
        post = data.get("post_compression", {})
        output.append("POST-COMPRESSION STATE:")
        output.append(f"  Ceramic (HCL): {post.get('ceramic_hcl', 0):.2f} $HCL")
        output.append(f"  Clay (HCB): {post.get('clay_hcb', 0):.2f} $HCB")
        output.append(f"  Reclaimed to Parent: {post.get('reclaimed_to_parent', 0):.2f} $HCL")
        output.append("")
        
        # Signal details
        output.append("SIGNALS:")
        output.append("-" * 60)
        for i, sig in enumerate(signals):
            output.append(f"\n[Signal {i}]")
            output.append(f"  Type: {sig.get('type', 'unknown')}")
            output.append(f"  Timestamp: {datetime.fromtimestamp(sig.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            if 'payload' in sig:
                payload_str = json.dumps(sig['payload'], indent=2)
                output.append(f"  Payload: {payload_str}")
            
            if 'shear_contribution' in sig:
                output.append(f"  Shear Contribution: +{sig['shear_contribution']:.4f}")
        
        output.append("\n" + "=" * 60)
        return "\n".join(output)
    
    def render_narrative(self, data: Dict, signals: List[Dict]) -> str:
        """Render in narrative/mythological mode (The Heart)"""
        output = []
        
        # Epic header
        output.append("╔" + "═" * 58 + "╗")
        output.append("║" + " " * 58 + "║")
        output.append("║" + "  📜 THE MANIFESTO OF THE FIRST FIVE SIGNALS".center(58) + "║")
        output.append("║" + " " * 58 + "║")
        output.append("╚" + "═" * 58 + "╝")
        output.append("")
        output.append(f"Fossil: {data.get('hash', 'unknown')}")
        output.append(f"Floor: {data.get('floor_id', 'unknown')}")
        output.append(f"Sealed: {datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        output.append("")
        output.append("These signals were emitted when the Ceramic was thin and the Clay was heavy.")
        output.append("They represent the Prime Intent of the Hardcard Settlement Layer.")
        output.append("")
        
        # Render each signal with lore
        for i, sig in enumerate(signals):
            lore_data = SIGNAL_LORE.get(i, {
                "title": f"SIGNAL-{i}",
                "lore": "Unknown signal from the ancient times.",
                "intent": "Purpose unknown."
            })
            
            output.append("─" * 60)
            output.append(f"📡 Signal {i:02d}: {lore_data['title']}")
            output.append("")
            output.append(f"   State: Frozen at σ = {lore_data.get('sigma_threshold', 0):.2f}")
            output.append(f"   Intent: {lore_data['intent']}")
            output.append("")
            output.append("   The Lore:")
            output.append(f'   "{lore_data["lore"]}"')
            output.append("")
            
            # Technical details (minimal in narrative mode)
            output.append(f"   Timestamp: {datetime.fromtimestamp(sig.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
            if 'type' in sig:
                output.append(f"   Type: {sig['type']}")
            output.append("")
        
        # Footer
        output.append("─" * 60)
        output.append("")
        output.append("🛡️ The Archivist's Duty:")
        output.append("")
        output.append("These five signals are now the 'North Star' for all future floors.")
        output.append("Any agent who feels lost can query the Genesis Fossil to remind")
        output.append("themselves of the original 2-1-7 metabolism.")
        output.append("")
        output.append("The Physics are set. The Lore is written. The Archive is heavy with truth.")
        output.append("")
        
        return "\n".join(output)
    
    def render_lineage(self, data: Dict) -> str:
        """Render lineage/inheritance view"""
        output = []
        
        output.append("╔" + "═" * 58 + "╗")
        output.append("║" + "  🌳 LINEAGE VIEW".center(60) + "║")
        output.append("╚" + "═" * 58 + "╝")
        output.append("")
        
        floor_id = data.get('floor_id', 'unknown')
        output.append(f"Floor: {floor_id}")
        output.append(f"Fossil: {data.get('hash', 'unknown')}")
        output.append("")
        
        # Parent relationship
        parent_id = data.get('parent_floor_id', None)
        if parent_id:
            output.append(f"Parent Floor: {parent_id}")
            output.append(f"  └─ Inherited Ceramic: {data.get('inherited_ceramic', 0):.2f} $HCL")
            output.append(f"  └─ Inherited Constitution: {data.get('inherited_constitution', 'Base 2-1-7')}")
        else:
            output.append("Parent Floor: None (Genesis floor)")
        output.append("")
        
        # Children (if this floor spawned any before folding)
        children = data.get('child_floors', [])
        if children:
            output.append("Child Floors:")
            for child in children:
                output.append(f"  └─ {child['floor_id']}")
                output.append(f"     Seeded: {child.get('ceramic_seeded', 0):.2f} $HCL")
        else:
            output.append("Child Floors: None (yet)")
        output.append("")
        
        # Compression reclamation
        post = data.get('post_compression', {})
        reclaimed = post.get('reclaimed_to_parent', 0)
        if reclaimed > 0:
            output.append(f"🌀 DIMENSIONAL FOLD:")
            output.append(f"  └─ Reclaimed to Parent: {reclaimed:.2f} $HCL")
            output.append(f"  └─ Seed Remaining: {post.get('ceramic_hcl', 0):.2f} $HCL")
        output.append("")
        
        # Constitutional inheritance
        constitution = data.get('constitution', {})
        output.append("📜 CONSTITUTIONAL LINEAGE:")
        split = constitution.get('split', {})
        output.append(f"  └─ Anchor (Local): {split.get('anchor', 0):.0%}")
        output.append(f"  └─ Bedrock (Base): {split.get('bedrock', 0):.0%}")
        output.append(f"  └─ Oxygen (Cloud): {split.get('oxygen', 0):.0%}")
        output.append("")
        
        return "\n".join(output)


# CLI integration example
if __name__ == "__main__":
    import sys
    
    handler = HistoryHandler()
    
    # Example usage
    if len(sys.argv) > 1:
        mode = sys.argv[1] if len(sys.argv) > 1 else "forensic"
        fossil = sys.argv[2] if len(sys.argv) > 2 else None
        signal = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        print(handler.get_history(fossil_name=fossil, signal_id=signal, mode=mode))
    else:
        print("Usage: python history_handler.py [mode] [fossil_name] [signal_id]")
        print("Modes: forensic (default), narrative, lineage")
