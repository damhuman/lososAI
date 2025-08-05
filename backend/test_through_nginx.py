import asyncio
import httpx
import base64

async def test_through_nginx():
    # Admin credentials
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    headers = {"Authorization": f"Basic {credentials}"}
    
    # Test through nginx (port 8081)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8081/api/v1/admin/products?page=1&size=100",
                headers=headers,
                timeout=10.0
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS through Nginx!")
                print(f"Total products: {data.get('total', 0)}")
                print(f"Items returned: {len(data.get('items', []))}")
            else:
                print(f"❌ ERROR: {response.status_code}")
                print(response.text)
                    
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_through_nginx())