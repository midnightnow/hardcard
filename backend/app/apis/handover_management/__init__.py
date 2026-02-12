from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import databutton as db
import json

# Import the definitive TrustHandoverStatus from the family_trusts API module
from app.apis.family_trusts import TrustHandoverStatus

# Constants for DB storage keys
TRUST_ACCOUNTS_KEY = "family_trust_accounts.json" # Consistent with family_trusts API

# Helper to load data from db.storage.json
def _load_json_data(key: str, default_value: Any = {}) -> Any:
    try:
        return db.storage.json.get(key, default=default_value)
    except Exception as e:
        print(f"Error loading data for key {key}: {e}")
        return default_value

# Helper to save data to db.storage.json
def _save_json_data(key: str, data: Any):
    try:
        db.storage.json.put(key, data)
    except Exception as e:
        print(f"Error saving data for key {key}: {e}")

def calculate_age(birthdate_str: str) -> int:
    """Calculates age given a birthdate string in YYYY-MM-DD format."""
    birthdate = date.fromisoformat(birthdate_str)
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def check_beneficiary_ages_and_update_status():
    """
    Checks beneficiary ages using child_date_of_birth from FamilyTrustData 
    and updates trust account statuses if they are 18 or older
    and the trust is currently in LOCKED_PARENTAL_CONTROL status.
    """
    print("Starting beneficiary age check...")
    trust_accounts_dict: Dict[str, Dict] = _load_json_data(TRUST_ACCOUNTS_KEY, default_value={})
    
    updated_trust_count = 0

    if not trust_accounts_dict:
        print("No trust accounts found.")
        return

    trusts_to_save = {}

    for trust_id, trust_data_dict in trust_accounts_dict.items():
        current_status = trust_data_dict.get("status")
        child_id = trust_data_dict.get("child_id") # For logging
        child_dob_str = trust_data_dict.get("child_date_of_birth") # Expect YYYY-MM-DD string

        if current_status == TrustHandoverStatus.LOCKED_PARENTAL_CONTROL:
            if not child_dob_str:
                print(f"Warning: child_date_of_birth not found for trust ID {trust_id}. Skipping age check.")
                trusts_to_save[trust_id] = trust_data_dict # Save as is
                continue
            
            try:
                age = calculate_age(child_dob_str)
                print(f"Trust ID: {trust_id}, Child ID: {child_id}, DOB: {child_dob_str}, Age: {age}")
                
                if age >= 18:
                    print(f"Beneficiary for trust {trust_id} (Child ID: {child_id}) is {age} (>=18). Updating status to ELIGIBLE_FOR_HANDOVER.")
                    trust_data_dict["status"] = TrustHandoverStatus.ELIGIBLE_FOR_HANDOVER
                    trust_data_dict["last_updated"] = datetime.utcnow().isoformat() # Add last_updated
                    updated_trust_count += 1
            except ValueError as e:
                print(f"Error calculating age for trust {trust_id} (Child ID: {child_id}): {e}. Birthdate string: {child_dob_str}")
            
        trusts_to_save[trust_id] = trust_data_dict

    if updated_trust_count > 0:
        print(f"Found {updated_trust_count} trusts eligible for handover. Saving updates...")
        _save_json_data(TRUST_ACCOUNTS_KEY, trusts_to_save)
        print("Updates saved.")
    else:
        print("No trusts required status updates based on age check.")

    print("Beneficiary age check finished.")

if __name__ == "__main__":
    mock_trusts_with_dob = {
        "trust_alice_1": {
            "trust_id": "trust_alice_1", "child_id": "child_alice_001", 
            "status": TrustHandoverStatus.LOCKED_PARENTAL_CONTROL, "account_name": "Alice Trust 1",
            "child_date_of_birth": (date.today() - timedelta(days=18*365 + 5)).isoformat()
        },
        "trust_bob_1": {
            "trust_id": "trust_bob_1", "child_id": "child_bob_002", 
            "status": TrustHandoverStatus.LOCKED_PARENTAL_CONTROL, "account_name": "Bob Trust 1",
            "child_date_of_birth": (date.today() - timedelta(days=17*365)).isoformat()
        },
        "trust_carol_1": {
            "trust_id": "trust_carol_1", "child_id": "child_carol_003", 
            "status": TrustHandoverStatus.LOCKED_PARENTAL_CONTROL, "account_name": "Carol Trust 1",
            "child_date_of_birth": (date.today() - timedelta(days=20*365)).isoformat()
        },
        "trust_dave_nodob": {
            "trust_id": "trust_dave_nodob", "child_id": "child_dave_004",
            "status": TrustHandoverStatus.LOCKED_PARENTAL_CONTROL, "account_name": "Dave No DOB Trust"
        }
    }
    _save_json_data(TRUST_ACCOUNTS_KEY, mock_trusts_with_dob)

    print("Running test for check_beneficiary_ages_and_update_status...")
    check_beneficiary_ages_and_update_status()

    print("\nVerifying results:")
    updated_trusts = _load_json_data(TRUST_ACCOUNTS_KEY)
    for tid, tdata in updated_trusts.items():
        print(f"Trust ID: {tid}, Status: {tdata.get('status')}, Child ID: {tdata.get('child_id')}, Child DOB: {tdata.get('child_date_of_birth')}")
