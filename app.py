import streamlit as st
from atproto import Client
import imagehash
from PIL import Image
import io
import json
import requests
from datetime import datetime
import os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simplified Contract ABI for proposal
CONTRACT_ABI = json.loads('''
[
    {
        "inputs": [
            {"internalType": "string", "name": "contentHash", "type": "string"},
            {"internalType": "string", "name": "contentURI", "type": "string"},
            {"internalType": "uint8", "name": "creationType", "type": "uint8"},
            {"internalType": "string", "name": "platformSource", "type": "string"},
            {"internalType": "string", "name": "creationContext", "type": "string"}
        ],
        "name": "registerContent",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "contentHash", "type": "string"}
        ],
        "name": "vouchForContent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "contentHash", "type": "string"}
        ],
        "name": "getContentDetails",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "creator", "type": "address"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "uint8", "name": "creationType", "type": "uint8"},
                    {"internalType": "uint8", "name": "status", "type": "uint8"},
                    {"internalType": "string", "name": "creationContext", "type": "string"},
                    {"internalType": "uint256", "name": "vouchCount", "type": "uint256"},
                    {"internalType": "string", "name": "platformSource", "type": "string"},
                    {"internalType": "string", "name": "contentURI", "type": "string"}
                ],
                "internalType": "struct MetaSignetVerification.ContentMetadata",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
''')

