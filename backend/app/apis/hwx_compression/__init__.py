import base64
import hashlib
import struct # For Chebyshev compression/decompression
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

import databutton as db
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Cryptography imports
from Crypto.Cipher import AES
from Crypto.PublicKey import ECC
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Signature import DSS
import argon2 # Added import for argon2
from argon2 import PasswordHasher # Already present, good

# KMS imports (if used for anchoring, currently not for user key derivation)
# from google.cloud import kms_v1
# from google.protobuf import wrappers_pb2

from app.auth import AuthorizedUser # For Firebase Auth User

router = APIRouter(
    prefix="/hwx-compression",
    tags=["hwx-compression"], # Grouping tag for Swagger UI
)

# --- Configuration ---
# KMS_KEY_RING_ID = "projects/your-gcp-project/locations/global/keyRings/your-key-ring"
# KMS_SIGNING_KEY_ID = "your-signing-key"
# KMS_SIGNING_KEY_VERSION_ID = "1" # or the specific version you want to use

# Construct the full key version name for KMS signing if needed later
# kms_signing_key_version_name = f"{KMS_KEY_RING_ID}/cryptoKeys/{KMS_SIGNING_KEY_ID}/cryptoKeyVersions/{KMS_SIGNING_KEY_VERSION_ID}"


# --- Data Models (Pydantic) ---

class GenerateKeyRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")

class GenerateKeyResponse(BaseModel):
    key_id: str = Field(..., description="The newly generated unique key identifier")
    message: str = Field("Successfully generated new key ID.", description="Status message")

class Point2D(BaseModel):
    x: float
    y: float

class Point3D(BaseModel):
    x: float
    y: float
    z: float

class StrokeTable(BaseModel):
    path_data: str = Field(..., description="SVG path data for the stroke")
    style_id: int = Field(1, description="Style ID including compression type in high nibble")
    collapse: int = Field(0, description="Collapse flag for quadtree")
    payload_deprecated: Optional[str] = Field(None, description="DEPRECATED: Old base64 encoded AES-GCM encrypted payload") # Renamed from payload
    payload_components: Optional[Dict[str, str]] = Field(None, description="AES-GCM components: nonce, tag, ciphertext, all base64 encoded") # New field
    point_count: Optional[int] = Field(None, description="24-bit point count (literature scan refinement)")
    chebyshev_degree: Optional[int] = Field(None, description="Degree of Chebyshev polynomial if used")

class HWXContainer(BaseModel):
    version: int = Field(1, description="HWX format version")
    strokes: List[StrokeTable] = Field(..., description="List of stroke tables")
    proofs: List[Dict[str, Any]] = Field([], description="List of proof blocks")

class HWXEncodeRequest(BaseModel):
    points: List[Point3D] = Field(..., description="List of 3D points to encode")
    master_passphrase: str = Field(..., description="User's master passphrase to unlock operational keys.")
    style_id: int = Field(1, description="Style ID for stroke rendering (1-255)")
    compression_type: Optional[int] = Field(1, description="Compression algorithm (1=standard, 2=Chebyshev)")

class HWXDecodeRequest(BaseModel):
    hwx_id: str = Field(..., description="HWX ID of the data stored by the /encode endpoint.") # Changed from hwx_data to hwx_id
    master_passphrase: str = Field(..., description="User's master passphrase to unlock operational keys.")
    # user_key_id: str = Field(..., description="User key ID for decryption") # Replaced
    compression_type: Optional[int] = Field(None, description="Force specific decompression algorithm (1=default, 2=Chebyshev)")

class HWXEncodingInfo(BaseModel):
    hwx_id: str
    timestamp: Optional[int] = None
    description: Optional[str] = None
    compression_type: Optional[int] = None
    original_point_count: Optional[int] = None
    compressed_data_size: Optional[int] = None
    svg_path_preview: Optional[str] = None
    user_key_id: Optional[str] = None # This refers to the old deprecated key ID, should be phased out

@router.get("/list", tags=["demo"])
async def list_encodings() -> list[HWXEncodingInfo]:
    # Attempt to get existing encodings, or default to an empty dict
    try:
        encodings_data = db.storage.json.get("hwx_encodings", default={})
    except FileNotFoundError: # Should be handled by default, but good practice
        encodings_data = {}
    
    # Ensure encodings_data is a dictionary
    if not isinstance(encodings_data, dict):
        print(f"Warning: hwx_encodings was not a dict, found {type(encodings_data)}. Returning empty list.")
        return []

    items = []
    for k, v in encodings_data.items():
        if isinstance(v, dict):
            # Ensure all fields expected by HWXEncodingInfo are present in v or have defaults
            # Pydantic will raise validation error if required fields are missing and have no default
            try:
                items.append(HWXEncodingInfo(hwx_id=k, **v))
            except Exception as e:
                print(f"Warning: Could not parse item for hwx_id {k} due to: {e}. Skipping.")
        else:
            print(f"Warning: Value for hwx_id {k} is not a dict. Skipping.")
    return items

class HWXAnchorRequest(BaseModel):
    hwx_id: str = Field(..., description="HWX ID to anchor")
    # user_key_id: str = Field(..., description="User key ID for signing") # Replaced by master_passphrase logic
    master_passphrase: str = Field(..., description="User's master passphrase to unlock operational keys for signing.")

class HWXSampleRequest(BaseModel):
    sample_type: str = Field("spiral", description="Sample type to generate (spiral, signature, etc)")
    complexity: int = Field(3, description="Complexity level (1-10)")
    length: int = Field(100, description="Number of points to generate")
    compression_type: Optional[int] = Field(1, description="Compression algorithm (1=Delta, 2=Chebyshev)")

# Models for MYA-208: Secure Key Storage Setup
class SetupHWXKeysRequest(BaseModel):
    master_passphrase: str = Field(..., min_length=12, description="User's master passphrase for HWX key encryption. Minimum 12 characters.")

