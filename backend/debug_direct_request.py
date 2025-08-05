import asyncio
import httpx
import base64

async def test_direct_request():
    # Admin credentials
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    headers = {"Authorization": f"Basic {credentials}"}
    
    # Test with the backend service directly
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/admin/products?page=1&size=100",
                headers=headers,
                timeout=10.0
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 500:
                print("Response text:")
                print(response.text)
            else:
                print("Success!")
                data = response.json()
                print(f"Total: {data.get('total', 0)}")
                if data.get('items'):
                    print(f"First item packages: {data['items'][0].get('packages', [])}")
                    
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_request())