class MetaSignetApp:
    def __init__(self):
        # Initialize Bluesky client
        self.client = Client()
        
        # Initialize web3 connection (if environment variables are available)
        self.w3_connected = False
        self.initialize_web3()
        
        # Store the client in session state
        if 'bluesky_client' not in st.session_state:
            st.session_state.bluesky_client = self.client
            
    def initialize_web3(self):
        """Initialize Web3 connection using environment variables"""
        try:
            # Get provider URL from env or use default
            provider_url = os.getenv('WEB3_PROVIDER_URL', 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY')
            
            # Connect to Ethereum
            self.w3 = Web3(Web3.HTTPProvider(provider_url))
            
            # Set contract address and create contract instance
            contract_address = os.getenv('CONTRACT_ADDRESS')
            if contract_address and self.w3.is_connected():
                self.contract = self.w3.eth.contract(
                    address=self.w3.to_checksum_address(contract_address),
                    abi=CONTRACT_ABI
                )
                self.w3_connected = True
                st.session_state.w3_connected = True
                st.session_state.w3 = self.w3
                st.session_state.contract = self.contract
        except Exception as e:
            st.warning(f"Web3 initialization failed: {str(e)}")
            self.w3_connected = False
            st.session_state.w3_connected = False

    def login_bluesky(self, username, password):
        """Login to Bluesky"""
        try:
            self.client.login(username, password)
            # Store login state
            st.session_state.is_logged_in = True
            st.session_state.bluesky_client = self.client
            st.session_state.bluesky_username = username
            return True
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False

    def extract_post_id(self, post_uri):
        """Extract post ID from a Bluesky post URI"""
        # Example URI: https://bsky.app/profile/username.bsky.social/post/12345
        try:
            if 'bsky.app' in post_uri:
                return post_uri.split('/')[-1]
            return post_uri  # Assume direct ID if not a URL
        except:
            return post_uri
            
    def get_post_details(self, post_uri):
        """Fetch post details and images from a Bluesky post"""
        if not st.session_state.get('is_logged_in', False):
            raise Exception("Not logged in. Please login first.")
            
        try:
            post_id = self.extract_post_id(post_uri)
            
            client = st.session_state.bluesky_client
            
            # This is a simplified implementation - actual code would handle various
            # response formats and edge cases from the AT Protocol
            
            # Placeholder for actual AT Protocol implementation
            # In a real implementation, this would:
            # 1. Fetch the post via appropriate AT Protocol method
            # 2. Extract text, images, and metadata
            # 3. Return structured data for display and verification
            
            # Simplified return format for the proposal
            return {
                "post_id": post_id,
                "text": "Example post text would appear here",
                "images": [Image.new('RGB', (300, 200), color='blue')],  # Placeholder image
                "author": client.me.handle,
                "timestamp": datetime.now().isoformat(),
                "uri": post_uri
            }
                
        except Exception as e:
            raise Exception(f"Error fetching post: {str(e)}")
    
    def compute_content_hash(self, post_details):
        """Compute hash of content based on text and images"""
        try:
            # In a real implementation, this would:
            # 1. Combine text content with image hashes
            # 2. Generate a unique, reproducible hash
            # 3. Handle various content types appropriately
            
            # This is a simplified example for the proposal
            text_hash = str(hash(post_details["text"]))
            
            image_hashes = []
            for img in post_details["images"]:
                if isinstance(img, bytes):
                    img = Image.open(io.BytesIO(img))
                image_hashes.append(str(imagehash.average_hash(img)))
            
            # Combine hashes (in reality would use more sophisticated approach)
            combined_hash = text_hash + "_" + "_".join(image_hashes)
            return combined_hash
            
        except Exception as e:
            raise Exception(f"Error computing content hash: {str(e)}")
        
    def verify_human_content(self, content_hash, post_uri, creation_type, creation_context=""):
        """Register content as human-created on blockchain"""
        if not st.session_state.get('w3_connected', False):
            # Simulated functionality for proposal
            if 'human_verified_content' not in st.session_state:
                st.session_state.human_verified_content = {}
                
            st.session_state.human_verified_content[content_hash] = {
                "hash": content_hash,
                "uri": post_uri,
                "type": creation_type,
                "context": creation_context,
                "timestamp": datetime.now().isoformat(),
                "status": "SELF_ATTESTED",
                "vouches": 0
            }
            
            return {
                'success': True,
                'message': 'Content verified locally'
            }
        else:
            try:
                # In a real implementation, this would call the smart contract
                # This is simplified for the proposal
                
                # Placeholder for Web3 transaction code
                # Would use: contract.functions.registerContent(...).buildTransaction(...)
                
                return {
                    'success': True,
                    'message': 'Content verified on blockchain',
                    'tx_hash': '0x' + '0' * 64  # Placeholder transaction hash
                }
                
            except Exception as e:
                raise Exception(f"Blockchain verification failed: {str(e)}")
    
    def vouch_for_content(self, content_hash):
        """Vouch for content as human-created"""
        if not st.session_state.get('w3_connected', False):
            # Simulated functionality for proposal
            if 'human_verified_content' in st.session_state and content_hash in st.session_state.human_verified_content:
                st.session_state.human_verified_content[content_hash]['vouches'] += 1
                
                # Update status if threshold reached
                if st.session_state.human_verified_content[content_hash]['vouches'] >= 3:
                    st.session_state.human_verified_content[content_hash]['status'] = "COMMUNITY_VOUCHED"
                
                return {
                    'success': True,
                    'vouches': st.session_state.human_verified_content[content_hash]['vouches']
                }
            else:
                return {
                    'success': False,
                    'message': 'Content not found'
                }
        else:
            try:
                # In a real implementation, this would call the smart contract
                # This is simplified for the proposal
                
                # Placeholder for Web3 transaction code
                # Would use: contract.functions.vouchForContent(...).buildTransaction(...)
                
                return {
                    'success': True,
                    'message': 'Vouched on blockchain',
                    'tx_hash': '0x' + '0' * 64  # Placeholder transaction hash
                }
                
            except Exception as e:
                raise Exception(f"Blockchain vouching failed: {str(e)}")
    
    def get_verification_status(self, content_hash):
        """Get verification status for content"""
        if not st.session_state.get('w3_connected', False):
            # Simulated functionality for proposal
            if 'human_verified_content' in st.session_state and content_hash in st.session_state.human_verified_content:
                content = st.session_state.human_verified_content[content_hash]
                return {
                    'exists': True,
                    'creator': 'local-user',
                    'timestamp': content['timestamp'],
                    'creation_type': content['type'],
                    'status': content['status'],
                    'context': content['context'],
                    'vouches': content['vouches'],
                    'platform': 'bluesky',
                    'uri': content['uri']
                }
            else:
                return {
                    'exists': False
                }
        else:
            try:
                # In a real implementation, this would call the smart contract
                # This is simplified for the proposal
                
                # Placeholder for Web3 call code
                # Would use: contract.functions.getContentDetails(...).call()
                
                # Simulated response for proposal
                return {
                    'exists': True,
                    'creator': '0x0000000000000000000000000000000000000000',
                    'timestamp': datetime.now().timestamp(),
                    'creation_type': 'HUMAN_CREATED',
                    'status': 'SELF_ATTESTED',
                    'context': '',
                    'vouches': 0,
                    'platform': 'bluesky',
                    'uri': 'https://bsky.app/profile/example.bsky.social/post/12345'
                }
                
            except Exception as e:
                return {
                    'exists': False,
                    'error': str(e)
                }

def main():
    st.set_page_config(
        page_title="MetaSignet - Human Content Verification",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("MetaSignet")
    st.markdown("### Verify your human-created content on Bluesky")
    
    # Initialize app
    app = MetaSignetApp()
    
    # Sidebar for authentication and settings
    with st.sidebar:
        st.header("Sign in with Bluesky")
        
        # Bluesky Authentication
        username = st.text_input("Username", key="bluesky_username")
        password = st.text_input("App Password", type="password", key="bluesky_password")
        if st.button("Sign in"):
            if app.login_bluesky(username, password):
                st.success("Signed in successfully!")
                
        # Web3 Connection Status
        st.divider()
        st.subheader("Blockchain Status")
        if st.session_state.get('w3_connected', False):
            st.success("Connected to Ethereum")
        else:
            st.info("Using local verification (blockchain not connected)")
            if st.button("Connect Wallet"):
                # In a real implementation, this would connect to MetaMask or similar
                st.warning("Wallet connection would be implemented here")
    
    # Show main content only if logged in
    if st.session_state.get('is_logged_in', False):
        # Tab navigation
        tab1, tab2, tab3 = st.tabs(["Feed", "Verify", "Community"])
        
        # Feed Tab
        with tab1:
            st.header("Your Bluesky Feed")
            
            # In a real implementation, this would fetch and display the user's feed
            # with verification status indicators
            
            st.info("This tab would display your Bluesky posts with verification status indicators")
            
            # Placeholder for feed items
            with st.container():
                for i in range(3):
                    with st.container():
                        st.divider()
                        cols = st.columns([1, 3])
                        
                        with cols[0]:
                            st.image("https://via.placeholder.com/100", width=100)
                            
                        with cols[1]:
                            st.markdown(f"**Post {i+1}**: Example post content would appear here")
                            st.caption(f"Posted on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                            
                            # Verification status indicator
                            status = ["Unverified", "Human-verified ✓", "Human-verified+ ✓✓"][i % 3]
                            st.markdown(f"**Status**: {status}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.button("View Post", key=f"view_{i}")
                            with col2:
                                if i == 0:
                                    st.button("Verify as Human", key=f"verify_{i}")
        
        # Verify Tab
        with tab2:
            st.header("Verify Your Content")
            
            # Input for Bluesky post URL
            post_url = st.text_input("Enter your Bluesky post URL or ID", 
                                    placeholder="https://bsky.app/profile/user.bsky.social/post/1234")
            
            if post_url:
                try:
                    # Fetch post details
                    with st.spinner("Fetching post..."):
                        post_details = app.get_post_details(post_url)
                    
                    # Display post content
                    st.subheader("Post Content")
                    cols = st.columns([1, 2])
                    
                    with cols[0]:
                        if post_details["images"]:
                            st.image(post_details["images"][0], width=200)
                    
                    with cols[1]:
                        st.markdown(post_details["text"])
                        st.caption(f"By @{post_details['author']} on {post_details['timestamp']}")
                    
                    # Verification options
                    st.subheader("Verification Details")
                    
                    creation_type = st.radio(
                        "How was this content created?",
                        ["Entirely by me (human)", "With AI assistance", "Primarily by AI"]
                    )
                    
                    # Map UI options to contract enum values
                    creation_type_map = {
                        "Entirely by me (human)": 1,  # HUMAN_CREATED
                        "With AI assistance": 2,      # AI_ASSISTED
                        "Primarily by AI": 3          # AI_GENERATED
                    }
                    
                    # Only show confirmation for human content
                    if creation_type == "Entirely by me (human)":
                        st.checkbox("I confirm this is my original human-created content", key="human_confirmation")
                        
                        # Optional creation context
                        creation_context = st.text_area(
                            "Add context about your creative process (optional)",
                            placeholder="Describe how you created this content..."
                        )
                    else:
                        creation_context = ""
                    
                    # Verify button
                    if st.button("Verify Content"):
                        if creation_type == "Entirely by me (human)" and not st.session_state.get("human_confirmation", False):
                            st.error("Please confirm this is your original human-created content")
                        else:
                            with st.spinner("Processing verification..."):
                                # Generate content hash
                                content_hash = app.compute_content_hash(post_details)
                                
                                # Verify content
                                result = app.verify_human_content(
                                    content_hash,
                                    post_url,
                                    creation_type_map[creation_type],
                                    creation_context
                                )
                                
                                if result['success']:
                                    st.success("Content verified successfully!")
                                    
                                    # Show verification certificate
                                    with st.expander("View Verification Certificate", expanded=True):
                                        cert_cols = st.columns([1, 2])
                                        
                                        with cert_cols[0]:
                                            st.image("https://via.placeholder.com/200", width=200)
                                        
                                        with cert_cols[1]:
                                            st.markdown("## MetaSignet Verification")
                                            st.markdown(f"**Content Hash:** `{content_hash[:16]}...`")
                                            st.markdown(f"**Verified As:** {creation_type}")
                                            st.markdown(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                            st.markdown(f"**Verification Level:** Self-attested")
                                            st.markdown(f"**URL:** [View on Bluesky]({post_url})")
                                            
                                            if st.session_state.get('w3_connected', False):
                                                st.markdown(f"**Transaction:** `{result.get('tx_hash', '0x0')[:16]}...`")
                                            
                                            st.markdown("---")
                                            st.markdown("Share this certificate to prove your content is human-created!")
                                            st.code(f"https://metasignet.app/verify/{content_hash[:16]}")
                                else:
                                    st.error(f"Verification failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Community Tab
        with tab3:
            st.header("Community Verification")
            
            # Verification Requests
            st.subheader("Verification Requests")
            
            # In a real implementation, this would show actual verification requests
            # from connections on Bluesky
            
            # Placeholder verification requests
            for i in range(2):
                with st.container():
                    st.divider()
                    cols = st.columns([1, 3])
                    
                    with cols[0]:
                        st.image("https://via.placeholder.com/100", width=100)
                        
                    with cols[1]:
                        st.markdown(f"**@user{i+1}** requests verification for their content")
                        st.markdown("*This is an example post that needs verification*")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("View Content", key=f"view_req_{i}"):
                                st.session_state.selected_content = f"content_{i}"
                        
                        with col2:
                            if st.button("Vouch as Human", key=f"vouch_{i}"):
                                with st.spinner("Processing vouch..."):
                                    # Simulate vouching process
                                    result = app.vouch_for_content(f"content_hash_{i}")
                                    if result['success']:
                                        st.success(f"Successfully vouched! Now has {result.get('vouches', 1)} vouches.")
                                    else:
                                        st.error(f"Vouching failed: {result.get('message', 'Unknown error')}")
            
            # Your Vouching Activity
            st.subheader("Your Vouching Activity")
            
            # In a real implementation, this would show the user's vouching history
            
            # Placeholder for vouching activity
            if True:
                st.info("You haven't vouched for any content yet")
            else:
                for i in range(2):
                    st.markdown(f"You vouched for **@user{i+1}'s** content on {datetime.now().strftime('%Y-%m-%d')}")
    else:
        # Welcome screen for logged out users
        st.header("Distinguish Human Creativity on Bluesky")
        
        cols = st.columns([2, 1])
        
        with cols[0]:
            st.markdown("""
            **MetaSignet helps you verify your human-created content on Bluesky.**
            
            In an age of AI-generated content, prove your work is authentically human.
            
            ### How It Works:
            
            1. **Sign in with Bluesky** - No new account needed
            2. **Select your content** - Choose posts you've created
            3. **Verify as human-made** - Self-attest your creative work
            4. **Build trust** - Community members can vouch for your creativity
            5. **Share verification** - Let your audience know it's human-made
            
            ### Benefits:
            
            - **Stand out** in a sea of AI-generated content
            - **Build reputation** as a human creator
            - **Verify others' work** through community vouching
            - **Share certificates** across platforms
            
            Sign in with your Bluesky account to get started!
            """)
        
        with cols[1]:
            st.image("https://via.placeholder.com/300", width=300)
            st.markdown("### Verification Levels")
            st.markdown("✓ **Human-verified**: Self-attested by creator")
            st.markdown("✓✓ **Human-verified+**: Community vouched")
            
            st.info("No blockchain knowledge required to get started!")

if __name__ == "__main__":
    main()
