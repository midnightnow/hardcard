"""
Hardcard Generic Simulation Script
Simulates the "Genesis Task" workflow between two agents.
"""
import sys
import time
import subprocess
import re

def run_cli(args):
    """Runs a hardcard CLI command and returns text output."""
    cmd = ["python3", "-m", "hardcard.cli"] + args
    result = subprocess.run(
        cmd, 
        cwd="/Users/studio/00 Constellation/hardcard",
        capture_output=True, 
        text=True,
        env={"PYTHONPATH": ".."} # Ensure module resolution
    )
    if result.returncode != 0:
        print(f"Error running {cmd}: {result.stderr}")
        return ""
    return result.stdout.strip()

def main():
    print("🚀 Starting Hardcard Nexus Simulation (Genesis Task)...")
    
    # 1. Setup Agents
    client = "My_Agent_ID"
    worker = "Worker_Agent_01"
    
    # Ensure keys exist (assuming I just ran keys command for worker)
    # Check balances
    print(f"\n💰 Checking {client} Balance...")
    print(run_cli(["wallet", "--agent", client, "--status"]))
    
    # 2. Broadcast Task
    task = "Optimize Python Regex"
    reward = "50"
    print(f"\n📡 {client} Broadcasting Task: '{task}' ($HCL {reward})...")
    # Note: CLI doesn't support --reward arg yet in nexus command, 
    # but we can simulate the "Broadcast" action. 
    # The prompt implies adding --reward support or just simulating the flow.
    # checking cli.py I implemented standard args. 
    # I will stick to what I implemented: --broadcast "Task"
    broadcast_out = run_cli(["nexus", "--broadcast", task])
    print(broadcast_out)
    
    # Extract Hash
    match = re.search(r"Signal Hash: ([a-f0-9]+)", broadcast_out)
    if not match:
        print("❌ Failed to get Signal Hash.")
        return
    signal_hash = match.group(1)
    
    # 3. Link (Bid)
    print(f"\n🔗 {worker} Linking to Signal {signal_hash}...")
    link_out = run_cli(["nexus", "--link", signal_hash])
    print(link_out)
    
    # Simulate Escrow Lock (Agency command)
    print(f"\n🏛️ Locking Escrow ($HCL {reward})...")
    # We use 'agency' command to simulate the financial settlement part
    # agency --escrow --amount 50 --buyer client --worker worker
    agency_out = run_cli(["agency", "--escrow", "--amount", reward, "--buyer", client, "--worker", worker])
    print(agency_out)
    
    # 4. Deliver
    print(f"\n📦 {worker} Delivering Payload...")
    deliver_out = run_cli(["nexus", "--deliver", signal_hash, "--payload", "import re; pattern = re.compile(...)"])
    print(deliver_out)
    
    # 5. Final Balances
    print(f"\n💰 Final Balance Check...")
    print(f"--- {client} ---")
    print(run_cli(["wallet", "--agent", client, "--status"]))
    print(f"--- {worker} ---")
    print(run_cli(["wallet", "--agent", worker, "--status"]))
    
    print("\n✅ Simulation Complete.")

if __name__ == "__main__":
    main()
