# EARS Translation Standard

**Location:** `~/.cursor/skills/ba-assistant/references/ears-translation.md`
**Owner:** ba-dev-handover (applies this at export), this standard (format)
**Last reviewed:** 2026-07-05

This file defines how a confirmed requirement from `register.md` is rendered into EARS form **at handover export time**. It exists so the delivery repo and the devs' agents receive requirements in a structured, parseable "shall" form, without changing how requirements are authored in the register.

**Key rule: the register is not touched.** Requirements are authored per `references/requirement-format.md` (prose Statement + Acceptance for met). EARS is generated from that content when a requirements pack is published. If the register and the EARS render ever disagree, the register wins and the render is regenerated.

---

## 1. Why EARS only at export

The register's `Statement` + `Acceptance for met` already carry testable intent for a human BA and stakeholders. Delivery agents parse structured "shall" statements more reliably than prose, and EARS is the notation the spec-driven-development tooling (Kiro, Spec Kit, OpenSpec) converged on. Rendering at export gets the agent benefit without imposing EARS on day-to-day authoring or on stakeholder-facing Confluence views.

---

## 2. The five EARS patterns

| Pattern | Shape | Use when |
|---|---|---|
| Ubiquitous | The `<system>` shall `<response>` | Always-true behaviour, no trigger |
| Event-driven | When `<trigger>`, the `<system>` shall `<response>` | Behaviour fires on an event |
| State-driven | While `<state>`, the `<system>` shall `<response>` | Behaviour holds during a state |
| Unwanted behaviour | If `<condition>`, then the `<system>` shall `<response>` | Error / guard / negative case |
| Optional | Where `<feature>`, the `<system>` shall `<response>` | Behaviour applies only when a feature is present |

`<system>` is the real named service where known (from Data Investigation grounding), not "the system" generically. If the service isn't known, that's a grounding gap — flag it, don't paper over it with "the system."

---

## 3. Mapping register fields to EARS

A single confirmed requirement usually produces **several** EARS statements: one per row of its `Acceptance for met`, because each acceptance line is a testable behaviour.

| Register field | Becomes |
|---|---|
| `Statement` | The ubiquitous/state-driven backbone statement (the always-true capability) |
| Each `Acceptance for met` line | One event-driven, state-driven, or unwanted-behaviour EARS statement |
| Negative cases in acceptance | Unwanted-behaviour pattern (`If ... then ... shall`) |
| `type` (COMP-, NFR-, etc.) | Preserved as a tag on the render; compliance and NFR statements keep their prefix |
| Grounded system facts (from Data Investigation) | Fill the `<system>`, real field names, real states |

The requirement ID (BR-005 etc.) is preserved as the trace anchor. Every EARS statement in the export carries its source requirement ID.

---

## 4. Worked example

### Register entry (unchanged, authored per requirement-format.md)

```
### BR-013 · Customers must see why verification failed
**Type:** Business requirement
**Status:** Confirmed
...
**Statement:**
Declined merchants must receive a generalised, approved reason for the decline,
without revealing which specific check failed.

**Acceptance for met:**
- Decline notification shows one of the approved reason codes from Reason Code Register SO-04
- The message includes the support contact channel
- The specific failed check is never revealed to the merchant
```

### EARS render at export (generated, in the requirements pack)

```
BR-013 — Verification decline messaging  [Business]

When a merchant application is declined at the verification stage,
the Onboarding Notification service shall send a decline message containing
one of the approved reason codes from Reason Code Register SO-04.

When a decline message is sent,
the Onboarding Notification service shall include the support contact channel.

If a decline reason maps to a specific failed check,
then the Onboarding Notification service shall NOT reveal which check failed.

Trace: BR-013  ·  Evidence: SO-04 register (data)  ·  Source: register.md
```

Three EARS statements from one requirement: event-driven, event-driven, unwanted-behaviour. Each traces back to BR-013.

---

## 5. When a requirement won't render

If a confirmed requirement can't be expressed as a testable "shall" (the response isn't observable, the trigger is vague), that is a signal the requirement isn't actually ready, even though it's marked confirmed. Do not force a mangled render. Flag it back to the Requirements Interrogator and hold it out of the pack. This is a genuine catch: a requirement that resists EARS often resists implementation too.

---

## 6. What EARS does NOT replace

- The register's rationale, history, linked elements, MoSCoW — none of that goes into the EARS statement. The EARS render is the behavioural core the agent implements against. The handover note links back to the full register entry for context.
- Acceptance-for-met stays the human-readable testability record in the register. EARS is its export-time structured twin, not a replacement.

---

## 7. Versioning

v1.0 (2026-07-04). Added with the Dev Handover skill (Wave 9). Changes to the pattern set or the field mapping require a version bump.
