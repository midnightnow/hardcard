from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/executor")

class TicketPayload(BaseModel):
    id: str
    type: str
    payload: dict

class ExecutionResponse(BaseModel):
    ok: bool
    result: str

@router.post("/execute", response_model=ExecutionResponse)
async def execute_ticket(ticket: TicketPayload):
    """
    Simulates executing a ticket. In a real scenario, this would
    trigger a longer-running process based on the ticket type.
    """
    print(f"Executing ticket {ticket.id} of type {ticket.type}")

    # Simulate different execution times based on ticket type
    if "HEAVY" in ticket.type:
        await asyncio.sleep(5)
        result = f"Heavy task {ticket.id} completed."
    elif "LIGHT" in ticket.type:
        await asyncio.sleep(1)
        result = f"Light task {ticket.id} completed."
    else:
        await asyncio.sleep(2)
        result = f"Standard task {ticket.id} completed."

    print(f"Execution finished for ticket {ticket.id}")
    return ExecutionResponse(ok=True, result=result)
