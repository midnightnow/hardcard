from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from firebase_admin import firestore, auth
from app.apis.firebase_init import initialize_firebase

# Initialize Firebase
initialize_firebase()

# Now get the firestore client at module level
firestore_client = firestore.client()
# Trivial comment to force backend refresh
from pydantic import BaseModel, Field
import databutton as db
from datetime import datetime
import uuid
import hashlib
from typing import List, Optional
import time # For retry delay
from bitcoin import SelectParams # Added for testnet selection
from bitcoinlib.transactions import Transaction, Output
from bitcoin.core.script import CScript, OP_RETURN # Corrected import path

from app.apis.gossip_broadcast import broadcast_json  # MYA-157 User Integration

# Placeholder for firebase_admin initialization if needed,
# but for Firestore access, db.storage.firestore will be used.
# from app.auth import firebase_admin_app

router = APIRouter(
    prefix="/merkle-batch-job",
    tags=["merkle-batch-job"]
)

class TriggerBatchRequest(BaseModel):
    max_tags_to_process: int = Field(100, description="Maximum number of event tags to process in this batch.")

class BatchProcessSummary(BaseModel):
    batch_id: str
    tags_processed_count: int
    merkle_root: Optional[str]
    tx_hash: Optional[str] = None # Added for blockchain transaction hash
    status: str
    message: str
    processed_at: datetime

