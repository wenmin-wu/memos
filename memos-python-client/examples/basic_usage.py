"""
Basic usage example for the Memos Python client.

This example demonstrates the core functionality:
- Authentication
- Creating memos
- Searching memos
- Updating memos
- Working with attachments
"""

import asyncio
from pathlib import Path

from memos_client import MemosClient, Visibility


async def main():
    """Main example function."""

    # Initialize client with JWT token (recommended)
    async with MemosClient(
        base_url="https://your-memos-instance.com",
        access_token="your-jwt-token-here"
    ) as client:

        print("🔗 Connected to Memos server")

        # Create a simple memo
        print("\n📝 Creating a memo...")
        memo = await client.create_memo(
            content="# My First Note\n\nThis is a test note created from Python!",
            visibility=Visibility.PRIVATE,
            tags=["python", "example", "test"]
        )
        print(f"✅ Created memo: {memo.name}")
        print(f"   Content snippet: {memo.snippet[:50]}...")

        # Search for memos
        print("\n🔍 Searching for memos...")
        search_results = await client.search_memos(
            query="python",
            limit=10
        )
        print(f"Found {len(search_results)} memos containing 'python'")

        # Get specific memo
        print(f"\n📖 Retrieving memo {memo.memo_id}...")
        retrieved_memo = await client.get_memo(memo.name)
        print(f"✅ Retrieved memo: {retrieved_memo.name}")
        print(f"   Tags: {retrieved_memo.tags}")
        print(f"   Created: {retrieved_memo.create_time}")

        # Update the memo
        print("\n✏️  Updating memo...")
        updated_memo = await client.update_memo(
            memo_id=memo.name,
            content="# My Updated Note\n\nThis note has been updated from Python!",
            visibility=Visibility.PUBLIC,
            pinned=True
        )
        print(f"✅ Updated memo: {updated_memo.name}")
        print(f"   New visibility: {updated_memo.visibility}")
        print(f"   Pinned: {updated_memo.pinned}")

        # Search with advanced filters
        print("\n🔍 Advanced search...")
        advanced_results = await client.search_memos(
            tags=["python", "example"],
            visibility=Visibility.PUBLIC,
            order_by="create_time desc",
            limit=5
        )
        print(f"Found {len(advanced_results)} public memos with python/example tags")

        # Clean up - delete the test memo
        print("\n🗑️  Cleaning up...")
        await client.delete_memo(memo.name)
        print("✅ Deleted test memo")


async def attachment_example():
    """Example of working with attachments."""

    async with MemosClient(
        base_url="https://your-memos-instance.com",
        access_token="your-jwt-token-here"
    ) as client:

        print("📎 Attachment Example")
        print("====================")

        # Create a test image file
        test_image_path = Path("test_image.png")
        if not test_image_path.exists():
            # Create a simple test file
            test_image_path.write_bytes(b"fake image data")

        try:
            # Upload attachment
            print("📤 Uploading attachment...")
            attachment = await client.upload_attachment(
                file_path=test_image_path,
                filename="my_screenshot.png",
                mime_type="image/png"
            )
            print(f"✅ Uploaded attachment: {attachment.name}")
            print(f"   Filename: {attachment.filename}")
            print(f"   Size: {attachment.format_size()}")
            print(f"   Type: {attachment.type}")

            # Create memo with attachment
            print("\n📝 Creating memo with attachment...")
            memo = await client.create_memo(
                content="# Screenshot\n\nHere's my latest screenshot:",
                attachments=[attachment.name],
                visibility=Visibility.PRIVATE
            )
            print(f"✅ Created memo with attachment: {memo.name}")

            # Download attachment
            print("\n📥 Downloading attachment...")
            binary_data = await client.get_attachment_binary(
                attachment_name=attachment.name,
                filename=attachment.filename
            )
            print(f"✅ Downloaded {len(binary_data)} bytes")

            # Clean up
            await client.delete_memo(memo.name)
            print("🧹 Cleaned up test memo")

        finally:
            # Clean up test file
            if test_image_path.exists():
                test_image_path.unlink()


async def batch_operations_example():
    """Example of batch operations."""

    async with MemosClient(
        base_url="https://your-memos-instance.com",
        access_token="your-jwt-token-here"
    ) as client:

        print("📦 Batch Operations Example")
        print("===========================")

        # Create multiple memos
        memo_contents = [
            "# Daily Standup Notes\n\n- Fixed bug #123\n- Started feature ABC",
            "# Meeting Notes\n\n## Attendees\n- Alice\n- Bob\n\n## Action Items\n- Review PR",
            "# Ideas\n\n💡 New feature idea: Smart tagging",
            "# Resources\n\n📚 Useful links:\n- https://example.com",
        ]

        print(f"📝 Creating {len(memo_contents)} memos...")
        created_memos = []

        for i, content in enumerate(memo_contents):
            memo = await client.create_memo(
                content=content,
                visibility=Visibility.PRIVATE,
                tags=["batch", f"memo-{i+1}"]
            )
            created_memos.append(memo)
            print(f"  ✅ Created memo {i+1}: {memo.memo_id}")

        # Search for all batch memos
        print("\n🔍 Searching for batch memos...")
        batch_memos = await client.search_memos(
            tags=["batch"],
            order_by="create_time asc"
        )
        print(f"Found {len(batch_memos)} batch memos")

        # Update all batch memos to be public
        print("\n🔄 Updating all batch memos to public...")
        for memo in batch_memos:
            await client.update_memo(
                memo_id=memo.name,
                visibility=Visibility.PUBLIC
            )
            print(f"  ✅ Updated {memo.memo_id} to public")

        # Clean up
        print("\n🧹 Cleaning up batch memos...")
        for memo in created_memos:
            await client.delete_memo(memo.name)
        print("✅ Cleaned up all batch memos")


if __name__ == "__main__":
    print("🚀 Memos Python Client Examples")
    print("================================")

    # You'll need to update these with your actual Memos server details
    print("⚠️  Please update the base_url and access_token in the examples!")
    print("   Get your access token from your Memos instance settings.")
    print()

    # Run basic example
    print("Running basic usage example...")
    asyncio.run(main())

    print("\n" + "="*50)

    # Run attachment example
    print("Running attachment example...")
    asyncio.run(attachment_example())

    print("\n" + "="*50)

    # Run batch operations example
    print("Running batch operations example...")
    asyncio.run(batch_operations_example())

    print("\n✨ All examples completed!")
