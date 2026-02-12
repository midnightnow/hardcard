#!/usr/bin/env python3
"""
HARDCARD ANCHOR SERVICE
=======================
Service that listens for VetSorcery Revenue Events and anchors them
to the Hardcard Spiral (L0 Trust Protocol).

In a real environment, this would consume a Pub/Sub queue.
For v3.0, it scans a directory for new invoice JSONs.
"""

import sys
import os
import time
import json
import hashlib
from datetime import datetime

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VET_INVOICE_DIR = os.path.join(os.path.dirname(BASE_DIR), "vetsorcery", "data", "invoices")

# Ensure directory exists
os.makedirs(VET_INVOICE_DIR, exist_ok=True)

class AnchorService:
    def __init__(self):
        self.processed = set()
        print(f"⚓️ Hardcard Anchor Service started.")
        print(f"   Watching: {VET_INVOICE_DIR}")
        
    def run(self):
        while True:
            self.scan()
            time.sleep(5)
            
    def scan(self):
        # Scan for .json files
        files = [f for f in os.listdir(VET_INVOICE_DIR) if f.endswith('.json')]
        
        for f in files:
            if f not in self.processed:
                self.process_invoice(f)
                self.processed.add(f)
                
    def process_invoice(self, filename):
        filepath = os.path.join(VET_INVOICE_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Create Hardcard Anchor
            amount = data.get('total', 0)
            client = data.get('client_id', 'anon')
            
            # Hash content
            content_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            
            # Simulate "Minting" a Solid Node
            print(f"\n🧱 NEW SOLID NODE MINTED")
            print(f"   Source: VetSorcery (L3)")
            print(f"   Value: ${amount}")
            print(f"   Hash: {content_hash[:16]}...")
            print(f"   Status: ANCHORED to Spiral")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

if __name__ == "__main__":
    service = AnchorService()
    service.run()
