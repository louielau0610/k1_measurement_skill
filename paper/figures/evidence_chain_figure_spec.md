# Evidence Chain Figure Specification

## Figure title

Evidence Chain and Claim Governance

## Purpose

Show how current evidence can support structural claims while blocking unsupported performance, safety, and readiness claims.

## Intended caption

Evidence chain for the current research pipeline. Raw measurement evidence is converted to validated datasets, model prediction contracts, advisory risk maps, and pipeline evaluation reports. Claim governance separates supported structural/software claims from literature context, candidate contributions, claims requiring more experiment, and prohibited non-claims.

## Flow

- raw measurement evidence。
- dataset validation。
- model prediction contract。
- risk map output。
- pipeline evaluation report。
- claim registry。
- non-claims。

## Claim status categories

- supported structural/software claim。
- literature context claim。
- candidate contribution。
- requires more experiment。
- non-claim。

## Prohibited claims to mark explicitly

- navigation safety improvement。
- collision reduction。
- success-rate improvement。
- compensation readiness。
- safe adapter readiness。

## Mermaid diagram

```mermaid
flowchart TD
    A[Raw measurement evidence] --> B[Dataset validation]
    B --> C[Model prediction contract]
    C --> D[Risk map output]
    D --> E[Pipeline evaluation report]
    E --> F[Supported structural/software claims]
    E --> G[Literature context claims]
    E --> H[Candidate contributions]
    E --> I[Requires more experiment]
    E --> J[Non-claims]
    J --> K[No navigation safety improvement]
    J --> L[No collision reduction]
    J --> M[No success-rate improvement]
    J --> N[No compensation readiness]
    J --> O[No safe adapter readiness]
```

