#!/usr/bin/env python3
"""
HardCard Secrets Migration Script
Migrates plaintext secrets to secure macOS keychain storage
"""

import sys
import logging
import json
from pathlib import Path

# Add security module to path
sys.path.insert(0, str(Path(__file__).parent))

from security.secrets_migrator import SecretsMigrator

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('secrets_migration.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main migration function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🔐 HardCard Secrets Migration Tool")
    print("=" * 50)
    
    # Initialize migrator
    migrator = SecretsMigrator()
    
    # Ask user for dry run or actual migration
    print("\nChoose migration mode:")
    print("1. Dry run (scan and show what would be migrated)")
    print("2. Full migration (actually migrate secrets)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        dry_run = True
        print("\n🔍 Running dry run migration...")
    elif choice == "2":
        dry_run = False
        print("\n⚠️  WARNING: This will migrate secrets to keychain!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Migration cancelled.")
            return
        print("\n🚀 Running full migration...")
    else:
        print("Invalid choice. Exiting.")
        return
    
    try:
        # Run migration
        results = migrator.run_full_migration(dry_run=dry_run)
        
        # Display results
        print(f"\n📊 Migration Results:")
        print(f"Secrets found: {results['secrets_found']}")
        print(f"Successfully migrated: {len(results['migration_results']['migrated'])}")
        print(f"Failed: {len(results['migration_results']['failed'])}")
        print(f"Skipped: {len(results['migration_results']['skipped'])}")
        
        if not dry_run:
            print(f"Backup directory: {results['backup_directory']}")
            print(f"Migration script: {results['script_path']}")
        
        # Save detailed results
        results_file = "migration_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Detailed results saved to: {results_file}")
        
        # Show specific secrets that would be migrated
        if results['migration_results']['migrated']:
            print(f"\n📋 Secrets to migrate:")
            for secret in results['migration_results']['migrated'][:10]:  # Show first 10
                print(f"  - {secret['key_name']} ({secret['secret_type']}) from {secret['location']}")
            
            if len(results['migration_results']['migrated']) > 10:
                print(f"  ... and {len(results['migration_results']['migrated']) - 10} more")
        
        # Show any failures
        if results['migration_results']['failed']:
            print(f"\n❌ Failed migrations:")
            for failure in results['migration_results']['failed']:
                print(f"  - {failure['key_name']}: {failure['reason']}")
        
        if dry_run:
            print(f"\n💡 Next steps:")
            print("1. Review the migration results above")
            print("2. Run with option 2 to perform actual migration")
            print("3. Update your code to use keychain.get_api_key() instead of environment variables")
        else:
            print(f"\n✅ Migration completed!")
            print("1. Review the migration script generated")
            print("2. Update your code to use the keychain manager")
            print("3. Remove or encrypt the original .env files")
            print("4. Test your application with the new keychain integration")
            
            # Show example usage
            print(f"\n🔧 Example usage in your code:")
            print("```python")
            print("from hardcard.security import KeychainManager")
            print("keychain = KeychainManager('hardcard')")
            print("openai_key = keychain.get_api_key('api_key_openai')")
            print("firebase_config = keychain.get_firebase_config()")
            print("```")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        print(f"\n❌ Migration failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())