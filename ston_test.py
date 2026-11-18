
import json
import urllib.request

API = "https://api.ston.fi/v1/pools"

try:
    req = urllib.request.Request(
        API,
        headers={
            "Accept": "application/json",
            "User-Agent": "TONCryptoAlert/1.0"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)

    pools = data.get("pool_list", [])

    print("STON.fi API connected!")
    print("Total pools:", len(pools))

    for pool in pools[:5]:
        print("--------------------")
        print("Address:", pool.get("address"))
        print("Token 1:", pool.get("token0_address"))
        print("Token 2:", pool.get("token1_address"))
        print("Available fields:", list(pool.keys()))

except Exception as e:
    print("STON.fi API ERROR:", str(e))
    raise
