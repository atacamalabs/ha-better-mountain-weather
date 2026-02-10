#!/usr/bin/env python3
"""Test script to validate Météo-France API tokens."""

import asyncio
import aiohttp
from meteofrance_api import MeteoFranceClient


async def test_arome_token(token: str):
    """Test AROME API token."""
    print(f"Testing AROME token: {token[:10]}...")

    try:
        async with aiohttp.ClientSession() as session:
            # Try different initialization methods
            print("\nAttempt 1: Using api_key parameter")
            try:
                client = MeteoFranceClient(api_key=token, session=session)
                places = await client.search_places(45.9237, 6.8694)
                print(f"✅ Success! Found {len(places)} places")
                if places:
                    print(f"   First place: {places[0].name}")
                return True
            except Exception as e:
                print(f"❌ Failed: {e}")

            print("\nAttempt 2: Using token parameter")
            try:
                client = MeteoFranceClient(token=token, session=session)
                places = await client.search_places(45.9237, 6.8694)
                print(f"✅ Success! Found {len(places)} places")
                if places:
                    print(f"   First place: {places[0].name}")
                return True
            except Exception as e:
                print(f"❌ Failed: {e}")

            print("\nAttempt 3: No token parameter (free API)")
            try:
                client = MeteoFranceClient(session=session)
                places = await client.search_places(45.9237, 6.8694)
                print(f"✅ Success! Found {len(places)} places")
                if places:
                    print(f"   First place: {places[0].name}")
                return True
            except Exception as e:
                print(f"❌ Failed: {e}")

    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 test_token.py YOUR_AROME_TOKEN")
        print("\nThis will test your Météo-France AROME API token")
        sys.exit(1)

    token = sys.argv[1]
    asyncio.run(test_arome_token(token))
