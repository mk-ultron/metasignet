"""
Bluesky API integration for MetaSignet
Handles authentication and content fetching through AT Protocol
"""

import os
import streamlit as st
from atproto import Client
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BlueskyAPI:
    def __init__(self):
        """Initialize the Bluesky API client"""
        self.client = Client()
        self.authenticated = False
        
    def login(self, username=None, password=None):
        """
        Login to Bluesky using provided credentials or from environment/secrets
        
        Parameters:
        - username: Bluesky username (optional if in env/secrets)
        - password: Bluesky app password (optional if in env/secrets)
        
        Returns:
        - bool: Success status
        """
        try:
            # Use provided credentials or fetch from environment/secrets
            username = username or st.secrets.get("BLUESKY_USERNAME", os.getenv("BLUESKY_USERNAME"))
            password = password or st.secrets.get("BLUESKY_PASSWORD", os.getenv("BLUESKY_PASSWORD"))
            
            if not username or not password:
                st.error("Bluesky credentials not found")
                return False
            
            # Log in to Bluesky
            self.client.login(username, password)
            self.authenticated = True
            
            # Store in session state
            if "bluesky_client" not in st.session_state:
                st.session_state.bluesky_client = self.client
                st.session_state.bluesky_username = username
                st.session_state.is_logged_in = True
            
            return True
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False
    
    def extract_post_id(self, post_uri):
        """
        Extract post ID from a Bluesky post URI
        
        Parameters:
        - post_uri: Full URI or post ID
        
        Returns:
        - str: Post ID
        """
        try:
            if 'bsky.app' in post_uri:
                parts = post_uri.split('/')
                return parts[-1]
            return post_uri  # Assume direct ID if not a URL
        except:
            return post_uri
    
    def get_profile(self):
        """Get the current user's profile"""
        if not self.authenticated:
            st.error("Not authenticated. Please login first.")
            return None
        
        try:
            return self.client.app.bsky.actor.getProfile({'actor': self.client.me.did})
        except Exception as e:
            st.error(f"Error fetching profile: {str(e)}")
            return None
    
    def get_post(self, post_uri):
        """
        Fetch a specific post by URI or ID
        
        Parameters:
        - post_uri: Post URI or ID
        
        Returns:
        - dict: Post data with content, images, and metadata
        """
        if not self.authenticated:
            st.error("Not authenticated. Please login first.")
            return None
        
        try:
            post_id = self.extract_post_id(post_uri)
            
            # Get the post record - we'll try several approaches
            try:
                # Try getting with the current user's DID (if it's their post)
                response = self.client.com.atproto.repo.get_record({
                    'repo': self.client.me.did,
                    'collection': 'app.bsky.feed.post',
                    'rkey': post_id
                })
                post_data = response.value
            except Exception:
                # If that fails, try getting the post from the feed
                response = self.client.app.bsky.feed.get_post({'uri': f'at://{self.client.me.did}/app.bsky.feed.post/{post_id}'})
                post_data = response.thread.post.record
            
            # Extract data from post
            text = post_data.text if hasattr(post_data, 'text') else ""
            
            # For this simplified implementation, we'll just note if images exist
            # A full implementation would extract and process the images
            has_images = hasattr(post_data, 'embed') and hasattr(post_data.embed, 'images')
            
            # Build the response
            post_info = {
                "post_id": post_id,
                "text": text,
                "has_images": has_images,
                "author_did": self.client.me.did,
                "author_handle": self.client.me.handle,
                "timestamp": datetime.now().isoformat(),
                "uri": post_uri if 'bsky.app' in post_uri else f"https://bsky.app/profile/{self.client.me.handle}/post/{post_id}"
            }
            
            return post_info
        except Exception as e:
            st.error(f"Error fetching post: {str(e)}")
            return None
    
    def get_user_posts(self, limit=10):
        """
        Get posts from the current user's feed
        
        Parameters:
        - limit: Number of posts to retrieve
        
        Returns:
        - list: List of posts
        """
        if not self.authenticated:
            st.error("Not authenticated. Please login first.")
            return []
        
        try:
            feed = self.client.app.bsky.feed.get_author_feed({
                'actor': self.client.me.did,
                'limit': limit
            })
            
            posts = []
            for feed_item in feed.feed:
                post = feed_item.post
                
                # Check if post has images
                has_images = False
                if hasattr(post, 'embed'):
                    has_images = hasattr(post.embed, 'images')
                
                post_info = {
                    "post_id": post.uri.split('/')[-1],
                    "text": post.record.text if hasattr(post.record, 'text') else "",
                    "has_images": has_images,
                    "author_did": post.author.did,
                    "author_handle": post.author.handle,
                    "timestamp": post.indexedAt,
                    "uri": f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
                }
                posts.append(post_info)
            
            return posts
        except Exception as e:
            st.error(f"Error fetching user posts: {str(e)}")
            return []
