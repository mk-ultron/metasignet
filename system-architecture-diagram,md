```mermaid
flowchart TD
    A[Content Creator] -->|Posts Content| B[Bluesky Platform]
    B -->|Content Accessed via AT Protocol| C[MetaSignet Application]
    C -->|Self-Attestation| D[Human Verification Layer]
    D -->|Content Hash Generation| E[Verification Engine]
    E -->|Register Verification| F[Blockchain Layer]
    F -->|Store Verification Record| G[Verification Database]
    
    H[Community Members] -->|Social Vouching| D
    I[Verification Requests] -->|Notify Connections| H
    
    J[Content Consumers] -->|Check Verification Status| C
    C -->|Display Verification Status| J
    
    K[AT Protocol API] <-->|Bluesky Content Access| C
    L[Content Hash System] <-->|Fingerprinting| E
    
    subgraph "Blockchain Layer"
    F
    end
    
    subgraph "Application Layer"
    C
    D
    E
    G
    end
    
    subgraph "Social Layer"
    H
    I
    end
    
    subgraph "Integration Layer"
    K
    L
    end
