#!/usr/bin/env python3
"""
Simple test to verify the Memos client installation.
"""

try:
    from memos_client import MemosClient, Visibility, State
    from memos_client.models.memo import Memo
    from memos_client.models.attachment import Attachment
    from memos_client.config import ClientConfig
    print("✅ All imports successful!")
    
    # Test basic model creation
    config = ClientConfig(
        base_url="https://example.com",
        access_token="test-token"
    )
    print(f"✅ Config created: {config.api_base_url}")
    
    # Test enum values
    print(f"✅ Visibility enum: {Visibility.PRIVATE.value}")
    print(f"✅ State enum: {State.NORMAL.value}")
    
    print("\n🎉 Installation test passed! All dependencies are working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)
