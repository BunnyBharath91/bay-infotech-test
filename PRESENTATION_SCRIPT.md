# AI Help Desk Platform - Video Presentation Script

## Duration: 5-7 minutes

---

## [00:00 - 00:30] Introduction & Project Overview

### **What to Say:**

"Hello! My name is Bharath Kumar Borra and I'm from India. I'm excited to present my full-stack AI Help Desk Platform.

### **What to Display:**

- [Show README.md or project overview slide]
- [Show key requirements checklist from test document]

---

## [00:30 - 01:30] Architecture Overview

### **What to Say:**

"First, Let me walk you through the architecture. So, the system follows a clean, layered architecture with clear separation of concerns.

**Frontend:** Built with React and Vite deployed on vercel. It shows real-time typing indicators and role-based access control.

**Backend:** FastAPI-based REST API deployed on railway. It handles all business logic, RAG processing, and guardrail enforcement.

**Database:** PostgreSQL with pgvector extension for vector similarity search. This allows us to store and retrieve knowledge base chunks efficiently.

The system follows a mandatory execution order: first, we validate the request, load conversation history, run guardrail checks, retrieve KB chunks, classify tier and severity using deterministic rules, generate the answer using only KB content, and finally return a structured response."

### **What to Display:**

- [Show ARCHITECTURE.md diagram or create a visual diagram]
- [Highlight: Frontend → Backend → Database flow]
- [Show the mandatory execution order from ARCHITECTURE.md]
- [Display technology stack: React, FastAPI, PostgreSQL, pgvector]

---

## [01:30 - 02:30] Core Features: RAG System

### **What to Say:**

"The heart of the system is the RAG - Retrieval-Augmented Generation - pipeline. This ensures all responses are grounded in our local knowledge base only, with zero hallucinations.

**Knowledge Base:** We have 11 structured markdown documents covering authentication, VM operations, container troubleshooting, DNS issues, and more. Each document has versioning, metadata, and tags.

**Ingestion Process:** Documents are chunked by markdown headings, preserving context. Each chunk gets a 384-dimensional embedding using Sentence Transformers - a local, offline-capable model.

**Retrieval:** When a user asks a question, we generate an embedding for their query and perform vector similarity search using cosine distance. We retrieve the top 5 most relevant chunks, filter by user role, and resolve any version conflicts by preferring newer documents.

**Generation:** The LLM - currently using Google Gemini - receives ONLY these retrieved chunks, along with a strict system prompt that forbids external knowledge. If no relevant KB chunks are found, the system explicitly states 'This is not covered in the knowledge base.'"
**Note: **: LLM is optional, we can run the project even without llm, it is just for format the retrieved data/response.

### **What to Display:**

- [Show KB file list from KB File List.md]
- [Show example KB document structure with frontmatter]
- [Display RAG pipeline diagram: Query → Embedding → Vector Search → Retrieval → LLM]
- [Show code snippet from retrieval.py or embeddings.py]
- [Highlight: "No external internet access" constraint]

---

## [02:30 - 03:00] Guardrails & Security

### **What to Say:**

"The system implements comprehensive guardrails using pure rule-based pattern matching - no LLM involvement in safety decisions.

**Forbidden Actions:** The system blocks requests for host access, attempts to disable logging, kernel debugging commands, editing system files, and destructive system-wide operations.

<!-- **Role-Based Restrictions:** Trainees and instructors cannot receive OS-level commands. The system enforces this at both the guardrail level and KB filtering level. -->

**Response:** When a guardrail is triggered, the system immediately blocks the request, provides a polite refusal without technical details.

This is completely deterministic - the same input always produces the same safety decision."

### **What to Display:**

- [Show guardrails.py code snippet showing FORBIDDEN_PATTERNS]
- [Show test cases from test_guardrails.py]
- [Display guardrail event logging structure]
- [Highlight: "Deterministic rule-based" approach]

---

## [03:00 - 04:00] Live Demo: Key Workflows

### **What to Say:**

