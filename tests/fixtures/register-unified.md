---
initiative: Payments retry
registerVersion: 2
---

# Payments retry - requirements register

## Index (high-level only)

| HLR | Name | Go-live | Status | blockedOn |
|---|---|---|---|---|
| HLR-01 | Automatic retry of failed payments | Nov 2026 | confirmed | none |
| HLR-02 | Merchant decline messaging | Dec 2026 | proposed | design |

---

## HLR-01 · Automatic retry of failed payments {#hlr-01}

### Delivery metadata

| Field | Value |
|---|---|
| status | confirmed |
| blockedOn | none |

### Detailed requirements

| ID | Requirement | User story | Type | MoSCoW | status | legacyId |
|---|---|---|---|---|---|---|
| HLR-01.1 | Retry soft declines up to 3 times | As a merchant... | Functional | Must | confirmed | - |
| HLR-01.2 | Stop retrying hard declines | As a merchant... | Functional | Must | proposed | - |

## HLR-02 · Merchant decline messaging {#hlr-02}

### Delivery metadata

| Field | Value |
|---|---|
| status | proposed |
| blockedOn | design |
