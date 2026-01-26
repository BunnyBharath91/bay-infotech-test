"""
Tickets API endpoint.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.ticket import TicketResponse, TicketListResponse
from app.db.repositories import TicketRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tickets", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> TicketListResponse:
    """
    List all tickets with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of tickets per page
        db: Database session
    
    Returns:
        Paginated list of tickets
    """
    ticket_repo = TicketRepository(db)
    
    skip = (page - 1) * page_size
    tickets, total = await ticket_repo.get_all_tickets(skip=skip, limit=page_size)
    
    return TicketListResponse(
        tickets=[TicketResponse.model_validate(ticket) for ticket in tickets],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Get a specific ticket by ID.
    
    Args:
        ticket_id: Ticket ID
        db: Database session
    
    Returns:
        Ticket details
    """
    ticket_repo = TicketRepository(db)
    
    ticket = await ticket_repo.get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return TicketResponse.model_validate(ticket)


@router.get("/tickets/session/{session_id}", response_model=list[TicketResponse])
async def get_session_tickets(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> list[TicketResponse]:
    """
    Get all tickets for a specific session.
    
    Args:
        session_id: Session ID
        db: Database session
    
    Returns:
        List of tickets for the session
    """
    ticket_repo = TicketRepository(db)
    
    tickets = await ticket_repo.get_tickets_by_session(session_id)
    
    return [TicketResponse.model_validate(ticket) for ticket in tickets]
