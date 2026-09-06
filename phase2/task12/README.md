# PlaceMux — Phase 2 Task 12

## E-Sign Integration & Tamper-Evidence

### AI/ML Focus

Build Resume/JD Parsing v0 that converts unstructured text into structured skill information.

### Parsing v0

The initial parser uses a controlled skills vocabulary and deterministic text matching.

The output contains:

- Profile ID
- Name
- Structured skills
- Skill count

This output can be handed off to downstream matching and ranking components.

### Offer Integrity

The task also demonstrates local offer tamper-evidence using SHA-256 hashing.

The demo:

1. Loads an offer.
2. Calculates a canonical SHA-256 hash.
3. Stores the hash with the offer.
4. Verifies the original offer.
5. Modifies the offer.
6. Verifies that the modified offer no longer matches the stored hash.

### Important

The SHA-256 demonstration provides tamper evidence and integrity verification.

It is not a production legal e-signature. Production e-signing should use the approved e-sign provider and its cryptographic signature/audit mechanism.

### Validation
