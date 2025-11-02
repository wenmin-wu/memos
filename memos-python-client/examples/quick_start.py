#!/usr/bin/env python3
"""
Quick start example for the Memos Python client.

This example shows the most basic usage to get you started quickly.
"""

from memos_client import MemosClient, Visibility


async def quick_start():
    """Quick start example."""

    # Initialize client (update with your actual server details)
    async with MemosClient(
        base_url="https://your-memos-server.com",
        access_token="your-jwt-access-token"  # Get this from your Memos settings
    ) as client:

        print("🔗 Connected to Memos!")

        # Create a memo
        memo = await client.create_memo(
            content="# Hello from Python! 🐍\n\nThis memo was created using the Python client.",
            visibility=Visibility.PRIVATE,
            tags=["python", "api", "hello-world"]
        )
        print(f"✅ Created memo: {memo.memo_id}")

        # Search for memos
        results = await client.search_memos(query="python", limit=5)
        print(f"🔍 Found {len(results)} memos containing 'python'")

        # Update the memo
        updated = await client.update_memo(
            memo_id=memo.name,
            content="# Updated Hello from Python! 🐍\n\nThis memo was updated via the API.",
            pinned=True
        )
        print(f"📝 Updated memo, now pinned: {updated.pinned}")

        # Get the specific memo
        retrieved = await client.get_memo(memo.name)
        print(f"📖 Retrieved memo snippet: {retrieved.snippet[:50]}...")

        # Clean up (optional)
        await client.delete_memo(memo.name)
        print("🧹 Cleaned up demo memo")


if __name__ == "__main__":
    print("🚀 Memos Python Client - Quick Start")
    print("====================================")
    print()
    print("⚠️  Before running this example:")
    print("   1. Update the base_url with your Memos server URL")
    print("   2. Get your access token from your Memos settings")
    print("   3. Replace 'your-jwt-access-token' with your actual token")
    print()

    # Uncomment the line below to run the example
    # asyncio.run(quick_start())

    print("💡 Uncomment the asyncio.run() line above to run the example!")