@router.post("/trigger-merkle-batch", response_model=BatchProcessSummary)
async def trigger_merkle_batch(request_body: TriggerBatchRequest):
    """
    Triggers the processing of un-anchored event tags into a Merkle batch.
    This endpoint is intended to be called by a scheduled job/cron.
    It will query for event tags that have not yet been batched,
    construct a Merkle tree from their hashes, store the Merkle root (conceptually),
    and update the processed tags with batch information.
    """
    print(f"Merkle batch job triggered with max_tags_to_process: {request_body.max_tags_to_process}")
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    processed_at_time = datetime.utcnow()

    # TODO:
    # 1. Query Firestore for un-anchored EventTags (where merkle_batch_id is None)
    #    - Use request_body.max_tags_to_process as a limit.
    #    - Fetch 'tag_id' and 'verification_hash'.
    # 2. If no tags, return a summary indicating nothing to process.
    print("Attempting to query Firestore for un-anchored event tags...")
    try:
        event_tags_ref = firestore_client.collection('event_tags') # firestore_client is now module-level
        
        query = event_tags_ref.where('merkle_batch_id', '==', None).limit(request_body.max_tags_to_process)
        docs_stream = query.stream()
        
        unanchored_tags = []
        for doc in docs_stream:
            tag_data = doc.to_dict()
            unanchored_tags.append({
                "doc_id": doc.id, # Keep document ID for updates
                "tag_id": tag_data.get("tag_id"), 
                "verification_hash": tag_data.get("verification_hash")
            })
        
        print(f"Found {len(unanchored_tags)} un-anchored event tags.")

        if not unanchored_tags:
            return BatchProcessSummary(
                batch_id=batch_id,
                tags_processed_count=0,
                merkle_root=None,
                status="no_tags_to_process",
                message="No un-anchored event tags found to process.",
                processed_at=processed_at_time
            )

    except Exception as e:
        print(f"Error querying Firestore: {e}")
        # It's good practice to log the original exception too for more detailed debugging
        # Consider using a more specific exception type if possible, e.g. from firebase_admin.exceptions
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error querying Firestore: {str(e)}") from e

    # 3. Build Merkle Tree:
    #    - If tags are found, get their 'verification_hash' values.
    #    - Implement or use a library for Merkle tree construction.
    #    - Calculate the Merkle root.
    print(f"Building Merkle tree for {len(unanchored_tags)} tags...")
    tag_hashes = [tag['verification_hash'] for tag in unanchored_tags if tag['verification_hash']]
    
    if not tag_hashes:
        # This case should ideally be caught by 'if not unanchored_tags' earlier,
        # but as a safeguard if tags exist but have no verification_hash.
        return BatchProcessSummary(
            batch_id=batch_id,
            tags_processed_count=0,
            merkle_root=None,
            status="no_hashes_to_process",
            message="No valid verification hashes found in un-anchored tags.",
            processed_at=processed_at_time
        )

    merkle_root_hash = calculate_merkle_root(tag_hashes)
    print(f"Calculated Merkle root: {merkle_root_hash}")

    # TODO: Implement actual Bitcoin transaction creation and broadcasting
    # For now, simulate tx_hash and OP_RETURN script creation
    tx_hash_placeholder = None
    if merkle_root_hash:
        try:
            # The broadcast_to_bitcoin_testnet function will handle script creation from merkle_root_hash
            import hashlib
            tx_hash_placeholder = hashlib.sha256(f"sim_tx_{merkle_root_hash}".encode('utf-8')).hexdigest()
            print(f"Generated placeholder tx_hash: {tx_hash_placeholder}")
            # The actual OP_RETURN script creation will happen in broadcast_to_bitcoin_testnet
        except ValueError:
            print(f"Error: Merkle root '{merkle_root_hash}' is not valid hex. Cannot create placeholder hash.")
            # Decide if this should halt the process or proceed without a tx_hash
            pass # Or raise, or set status to error

    # Blockchain broadcast attempt with retry logic
    actual_tx_hash = None
    broadcast_status_message = "Blockchain broadcast not attempted."

    if merkle_root_hash and tx_hash_placeholder: # Proceed if Merkle root and initial script setup were okay
        max_retries = 3
        retry_delay_seconds = 10
        
        # Placeholder for actual broadcast function
        async def broadcast_to_bitcoin_testnet(merkle_root: str) -> Optional[str]:
            # This function will contain the actual logic for:
            # 1. Constructing the full raw transaction with OP_RETURN and fees
            # 2. Signing the transaction
            # 3. Broadcasting via a public API (e.g., requests.post(...))
            # 4. Returning the real tx_hash if successful, None otherwise.
            print(f"Attempting to construct and sign transaction for Merkle root {merkle_root}...")

            # --- Placeholder for User-Provided Testnet Credentials & UTXO ---
            # IMPORTANT: Replace these with actual testnet values from the user or a secure config
            testnet_private_key_wif = "cVERYSECRETTESTNETPRIVATEKEYWIFDONOTCOMMITREALKEYS" # Example: cVpAdUXPA72WAbC5YwnJCoL7f2NBBMf4CUnx4EPgYUNRgdGKvoqM
            # source_address = "tb1q..." # Corresponding P2WPKH or P2PKH testnet address
            utxo_txid = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" # Example UTXO TXID
            utxo_vout = 0  # Example UTXO output index
            utxo_amount_satoshi = 50000  # Example UTXO amount in satoshis (e.g., 0.0005 BTC)
            fee_satoshi = 1000  # Example fee in satoshis
            # --- End of Placeholders ---

            if testnet_private_key_wif == "cVERYSECRETTESTNETPRIVATEKEYWIFDONOTCOMMITREALKEYS":
                print("WARNING: Using placeholder testnet credentials. Transaction will not be broadcastable without real values.")
                # Fallback to simulated hash if real credentials aren't set
                simulated_real_tx_hash = hashlib.sha256(f"actual_tx_needs_real_creds_{merkle_root}".encode('utf-8')).hexdigest()
                print(f"Generated simulated tx_hash due to placeholder credentials: {simulated_real_tx_hash}")
                return simulated_real_tx_hash

            try:
                # Ensure bitcoinlib components are available in this scope
                from bitcoinlib.transactions import Transaction
                # Corrected import path for CScript, OP_RETURN for local scope if needed, though global should suffice
                from bitcoin.core.script import CScript, OP_RETURN 
                # Removed: from bitcoinlib.networks import BitcoinTestnet
                from bitcoinlib.keys import Key

                SelectParams('testnet') # Set global network context
                merkle_root_bytes = bytes.fromhex(merkle_root)
                op_return_output_script = CScript([OP_RETURN, merkle_root_bytes]) # Renamed and will be used

                tx = Transaction()
                tx.add_input(prev_txid=utxo_txid, output_n=utxo_vout, value=int(utxo_amount_satoshi))
                tx.add_output(script_pubkey=op_return_output_script, value=0) # Using the script here

                change_amount = utxo_amount_satoshi - fee_satoshi # OP_RETURN value is 0
                if change_amount < 0:
                    print(f"Error: UTXO amount {utxo_amount_satoshi} is less than fee {fee_satoshi}. Cannot create transaction.")
                    return None
                
                # For simplicity, assuming the source_address is where change goes back to.
                # This requires knowing the script_pubkey of the source_address.
                # A proper implementation would derive script_pubkey from the WIF or address.
                # For now, this part is simplified / placeholder.
                if change_amount > 546: # Dust limit for P2WPKH, roughly
                    # IMPORTANT: This needs the script_pubkey of the change address.
                    # For a real implementation, derive this from the source_address or WIF.
                    # from bitcoinlib.keys import Key
                    # priv_key_obj = Key(testnet_private_key_wif)
                    # change_script_pubkey = priv_key_obj.script()
                    # tx.add_output(script_pubkey=change_script_pubkey, value=change_amount)
                    print(f"Placeholder for adding change output of {change_amount} satoshis. Real script_pubkey needed.")
                    # If we don't add a change output, the remainder becomes part of the fee.
                    # To keep it simple for now, we'll let the remainder be absorbed by fees if not explicitly handled.
                    # If change_amount is not added as an output, the effective fee will be utxo_amount_satoshi.
                    # For OP_RETURN, often the fee is the primary concern, and exact change might not be critical if UTXO is small.

                # priv_key = Key(testnet_private_key_wif) # Original line causing re-import warning
                # Use Key imported at the start of the try block
                priv_key = Key(testnet_private_key_wif) 
                tx.sign(priv_key, utxo_index=0) # Assuming only one input at index 0

                raw_tx_hex = tx.raw_hex()
                print(f"Constructed and signed raw transaction hex: {raw_tx_hex}")
                tx_id = tx.txid()
                print(f"Calculated TXID: {tx_id}")

                # TODO: Implement actual broadcasting of raw_tx_hex here
                # e.g., response = requests.post("some_testnet_broadcast_api_url", data=raw_tx_hex)
                # if response.ok: return response.text() # or response.json().get('txid')

                return tx_id # For now, return the locally calculated txid

            except Exception as e:
                print(f"Error during Bitcoin transaction construction/signing: {e}")
                import traceback
                traceback.print_exc()
                return None

        for attempt in range(max_retries):
            try:
                print(f"Broadcast attempt {attempt + 1} of {max_retries}...")
                actual_tx_hash = await broadcast_to_bitcoin_testnet(merkle_root_hash)
                if actual_tx_hash:
                    broadcast_status_message = f"Successfully broadcasted to Bitcoin testnet. tx_hash: {actual_tx_hash}"
                    print(broadcast_status_message)
                    break # Exit loop on success
                else:
                    broadcast_status_message = "Broadcast attempt returned no tx_hash."
                    print(broadcast_status_message)
            except Exception as e:
                broadcast_status_message = f"Broadcast attempt {attempt + 1} failed: {e}"
                print(broadcast_status_message)
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay_seconds} seconds...")
                    time.sleep(retry_delay_seconds)
                else:
                    print("Max broadcast retries reached. Proceeding without blockchain anchor.")
                    # actual_tx_hash remains None
        
    # Update tx_hash_placeholder to actual_tx_hash if successful, otherwise it stays None or its simulated value
    # Depending on earlier logic, tx_hash_placeholder might already be the one from the simulation
    # For clarity, we use actual_tx_hash from the broadcast attempt for Firestore and summary.
    final_tx_hash_for_storage = actual_tx_hash # This will be None if broadcast failed

    # 4. Update EventTags in Firestore:
    print(f"Updating {len(unanchored_tags)} event tags in Firestore...")
    try:
        # firestore_client is already defined from the query part
        batch = firestore_client.batch()
        tags_actually_updated_count = 0

        for tag_info in unanchored_tags:
            # Ensure the tag was part of the hash calculation (i.e., had a verification_hash)
            if tag_info.get("verification_hash"):
                tag_doc_ref = firestore_client.collection('event_tags').document(tag_info["doc_id"])
                batch.update(tag_doc_ref, {
                    'merkle_batch_id': batch_id,
                    'anchored_at': processed_at_time,
                    'anchor_root_hash': merkle_root_hash,
                    'anchor_tx_hash': final_tx_hash_for_storage, # Store the actual/None tx_hash
                    'merkle_tx_hash': final_tx_hash_for_storage,
                    'merkle_anchor_status': 'anchored' if final_tx_hash_for_storage else 'processed'
                })
                tags_actually_updated_count += 1
        
        batch.commit()
        print(f"Successfully updated {tags_actually_updated_count} event tags in Firestore.")

    except Exception as e:
        print(f"Error updating EventTags in Firestore: {e}")
        # Potentially return a partial success or error state if updates fail
        # For now, we'll raise an HTTP exception, but a more robust job
        # might try to mark partially completed work or retry.
        raise HTTPException(status_code=500, detail=f"Error updating EventTags in Firestore: {str(e)}") from e

    # 5. Log the Merkle root (simulating storing it).
    # For now, it's printed above. In a real system, this might go to a separate log or DB table.
    
    # 6. Return BatchProcessSummary.
    summary_status = "success"
    if final_tx_hash_for_storage:
        summary_status = "success_anchored"
        summary_message = f"Successfully processed {tags_actually_updated_count} tags. Anchored with tx_hash: {final_tx_hash_for_storage}."
    elif merkle_root_hash: # Processed but not anchored
        summary_status = "success_not_anchored"
        summary_message = f"Successfully processed {tags_actually_updated_count} tags. Blockchain anchor failed: {broadcast_status_message}."
    else: # No tags or no hashes
        summary_status = "no_action_taken" # Or specific status from earlier
        summary_message = broadcast_status_message # or message from initial checks
        if tags_actually_updated_count == 0 and not merkle_root_hash :
             summary_status = "no_tags_to_process"
             summary_message = "No un-anchored event tags found to process."


    summary = BatchProcessSummary(
        batch_id=batch_id,
        tags_processed_count=tags_actually_updated_count,
        merkle_root=merkle_root_hash,
        tx_hash=final_tx_hash_for_storage, # Include actual/None tx_hash in summary
        status=summary_status,
        message=summary_message,
        processed_at=processed_at_time
    )

    # MYA-157: Broadcast the summary using user's gossip_broadcast
    try:
        print(
            f"Broadcasting Merkle batch summary for batch_id: {summary.batch_id} via gossip_broadcast..."
        )
        # broadcast_json expects a dict, model_dump() provides that for Pydantic v2
        await broadcast_json(summary.model_dump())
        print(
            f"Successfully broadcasted Merkle batch summary for batch_id: {summary.batch_id}"
        )
    except Exception as e:
        # Log the error but don't let it fail the main batch job process
        print(
            f"Error broadcasting Merkle batch summary for batch_id: {summary.batch_id}: {e}"
        )

    return summary

