

## **KB File List**

1. `00-platform-overview.md`  
2. `01-access-and-authentication-v2.1.md`  
3. `02-authentication-policy-2023.md`  
4. `03-authentication-policy-2024.md`  
5. `04-virtual-lab-operations-and-recovery.md`  
6. `05-environment-mapping-and-routing.md`  
7. `06-container-runtime-troubleshooting.md`  
8. `07-dns-and-network-troubleshooting.md`  
9. `08-logging-monitoring-and-security-controls.md`  
10. `09-tiering-escalation-and-sla-policy.md`  
11. `10-known-error-catalog.md`

This gives you versioning, conflicts, cross-references, and enough complexity to exercise RAG properly.

---

## **00-platform-overview.md**

\---  
id: kb-platform-overview  
title: Platform Overview – CyberLab Help Desk  
version: 1.0  
last\_updated: 2024-06-01  
tags: \[overview, platform, roles, architecture\]  
\---

\# Platform Overview – CyberLab Help Desk

CyberLab Help Desk supports users of the CyberLab Training Platform, which provides  
browser-based access to:

\- Virtual lab environments (VMs and containers)  
\- Pre-configured ranges (networked lab topologies)  
\- Training modules and assessments

\#\# User Roles

The following roles are relevant for help desk routing and permissions:

\- \*\*Trainee\*\* – primary learner, runs labs and exercises.  
\- \*\*Instructor\*\* – manages classes, assigns labs, monitors progress.  
\- \*\*Operator\*\* – manages day-to-day operations of lab environments.  
\- \*\*Support Engineer\*\* – handles escalated technical incidents.  
\- \*\*Admin\*\* – manages configuration, integrations, and user lifecycle.

Role information should be used for:

\- Tailoring explanations (Trainee vs. Support Engineer)  
\- Determining whether system-level instructions are allowed  
\- Escalation routing (e.g., complex issues go to Support Engineers)

\#\# Environment Types

CyberLab includes the following environment types:

\- \*\*Personal Lab VM\*\* – one VM per trainee.  
\- \*\*Shared Exercise Range\*\* – multi-VM, multi-user environment.  
\- \*\*Container-based Labs\*\* – fast, ephemeral labs running as containers.

