
import json
import os
import urllib.request

API = "https://api.ston.fi/v1/pools"
STATE = "ston_seen.json"
MIN_USD = 500


def fetch_pools():
    req = urllib.request.Request(
        API,
        headers={
            "Accept": "application/json",
            "User-Agent": "TONCryptoAlert/1.0"
        }
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.load(response)

    pools = data.get("pool_list", [])
    if not isinstance(pools, list):
        raise ValueError("Invalid STON.fi response")

    return pools


def main():
    pools = fetch_pools()
    current = {
        p["address"] for p in pools
        if p.get("address")
    }

    print("Total STON.fi pools:", len(current))

    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            seen = set(json.load(f))
    else:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(sorted(current), f)

        print("First scan: old pools saved.")
        print("No alerts sent.")
        return

    new_count = 0
    qualified = 0

    for pool in pools:
        address = pool.get("address")

        if not address or address in seen:
            continue

        new_count += 1

        try:
            value_usd = float(
                pool.get("lp_total_supply_usd") or 0
            )
        except (ValueError, TypeError):
            value_usd = 0

        if value_usd > MIN_USD:
            qualified += 1
            print("--------------------")
            print("NEW STON.fi POOL")
            print("Address:", address)
            print("Candidate liquidity USD:", value_usd)
            print("Volume 24h:", pool.get("volume_24h_usd"))

    with open(STATE, "w", encoding="utf-8") as f:
        
        json.dump(sorted(seen | {
            p["address"] for p in pools
            if p.get("address") and (
                p["address"] in seen or
                (
                    p.get("lp_total_supply_usd") is not None
                    and float(p["lp_total_supply_usd"]) > MIN_USD
                )
            )
        }), f)


    print("New pools:", new_count)
    print("Above $500:", qualified)
    print("Test only: no Telegram messages sent.")


if __name__ == "__main__":
    main()