# Placeholder for a simple Merkle tree function (to be expanded)
def calculate_merkle_root(hashes: List[str]) -> Optional[str]:
    if not hashes:
        return None
    
    # Ensure all elements are strings, filter out None if any slip through upstream
    current_level_hashes = [h for h in hashes if h is not None]
    if not current_level_hashes:
        return None

    # If there's an odd number of hashes, duplicate the last one to make pairs
    if len(current_level_hashes) % 2 == 1:
        current_level_hashes.append(current_level_hashes[-1])

    # If only one hash remains, it's the root
    if len(current_level_hashes) == 1 and len(hashes) == 1: # Edge case for single item initial list
        return current_level_hashes[0]

    while len(current_level_hashes) > 1:
        next_level_hashes = []
        # Process hashes in pairs
        for i in range(0, len(current_level_hashes), 2):
            hash1 = current_level_hashes[i]
            hash2 = current_level_hashes[i+1]
            # Ensure correct encoding before hashing
            combined_hash_input = (hash1 + hash2).encode('utf-8')
            parent_hash = hashlib.sha256(combined_hash_input).hexdigest()
            next_level_hashes.append(parent_hash)
        
        current_level_hashes = next_level_hashes
        # If an odd number of hashes in the new level, duplicate the last one for the next iteration
        if len(current_level_hashes) % 2 == 1 and len(current_level_hashes) > 1:
            current_level_hashes.append(current_level_hashes[-1])

    return current_level_hashes[0] if current_level_hashes else None