class SetupHWXKeysResponse(BaseModel):
    message: str = Field("HWX keys set up successfully.")
    user_id: str # To confirm which user it was set up for
    public_key_pem: str # The PEM format of the public ECDSA key

# Helper functions

# --- New endpoint for MYA-208: Secure Key Storage Setup ---
@router.post("/setup-hwx-keys", response_model=SetupHWXKeysResponse, tags=["hwx-key-management"], summary="Set up or re-set HWX operational keys using a master passphrase.")
async def setup_hwx_keys_endpoint(
    request: SetupHWXKeysRequest,
    user: AuthorizedUser
):
    """
    Sets up (or overwrites) the HWX operational keys for the authenticated user.
    A master passphrase is used to derive a Master Encryption Key (MEK),
    which then encrypts newly generated AES and ECDSA keys.
    These encrypted keys, along with necessary salts and nonces, are stored in db.storage.json.
    A verifiable hash of the passphrase is also stored for future passphrase checks.
    """
    user_id = user.sub
    passphrase_bytes = request.master_passphrase.encode('utf-8')

    # Initialize Argon2 PasswordHasher
    ph = PasswordHasher()

    # 1. Store a verifiable hash of the master passphrase (for quick passphrase checks)
    try:
        passphrase_argon2_hash = ph.hash(passphrase_bytes) # PasswordHasher handles its own salting and parameters
        passphrase_hash_storage_key = f"secure_user_data/{user_id}/hwx_credentials/passphrase_argon2_hash"
        db.storage.json.put(passphrase_hash_storage_key, {"hash": passphrase_argon2_hash, "version": 2, "kdf_params": ph.parameters.as_dict(), "timestamp_utc": datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        print(f"Error storing passphrase hash for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not store passphrase hash: {str(e)}") from e

    # 2. Generate a unique salt for deriving the Master Encryption Key (MEK)
    mek_salt = get_random_bytes(16) # 16 bytes is a common size for salt

    # 3. Derive the Master Encryption Key (MEK) from the passphrase and mek_salt
    #    Using argon2.hash_password_raw to get raw key bytes for encryption.
    #    Parameters should be strong.
    try:
        # Argon2 parameters for MEK derivation (can be tuned)
        mek_time_cost = 2
        mek_memory_cost = 102400  # KiB, so 100MB
        mek_parallelism = 8
        mek_hash_len = 32  # For AES-256

        mek = argon2.hash_password_raw(
            password=passphrase_bytes,
            salt=mek_salt,
            time_cost=mek_time_cost,
            memory_cost=mek_memory_cost,
            parallelism=mek_parallelism,
            hash_len=mek_hash_len,
            type=argon2.Type.ID # Use Argon2id for better resistance
        )
    except Exception as e:
        print(f"Error deriving MEK for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not derive MEK: {str(e)}") from e

    # 4. Generate new operational keys (AES for payload, ECDSA for proofs)
    try:
        aes_op_key_bytes = get_random_bytes(32)  # AES-256
        ecdsa_op_key = ECC.generate(curve='P-256')
        ecdsa_public_key_pem = ecdsa_op_key.public_key().export_key(format='PEM')
        # Export private key without encryption here, as it will be encrypted by MEK
        ecdsa_private_key_pem_bytes = ecdsa_op_key.export_key(format='PEM').encode('utf-8')
    except Exception as e:
        print(f"Error generating operational keys for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not generate operational keys: {str(e)}") from e

    # 5. Encrypt operational keys with the MEK using AES-GCM
    encrypted_op_keys_bundle = {}
    try:
        # Encrypt AES operational key
        cipher_for_aes_op = AES.new(mek, AES.MODE_GCM) # New cipher instance for each encryption
        encrypted_aes_op_key_cipherpayload, tag_for_aes_op = cipher_for_aes_op.encrypt_and_digest(aes_op_key_bytes)
        encrypted_op_keys_bundle['aes_op_key'] = {
            "nonce_b64": base64.b64encode(cipher_for_aes_op.nonce).decode('utf-8'),
            "ciphertext_b64": base64.b64encode(encrypted_aes_op_key_cipherpayload).decode('utf-8'),
            "tag_b64": base64.b64encode(tag_for_aes_op).decode('utf-8')
        }

        # Encrypt ECDSA private key PEM
        cipher_for_ecdsa_priv = AES.new(mek, AES.MODE_GCM) # New cipher instance
        encrypted_ecdsa_priv_key_cipherpayload, tag_for_ecdsa_priv = cipher_for_ecdsa_priv.encrypt_and_digest(ecdsa_private_key_pem_bytes)
        encrypted_op_keys_bundle['ecdsa_private_key_pem'] = {
            "nonce_b64": base64.b64encode(cipher_for_ecdsa_priv.nonce).decode('utf-8'),
            "ciphertext_b64": base64.b64encode(encrypted_ecdsa_priv_key_cipherpayload).decode('utf-8'),
            "tag_b64": base64.b64encode(tag_for_ecdsa_priv).decode('utf-8')
        }
        
        # Store the public key unencrypted, as it's public.
        encrypted_op_keys_bundle['ecdsa_public_key_pem'] = ecdsa_public_key_pem
        
        # Store MEK derivation parameters needed for decryption
        encrypted_op_keys_bundle['mek_derivation_params'] = {
            "salt_b64": base64.b64encode(mek_salt).decode('utf-8'),
            "time_cost": mek_time_cost,
            "memory_cost": mek_memory_cost,
            "parallelism": mek_parallelism,
            "hash_len": mek_hash_len,
            "type": "argon2id" # Storing type as string for clarity
        }
    except Exception as e:
        print(f"Error encrypting operational keys for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not encrypt operational keys: {str(e)}") from e
    
    hwx_keys_storage_key = f"secure_user_data/{user_id}/hwx_keys/operational_keys"
    try:
        db.storage.json.put(hwx_keys_storage_key, encrypted_op_keys_bundle)
    except Exception as e:
        print(f"Error storing HWX operational keys for user {user_id}: {str(e)}")
        # Consider cleanup of passphrase hash if key storage fails, to keep state consistent
        # For now, just raising the error.
        raise HTTPException(status_code=500, detail=f"Could not store encrypted HWX operational keys: {str(e)}") from e

    return SetupHWXKeysResponse(
        message="HWX operational keys generated, encrypted, and stored successfully.",
        user_id=user_id,
        public_key_pem=ecdsa_public_key_pem # Corrected variable name
    )
# --- End of new endpoint for MYA-208 ---

# --- New key retrieval function for MYA-208 ---
def get_hwx_operational_keys(user_id: str, master_passphrase_str: str) -> Tuple[bytes, ECC.EccKey]:
    """
    Retrieves and decrypts the user's HWX operational keys (AES for payload, ECDSA for signing).

    Args:
        user_id: The ID of the authorized user.
        master_passphrase_str: The user's master passphrase.

    Returns:
        A tuple containing: (plaintext_aes_op_key: bytes, ecdsa_op_key_object: ECC.EccKey)

    Raises:
        HTTPException if passphrase verification fails, keys are not found, or decryption fails.
    """
    passphrase_bytes = master_passphrase_str.encode('utf-8')
    ph = PasswordHasher()

    # 1. Verify master passphrase
    passphrase_hash_storage_key = f"secure_user_data/{user_id}/hwx_credentials/passphrase_argon2_hash"
    try:
        stored_passphrase_data = db.storage.json.get(passphrase_hash_storage_key)
        if not stored_passphrase_data or "hash" not in stored_passphrase_data:
            raise HTTPException(status_code=404, detail="Passphrase hash not found for user. Please set up HWX keys first.")
        
        # Re-initialize PasswordHasher with stored parameters if available, for verification
        # This step is crucial if PasswordHasher parameters were changed since hashing.
        # For now, assuming default or consistent parameters. A more robust solution would store
        # and re-use the exact kdf_params stored during hashing.
        # ph_verify = PasswordHasher.from_parameters(argon2.Parameters.from_dict(stored_passphrase_data.get("kdf_params"))) if stored_passphrase_data.get("kdf_params") else ph
        # ph_verify.verify(stored_passphrase_data["hash"], passphrase_bytes)

        # Simpler verification if PasswordHasher parameters are consistent:
        ph.verify(stored_passphrase_data["hash"], passphrase_bytes) # Verifies against the stored hash
        print(f"Passphrase verified for user {user_id}")

    except argon2.exceptions.VerifyMismatchError:
        print(f"Passphrase verification failed for user {user_id}.")
        raise HTTPException(status_code=401, detail="Invalid master passphrase.")
    except FileNotFoundError:
        print(f"Passphrase hash not found for user {user_id} at {passphrase_hash_storage_key}")
        raise HTTPException(status_code=404, detail="Passphrase data not found. Please set up HWX keys first.")
    except Exception as e:
        print(f"Error during passphrase verification for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Passphrase verification error: {str(e)}") from e

    # 2. Retrieve the encrypted operational keys bundle
    encrypted_op_keys_storage_key = f"secure_user_data/{user_id}/hwx_keys/operational_keys"
    try:
        encrypted_op_keys_bundle = db.storage.json.get(encrypted_op_keys_storage_key)
        if not encrypted_op_keys_bundle:
            raise FileNotFoundError # Should be caught below
        
        mek_params = encrypted_op_keys_bundle.get('mek_derivation_params')
        if not mek_params:
            raise ValueError("MEK derivation parameters not found in bundle.")

        aes_bundle = encrypted_op_keys_bundle.get('aes_op_key')
        ecdsa_bundle = encrypted_op_keys_bundle.get('ecdsa_private_key_pem')
        if not aes_bundle or not ecdsa_bundle:
            raise ValueError("Encrypted AES or ECDSA key data missing from bundle.")

    except FileNotFoundError:
        print(f"Encrypted operational keys not found for user {user_id} at {encrypted_op_keys_storage_key}")
        raise HTTPException(status_code=404, detail="Encrypted operational keys not found. Please set up HWX keys.")
    except Exception as e:
        print(f"Error retrieving encrypted operational keys for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve encrypted keys: {str(e)}") from e

    # 3. Re-derive the Master Encryption Key (MEK)
    try:
        mek_salt = base64.b64decode(mek_params['salt_b64'])
        # Ensure argon2.Type.ID is used if 'type' stored is 'argon2id'
        argon2_type = argon2.Type.ID if mek_params.get('type') == 'argon2id' else argon2.Type.D # Default or map as needed

        mek = argon2.hash_password_raw(
            password=passphrase_bytes,
            salt=mek_salt,
            time_cost=mek_params['time_cost'],
            memory_cost=mek_params['memory_cost'],
            parallelism=mek_params['parallelism'],
            hash_len=mek_params['hash_len'],
            type=argon2_type
        )
    except Exception as e:
        print(f"Error re-deriving MEK for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not re-derive MEK: {str(e)}") from e

    # 4. Decrypt operational keys
    try:
        # Decrypt AES operational key
        aes_nonce = base64.b64decode(aes_bundle['nonce_b64'])
        aes_ciphertext = base64.b64decode(aes_bundle['ciphertext_b64'])
        aes_tag = base64.b64decode(aes_bundle['tag_b64'])
        cipher_for_aes_op = AES.new(mek, AES.MODE_GCM, nonce=aes_nonce)
        plaintext_aes_op_key = cipher_for_aes_op.decrypt_and_verify(aes_ciphertext, aes_tag)

        # Decrypt ECDSA private key PEM
        ecdsa_nonce = base64.b64decode(ecdsa_bundle['nonce_b64'])
        ecdsa_ciphertext = base64.b64decode(ecdsa_bundle['ciphertext_b64'])
        ecdsa_tag = base64.b64decode(ecdsa_bundle['tag_b64'])
        cipher_for_ecdsa_priv = AES.new(mek, AES.MODE_GCM, nonce=ecdsa_nonce)
        decrypted_ecdsa_private_key_pem_bytes = cipher_for_ecdsa_priv.decrypt_and_verify(ecdsa_ciphertext, ecdsa_tag)
        
        # Reconstruct ECDSA key object
        ecdsa_op_key_object = ECC.import_key(decrypted_ecdsa_private_key_pem_bytes)

    except (ValueError, KeyError) as e: # Catches MAC check failed, key incorrect, or missing dict keys
        print(f"Decryption failed for user {user_id}. MEK might be incorrect or data corrupted: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to decrypt operational keys. Ensure passphrase is correct or data is intact.") from e
    except Exception as e:
        print(f"General error during decryption for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Operational key decryption error: {str(e)}") from e

    return plaintext_aes_op_key, ecdsa_op_key_object
# --- End of new key retrieval function ---


# --- Existing HWX Core Logic (adapted for new key management) ---

# Helper for encoding points to SVG path data (simplified)
def points_to_svg_path(points: List[Point3D]) -> str:
    if not points:
        return ""
    path_parts = [f"M {points[0].x} {points[0].y}"]
    for point in points[1:]:
        path_parts.append(f"L {point.x} {point.y}")
    return " ".join(path_parts)

# Basic Delta Compression (Conceptual - a real implementation would be more complex)
def compress_delta(points: List[Point3D]) -> bytes:
    if not points:
        return b''
    
    # Header: 0x01 for Delta compression, followed by number of points (e.g., 4 bytes)
    compressed_data = bytearray([0x01])
    compressed_data.extend(len(points).to_bytes(4, 'little'))

    last_x, last_y, last_z = 0.0, 0.0, 0.0
    if points:
        # Store initial point directly (as floats - 4 bytes each)
        initial_point = points[0]
        compressed_data.extend(struct.pack('<f', initial_point.x))
        compressed_data.extend(struct.pack('<f', initial_point.y))
        compressed_data.extend(struct.pack('<f', initial_point.z))
        last_x, last_y, last_z = initial_point.x, initial_point.y, initial_point.z

        for point in points[1:]:
            # Store deltas (as floats - could be optimized further, e.g. fixed point, varint)
            delta_x = point.x - last_x
            delta_y = point.y - last_y
            delta_z = point.z - last_z
            compressed_data.extend(struct.pack('<f', delta_x))
            compressed_data.extend(struct.pack('<f', delta_y))
            compressed_data.extend(struct.pack('<f', delta_z))
            last_x, last_y, last_z = point.x, point.y, point.z
            
    return bytes(compressed_data)

def decompress_delta(compressed_bytes: bytes) -> List[Point3D]:
    if not compressed_bytes or compressed_bytes[0] != 0x01:
        # Not delta compressed or empty
        return []

    points_3d: List[Point3D] = []
    try:
        num_points = int.from_bytes(compressed_bytes[1:5], 'little')
        offset = 5

        if num_points == 0:
            return []

        # Read initial point
        initial_x = struct.unpack('<f', compressed_bytes[offset:offset+4])[0]
        offset += 4
        initial_y = struct.unpack('<f', compressed_bytes[offset:offset+4])[0]
        offset += 4
        initial_z = struct.unpack('<f', compressed_bytes[offset:offset+4])[0]
        offset += 4
        points_3d.append(Point3D(x=initial_x, y=initial_y, z=initial_z))
        current_x, current_y, current_z = initial_x, initial_y, initial_z

        for _ in range(num_points - 1):
            delta_x = struct.unpack('<f', compressed_bytes[offset:offset+4])[0]
            offset += 4
            delta_y = struct.unpack('<f', compressed_bytes[offset:offset+4])[0]
            offset += 4
            delta_z = struct.unpack('<f', compressed_bytes[offset:offset+4])[0]
            offset += 4
            current_x += delta_x
            current_y += delta_y
            current_z += delta_z
            points_3d.append(Point3D(x=current_x, y=current_y, z=current_z))
    except (struct.error, IndexError) as e:
        print(f"Error decompressing delta data: {e}")
        return [] # Return partial or empty if error
    return points_3d


# Placeholder for Chebyshev compression logic
def compress_chebyshev(points: List[Point3D]) -> bytes:
    # This would involve fitting Chebyshev polynomials to x(t), y(t), z(t)
    # and storing coefficients, degree, and normalization factors.
    # For now, returning a simple header indicating Chebyshev type.
    if not points: return b''
    
    # Example: Header 0x02, degree 5 (dummy), point_count
    header = bytearray([0x02, 5]) 
    header.extend(len(points).to_bytes(3, 'little')) # 24-bit point count
    # ... actual Chebyshev coefficient data would follow ...
    # For this placeholder, just add some dummy bytes to make it non-empty
    header.extend(b'\x00' * 20) # Dummy data
    return bytes(header)

# --- New proof creation function using local ECDSA key ---
def create_hwx_proof(user_id: str, data_to_sign: bytes, ecdsa_op_key: ECC.EccKey) -> Dict[str, Any]:
    """
    Creates a cryptographic proof (signature) for the given data using the user's ECDSA key.

    Args:
        user_id: The ID of the user, for context in the proof.
        data_to_sign: The bytes to be signed (e.g., a hash of the HWX content).
        ecdsa_op_key: The user's ECC private key object for signing.

    Returns:
        A dictionary representing the proof, including the signature and metadata.
    """
    try:
        hash_obj = SHA256.new(data_to_sign)
        signer = DSS.new(ecdsa_op_key, 'fips-186-3') # Digital Signature Standard with SHA
        signature_bytes = signer.sign(hash_obj)
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        # Export public key in PEM format to include in the proof for verifiability
        # This allows verification without needing to re-derive/fetch the public key separately,
        # if the verifier trusts the source of this proof block.
        public_key_pem = ecdsa_op_key.public_key().export_key(format='PEM')

        proof = {
            "type": "ECDSA_P256_SHA256_Local", # Using NIST P-256 curve via ECC module
            "signature_b64": signature_b64,
            "signer_public_key_pem": public_key_pem, 
            "hash_algorithm": "SHA256",
            "signature_algorithm": "ECDSA_FIPS-186-3", # Based on PyCryptodome DSS
            "user_id_context": user_id, # For context, not primary auth
            "timestamp_utc": datetime.now(timezone.utc).isoformat()
        }
        return proof
    except Exception as e:
        print(f"Error creating HWX proof for user {user_id}: {str(e)}")
        # Depending on policy, might raise an exception or return an error structure
        raise HTTPException(status_code=500, detail=f"Failed to create proof: {str(e)}") from e
# --- End of new proof creation function ---


@DeprecationWarning
def get_user_key(user_key_id: str) -> bytes:
    """DEPRECATED: Get user key from key storage or generate a temporary one for demo.
    This function is deprecated and will be removed. 
    Use get_hwx_operational_keys with a master passphrase instead.
    """
    print("WARNING: get_user_key is deprecated and will be removed. Use get_hwx_operational_keys instead.")
    # Existing demo logic remains for now to avoid breaking things immediately
    key_storage = db.storage.json.get("hwx_keys", default={})
    
    if user_key_id in key_storage:
        # Return stored key
        return base64.b64decode(key_storage[user_key_id])
    else:
        # For demo/testing, generate a key deterministically from ID
        # In production, this would come from a secure key management system
        seed = f"hwx-demo-key-{user_key_id}".encode('utf-8')
        key_hash = hashlib.sha256(seed).digest()
        
        # Store it for future reference
        key_storage[user_key_id] = base64.b64encode(key_hash).decode('utf-8')
        db.storage.json.put("hwx_keys", key_storage)
        
        return key_hash

def sign_data(kms_client: any, kms_signing_key_version_name: str, data_digest_for_signing: bytes) -> Dict[str, str]: # kms_client type hinted as any for now
    """Sign data with the KMS asymmetric signing key."""
    # This function currently uses a mock KMS client setup if not configured.
    # For actual KMS, kms_client should be kms_v1.KeyManagementServiceClient
    # and properly initialized.
    print("WARNING: sign_data using KMS is likely using a MOCK client if not fully configured.")
    try:
        # Placeholder for actual KMS client usage. For now, this will likely fail or use mock
        # if kms_client is not a real KMS client.
        # response = kms_client.asymmetric_sign(
        #     name=kms_signing_key_version_name,
        #     digest={'sha256': data_digest_for_signing}
        # )
        # signature_b64 = base64.b64encode(response.signature).decode('utf-8')
        
        # Fallback to a deterministic signature for testing if KMS is not live
        # This is NOT secure and only for placeholder functionality.
        mock_signature_seed = kms_signing_key_version_name.encode() + data_digest_for_signing
        mock_signature_bytes = hashlib.sha256(mock_signature_seed).digest()
        signature_b64 = base64.b64encode(mock_signature_bytes).decode('utf-8')

        return {
            "signature": signature_b64,
            "algorithm": "MOCK_KMS_ASYMMETRIC_SIGN_SHA256" # Clearly indicate it's mocked
        }
    except Exception as e:
        print(f"KMS asymmetric signing (or mock fallback) failed: {e}")
        raise HTTPException(status_code=500, detail=f"KMS asymmetric signing failed: {str(e)}") from e


def decompress_chebyshev(compressed_data: bytes) -> List[Point2D]:
    """Decompress data encoded with Chebyshev polynomial compression
    
    This function reconstructs the original points from Chebyshev polynomial coefficients.
    It's the counterpart to compress_chebyshev and follows the same mathematical principles.
    
    Args:
        compressed_data: Bytes containing Chebyshev-encoded data
    
    Returns:
        List of reconstructed 2D points
    """
    if len(compressed_data) < 2 or compressed_data[0] != 0x02:
        # Not Chebyshev encoded or invalid format
        return []
    
    # Extract degree from data
    degree = compressed_data[1]
    
    # Verify minimum required data length
    min_length = 2 + 16 + (degree + 1) * 8 + 3  # header + normalization + coefficients + point count
    if len(compressed_data) < min_length:
        print(f"Invalid Chebyshev data: too short ({len(compressed_data)} < {min_length})")
        return []
    
    offset = 2  # Skip header and degree
    
    # Extract normalization factors
    try:
        x_scale = struct.unpack('<f', compressed_data[offset:offset+4])[0]
        offset += 4
        y_scale = struct.unpack('<f', compressed_data[offset:offset+4])[0]
        offset += 4
        x_offset = struct.unpack('<f', compressed_data[offset:offset+4])[0]
        offset += 4
        y_offset = struct.unpack('<f', compressed_data[offset:offset+4])[0]
        offset += 4
    except Exception as e:
        print(f"Error unpacking normalization factors: {e}")
        return []
    
    # Extract coefficients
    x_coeffs = []
    y_coeffs = []
    for _ in range(degree + 1):
        try:
            x_coeffs.append(struct.unpack('<f', compressed_data[offset:offset+4])[0])
            offset += 4
            y_coeffs.append(struct.unpack('<f', compressed_data[offset:offset+4])[0])
            offset += 4
        except Exception as e:
            print(f"Error unpacking coefficients: {e}")
            return [] # Error during coefficient extraction
            
    # Extract point count
    try:
        point_count = int.from_bytes(compressed_data[offset:offset+3], 'little')
        offset += 3
    except Exception as e:
        print(f"Error unpacking point count: {e}")
        return []
    
    # Reconstruct points
    points = []
    if point_count > 0:
        # The parameter t for Chebyshev polynomials typically ranges from -1 to 1.
        # We need to map the point index (0 to point_count-1) to this range.
        for i in range(point_count):
            t = -1.0 + 2.0 * i / (point_count - 1 if point_count > 1 else 1) 
            
            x_val_normalized = sum(c * chebyshev_t(k, t) for k, c in enumerate(x_coeffs))
            y_val_normalized = sum(c * chebyshev_t(k, t) for k, c in enumerate(y_coeffs))
            
            # Denormalize
            x_val = x_val_normalized * x_scale + x_offset
            y_val = y_val_normalized * y_scale + y_offset
            points.append(Point2D(x=x_val, y=y_val))
            
    return points

def chebyshev_t(n: int, x: float) -> float:
    """Evaluates the nth Chebyshev polynomial of the first kind at x."""
    if n == 0:
        return 1.0
    elif n == 1:
        return x
    else:
        # T_n(x) = 2*x*T_{n-1}(x) - T_{n-2}(x)
        # Iterative calculation to avoid deep recursion
        t_prev = 1.0 # T_0(x)
        t_curr = x   # T_1(x)
        for _ in range(2, n + 1):
            t_next = 2 * x * t_curr - t_prev
            t_prev = t_curr
            t_curr = t_next
        return t_curr

# --- API Endpoints ---

# @router.post("/generate-key", response_model=GenerateKeyResponse, tags=["demo"])
# async def generate_key_endpoint(request: GenerateKeyRequest):
#     """DEPRECATED: Generates a unique key ID for a user and stores a derived key.
#     This is a demo endpoint and should not be used for production key management.
#     It will be replaced by secure key setup using master passphrase.
#     """
#     # In a real system, you'd use a secure key generation and management service.
#     # For this demo, we'll just create a unique ID and a deterministic key based on it.
#     key_id = f"hwx_key_{request.user_id}_{int(datetime.now().timestamp())}"
    
#     # Generate a pseudo-key (SHA256 hash of the key_id for simplicity)
#     # WARNING: This is NOT cryptographically secure key generation for production.
#     pseudo_key_bytes = hashlib.sha256(key_id.encode('utf-8')).digest()
    
#     # Store the key (base64 encoded) in db.storage.json - simple key store for demo
#     key_storage = db.storage.json.get("hwx_keys", default={})
#     key_storage[key_id] = base64.b64encode(pseudo_key_bytes).decode('utf-8')
#     db.storage.json.put("hwx_keys", key_storage)
    
#     return GenerateKeyResponse(key_id=key_id, message="Demo key ID generated and stored. Use /setup-hwx-keys for secure setup.")

@router.post("/encode", tags=["hwx-core"], summary="Encode 3D points into HWX format with payload encryption")
async def encode_hyperspace_path_endpoint(request: HWXEncodeRequest, user: AuthorizedUser):
    user_id = user.sub
    try:
        aes_op_key, ecdsa_op_key = get_hwx_operational_keys(user_id, request.master_passphrase)
    except HTTPException as e:
        # Pass through HTTPException from get_hwx_operational_keys (e.g., 401, 404)
        raise e
    except Exception as e:
        print(f"Failed to get operational keys for user {user_id} during encode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Key retrieval failed: {str(e)}") from e

    points = request.points
    if not points:
        raise HTTPException(status_code=400, detail="No points provided for encoding.")

    if request.compression_type == 1:
        compressed_stroke_data = compress_delta(points)
    elif request.compression_type == 2:
        # For Chebyshev, points are expected to be 2D if using the current decompress_chebyshev.
        # If points are 3D, compress_chebyshev needs to handle 3D or this needs adjustment.
        # Assuming compress_chebyshev will be updated or expects 2D for now.
        # points_2d = [Point2D(x=p.x, y=p.y) for p in points] # Convert if necessary
        compressed_stroke_data = compress_chebyshev(points) # Pass 3D points, compress_chebyshev should handle
    else:
        raise HTTPException(status_code=400, detail="Invalid compression type specified.")

    svg_path = points_to_svg_path(points)
    
    # Create a unique ID for this HWX data block
    hwx_id = f"hwx_{user_id}_{int(datetime.now().timestamp())}_{get_random_bytes(4).hex()}"
    
    # Payload will be the compressed stroke data itself for now, encrypted
    # A more complex payload could include metadata, timestamps, etc.
    payload_to_encrypt = compressed_stroke_data
    
    try:
        cipher = AES.new(aes_op_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(payload_to_encrypt)
        payload_components = {
            "nonce_b64": base64.b64encode(cipher.nonce).decode('utf-8'),
            "ciphertext_b64": base64.b64encode(ciphertext).decode('utf-8'),
            "tag_b64": base64.b64encode(tag).decode('utf-8')
        }
    except Exception as e:
        print(f"Error encrypting payload for HWX ID {hwx_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payload encryption failed: {str(e)}") from e

    stroke_table_entry = StrokeTable(
        path_data=svg_path, 
        style_id=request.style_id, # User can specify style
        payload_components=payload_components,
        point_count=len(points),
        chebyshev_degree=None # Or determine if Chebyshev was used
    )

    # Prepare data for signing proof
    # For example, sign the HWX ID and the encrypted payload's ciphertext
    # Concatenate hwx_id and the ciphertext of the payload for signing
    # Ensure ciphertext_b64 is available from payload_components
    if not payload_components or 'ciphertext_b64' not in payload_components:
        print(f"Error: Ciphertext missing in payload_components for HWX ID {hwx_id}")
        raise HTTPException(status_code=500, detail="Failed to prepare data for proof: Ciphertext missing.")

    data_to_sign_str = f"{hwx_id}:{payload_components['ciphertext_b64']}"
    data_to_sign_bytes = data_to_sign_str.encode('utf-8')

    proof_included_flag = False
    proofs_list = []
    try:
        proof = create_hwx_proof(user_id, data_to_sign_bytes, ecdsa_op_key)
        proofs_list.append(proof)
        proof_included_flag = True
        print(f"Successfully created proof for HWX ID {hwx_id}")
    except Exception as e:
        print(f"Warning: Could not create proof for HWX ID {hwx_id}: {str(e)}. Proceeding without proof.")
        # Optionally, raise HTTPException here if proofs are mandatory

    hwx_container = HWXContainer(version=1, strokes=[stroke_table_entry], proofs=proofs_list)

    # Store the HWX container in db.storage.json, keyed by hwx_id
    try:
        db.storage.json.put(f"hwx_data/{hwx_id}", hwx_container.model_dump(exclude_none=True))
        
        encodings_data = db.storage.json.get("hwx_encodings", default={})
        encodings_data[hwx_id] = {
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "description": f"Encoded stroke, style {request.style_id}",
            "compression_type": request.compression_type,
            "original_point_count": len(points),
            "compressed_data_size": len(payload_to_encrypt),
            "svg_path_preview": svg_path[:200] + "..." if len(svg_path) > 200 else svg_path,
        }
        db.storage.json.put("hwx_encodings", encodings_data)

    except Exception as e:
        print(f"Error storing HWX data for ID {hwx_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store HWX data: {str(e)}") from e

    return {
        "hwx_id": hwx_id, 
        "message": "HWX data encoded, encrypted, and stored successfully.",
        "svg_path_preview": svg_path,
        "proof_included": proof_included_flag
    }

@router.post("/decode", response_model=List[Point3D], tags=["hwx-core"], summary="Decode HWX data and decrypt payload")
async def decode_hwx_endpoint(request: HWXDecodeRequest, user: AuthorizedUser):
    user_id = user.sub
    try:
        aes_op_key, _ = get_hwx_operational_keys(user_id, request.master_passphrase)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Failed to get operational keys for user {user_id} during decode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Key retrieval failed: {str(e)}") from e

    try:
        hwx_data_key = f"hwx_data/{request.hwx_id}"
        stored_hwx_container_dict = db.storage.json.get(hwx_data_key)
        if not stored_hwx_container_dict:
            raise HTTPException(status_code=404, detail="HWX data not found for the given ID.")
        
        # Validate with Pydantic model
        hwx_container = HWXContainer(**stored_hwx_container_dict)

    except FileNotFoundError: # Explicitly catch if get() doesn't find and no default is set for some reason
        raise HTTPException(status_code=404, detail="HWX data not found (FileNotFound).")
    except Exception as e: # Catch Pydantic validation errors or other issues
        print(f"Error loading/validating HWX container for ID {request.hwx_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invalid HWX data format or load error: {str(e)}") from e

    if not hwx_container.strokes or not hwx_container.strokes[0].payload_components:
        raise HTTPException(status_code=400, detail="No encrypted payload found in HWX data.")

    payload_components = hwx_container.strokes[0].payload_components
    try:
        nonce = base64.b64decode(payload_components['nonce_b64'])
        ciphertext = base64.b64decode(payload_components['ciphertext_b64'])
        tag = base64.b64decode(payload_components['tag_b64'])
        
        cipher = AES.new(aes_op_key, AES.MODE_GCM, nonce=nonce)
        decrypted_payload = cipher.decrypt_and_verify(ciphertext, tag)
    except (ValueError, KeyError) as e: # Catches MAC check failed, key incorrect or missing dict keys
        print(f"Decryption failed for HWX ID {request.hwx_id} (user {user_id}): {str(e)}")
        raise HTTPException(status_code=401, detail="Decryption failed. Invalid master passphrase or corrupted data.") from e
    except Exception as e:
        print(f"General error during payload decryption for HWX ID {request.hwx_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payload decryption error: {str(e)}") from e

    # Determine compression type from stored data or request override
    # For simplicity, let's assume the first byte of decrypted_payload indicates type if not overridden
    compression_type_to_use = request.compression_type
    if compression_type_to_use is None and decrypted_payload:
        # Infer from payload if possible (e.g., 0x01 for delta, 0x02 for Chebyshev)
        # This is a simplified inference. A more robust system might store type explicitly.
        payload_type_indicator = decrypted_payload[0]
        if payload_type_indicator == 0x01:
            compression_type_to_use = 1
        elif payload_type_indicator == 0x02:
            compression_type_to_use = 2
        else:
            # Fallback or error if type cannot be inferred and isn't specified
            print(f"Could not infer compression type from payload for HWX ID {request.hwx_id}")
            # Defaulting to delta if not specified and not inferable
            compression_type_to_use = 1 
    elif compression_type_to_use is None and not decrypted_payload:
         raise HTTPException(status_code=400, detail="No payload to decompress and compression type not specified.")

    if compression_type_to_use == 1:
        decompressed_points = decompress_delta(decrypted_payload)
    elif compression_type_to_use == 2:
        # decompress_chebyshev expects 2D points as per its current implementation
        # If the payload was from 3D points, this might need adjustment
        # or decompress_chebyshev needs to handle 3D->2D reconstruction if that was the intent.
        points_2d = decompress_chebyshev(decrypted_payload)
        # Convert 2D points from Chebyshev back to 3D points with z=0, or fetch z if stored separately
        decompressed_points = [Point3D(x=p.x, y=p.y, z=0.0) for p in points_2d] 
    else:
        raise HTTPException(status_code=400, detail="Invalid or unsupported compression type for decompression.")

    return decompressed_points


@router.post("/anchor-hwx", tags=["hwx-core"], summary="Create a proof for HWX data using user's local key")
async def anchor_hwx_data_endpoint(request: HWXAnchorRequest, user: AuthorizedUser):
    user_id = user.sub
    try:
        _, ecdsa_op_key = get_hwx_operational_keys(user_id, request.master_passphrase)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Failed to get operational keys for user {user_id} during anchor: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Key retrieval failed: {str(e)}") from e

    hwx_data_key = f"hwx_data/{request.hwx_id}"
    try:
        hwx_container_dict = db.storage.json.get(hwx_data_key)
        if not hwx_container_dict:
            raise HTTPException(status_code=404, detail="HWX data not found for anchoring.")
        hwx_container = HWXContainer(**hwx_container_dict)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HWX data not found (FileNotFound).")
    except Exception as e:
        print(f"Error loading HWX container for anchoring (ID {request.hwx_id}): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invalid HWX data format or load error: {str(e)}") from e

    # For anchoring, we typically sign the content or a hash of it.
    # Here, let's sign the JSON representation of the strokes data for simplicity.
    # A more robust approach might involve canonicalizing and hashing specific fields.
    if not hwx_container.strokes:
        raise HTTPException(status_code=400, detail="No strokes found in HWX data to anchor.")

    # Serialize the strokes part to a canonical JSON string for signing
    # Using model_dump_json ensures a consistent representation if Pydantic is used for serialization.
    # We only sign the strokes, not existing proofs, to avoid circular dependencies if re-anchoring.
    strokes_json_for_signing = HWXContainer(version=hwx_container.version, strokes=hwx_container.strokes, proofs=[]).model_dump_json()
    data_to_sign_bytes = strokes_json_for_signing.encode('utf-8')
    
    try:
        proof = create_hwx_proof(user_id, data_to_sign_bytes, ecdsa_op_key)
        hwx_container.proofs.append(proof)
        
        # Update the stored HWX container with the new proof
        db.storage.json.put(hwx_data_key, hwx_container.model_dump(exclude_none=True))
        return {"message": "HWX data anchored successfully with local key.", "proof": proof, "hwx_id": request.hwx_id}
    except HTTPException as e: # If create_hwx_proof raises an HTTPException
        raise e
    except Exception as e:
        print(f"Error creating or storing proof for HWX ID {request.hwx_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anchoring failed: {str(e)}") from e


@router.post("/generate-sample", tags=["demo"], summary="Generate sample HWX data (e.g., spiral, signature)")
async def generate_sample_hwx_data(
    request: HWXSampleRequest, 
    # user: AuthorizedUser # Not strictly needed if it's just generating sample points, unless we auto-encode/store
):
    """Generates sample point data for HWX. 
    Does NOT automatically encode or store it through the secure pipeline yet.
    This is a helper to get point data for testing the /encode endpoint.
    """
    points: List[Point3D] = []
    num_points = request.length
    complexity = request.complexity

    if request.sample_type == "spiral":
        # Simple logarithmic spiral in 2D (z=0)
        a = 0.5  # Controls tightness
        b = 0.1 * complexity # Controls expansion rate
        for i in range(num_points):
            theta = i * 0.1 * (1 + complexity/10) # Angle
            r = a * воплотила**(b * theta) # Using Russian word for exp for fun, translates to "embodied" or e
            # Let's use math.exp for clarity if math is imported, or a constant like 2.71828
            # For now, let's use a simple r = a * (1 + b*theta/num_points) to avoid large numbers quickly
            # Corrected spiral formula for better visual:
            r_factor = 50 + complexity * 10 # Scale factor
            theta_factor = 0.1 + complexity * 0.05
            r = r_factor * theta_factor * (i + 1) # Linear growth for simplicity for now
            x = r * (theta_factor * (i+1) * 0.1) # Cosine part missing, simplified for non-circular spiral
            y = r * (theta_factor * (i+1) * 0.05) # Sine part missing
            # A better spiral:
            k = 0.1 * complexity
            x = (a + b * theta) * (theta * k) # math.cos(theta)
            y = (a + b * theta) * (theta * k*0.5) # math.sin(theta)
            # Let's try again with a standard Archimedean spiral for simplicity
            # r = a + b * θ
            # x = r * cos(θ)
            # y = r * sin(θ)
            # For simplicity, we'll make a pseudo-spiral that looks somewhat like handwriting strokes
            scale = 100 + complexity * 20
            for i in range(num_points):
                angle_rad = (i / num_points) * (2 * 3.1415926535 * (complexity / 2.0)) # angle in radians
                radius = scale * (i / num_points) # radius increases with i
                x = radius * (angle_rad * 0.1) # simplified cos
                y = radius * (angle_rad * 0.05) # simplified sin
                z = i * (complexity / 10.0) # z increases with i and complexity
                points.append(Point3D(x=round(x,2), y=round(y,2), z=round(z,2)))
            # To avoid duplicates if loop was reset, clear points list first if it was a copy-paste error:
            if len(points) > num_points: points = points[:num_points] # Ensure correct length if logic above was messy
            # If points still empty or too short due to loop error, generate simple line
            if not points or len(points) < 2:
                points = [Point3D(x=i*10.0, y=i*5.0, z=float(i)) for i in range(num_points if num_points > 0 else 2)]

    elif request.sample_type == "signature":
        # Simplified "signature-like" pattern
        for i in range(num_points):
            x = i * (1 + complexity/5.0)
            # Simulate some up and down movement for signature
            y_base = 50 * ( (i % (20 + complexity * 2)) / (10.0 + complexity) - 0.5) # Sinusoidal-like based on modulo
            y_random_jitter = (get_random_bytes(1)[0] / 255.0 - 0.5) * 10 * (complexity/2.0) # Add some randomness
            y = y_base + y_random_jitter
            z = (i / num_points) * 5.0 # Slight increase in z
            points.append(Point3D(x=round(x,2), y=round(y,2), z=round(z,2)))
        if not points: # Ensure points if loop failed
            points = [Point3D(x=i*15.0, y=10.0, z=1.0) for i in range(num_points if num_points > 0 else 2)]
    else:
        raise HTTPException(status_code=400, detail="Invalid sample_type specified.")

    if not points:
        # Default to a simple line if no points were generated for some reason
        points = [Point3D(x=float(i*2), y=float(i), z=0.0) for i in range(max(2, num_points))]

    return {"sample_name": request.sample_type, "point_count": len(points), "points": points}


# @router.get("/kms-test-sign") # Example, not for production use without securing this endpoint
# async def kms_test_sign():
#     """FOR TESTING KMS Connection & Signing ONLY. DO NOT EXPOSE PUBLICLY.
#     This endpoint requires Google Cloud credentials to be set up in the environment.
#     """
#     try:
#         kms_client = kms_v1.KeyManagementServiceClient()
#         data_to_sign = b"Test data for KMS signing"
#         data_digest = hashlib.sha256(data_to_sign).digest()
        
#         signature_info = sign_data(kms_client, kms_signing_key_version_name, data_digest)
#         return {"message": "KMS Test Sign Successful (check logs for details)", "signature_info": signature_info}
#     except Exception as e:
#         print(f"KMS Test Sign Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
