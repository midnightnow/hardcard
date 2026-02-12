from fastapi import APIRouter, Depends, HTTPException, Body, Header
from pydantic import BaseModel, Field
import databutton as db
from bitcoinlib.wallets import Wallet
from bitcoinlib.services.services import Service
import os
import qrcode
from io import BytesIO
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])

# --- Pydantic Models ---
class InvoiceRequest(BaseModel):
    amount_sats: int = Field(..., gt=0, description="Amount in satoshis")
    memo: str | None = None

class InvoiceResponse(BaseModel):
    payment_request: str = Field(description="The BOLT11 payment request")
    payment_hash: str = Field(description="The hash of the payment")
    qr_code: str | None = Field(description="Base64 encoded QR code of the payment request")

class AddressResponse(BaseModel):
    address: str = Field(description="The generated Bitcoin address")
    qr_code: str | None = Field(description="Base64 encoded QR code of the address")

class WebhookNotification(BaseModel):
    type: str # e.g., 'onchain', 'lightning'
    tx_hash: str | None = None
    invoice_id: str | None = None
    status: str

# --- Bitcoin On-Chain ---
def get_wallet():
    # In a real app, manage wallets more robustly. This is for demonstration.
    wallet_name = "nexusai_wallet"
    if not os.path.exists(wallet_name):
        wallet = Wallet.create(wallet_name, network='bitcoin')
        logger.info(f"Created new wallet: {wallet_name}")
    else:
        wallet = Wallet(wallet_name)
    return wallet






