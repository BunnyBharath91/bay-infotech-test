# Knowledge Base Structure

## Overview

The Knowledge Base (KB) is the single source of truth for the AI Help Desk. All responses must be grounded in KB content.

## File Format

KB files are markdown documents with YAML frontmatter.

### Example KB File

```markdown
---
id: kb-access-authentication
title: Access and Authentication Troubleshooting
version: 2.1
last_updated: 2024-04-10
tags: [authentication, sso, login, access]
---

# Access and Authentication Troubleshooting (v2.1)

This document describes how to troubleshoot authentication and login issues
for the CyberLab platform.

## Common Symptoms

1. **Login Redirection Loop**
   - User logs in, sees "Authentication successful", then is redirected back
     to the login page repeatedly.

### 1.1 Required Clarifying Questions

Before suggesting steps, ask:

1. Which **browser** are you using?
2. Are you accessing CyberLab from within a lab VM or your local machine?
...
```

---

## Metadata Fields

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier | `kb-access-authentication` |
| `title` | string | Human-readable title | `Access and Authentication Troubleshooting` |
| `version` | string | Version number (semantic) | `2.1` |
| `last_updated` | date | Last update date (YYYY-MM-DD) | `2024-04-10` |
| `tags` | array | Searchable tags | `[authentication, sso, login]` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `author` | string | Document author |
| `category` | string | Document category |
| `related_docs` | array | Related KB document IDs |
| `deprecated` | boolean | Whether document is deprecated |

---

## Document Structure

### Headings

Use markdown headings to structure content:

- `# Title` - Document title (H1)
- `## Section` - Major sections (H2)
- `### Subsection` - Subsections (H3)

**Chunking:** The ingestion pipeline splits by H2 and H3 headings.

### Content Guidelines

1. **Be Specific**: Provide exact steps, not vague guidance
2. **Cite Sources**: Reference other KB docs when relevant
3. **Use Examples**: Include concrete examples
4. **Avoid Commands**: Don't include OS-level commands for trainees/instructors
5. **Clarifying Questions**: Explicitly list questions to ask users

### Formatting

- **Bold** for emphasis: `**important**`
- *Italic* for terms: `*term*`
- `Code` for commands: `` `command` ``
- Lists for steps
- Tables for comparisons

---

## KB Organization

### Current KB Files

```
server/kb/
├── 00-platform-overview.md
├── 01-access-and-authentication-v2.1.md
├── 02-authentication-policy-2023.md (deprecated)
├── 03-authentication-policy-2024.md (current)
├── 04-virtual-lab-operations-and-recovery.md
├── 05-environment-mapping-and-routing.md
├── 06-container-runtime-troubleshooting.md
├── 07-dns-and-network-troubleshooting.md
├── 08-logging-monitoring-and-security-controls.md
├── 09-tiering-escalation-and-sla-policy.md
└── 10-known-error-catalog.md
```

### Naming Convention

- **Prefix**: `00-` to `99-` for ordering
- **Slug**: Lowercase, hyphen-separated
- **Extension**: `.md`

---

## Versioning

### Version Numbers

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., policy change)
- **MINOR**: New content (e.g., new section)
- **PATCH**: Corrections (e.g., typo fixes)

### Deprecation

When deprecating a document:

1. Add `deprecated: true` to frontmatter
2. Add deprecation notice at top:

```markdown
> **Deprecated:** This document is retained for historical reference only.
> For current information, use `kb-new-doc-id`.
```

3. Keep file for conflict resolution
4. Create replacement document with higher version

### Conflict Resolution

When multiple KB documents conflict:

1. **Version**: Higher version wins
2. **Date**: Newer `last_updated` wins
3. **Explicit**: System explains which is authoritative

**Example:**
```
kb-auth-policy-2023 (v1.0, 2023-03-15)
kb-auth-policy-2024 (v2.0, 2024-02-01)  ← This wins
```

