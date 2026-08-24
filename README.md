# Evidence Milestone Adjudicator

A reusable GenLayer Intelligent Contract for evidence-backed milestone verification.

## Overview

The Evidence Milestone Adjudicator allows a milestone owner to define:

- a milestone title
- acceptance criteria
- a public evidence URL
- a minimum acceptance score
- a submission deadline

When a milestone is submitted, the contract retrieves the public evidence using GenLayer's nondeterministic web capabilities and asks an AI evaluator to determine whether the evidence satisfies the specified criteria.

The evaluation is subjected to GenLayer's Equivalence Principle so that independent evaluations must reach a consistent decision.

The consensus-approved result is then persisted on-chain.

## Consensus Flow

The contract follows this workflow:

1. The owner creates a milestone.
2. A submitter submits the milestone for verification.
3. GenLayer retrieves the evidence from the specified public URL.
4. An AI evaluator assesses the evidence against the acceptance criteria.
5. The Equivalence Principle compares independent evaluations.
6. The resulting decision and score are checked against the milestone's minimum score.
7. The contract stores the final result as `ACCEPTED` or `REJECTED`.

## Stored Result

For each milestone, the contract stores:

- title
- acceptance criteria
- evidence URL
- minimum score
- deadline
- status
- submitter
- decision
- score
- evidence-grounded reasoning
- verification timestamp

## Example

A milestone can require evidence that a public webpage satisfies a particular condition.

For example:

```text
Milestone ID: test3

Title:
GenLayer Web Test V3

Criteria:
The evidence page must clearly demonstrate that this is a publicly
accessible webpage.

Evidence URL:
https://example.com

Minimum Score:
70
During testing, GenLayer successfully retrieved and evaluated the evidence.

The Equivalence Principle returned:

Decision: REJECT
Score: 65

Because the minimum required score was 70, the contract deterministically stored:

Status: REJECTED
Decision: REJECT
Score: 65

## Why This Primitive Is Useful

The contract can be reused for applications where completion cannot be determined solely from deterministic blockchain state.

Potential applications include:

- bounty completion verification
- DAO milestone verification
- grant milestone verification
- freelance work verification
- public-content verification
- evidence-based governance workflows
- agent-to-agent task completion
- web-based compliance checks

## GenLayer Features Demonstrated

This project demonstrates:

- Intelligent Contracts
- nondeterministic web access
- AI-based evaluation
- Equivalence Principle consensus
- persistent contract state
- deterministic post-consensus validation

## Version

V3 includes explicit persistence of modified milestone state back into the contract's `TreeMap` after adjudication.

## License

This project is provided as an educational and reusable GenLayer contract primitive.
