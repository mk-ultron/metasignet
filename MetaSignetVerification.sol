// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

contract MetaSignetVerification {
    // ===== ENUMS =====
    
    // Types of content creation
    enum CreationType { 
        UNDECLARED,      // Default state
        HUMAN_CREATED,   // Content created entirely by human
        AI_ASSISTED,     // Human created with AI tools
        AI_GENERATED     // Primarily AI-generated
    }
    
    // Verification status levels
    enum VerificationStatus {
        UNVERIFIED,      // Not yet verified
        SELF_ATTESTED,   // Creator has self-attested
        COMMUNITY_VOUCHED // Has received community vouching
    }
    
    // ===== STATE VARIABLES =====
    
    // Admin controls
    address public admin;
    address public feeCollector;
    uint256 public registrationFee = 0.0005 ether; // Minimal fee
    
    // Thresholds
    uint256 public vouchThreshold = 3; // Number of vouches needed for community verification
    
    // Core data structures for storing content information
    struct Content {
        address creator;             // Address of the content creator
        string contentHash;          // Unique hash identifying the content
        string contentURI;           // URI of the content (e.g., Bluesky post URL)
        uint256 timestamp;           // When the content was registered
        CreationType creationType;   // How the content was created
        VerificationStatus status;   // Current verification status
        string creationContext;      // Optional context about the creation process
        uint256 vouchCount;          // Number of community vouches received
        string platformSource;       // Platform where content originated
    }
    
    struct ContentMetadata {
        // Simplified version of Content struct for returns
        address creator;
        uint256 timestamp;
        CreationType creationType;
        VerificationStatus status;
        string creationContext;
        uint256 vouchCount;
        string platformSource;
        string contentURI;
    }
    
    // === Primary Storage Mappings ===
    
    // Maps content hashes to their full Content struct data
    mapping(string => Content) public verifiedContent;
    
    // Reverse lookup: maps creator addresses to their content hashes
    mapping(address => string[]) public creatorContent;
    
    // Tracks vouching: contentHash => voucher address => has vouched
    mapping(string => mapping(address => bool)) public contentVouches;
    
    // ===== EVENTS =====
    
    event ContentRegistered(string contentHash, address creator, string contentURI, CreationType creationType);
    event ContentVouched(string contentHash, address voucher);
    event VerificationStatusUpdated(string contentHash, VerificationStatus newStatus);
    
    // ===== MODIFIERS =====
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function");
        _;
    }
    
    modifier contentExists(string memory contentHash) {
        require(verifiedContent[contentHash].timestamp > 0, "Content does not exist");
        _;
    }
    
    modifier onlyContentCreator(string memory contentHash) {
        require(verifiedContent[contentHash].creator == msg.sender, "Only content creator can call this function");
        _;
    }
    
    modifier hasNotVouched(string memory contentHash) {
        require(!contentVouches[contentHash][msg.sender], "Address has already vouched for this content");
        _;
    }
    
    // ===== CONSTRUCTOR =====
    
    constructor() {
        admin = msg.sender;
        feeCollector = msg.sender;
    }
    
    // ===== ADMIN FUNCTIONS =====
    
    function setFeeCollector(address newFeeCollector) public onlyAdmin {
        feeCollector = newFeeCollector;
    }
    
    function setRegistrationFee(uint256 newFee) public onlyAdmin {
        registrationFee = newFee;
    }
    
    function setVouchThreshold(uint256 newThreshold) public onlyAdmin {
        vouchThreshold = newThreshold;
    }
    
    // ===== CORE FUNCTIONS =====
    
    /**
     * @dev Registers new content with human attestation
     * @param contentHash Unique identifier for the content
     * @param contentURI URI where the content can be accessed
     * @param creationType Type of creation (human, AI-assisted, AI-generated)
     * @param platformSource Platform where content was originally posted
     * @param creationContext Optional details about the creation process
     */
    function registerContent(
        string memory contentHash,
        string memory contentURI,
        CreationType creationType,
        string memory platformSource,
        string memory creationContext
    ) public payable {
        require(msg.value >= registrationFee, "Insufficient registration fee");
        require(verifiedContent[contentHash].timestamp == 0, "Content already registered");
        
        Content storage newContent = verifiedContent[contentHash];
        newContent.creator = msg.sender;
        newContent.contentHash = contentHash;
        newContent.contentURI = contentURI;
        newContent.timestamp = block.timestamp;
        newContent.creationType = creationType;
        newContent.status = VerificationStatus.SELF_ATTESTED;
        newContent.creationContext = creationContext;
        newContent.vouchCount = 0;
        newContent.platformSource = platformSource;
        
        creatorContent[msg.sender].push(contentHash);
        
        if (msg.value > 0) {
            payable(feeCollector).transfer(msg.value);
        }
        
        emit ContentRegistered(contentHash, msg.sender, contentURI, creationType);
        emit VerificationStatusUpdated(contentHash, VerificationStatus.SELF_ATTESTED);
    }
    
    /**
     * @dev Vouches for the authenticity of content as human-created
     * @param contentHash Hash of content to vouch for
     */
    function vouchForContent(string memory contentHash) 
        public 
        contentExists(contentHash) 
        hasNotVouched(contentHash) 
    {
        require(verifiedContent[contentHash].creator != msg.sender, "Cannot vouch for your own content");
        require(verifiedContent[contentHash].creationType == CreationType.HUMAN_CREATED, 
                "Can only vouch for human-created content");
        
        // Record the vouch
        contentVouches[contentHash][msg.sender] = true;
        verifiedContent[contentHash].vouchCount += 1;
        
        emit ContentVouched(contentHash, msg.sender);
        
        // Update verification status if threshold reached
        if (verifiedContent[contentHash].vouchCount >= vouchThreshold && 
            verifiedContent[contentHash].status == VerificationStatus.SELF_ATTESTED) {
            verifiedContent[contentHash].status = VerificationStatus.COMMUNITY_VOUCHED;
            emit VerificationStatusUpdated(contentHash, VerificationStatus.COMMUNITY_VOUCHED);
        }
    }
    
    /**
     * @dev Updates the creation type for content
     * @param contentHash Content to update
     * @param newCreationType New creation classification
     */
    function updateCreationType(string memory contentHash, CreationType newCreationType) 
        public 
        onlyContentCreator(contentHash) 
        contentExists(contentHash) 
    {
        verifiedContent[contentHash].creationType = newCreationType;
        
        // If changing away from human-created, reset verification status and vouches
        if (newCreationType != CreationType.HUMAN_CREATED && 
            verifiedContent[contentHash].status != VerificationStatus.UNVERIFIED) {
            verifiedContent[contentHash].status = VerificationStatus.SELF_ATTESTED;
            emit VerificationStatusUpdated(contentHash, VerificationStatus.SELF_ATTESTED);
        }
        
        emit ContentRegistered(
            contentHash, 
            verifiedContent[contentHash].creator,
            verifiedContent[contentHash].contentURI, 
            newCreationType
        );
    }
    
    /**
     * @dev Register content with minimal gas costs (for bulk operations)
     * @param contentHash Hash of content
     * @param contentURI Content URI
     * @param creationType How content was created
     */
    function batchRegisterContent(
        string memory contentHash,
        string memory contentURI,
        CreationType creationType
    ) public {
        require(verifiedContent[contentHash].timestamp == 0, "Content already registered");
        
        Content storage newContent = verifiedContent[contentHash];
        newContent.creator = msg.sender;
        newContent.contentHash = contentHash;
        newContent.contentURI = contentURI;
        newContent.timestamp = block.timestamp;
        newContent.creationType = creationType;
        newContent.status = VerificationStatus.SELF_ATTESTED;
        newContent.platformSource = "bluesky";
        
        creatorContent[msg.sender].push(contentHash);
        
        emit ContentRegistered(contentHash, msg.sender, contentURI, creationType);
        emit VerificationStatusUpdated(contentHash, VerificationStatus.SELF_ATTESTED);
    }
    
    // ===== VIEW FUNCTIONS =====
    
    /**
     * @dev Retrieves content metadata in a format that can be returned
     * @param contentHash Hash of content to retrieve
     * @return ContentMetadata struct with content details
     */
    function getContentDetails(string memory contentHash) 
        public 
        view 
        returns (ContentMetadata memory) 
    {
        Content storage content = verifiedContent[contentHash];
        return ContentMetadata({
            creator: content.creator,
            timestamp: content.timestamp,
            creationType: content.creationType,
            status: content.status,
            creationContext: content.creationContext,
            vouchCount: content.vouchCount,
            platformSource: content.platformSource,
            contentURI: content.contentURI
        });
    }
    
    /**
     * @dev Checks if an address has vouched for content
     * @param contentHash Content hash to check
     * @param voucher Address to check for vouching
     * @return Boolean indicating if address has vouched
     */
    function hasVouched(string memory contentHash, address voucher) 
        public 
        view 
        returns (bool) 
    {
        return contentVouches[contentHash][voucher];
    }
    
    /**
     * @dev Gets all content registered by a creator
     * @param creator Address of the creator
     * @return Array of content hashes
     */
    function getCreatorContent(address creator) 
        public 
        view 
        returns (string[] memory) 
    {
        return creatorContent[creator];
    }
    
    /**
     * @dev Checks if content is verified as human-created
     * @param contentHash Hash to check
     * @return Boolean indicating human verification status and verification level
     */
    function isHumanVerified(string memory contentHash) 
        public 
        view 
        returns (bool isHuman, VerificationStatus verificationLevel) 
    {
        Content storage content = verifiedContent[contentHash];
        bool isHumanContent = (content.creationType == CreationType.HUMAN_CREATED);
        
        return (isHumanContent, content.status);
    }
}