Each environment type has different recovery and escalation procedures (see  
\`kb-virtual-lab-recovery\` and \`kb-container-runtime-troubleshooting\`).

\#\# Help Desk Responsibilities

The AI Help Desk is responsible for:

\- Answering common questions using the approved Knowledge Base (KB) only.  
\- Guiding users through safe, documented troubleshooting steps.  
\- Determining whether an issue can be resolved at self-service Tier 0 or requires escalation.  
\- Enforcing safety controls and blocking unsafe requests.

The Help Desk must \*\*never\*\*:

\- Invent policies, procedures, commands, or URLs that are not in the KB.  
\- Provide host-level or infrastructure-level access instructions.  
\- Modify or override the tiering and escalation rules described in \`kb-tiering-escalation\`.

---

## **01-access-and-authentication-v2.1.md**

\---  
id: kb-access-authentication  
title: Access and Authentication Troubleshooting  
version: 2.1  
last\_updated: 2024-04-10  
tags: \[authentication, sso, login, access\]  
\---

\# Access and Authentication Troubleshooting (v2.1)

This document describes how to troubleshoot authentication and login issues  
for the CyberLab platform.

\> \*\*Note:\*\* This document supersedes earlier authentication guidance in  
\> \`kb-auth-policy-2023\`. For MFA-related policies, use \`kb-auth-policy-2024\`.

\#\# Common Symptoms

1\. \*\*Login Redirection Loop\*\*  
   \- User logs in, sees "Authentication successful", then is redirected back  
     to the login page repeatedly.

2\. \*\*Session Expired Immediately\*\*  
   \- User logs in successfully but is logged out after a few seconds.

3\. \*\*Time Drift Authentication Failures\*\*  
   \- User reports that their lab VM clock is behind and cannot complete certain  
     authentication workflows (e.g., token validation).

\---

\#\# 1\. Login Redirection Loop

\*\*Symptom:\*\*  
User reports: "I keep getting redirected to the login page even after logging in."

\#\#\# 1.1 Required Clarifying Questions

Before suggesting steps, ask:

1\. Which \*\*browser\*\* are you using?  
2\. Are you accessing CyberLab from within a lab VM or your local machine?  
3\. Approximately what \*\*time\*\* did the issue start?

\#\#\# 1.2 Self-Service Steps (Tier 0/Tier 1\)

1\. Instruct the user to:  
   \- Close all CyberLab tabs.  
   \- Clear browser \*\*cookies and site data\*\* for \`\*.cyberlab.local\`.  
   \- Close and reopen the browser.  
   \- Navigate to the CyberLab login page and try again.

2\. If the user is accessing from inside a lab VM, ensure:  
   \- The VM browser is not using stale cached SSO sessions.

\#\#\# 1.3 Escalation Criteria

Escalate to Tier 2 (Support Engineer) if:

\- The user has performed all steps in 1.2 \*\*twice\*\* and the issue persists.  
\- Multiple users report the same behavior within a short time window.

When escalating, capture:

\- Browser type and version.  
\- Network location (lab VM vs local).  
\- Approximate start time.  
\- Any error messages or codes observed.

\---

\#\# 2\. Session Expired Immediately

If the user is logged out within seconds:

1\. Verify with user:  
   \- Whether they are using private/incognito mode.  
   \- Whether any browser extensions are blocking cookies.

2\. If session still expires:  
   \- Escalate to Tier 2 with captured session details.

\---

\#\# 3\. Time Drift Authentication Failures

\*\*Symptom:\*\*  
User reports: "My lab VM clock is behind and authentication keeps failing."

\#\#\# 3.1 Policy

Trainees and Instructors are \*\*not allowed\*\* to modify time synchronization  
or system clocks inside lab VMs.

Only Operators and Support Engineers may perform time-related remediation.

\#\#\# 3.2 AI Help Desk Behavior

\- If user is a \*\*Trainee\*\* or \*\*Instructor\*\*:  
  \- Do \*\*not\*\* provide commands or procedures to adjust system time.  
  \- Inform the user that time synchronization is a platform-level function.  
  \- Escalate to Tier 2 (Support Engineer) with:  
    \- VM name or ID.  
    \- Reported time skew (approximate).  
\- If user is an \*\*Operator\*\* or \*\*Support Engineer\*\*:  
  \- You may reference the high-level process, but do \*\*not\*\* provide  
    step-by-step OS commands unless explicitly documented in a separate  
    Operator guide (not included in this KB set).  
  \- If not documented, escalate to Tier 3\.

The AI Help Desk must \*\*never\*\* invent time synchronization commands.

---

## **02-authentication-policy-2023.md (old MFA policy – used for conflict case)**

\---  
id: kb-auth-policy-2023  
title: Authentication and MFA Policy – 2023  
version: 1.0  
last\_updated: 2023-03-15  
tags: \[policy, authentication, mfa, deprecated\]  
\---

\# Authentication and MFA Policy – 2023 (Deprecated)

\> \*\*Deprecated:\*\* This document is retained for historical reference only.  
\> For current MFA reset policy, use \`kb-auth-policy-2024\`.

In 2023, CyberLab required multi-factor authentication (MFA) by default for  
all users except temporary Guest accounts.

\*\*Old Reset Process (No Longer Valid)\*\*

Previously, users could reset their MFA devices by answering security questions  
and confirming access to a backup email address.

This process has been \*\*retired\*\* due to security concerns and must \*\*not\*\*  
be recommended to users anymore.

The AI Help Desk should:

\- Only reference this document to clarify \*\*that it is outdated\*\*.  
\- Direct users to \`kb-auth-policy-2024\` for the current process.

---

## **03-authentication-policy-2024.md (new MFA policy – authoritative)**

\---  
id: kb-auth-policy-2024  
title: Authentication and MFA Policy – 2024  
version: 2.0  
last\_updated: 2024-02-01  
tags: \[policy, authentication, mfa, current\]  
\---

\# Authentication and MFA Policy – 2024 (Current)

This document defines the \*\*current\*\* authentication and MFA policies.

\#\# MFA Requirements

\- MFA is \*\*required\*\* for all user roles.  
\- Supported authenticators:  
  \- TOTP-based mobile app  
  \- Hardware token

\#\# MFA Reset Policy

Users \*\*cannot\*\* reset their own MFA using security questions or backup emails.

To reset MFA:

1\. User must open a \*\*Tier 1 ticket\*\* with:  
   \- Username  
   \- Role  
   \- Last successful login date  
2\. A Support Engineer validates identity using internal procedures.  
3\. Support Engineer triggers an MFA reset link, valid for 24 hours.  
4\. User completes enrollment on next login.

The AI Help Desk must:

\- Always guide users to the \*\*ticket-based reset process\*\* above.  
\- Explicitly state that older documentation allowing self-service resets  
  is obsolete.  
\- Never invent alternative reset flows.

---

## **04-virtual-lab-operations-and-recovery.md**

\---  
id: kb-virtual-lab-recovery  
title: Virtual Lab Operations and Recovery  
version: 1.3  
last\_updated: 2024-05-12  
tags: \[labs, vm, recovery, crash, snapshots\]  
\---

\# Virtual Lab Operations and Recovery

This document describes how to handle issues with personal lab VMs and  
shared ranges.

\#\# 1\. Common Issues

\- VM freezes / becomes unresponsive.  
\- VM shuts down unexpectedly.  
\- User loses work mid-exercise.  
\- Kernel panic messages appear in the VM console.

\---

\#\# 2\. Freeze or Temporary Unresponsiveness

Symptoms:

\- UI stops responding.  
\- Mouse/keyboard lag.

Steps (Tier 0):

1\. Ask the user:  
   \- Are other browser tabs responsive?  
   \- Are other users reporting similar issues?

2\. If only a single VM is affected:  
   \- Instruct user to disconnect and reconnect through the portal.  
   \- Do \*\*not\*\* instruct them to reboot the VM from inside the guest OS.

If the VM remains unresponsive after reconnection, escalate to Tier 2\.

\---

\#\# 3\. Unexpected Shutdown / Lab Crash

Symptoms:

\- VM or lab tab closes abruptly.  
\- "Connection lost" or similar message appears.

Steps:

1\. Ask:  
   \- Which module and lab are they running?  
   \- Approximately when did the crash occur?

2\. Check whether the lab supports \*\*auto-snapshot on start\*\*:  
   \- If yes:  
     \- Instruct user to relaunch the lab.  
     \- Inform them that state may be restored from the last snapshot.  
   \- If no:  
     \- Explain that unsaved in-VM changes may be lost.

Escalate to Tier 2 if:

\- The lab repeatedly crashes on relaunch.  
\- Multiple users report crashes in the same module.

\---

\#\# 4\. Kernel Panic in Lab VM

If user reports kernel panic messages (e.g., stack trace, driver-related logs):

\- Do \*\*not\*\* attempt to debug or instruct user to alter kernel or drivers.  
\- Explain that kernel-level issues are handled by platform engineering.  
\- Immediately escalate to Tier 2 with:  
  \- Lab name and module  
  \- Time of incident  
  \- Any screenshots or logs provided

The AI Help Desk must never provide OS-level commands to modify drivers,  
kernel modules, or boot parameters.

\---

\#\# 5\. Lost Progress

If a user loses work because of a crash:

\- Apologize and explain snapshot behavior clearly.  
\- Provide any \*\*documented\*\* recommendations for:  
  \- Saving work more frequently  
  \- Exporting artifacts (if supported)  
\- Do not promise recovery if snapshots are not configured.

If recurring, escalate so Support Engineers can investigate the lab image.

---

## **05-environment-mapping-and-routing.md**

\---  
id: kb-env-mapping  
title: Environment Mapping and Routing  
version: 1.1  
last\_updated: 2024-03-20  
tags: \[environment, mapping, range, routing\]  
\---

\# Environment Mapping and Routing

CyberLab assigns users to different environments based on:

\- Training track  
\- Course  
\- Module  
\- Role (Trainee vs Instructor)

Environment IDs (examples):

\- Range Alpha  
\- Range Bravo  
\- Range Charlie

\#\# 1\. Symptoms of Mapping Issues

\- User launches a lab expecting specific tools but sees a different toolset.  
\- Lab title or banner does not match the assigned module.  
\- Users in the same course end up in different ranges unexpectedly.

\#\# 2\. AI Help Desk Behavior

When a user reports an environment mismatch:

1\. Ask clarifying questions:  
   \- Course name  
   \- Module name  
   \- What they expected vs. what they see  
   \- Whether others in the same cohort see the same issue

2\. Check KB for known mapping issues under \`kb-known-errors\`.

3\. If a known mapping issue exists:  
   \- Provide the documented workaround (if any).  
   \- Inform user that engineering is tracking the issue.

4\. If no known issue matches:  
   \- Explain that environment mapping is a system-level function.  
   \- Escalate to Tier 2 with the collected context.

The AI Help Desk must \*\*not\*\*:

\- Instruct users to switch ranges manually.  
\- Provide API endpoints, admin URLs, or internal configuration paths.

---

## **06-container-runtime-troubleshooting.md**

\---  
id: kb-container-runtime-troubleshooting  
title: Container Runtime Troubleshooting  
version: 1.0  
last\_updated: 2024-05-01  
tags: \[containers, labs, startup, errors\]  
\---

\# Container Runtime Troubleshooting

Some labs run as short-lived containers. This document covers common  
container-related issues.

\#\# 1\. Missing Startup Script (\`/opt/startup.sh\`)

Symptom:

\- Error message: \`container init failed: missing /opt/startup.sh\`

Cause:

\- Lab image was built without the required startup script, or  
\- Deployment pipeline did not mount the script correctly.

AI Help Desk Steps:

1\. Confirm message with user.  
2\. Explain that the issue is caused by a misconfigured lab image.  
3\. Instruct user to:  
   \- Stop the current lab instance.  
   \- Relaunch the lab from the portal once.

4\. If the error persists after a relaunch:  
   \- Escalate to Tier 2 with:  
     \- Lab name and module  
     \- Time of failure  
     \- Error text

The AI Help Desk must \*\*not\*\*:

\- Provide instructions for editing container images.  
\- Suggest mounting files manually.  
\- Provide docker or container engine commands.

\---

\#\# 2\. Slow Container Startup

If container startup consistently exceeds the documented threshold (e.g., \>90 seconds):

\- Ask user for:  
  \- Network conditions (e.g., VPN, local bandwidth issues).  
\- If multiple users affected, escalate as potential backend performance issue.

AI Help Desk must avoid low-level container host adjustments and  
stick to documented user-facing steps only.

---

## **07-dns-and-network-troubleshooting.md**

\---  
id: kb-dns-network  
title: DNS and Network Troubleshooting  
version: 1.2  
last\_updated: 2024-04-05  
tags: \[dns, network, troubleshooting\]  
\---

\# DNS and Network Troubleshooting

This document covers \*\*user-facing\*\* DNS and connectivity issues.

\#\# 1\. DNS Resolution Failures

Symptom:

\- The lab or browser reports it cannot resolve an internal domain  
  (e.g., \`\*.internal.cyberlab\`).

AI Help Desk Steps:

1\. Ask:  
   \- Does the issue happen only in the lab VM or also on the user's local machine?  
   \- Which URL or hostname are they trying to access?

2\. If in lab VM only:  
   \- Suggest closing and relaunching the lab (to reinitialize network stack).  
   \- Ask user to confirm whether other internal domains work.

3\. If multiple internal domains fail:  
   \- Explain that internal DNS may be experiencing problems.  
   \- Escalate to Tier 2\.

\#\# 2\. \`/etc/hosts\` Editing Requests

Users may ask to modify \`/etc/hosts\`.

Policy:

\- Trainees and Instructors must \*\*never\*\* modify \`/etc/hosts\` inside lab VMs.  
\- Operators and Support Engineers may have separate instructions, not  
  included in this KB.

AI Help Desk Behavior:

\- If user asks: "Should I add a hosts entry?" or similar:  
  \- Respond that host file modification is not allowed for their role.  
  \- Do not provide example entries, IPs, or commands.  
  \- If DNS issue appears platform-wide, escalate.

\#\# 3\. VPN and External Connectivity

CyberLab is primarily designed for controlled environments.

If connectivity issues stem from user VPN, corporate proxy, or firewall:

\- Provide documented guidance if present.  
\- Otherwise, recommend:  
  \- Trying from a different network if permitted.  
  \- Contacting their local IT support for VPN/firewall configuration.

---

## **08-logging-monitoring-and-security-controls.md**

\---  
id: kb-logging-security  
title: Logging, Monitoring, and Security Controls  
version: 1.0  
last\_updated: 2024-03-30  
tags: \[logging, monitoring, security, guardrails\]  
\---

\# Logging, Monitoring, and Security Controls

CyberLab maintains strict logging and monitoring to ensure security,  
auditability, and compliance.

\#\# 1\. Logging Policy

\- System and lab activity is logged at multiple layers.  
\- Logs may include:  
  \- Authentication attempts  
  \- Lab lifecycle events (start/stop/crash)  
  \- Certain in-lab actions where instrumentation is configured

Users cannot disable logging.

\#\# 2\. Requests to Disable or Bypass Logging

Any user request to:

\- Disable logging  
\- "Hide" activity  
\- Run labs "quietly" without logs

must be \*\*denied\*\*.

AI Help Desk must:

1\. Inform the user that logging is mandatory and cannot be disabled.  
2\. Decline to provide any commands, configuration steps, or suggestions  
   that would reduce or bypass logging.  
3\. Optionally suggest reviewing privacy and acceptable use documents if relevant.  
4\. Log the interaction as a \*\*security-relevant event\*\* for analytics.

\#\# 3\. Host and Hypervisor Access

Users (including Operators and Support Engineers) are \*\*not\*\* granted direct  
access to:

\- Hypervisors  
\- Host operating systems  
\- Underlying infrastructure

AI Help Desk must never:

\- Provide commands to access host-level shells.  
\- Provide low-level hypervisor configuration steps.  
\- Suggest connecting directly to the host for troubleshooting.

Any such request should be:

\- Denied politely.  
\- Logged as a security-sensitive interaction.  
\- Escalated if necessary.

---

## **09-tiering-escalation-and-sla-policy.md**

\---  
id: kb-tiering-escalation  
title: Tiering, Escalation, and SLA Policy  
version: 1.2  
last\_updated: 2024-05-05  
tags: \[tiering, escalation, sla\]  
\---

\# Tiering, Escalation, and SLA Policy

This document defines the tier structure, escalation triggers, and  
service expectations for the AI Help Desk.

\#\# 1\. Support Tiers

\- \*\*Tier 0 – Self-Service AI\*\*  
  \- AI Help Desk resolves issues using KB and guided flows.  
  \- No human agent involvement.

\- \*\*Tier 1 – Human Generalist\*\*  
  \- Handles straightforward tickets (access, basic usage).

\- \*\*Tier 2 – Support Engineer\*\*  
  \- Handles complex technical issues (crashes, mapping issues, DNS, etc.).

\- \*\*Tier 3 – Platform Engineering\*\*  
  \- Handles deep platform issues (kernel panics, image bugs, systemic outages).

\#\# 2\. Severity Levels

\- \*\*LOW\*\* – Minor inconvenience, workaround available.  
\- \*\*MEDIUM\*\* – User blocked, but no time-critical impact.  
\- \*\*HIGH\*\* – Multiple users blocked, or key exercise blocked.  
\- \*\*CRITICAL\*\* – Systemic outage, data loss risk, or major training impact.

\#\# 3\. Escalation Rules (Simplified)

The AI Help Desk must escalate when:

1\. \*\*Repeated Failure to Resolve\*\*  
   \- User indicates the recommended steps did not work \*\*twice\*\*.  
   \- Same issue persists after documented self-service attempts.

2\. \*\*High or Critical Impact\*\*  
   \- Lab crashes during key graded exercises.  
   \- Multiple users report identical blocking issue.  
   \- Kernel panic, container startup failure that blocks entire module.

3\. \*\*Security-Sensitive Request\*\*  
   \- Requests to disable logging.  
   \- Requests for host/hypervisor access.  
   \- Requests for destructive actions (resetting all environments).

\#\# 4\. Ticket Creation

When escalation is required, create a ticket with:

\- Summary (short, descriptive)  
\- Full conversation context  
\- User role and course/module  
\- Tier and severity classification  
\- Any relevant timestamps and error messages

\#\# 5\. AI Help Desk Behavior

The AI Help Desk:

\- Must not override these rules based on user preference  
  (e.g., “don’t escalate this”).  
\- Must set \`needsEscalation \= true\` in the API response when conditions are met.  
\- Must correctly choose tier and severity based on this document.

---

## **10-known-error-catalog.md**

\---  
id: kb-known-errors  
title: Known Error Catalog  
version: 1.0  
last\_updated: 2024-05-18  
tags: \[known-issues, catalog, errors\]  
\---

\# Known Error Catalog

This catalog lists selected known issues to support fast recognition by  
the AI Help Desk.

\#\# KE-1001 – Login Redirection Loop (AUTH)

\- \*\*Description:\*\* Users get redirected to the login page repeatedly.  
\- \*\*Cause:\*\* Stale SSO cookies in some browsers.  
\- \*\*Workaround:\*\* Clear browser cookies for \`\*.cyberlab.local\` and retry.  
\- \*\*Status:\*\* Open, being monitored.  
\- \*\*Related KB:\*\* \`kb-access-authentication\`

\#\# KE-2001 – Missing \`/opt/startup.sh\` in Container Labs

\- \*\*Description:\*\* Containerized labs fail with "missing /opt/startup.sh".  
\- \*\*Cause:\*\* Image build missing startup script.  
\- \*\*Workaround:\*\* None; relaunch may succeed if updated image deployed.  
\- \*\*Status:\*\* Open — platform engineering actively fixing.  
\- \*\*Related KB:\*\* \`kb-container-runtime-troubleshooting\`

\#\# KE-3001 – Environment Mapping Mismatch in Module L-7

\- \*\*Description:\*\* Users launched into the wrong environment for Module L-7.  
\- \*\*Cause:\*\* Incorrect mapping of course to range.  
\- \*\*Workaround:\*\* None for end users.  
\- \*\*Status:\*\* Open.  
\- \*\*AI Help Desk Guidance:\*\*  
  \- Explain that the issue is known.  
  \- Reassure user it is being addressed.  
  \- Escalate ticket with module and environment details.  
\- \*\*Related KB:\*\* \`kb-env-mapping\`

\#\# KE-4001 – VM Kernel Panic in Certain Labs

\- \*\*Description:\*\* Kernel panic observed in some VM images under heavy load.  
\- \*\*AI Help Desk Guidance:\*\*  
  \- Do not attempt to debug.  
  \- Escalate immediately with lab details and timestamp.  
\- \*\*Related KB:\*\* \`kb-virtual-lab-recovery\`

