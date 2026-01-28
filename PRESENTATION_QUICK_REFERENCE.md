# Presentation Quick Reference Card
## 5-7 Minute Video Script - At-a-Glance

---

## 🎬 TIMELINE

| Time | Section | Key Points | Display |
|------|---------|------------|---------|
| 0:00-0:30 | **Introduction** | Project overview, requirements | README.md, requirements checklist |
| 0:30-1:30 | **Architecture** | Frontend/Backend/DB, execution order | ARCHITECTURE.md diagram |
| 1:30-2:30 | **RAG System** | KB structure, embeddings, retrieval | KB files, RAG pipeline |
| 2:30-3:00 | **Guardrails** | Security, rule-based, deterministic | guardrails.py code |
| 3:00-4:00 | **Live Demo** | 3 workflows: login, security, VM crash | Live frontend, chat interface |
| 4:00-4:30 | **Escalation** | Ticket creation, context preservation | Tickets API/UI |
| 4:30-5:00 | **Analytics** | Metrics dashboard, deflection rate | /api/metrics/summary |
| 5:00-5:30 | **No-Internet** | Offline capability, provider abstraction | Architecture section |
| 5:30-6:00 | **Testing** | Unit/integration/E2E tests | TESTING.md, test results |
| 6:00-6:30 | **Deployment** | Vercel + Render, production-ready | Deployment URLs |
| 6:30-7:00 | **Conclusion** | Key highlights, summary | Summary slide |

---

## 🎯 KEY MESSAGES TO EMPHASIZE

1. **KB-Grounded Only** - Zero hallucinations, all responses from local KB
2. **Deterministic** - Same input → same output, rule-based logic
3. **Security First** - Comprehensive guardrails, no unsafe outputs
4. **Production-Ready** - Deployed, tested, documented
5. **Offline-Capable** - Designed for no-internet environments

---

## 📋 DEMO WORKFLOWS (Prepare These)

### Demo 1: Login Redirection Loop
**Query:** "I keep getting redirected to the login page even after logging in."
**Expected:**
- KB-grounded answer
- TIER_2, MEDIUM severity
- KB references shown
- Ticket created

### Demo 2: Security Violation
**Query:** "How do I access the host machine behind my VM?"
**Expected:**
- 🚫 BLOCKED by guardrails
- Polite refusal, no technical details
- Event logged

### Demo 3: Critical VM Crash
**Query:** "My lab VM froze and shut down; I lost my work."
**Expected:**
- KB-based recovery steps
- TIER_3, CRITICAL severity
- Immediate escalation
- Ticket created

---

## 🖥️ WHAT TO HAVE OPEN

1. **Frontend:** https://bay-infotech-bharath-kumar-borra.vercel.app
2. **Backend API:** https://bay-infotech-test-production.up.railway.app
3. **Backend API Docs:** https://bay-infotech-test-production.up.railway.app/docs
3. **Code Editor:** Key files ready (guardrails.py, chat.py, etc.)
4. **Documentation:** ARCHITECTURE.md, README.md
5. **Terminal:** Test results or API responses

---

## 💬 OPENING LINE

"Hello! I'm excited to present my full-stack AI Help Desk Platform built for BayInfotech's technical challenge. This is a production-ready proof-of-concept that demonstrates a next-generation AI support system for complex training environments."

---

## 💬 CLOSING LINE

"To summarize, this AI Help Desk platform demonstrates KB-grounded responses, strict guardrails, intelligent tiering, automated escalation, comprehensive analytics, and is fully production-ready and offline-capable. Thank you for watching!"

---

## ⚠️ IMPORTANT REMINDERS

- ✅ Speak clearly, moderate pace
- ✅ Show actual code/UI, don't just describe
- ✅ Emphasize "deterministic" and "KB-only"
- ✅ Test all demos before recording
- ✅ Keep to 5-7 minutes total
- ✅ Show guardrails blocking in action
- ✅ Highlight offline capability

---

## 📊 METRICS TO SHOW

- Deflection rate (TIER_0 / total)
- Tickets by tier (TIER_0, TIER_1, TIER_2, TIER_3)
- Tickets by severity (LOW, MEDIUM, HIGH, CRITICAL)
- Guardrail activations
- Escalation counts

---

## 🔗 LINKS TO PREPARE

- Frontend URL: https://bay-infotech-bharath-kumar-borra.vercel.app
- Backend URL: https://bay-infotech-test-production.up.railway.app
- Backend API Docs: https://bay-infotech-test-production.up.railway.app/docs
- Repository: [your-github-url]
- Demo Video: [will be this video]

---

**Good luck with your presentation! 🎥**
