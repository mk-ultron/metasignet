```mermaid
sequenceDiagram
    participant Creator as Content Creator
    participant Bluesky as Bluesky Platform
    participant App as MetaSignet App
    participant Verification as Verification Engine
    participant Blockchain as Blockchain Layer
    participant Community as Community Members
    
    Creator->>Bluesky: Publish content (post/images)
    Creator->>App: Sign in with Bluesky credentials
    App->>Bluesky: Authenticate via AT Protocol
    App->>Bluesky: Fetch creator's posts
    Bluesky->>App: Return posts data
    
    Creator->>App: Select post to verify
    App->>App: Display attestation options
    Creator->>App: Attest "Human-Created"
    App->>App: Optional: Add creation context
    App->>Verification: Generate content fingerprint
    
    alt Blockchain Verification Path
        Verification->>Blockchain: Register attestation on-chain
        Blockchain->>App: Return transaction confirmation
    else Local Verification Path
        Verification->>App: Store attestation in database
    end
    
    App->>Creator: Display verification certificate
    
    opt Social Vouching Process
        App->>Community: Notify connections about verification
        Community->>App: View verification request
        Community->>App: Vouch for human creation
        App->>Verification: Update verification status to "Human-verified+"
    end
    
    Creator->>App: Generate shareable certificate
    
    Note over App,Verification: Future Integration with Gitcoin Passport or BrightID
