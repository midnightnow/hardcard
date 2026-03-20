#!/usr/bin/env python3
"""Minimal CLI for Hardcard primitives."""

import argparse
import sys
import json
from pathlib import Path

from hardcard import anchor, verify, Chain
from hardcard.identity.ed25519 import Identity

def main():
    parser = argparse.ArgumentParser(description="Hardcard verification primitives")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # anchor command
    anchor_parser = subparsers.add_parser("anchor", help="Create hash of content")
    anchor_parser.add_argument("content", help="Content to hash (JSON string or @file)")
    
    # verify command
    verify_parser = subparsers.add_parser("verify", help="Verify content against hash")
    verify_parser.add_argument("hash", help="Claimed hash")
    verify_parser.add_argument("content", help="Content to verify")
    
    # chain command
    chain_parser = subparsers.add_parser("chain", help="Manage hash chain")
    chain_parser.add_argument("--file", default=".hardcard-chain.json", help="Chain file")
    chain_parser.add_argument("--add", help="Add content to chain")
    chain_parser.add_argument("--verify", action="store_true", help="Verify chain")
    
    # identity commands
    id_parser = subparsers.add_parser("identity", help="Identity management")
    id_parser.add_argument("--generate", action="store_true", help="Generate new key")
    id_parser.add_argument("--sign", help="Sign message")
    id_parser.add_argument("--verify", nargs=3, metavar=('MSG', 'SIG', 'PUBKEY'), 
                          help="Verify signature")
    
    args = parser.parse_args()
    
    def load_content(content_arg):
        if content_arg.startswith('@'):
            with open(content_arg[1:]) as f:
                return f.read()
        return content_arg
    
    if args.command == "anchor":
        content = load_content(args.content)
        try:
            data = json.loads(content) if content.startswith('{') else content
        except:
            data = content
        print(anchor(data))
    
    elif args.command == "verify":
        content = load_content(args.content)
        try:
            data = json.loads(content) if content.startswith('{') else content
        except:
            data = content
        print(verify(args.hash, data))
    
    elif args.command == "chain":
        chain_file = Path(args.file)
        chain = Chain()
        
        if chain_file.exists():
            with open(chain_file) as f:
                data = json.load(f)
                chain.blocks = data.get("blocks", [])
        
        if args.add:
            content = load_content(args.add)
            try:
                data = json.loads(content) if content.startswith('{') else content
            except:
                data = content
            h = chain.add(data)
            print(f"Added: {h}")
            with open(chain_file, 'w') as f:
                json.dump({"blocks": chain.blocks}, f, indent=2)
        
        if args.verify:
            print(chain.verify())
    
    elif args.command == "identity":
        id = Identity()
        if args.generate:
            print(f"Public: {id.public_key}")
            print(f"Private: {id.private_key}")
        elif args.sign:
            sig = id.sign(args.sign.encode())
            print(sig)
        elif args.verify:
            msg, sig, pubkey = args.verify
            result = id.verify(msg.encode(), sig, pubkey)
            print(result)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
