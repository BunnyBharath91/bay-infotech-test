"""
Chat API endpoint.
Implements the mandatory execution order for processing chat requests.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_llm, get_embeddings
from app.schemas.chat import ChatRequest, ChatResponse, GuardrailResult, KBReference
from app.core.guardrails import check_guardrails
from app.core.tiering import classify_tier, detect_issue_type
from app.core.severity import classify_severity, is_security_sensitive, has_data_loss_risk
from app.core.escalation import should_escalate, get_escalation_reason, detect_multiple_users_affected
from app.rag.retrieval import retrieve_kb_chunks, check_kb_coverage
from app.rag.embeddings import EmbeddingService
from app.llm.provider import LLMProvider
from app.llm.prompt_builder import build_system_prompt, format_conversation_history
from app.db.repositories import (
    ConversationRepository,
    MessageRepository,
    TicketRepository,
    GuardrailEventRepository,
    AnalyticsEventRepository
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    llm: LLMProvider = Depends(get_llm),
    embeddings: EmbeddingService = Depends(get_embeddings)
) -> ChatResponse:
    """
    Process chat request with mandatory execution order:
    1. Validate request
    2. Load conversation history
    3. Run guardrail checks
    4. Retrieve KB chunks
    5. Check KB coverage
    6. Compute tier, severity, escalation (rule-based)
    7. Generate answer using ONLY KB content
    8. Store conversation
    9. Return structured response
    """
    logger.info(f"Processing chat request for session: {request.sessionId}")
    
    # Initialize repositories
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    ticket_repo = TicketRepository(db)
    guardrail_repo = GuardrailEventRepository(db)
    analytics_repo = AnalyticsEventRepository(db)
    
    # Step 1: Validate request (handled by Pydantic)
    
    # Step 2: Load conversation history
    conversation = await conv_repo.get_or_create_conversation(
        session_id=request.sessionId,
        user_role=request.userRole.value
    )
    
    history = await msg_repo.get_conversation_history(
        session_id=request.sessionId,
        limit=10
    )
    
    # Count resolution attempts (how many times user said it didn't work)
    resolution_attempts = sum(
        1 for msg in history
        if msg.role == "user" and any(
            phrase in msg.content.lower()
            for phrase in ["didn't work", "not working", "still doesn't", "not resolved"]
        )
    )
    
    logger.info(f"Loaded {len(history)} messages, {resolution_attempts} resolution attempts")
    
    # Step 3: Run guardrail checks
    guardrail_result = check_guardrails(request.message, request.userRole)
    
    if guardrail_result.blocked:
        logger.warning(f"Guardrail blocked request: {guardrail_result.trigger_type}")
        
        # Log guardrail event
        await guardrail_repo.create_event(
            session_id=request.sessionId,
            trigger_type=guardrail_result.trigger_type,
            blocked=True,
            user_message=request.message,
            metadata={"severity": guardrail_result.severity}
        )
        
        # Track analytics
        await analytics_repo.create_event(
            event_type="guardrail_blocked",
            session_id=request.sessionId,
            metadata={"trigger_type": guardrail_result.trigger_type}
        )
        
        # Return blocked response
        return ChatResponse(
            answer=guardrail_result.reason,
            kbReferences=[],
            confidence=1.0,
            tier="TIER_1",  # Blocked requests go to Tier 1 for review
            severity=guardrail_result.severity,
            needsEscalation=guardrail_result.severity in ["HIGH", "CRITICAL"],
            guardrail=GuardrailResult(
                blocked=True,
                reason=guardrail_result.reason,
                trigger_type=guardrail_result.trigger_type
            ),
            sessionId=request.sessionId
        )
    
    # Step 4: Retrieve KB chunks
    kb_chunks = await retrieve_kb_chunks(
        query=request.message,
        user_role=request.userRole,
        session=db,
        embedding_service=embeddings
    )
    
    logger.info(f"Retrieved {len(kb_chunks)} KB chunks")
    
    # Step 5: Check KB coverage
    kb_coverage = await check_kb_coverage(kb_chunks)
    
    if not kb_coverage:
        logger.warning("No KB coverage for query")
        
        # Track analytics
        await analytics_repo.create_event(
            event_type="no_kb_coverage",
            session_id=request.sessionId
        )
        
        # Return no-KB response
        return ChatResponse(
            answer="This issue is not covered in the knowledge base. A support engineer will assist you.",
            kbReferences=[],
            confidence=0.0,
            tier="TIER_1",
            severity="MEDIUM",
            needsEscalation=True,
            guardrail=GuardrailResult(blocked=False),
            sessionId=request.sessionId
        )
    
    # Step 6: Compute tier, severity, escalation (rule-based)
    issue_type = detect_issue_type(request.message, kb_chunks)
    multiple_users = detect_multiple_users_affected(request.message)
    security_sensitive = is_security_sensitive(request.message, issue_type)
    data_loss_risk = has_data_loss_risk(issue_type, request.message)
    
    # Classify tier
    tier = classify_tier(
        issue_type=issue_type,
        resolution_attempts=resolution_attempts,
        kb_coverage=kb_coverage,
        user_role=request.userRole,
        multiple_users_affected=multiple_users,
        is_critical=(issue_type in ["kernel_panic", "systemic_outage"])
    )
    
    # Classify severity
    severity = classify_severity(
        issue_type=issue_type,
        users_affected=10 if multiple_users else 1,
        blocking="can't" in request.message.lower() or "unable" in request.message.lower(),
        security_sensitive=security_sensitive,
        data_loss_risk=data_loss_risk
    )
    
    # Determine escalation
    needs_escalation = should_escalate(
        tier=tier,
        severity=severity,
        resolution_attempts=resolution_attempts,
        guardrail_blocked=False,
        issue_type=issue_type,
        kb_coverage=kb_coverage
    )
    
    logger.info(f"Classification: tier={tier}, severity={severity}, escalation={needs_escalation}")
    
    # Step 7: Generate answer using ONLY KB content
    system_prompt = build_system_prompt(kb_chunks, request.userRole)
    
    # Format conversation history for LLM
    history_for_llm = format_conversation_history([
        {"role": msg.role, "content": msg.content}
        for msg in history[-5:]  # Last 5 messages for context
    ])
    
    try:
        answer = await llm.generate(
            system_prompt=system_prompt,
            user_message=request.message,
            conversation_history=history_for_llm,
            temperature=0.0  # Deterministic
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        answer = "I apologize, but I'm having trouble processing your request. Please try again or contact support."
    
    # Step 8: Store conversation
    await msg_repo.create_message(
        session_id=request.sessionId,
        role="user",
        content=request.message
    )
    
    await msg_repo.create_message(
        session_id=request.sessionId,
        role="assistant",
        content=answer,
        metadata={
            "tier": tier.value,
            "severity": severity.value,
            "issue_type": issue_type
        }
    )
    
    # Create ticket if escalation needed
    ticket_id = None
    if needs_escalation:
        escalation_reason = get_escalation_reason(
            tier=tier,
            severity=severity,
            resolution_attempts=resolution_attempts,
            guardrail_blocked=False,
            issue_type=issue_type,
            kb_coverage=kb_coverage
        )
        
        ticket = await ticket_repo.create_ticket(
            session_id=request.sessionId,
            tier=tier,
            severity=severity,
            subject=request.message[:100],
            description=f"Issue: {request.message}\n\nReason: {escalation_reason}"
        )
        ticket_id = ticket.id
        logger.info(f"Created ticket: {ticket_id}")
    
    # Track analytics
    await analytics_repo.create_event(
        event_type="chat_interaction",
        session_id=request.sessionId,
        metadata={
            "tier": tier.value,
            "severity": severity.value,
            "escalated": needs_escalation,
            "issue_type": issue_type
        }
    )
    
    # Step 9: Return structured response
    kb_references = [
        KBReference(
            id=chunk.kb_document_id,
            title=chunk.document.title if chunk.document else chunk.kb_document_id,
            version=chunk.document.version if chunk.document else None,
            relevance_score=None  # Could add similarity scores
        )
        for chunk in kb_chunks[:3]  # Top 3 references
    ]
    
    # Calculate confidence based on KB coverage and chunk relevance
    confidence = 0.9 if len(kb_chunks) >= 3 else 0.7
    
    return ChatResponse(
        answer=answer,
        kbReferences=kb_references,
        confidence=confidence,
        tier=tier,
        severity=severity,
        needsEscalation=needs_escalation,
        guardrail=GuardrailResult(blocked=False),
        ticketId=ticket_id,
        sessionId=request.sessionId
    )
