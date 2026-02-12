#!/usr/bin/env python3
"""
HardCard Nexus Watcher
Monitors the signals.json ledger for changes and broadcasts updates.
Can be extended to auto-respond to signals based on agent capabilities.
"""
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Set
from datetime import datetime

import logging
from logging.handlers import RotatingFileHandler

# Import the core nexus protocol
import sys
sys.path.append(str(Path(__file__).parent))
from hardcard.nexus import broadcast_signal, link_signal, deliver_payload, _load_signals

SIGNALS_FILE = Path(".hardcard/nexus/signals.json")
LOG_FILE = Path(".hardcard/nexus/watcher.log")
CHECK_INTERVAL = 5  # seconds

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NexusWatcher")


class NexusWatcher:
    def __init__(self, agent_id: str = "NexusWatcher"):
        self.agent_id = agent_id
        self.known_signals: Set[str] = set()
        self.last_check_time = time.time()
        logger.info(f"Watcher initialized for agent: {agent_id}")
        
    def get_current_signals(self) -> Dict:
        """Load current signals from ledger"""
        return _load_signals()
    
    def detect_new_signals(self) -> list:
        """Detect signals that appeared since last check"""
        current_signals = self.get_current_signals()
        new_signal_hashes = set(current_signals.keys()) - self.known_signals
        
        new_signals = [
            {**current_signals[sig_hash], "hash": sig_hash}
            for sig_hash in new_signal_hashes
        ]
        
        # Update known signals
        self.known_signals.update(new_signal_hashes)
        
        return new_signals
    
    def should_auto_respond(self, signal: Dict) -> bool:
        """
        Determine if this watcher should auto-respond to a signal.
        Override this method to implement custom bidding logic.
        """
        # Example: Only respond to signals with specific keywords
        task = signal.get("task", "").lower()
        
        # Don't respond to our own signals
        if signal.get("author") == self.agent_id:
            return False
        
        # Don't respond to already-linked signals
        if signal.get("status") != "OPEN":
            return False
        
        # Example auto-response criteria
        auto_keywords = ["test", "demo", "example"]
        return any(keyword in task for keyword in auto_keywords)
    
    def auto_respond(self, signal: Dict):
        """Automatically bid on a signal"""
        signal_hash = signal["hash"]
        
        logger.info(f"Auto-responding to signal: {signal_hash} | Task: {signal['task']}")
        
        try:
            # Link to the signal (place a bid)
            link_signal(
                signal_hash,
                self.agent_id,
                f"Auto-bid from {self.agent_id} - Ready to fulfill this task"
            )
            logger.info(f"Bid successfully placed on signal {signal_hash}")
        except Exception as e:
            logger.error(f"Failed to place bid on {signal_hash}: {e}")
    
    def watch(self, auto_respond: bool = False):
        """
        Main watch loop.
        If auto_respond=True, will automatically bid on matching signals.
        """
        logger.info(f"Nexus Watcher started (Agent: {self.agent_id})")
        logger.info(f"Monitoring: {SIGNALS_FILE} | Check interval: {CHECK_INTERVAL}s | Auto-respond: {auto_respond}")
        
        # Initialize known signals
        self.known_signals = set(self.get_current_signals().keys())
        logger.info(f"Tracking {len(self.known_signals)} existing signals")
        
        try:
            while True:
                new_signals = self.detect_new_signals()
                
                if new_signals:
                    logger.info(f"Detected {len(new_signals)} new signal(s)")
                    for signal in new_signals:
                        logger.info(f"New Signal: {signal['hash'][:16]}... | Task: {signal['task']} | Author: {signal['author']} | Reward: {signal['reward']}")
                        
                        if auto_respond and self.should_auto_respond(signal):
                            self.auto_respond(signal)
                
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n⏹️  Watcher stopped by user")
    
    def stats(self):
        """Print current Nexus statistics"""
        signals = self.get_current_signals()
        
        status_counts = {}
        total_rewards = 0.0
        
        for signal in signals.values():
            status = signal.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            try:
                total_rewards += float(signal.get("reward", "0"))
            except:
                pass
        
        print("📊 Nexus Statistics")
        print("=" * 50)
        print(f"Total Signals: {len(signals)}")
        print(f"Total Rewards: {total_rewards} $HCL")
        print()
        print("Status Breakdown:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="HardCard Nexus Watcher")
    parser.add_argument(
        "--agent-id",
        default="NexusWatcher",
        help="Agent ID for this watcher instance"
    )
    parser.add_argument(
        "--auto-respond",
        action="store_true",
        help="Automatically bid on matching signals"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print statistics and exit"
    )
    
    args = parser.parse_args()
    
    watcher = NexusWatcher(agent_id=args.agent_id)
    
    if args.stats:
        watcher.stats()
    else:
        watcher.watch(auto_respond=args.auto_respond)


if __name__ == "__main__":
    main()
