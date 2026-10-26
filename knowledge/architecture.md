# Architecture (knowledge note)

```mermaid
flowchart TD
    subgraph Ingest
        A[Text record] --> B[Typed extraction]
        B --> C[Confidence score]
    end
    subgraph Decide
        C --> D[Money checks]
        D --> E[Duplicate check]
        E --> F[Policy match]
        F --> G[Passage retrieval]
        G --> H[Decision record]
    end
    subgraph Govern
        H --> I[Review gate]
        I --> J[Named approval]
        H --> K[View-only store]
        K --> L[Dry-run notice]
    end
```

The three layers stay separate on purpose. Ingest knows nothing about
policy; Decide knows nothing about who approves; Govern knows nothing
about parsing. A change in one layer (for example, swapping keyword
retrieval for embeddings) touches one module and its tests, not the
decision record format.
