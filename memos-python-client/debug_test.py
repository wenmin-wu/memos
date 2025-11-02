#!/usr/bin/env python3
"""Debug test for Pydantic issue."""

import traceback

try:
    print("Testing basic imports...")
    from datetime import datetime
    from enum import Enum
    print("✅ Basic imports OK")
    
    print("Testing Pydantic...")
    from pydantic import BaseModel, Field
    print("✅ Pydantic imports OK")
    
    print("Testing enum creation...")
    class TestEnum(str, Enum):
        TEST = "TEST"
    print("✅ Enum creation OK")
    
    print("Testing basic model...")
    class TestModel(BaseModel):
        name: str = Field(description="Test name")
        value: int = Field(default=0)
    
    test_instance = TestModel(name="test")
    print(f"✅ Basic model creation OK: {test_instance}")
    
    print("Testing visibility enum...")
    from memos_client.models.memo import Visibility
    print(f"✅ Visibility enum OK: {Visibility.PRIVATE}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Full traceback:")
    traceback.print_exc()