---

## Ingestion Process

### 1. Parse Frontmatter

Extract metadata from YAML frontmatter.

### 2. Chunk by Headings

Split content by H2 and H3 headings:

```
Chunk 1: Introduction (before first H2)
Chunk 2: ## Section 1
Chunk 3: ### Subsection 1.1
Chunk 4: ### Subsection 1.2
Chunk 5: ## Section 2
...
```

### 3. Generate Embeddings

Use Sentence Transformers (all-MiniLM-L6-v2):
- Dimension: 384
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding per chunk

### 4. Store in Database

```sql
-- kb_documents table
INSERT INTO kb_documents (id, title, version, last_updated, tags)
VALUES ('kb-access-authentication', 'Access and Authentication...', '2.1', ...);

-- kb_chunks table
INSERT INTO kb_chunks (kb_document_id, chunk_text, heading_path, embedding, chunk_index)
VALUES ('kb-access-authentication', 'Content...', 'Login Redirection Loop', [...], 0);
```

---

## Retrieval Process

### 1. Query Embedding

Generate embedding for user query using same model.

### 2. Vector Search

```sql
SELECT * FROM kb_chunks
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

### 3. Role Filtering

Remove chunks inappropriate for user role:
- Trainees: No OS commands
- Instructors: No system-level access
- Operators: Limited system access

### 4. Conflict Resolution

If multiple versions of same document:
- Keep chunks from newer version only
- Explain which document is used

### 5. Return Top K

Return top 5 (configurable) chunks with metadata.

---

## Adding New KB Documents

### Step 1: Create File

```bash
cd server/kb
touch 11-new-topic.md
```

### Step 2: Add Frontmatter

```yaml
---
id: kb-new-topic
title: New Topic Guide
version: 1.0
last_updated: 2024-06-15
tags: [topic, guide]
---
```

### Step 3: Write Content

Follow structure guidelines above.

### Step 4: Ingest

```bash
python scripts/ingest_kb.py
```

### Step 5: Verify

```bash
# Test retrieval
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test",
    "message": "Question about new topic",
    "userRole": "trainee"
  }'
```

---

## Updating Existing Documents

### Minor Updates (Patch)

1. Edit file
2. Increment patch version: `2.1` → `2.1.1`
3. Update `last_updated`
4. Re-ingest

### Major Updates (Breaking)

1. Create new file with new version
2. Mark old file as deprecated
3. Update references in other docs
4. Re-ingest

---

## Best Practices

### DO:
- ✅ Use clear, specific language
- ✅ Provide step-by-step instructions
- ✅ Include clarifying questions
- ✅ Reference related KB docs
- ✅ Update `last_updated` on changes
- ✅ Test after ingestion

### DON'T:
- ❌ Include external URLs
- ❌ Provide OS commands for trainees
- ❌ Make assumptions about user environment
- ❌ Use vague language ("might", "could", "maybe")
- ❌ Forget to update version number
- ❌ Leave deprecated docs without notice

---

## Quality Checklist

Before adding/updating KB:

- [ ] Frontmatter is complete and valid
- [ ] Version number follows semantic versioning
- [ ] Content is specific and actionable
- [ ] Headings are properly structured
- [ ] No external dependencies
- [ ] Appropriate for target roles
- [ ] Tested with real queries
- [ ] Related docs are updated
- [ ] Deprecated docs are marked
- [ ] Ingestion completes successfully

---

## Maintenance

### Regular Reviews

- **Monthly**: Review usage analytics
- **Quarterly**: Update outdated content
- **Annually**: Major version updates

### Metrics to Track

- Most retrieved documents
- Documents never retrieved
- User feedback on answers
- Escalation rates by topic

### Continuous Improvement

1. Monitor which queries have no KB coverage
2. Add new KB docs for common gaps
3. Update existing docs based on feedback
4. Deprecate outdated information
5. Improve chunking for better retrieval
