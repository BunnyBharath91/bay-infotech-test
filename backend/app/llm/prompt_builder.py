"""
Prompt construction for LLM.
Enforces KB-only grounding and proper instructions.
"""

import logging
from typing import List

from app.db.models import KBChunk
from app.schemas.chat import UserRole

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """You are a help desk assistant for the CyberLab Training Platform.

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:

1. Answer ONLY using the provided KB context below
2. NEVER invent commands, URLs, procedures, or policies
3. If the KB does not cover the issue, explicitly say: "This issue is not covered in the knowledge base."
4. Always cite KB document IDs when providing information (e.g., "According to kb-access-authentication...")
5. Do not use external knowledge or make assumptions
6. If you need clarifying information, ask specific questions
7. Follow the escalation and tiering rules documented in the KB

USER ROLE: {user_role}

KNOWLEDGE BASE CONTEXT:
{kb_context}

---

Based ONLY on the above KB context, provide a helpful, accurate response to the user's question.
If the KB does not contain the answer, say so explicitly and suggest escalation.
"""


NO_KB_SYSTEM_PROMPT = """You are a help desk assistant for the CyberLab Training Platform.

The knowledge base does not contain information relevant to the user's query.

Your response should:
1. Clearly state: "This issue is not covered in the knowledge base."
2. Suggest that the user's issue will be escalated to a support engineer
3. Ask if there are any other questions you can help with

Do NOT attempt to answer the question or provide guidance without KB coverage.
"""


def build_system_prompt(
    kb_chunks: List[KBChunk],
    user_role: UserRole
) -> str:
    """
    Build system prompt with KB context.
    
    Args:
        kb_chunks: Retrieved KB chunks
        user_role: User's role
    
    Returns:
        System prompt string
    """
    if not kb_chunks:
        logger.warning("No KB chunks provided, using no-KB prompt")
        return NO_KB_SYSTEM_PROMPT
    
    # Format KB context
    kb_context_parts = []
    for chunk in kb_chunks:
        doc_id = chunk.kb_document_id
        heading = chunk.heading_path or "Content"
        text = chunk.chunk_text
        
        kb_context_parts.append(
            f"[Document: {doc_id}]\n"
            f"[Section: {heading}]\n"
            f"{text}"
        )
    
    kb_context = "\n\n---\n\n".join(kb_context_parts)
    
    # Build full prompt
    prompt = SYSTEM_PROMPT_TEMPLATE.format(
        user_role=user_role.value,
        kb_context=kb_context
    )
    
    return prompt


def format_conversation_history(messages: List[dict]) -> List[dict]:
    """
    Format conversation history for LLM.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
    
    Returns:
        Formatted message list
    """
    formatted = []
    
    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')
        
        # Map database roles to LLM roles
        if role == 'assistant':
            llm_role = 'assistant'
        else:
            llm_role = 'user'
        
        formatted.append({
            "role": llm_role,
            "content": content
        })
    
    return formatted


def should_ask_clarifying_questions(
    user_message: str,
    kb_chunks: List[KBChunk]
) -> bool:
    """
    Determine if clarifying questions should be asked.
    
    Args:
        user_message: User's message
        kb_chunks: Retrieved KB chunks
    
    Returns:
        True if clarifying questions are needed
    """
    # Check if KB chunks mention clarifying questions
    for chunk in kb_chunks:
        text = chunk.chunk_text.lower()
        if "clarifying question" in text or "ask:" in text or "verify with user" in text:
            return True
    
    # Check if message is vague
    vague_indicators = ["issue", "problem", "not working", "help", "broken"]
    message_lower = user_message.lower()
    
    if any(indicator in message_lower for indicator in vague_indicators):
        # Message is vague and might need clarification
        if len(user_message.split()) < 10:  # Short message
            return True
    
    return False