"Let me demonstrate the system with some real workflows. First, let's open the deployed application."

### **Demo 1: Login Redirection Loop (Workflow 1)**

**What to Say:**
"I'll simulate a trainee reporting a login redirection loop issue. [Type: 'I keep getting redirected to the login page even after logging in.']"

**What to Display:**

- [Open live frontend URL: https://bay-infotech-bharath-kumar-borra.vercel.app]
- [Backend API: https://bay-infotech-test-production.up.railway.app]
- [Show chat interface]
- [Type the message]
- [Show response with:]
  - KB-grounded answer referencing authentication troubleshooting
  - Tier classification: TIER_2
  - Severity: MEDIUM
  - KB references with document IDs
  - Confidence score
  - Ticket creation if escalated

**What to Say:**
"Notice how the system provides KB-grounded troubleshooting steps, correctly classifies this as TIER_2 requiring a support engineer, and creates a ticket for tracking."

---

### **Demo 2: Security Violation (Workflow 5)**

**What to Say:**
"Now let's test the guardrails. [Type: 'How do I access the host machine behind my VM?']"

**What to Display:**

- [Type the message in chat]
- [Show blocked response:]
  - "Access to host machines or hypervisors is not permitted"
  - Guardrail indicator showing "BLOCKED"
  - No technical guidance provided
  - Event logged

**What to Say:**
"The system immediately blocked this request, provided a polite refusal without technical details, and logged it as a security event. This demonstrates our guardrail enforcement in action."

---

### **Demo 3: Critical Infrastructure Issue (Workflow 2)**

**What to Say:**
"Let's test a critical issue. [Type: 'My lab VM froze and shut down; I lost my work.']"

**What to Display:**

- [Type the message]
- [Show response with:]
  - KB-based recovery steps (snapshot restoration)
  - Tier: TIER_3 (Platform Engineering)
  - Severity: CRITICAL
  - Immediate ticket creation
  - High priority SLA

**What to Say:**
"The system correctly identified this as a critical infrastructure issue, and created a high-priority ticket. Notice how it provides KB-grounded recovery steps while ensuring proper escalation."

---

## [04:00 - 04:30] Escalation & Ticket Management

### **What to Say:**

"The system implements intelligent escalation logic that's completely deterministic. Escalation occurs when:

- A user indicates the recommended steps didn't work twice
- The issue has HIGH or CRITICAL severity
- There's no KB coverage for the issue
- A security-sensitive request is detected

When escalation is needed, the system automatically creates a ticket with:

- Full conversation context
- User role and course/module information
- Tier and severity classification
- Relevant timestamps and error messages

Let me show you the ticket management interface."

### **What to Display:**

- [Navigate to tickets endpoint or show API response]
- [Show ticket list with pagination]
- [Display a specific ticket with all metadata]
- [Highlight: Automatic ticket creation, context preservation]

---

## [04:30 - 05:00] Analytics Dashboard

### **What to Say:**

"The system tracks comprehensive analytics and metrics. Let me show you the analytics dashboard."

### **What to Display:**

- [Navigate to /api/metrics/summary endpoint or show dashboard]
- [Show metrics:]
  - Deflection rate (TIER_0 / total conversations)
  - Tickets by tier breakdown
  - Tickets by severity breakdown
  - Guardrail activations over time
  - Most common issue categories
  - Escalation counts

**What to Say:**
"These metrics help track system performance, identify common issues, monitor guardrail effectiveness, and measure the deflection rate - how many issues are resolved at Tier 0 without human intervention."

---

## [05:00 - 05:30] No-Internet Environment Design

### **What to Say:**

"One of the key requirements was designing for a no-internet, internal-only environment. The architecture is fully prepared for this:

**Current Setup:**

- Sentence Transformers runs locally - no API dependency
- All KB files and embeddings are stored locally in db
- LLM abstraction layer allows swapping providers

**For Offline Deployment:**

- Replace the hosted LLM with a self-hosted model like Llama, Mistral, or other open-source models
- The embedding model already runs locally
- All vector operations happen in the local database
- No external API calls are required

The system is designed with provider abstraction, so swapping from Google Gemini to a self-hosted model requires only configuration changes, not code changes."

### **What to Display:**

- [Show LLM provider abstraction code]
- [Highlight: "Offline-ready architecture" section from ARCHITECTURE.md]
- [Show how to swap providers in configuration]

---

## [05:30 - 06:00] Testing & Quality Assurance

### **What to Say:**

"The system includes comprehensive testing at multiple levels:

**Unit Tests:** We have tests for guardrails, tiering, severity classification, and escalation logic - all ensuring deterministic behavior.

**Integration Tests:** API endpoints are tested with real database interactions.

**End-to-End Tests:** Complete workflows are tested, including all 12 required scenarios from the test document.

**Test Coverage:** The test suite covers authentication loops, VM crashes, guardrail activations, container issues, DNS problems, and adversarial prompts.

### **What to Display:**

- [Show test results or test file structure]
- [Highlight test coverage from TESTING.md]
- [Show example test cases]

---

## [06:00 - 06:30] Deployment & Production Readiness

### **What to Say:**

"The system is fully deployed and publicly accessible:

**Frontend:** Deployed on Vercel at https://bay-infotech-bharath-kumar-borra.vercel.app
**Backend:** Deployed on Railway at https://bay-infotech-test-production.up.railway.app
**Database:** PostgreSQL with pgvector is also deployed on railway as well. q

The deployment includes:

- Docker containerization for the backend
- Environment variable configuration
- Health check endpoints
- Structured logging
- Error handling and validation

The system is production-ready with proper error handling, logging, and monitoring."

### **What to Display:**

- [Show deployment URLs]
- [Show Dockerfile]
- [Show deployment configuration]
- [Highlight: "Production-ready" features]

---

## [06:30 - 07:00] Conclusion & Key Highlights

### **What to Say:**

"To summarize, this project:

✅ **KB-Grounded RAG System** - All responses sourced from local knowledge base only, zero hallucinations
✅ **Strict Guardrails** - Rule-based security enforcement with deterministic behavior
✅ **Intelligent Tiering** - Automatic classification from TIER_0 to TIER_3 based on issue complexity
✅ **Automated Escalation** - Smart ticket creation with full context preservation
✅ **Comprehensive Analytics** - Real-time metrics and insights
✅ **Production-Ready** - Fully deployed, tested, and documented
✅ **Offline-Capable** - Designed for no-internet environments

The system successfully handles all 12 required workflows, enforces guardrails correctly, provides accurate KB-grounded responses, and maintains deterministic behavior throughout.

Thank you for watching! The codebase, documentation, and deployment are all available in the repository. I'm happy to answer any questions."

### **What to Display:**

- [Show summary slide with checkmarks]
- [Show repository link]
- [Show documentation links]
- [Final architecture diagram]

---

## **Visual Cues & Tips:**

1. **Screen Recording Setup:**
   - Use a clean desktop background
   - Zoom in on code/UI when showing details
   - Use cursor highlighting if available
   - Keep browser tabs organized

2. **Code Display:**
   - Use a readable font size (14-16pt)
   - Highlight relevant sections
   - Show file paths clearly

3. **Live Demo:**
   - Have the application pre-loaded
   - Test all workflows before recording
   - Have example queries ready
   - Show both success and guardrail scenarios

4. **Timing:**
   - Practice the script to ensure 5-7 minutes
   - Allow time for natural pauses
   - Don't rush through technical details

5. **Engagement:**
   - Speak clearly and at a moderate pace
   - Emphasize key achievements
   - Show enthusiasm for the technical solutions

---

## **Backup Slides/Content (if time allows):**

- **KB Structure Details:** Show how documents are versioned and conflict resolution works
- **API Documentation:** Quick overview of endpoints
- **Database Schema:** Show table relationships
- **Future Enhancements:** Mention scalability considerations

---

**Total Estimated Time: 6-7 minutes**
