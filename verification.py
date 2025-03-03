"""
Content verification module for MetaSignet
Handles content fingerprinting and verification processes
"""

import hashlib
import imagehash
from PIL import Image
import io
import json
import streamlit as st
from datetime import datetime
import requests
from urllib.parse import urlparse
from .database import store_verification, get_verification, add_vouch, get_user_verifications

class ContentVerifier:
    def __init__(self):
        """Initialize the content verifier"""
        pass
    
    def compute_text_hash(self, text):
        """
        Compute hash for text content
        
        Parameters:
        - text: Text content to hash
        
        Returns:
        - str: Text hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def compute_image_hash(self, image):
        """
        Compute perceptual hash for image
        
        Parameters:
        - image: PIL Image or bytes
        
        Returns:
        - str: Image perceptual hash
        """
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        
        # Use average hash algorithm for perceptual hashing
        return str(imagehash.average_hash(image))
    
    def compute_content_hash(self, post_data):
        """
        Generate a combined hash for post content
        
        Parameters:
        - post_data: Post data including text and image info
        
        Returns:
        - str: Combined content hash
        """
        # In a production system, we would:
        # 1. Generate hashes for text content
        # 2. Retrieve and generate perceptual hashes for images
        # 3. Combine them in a deterministic way
        
        # For this simplified implementation, we'll hash the text and post ID
        text = post_data.get("text", "")
        post_id = post_data.get("post_id", "")
        author = post_data.get("author_handle", "")
        
        combined = f"{text}|{post_id}|{author}"
        return self.compute_text_hash(combined)
    
    def verify_human_content(self, content_hash, content_uri, user_id, creation_type, creation_context=""):
        """
        Register content as human-created
        
        Parameters:
        - content_hash: Hash of the content
        - content_uri: URI of the original content
        - user_id: User ID (DID or handle)
        - creation_type: Type of creation (1=human, 2=AI-assisted, 3=AI-generated)
        - creation_context: Optional context about creation
        
        Returns:
        - dict: Verification result
        """
        try:
            # Store verification in database
            result = store_verification(
                content_hash=content_hash,
                content_uri=content_uri,
                user_id=user_id,
                creation_type=creation_type,
                creation_context=creation_context
            )
            
            if result:
                return {
                    'success': True,
                    'message': 'Content verified successfully',
                    'verification': result
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to store verification'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Verification error: {str(e)}'
            }
    
    def check_verification_status(self, content_hash):
        """
        Check verification status for content
        
        Parameters:
        - content_hash: Hash of the content to check
        
        Returns:
        - dict: Verification status and details
        """
        verification = get_verification(content_hash)
        
        if verification:
            # Map numeric status to human-readable status
            status_map = {
                1: "Self-attested",
                2: "Community-vouched"
            }
            
            # Map numeric creation type to human-readable type
            creation_type_map = {
                1: "Human-created",
                2: "AI-assisted",
                3: "AI-generated"
            }
            
            return {
                'exists': True,
                'verified': True,
                'creator': verification['user_id'],
                'timestamp': verification['created_at'],
                'creation_type': creation_type_map.get(verification['creation_type'], "Unknown"),
                'status': status_map.get(verification['status'], "Unknown"),
                'context': verification['creation_context'],
                'vouches': verification['vouches'],
                'uri': verification['content_uri']
            }
        else:
            return {
                'exists': False,
                'verified': False
            }
    
    def vouch_for_content(self, content_hash, voucher_id):
        """
        Add a vouch for content
        
        Parameters:
        - content_hash: Hash of content to vouch for
        - voucher_id: ID of user vouching
        
        Returns:
        - dict: Vouching result
        """
        try:
            # Check verification exists
            verification = get_verification(content_hash)
            if not verification:
                return {
                    'success': False,
                    'message': 'Content not found'
                }
            
            # Check not self-vouching
            if verification['user_id'] == voucher_id:
                return {
                    'success': False,
                    'message': 'Cannot vouch for your own content'
                }
            
            # Add vouch
            result = add_vouch(content_hash, voucher_id)
            
            if result:
                return {
                    'success': True,
                    'message': 'Successfully vouched for content',
                    'vouches': result['vouches']
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to add vouch'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Vouching error: {str(e)}'
            }
    
    def generate_certificate(self, verification, include_image=False):
        """
        Generate a verification certificate (HTML format)
        
        Parameters:
        - verification: Verification data
        - include_image: Whether to include content image
        
        Returns:
        - str: HTML certificate
        """
        if not verification or not verification.get('exists', False):
            return None
        
        # Parse creation timestamp
        try:
            timestamp = datetime.fromisoformat(verification['timestamp'])
            formatted_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_date = verification['timestamp']
        
        # Generate certificate HTML
        certificate = f"""
        <div style="border: 2px solid #1E40AF; border-radius: 8px; padding: 20px; max-width: 600px; font-family: Arial, sans-serif;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #1E40AF; margin: 0;">MetaSignet</h2>
                <p style="color: #666; margin: 5px 0;">Human Content Verification</p>
            </div>
            
            <div style="display: flex; margin-bottom: 20px;">
                <div style="flex: 1;">
                    <p><strong>Content Hash:</strong><br/>{verification['content_hash'][:16]}...</p>
                    <p><strong>Creator:</strong><br/>{verification['creator']}</p>
                    <p><strong>Verified As:</strong><br/>{verification['creation_type']}</p>
                </div>
                <div style="flex: 1;">
                    <p><strong>Verification Level:</strong><br/>{verification['status']}</p>
                    <p><strong>Vouches:</strong><br/>{verification['vouches']}</p>
                    <p><strong>Verified On:</strong><br/>{formatted_date}</p>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <p><strong>Original Content:</strong><br/>
                <a href="{verification['uri']}" target="_blank" style="color: #1E40AF;">{verification['uri']}</a></p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
                <p style="color: #666; margin: 0; font-size: 14px;">Verify at: metasignet.app/verify/{verification['content_hash'][:16]}</p>
            </div>
        </div>
        """
        
        return certificate
