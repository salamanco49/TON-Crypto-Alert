
import json
import os
import urllib.parse
import urllib.request

API = "https://api.geckoterminal.com/api/v2/networks/ton/new_pools?page=1"
STATE = os.getenv("STATE_FILE", "seen_pools.json")
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "TONPoolAlert/1.0"},
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.load(response)


def send(message):
    data = urllib.parse.urlencode({
        "chat_id": CHAT,
        "text": message,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data=data,
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.status


def main():
    result = fetch(API)
    pools = result.get("data", [])
    if not isinstance(pools, list):
        raise ValueError("Unexpected API response")

    current = [p["id"] for p in pools if p.get("id")]

    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as f:
            seen = set(json.load(f))
    else:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(current, f)
        print("First scan completed. Existing pools skipped.")
        return

    for pool in reversed(pools):
        pid = pool.get("id")
        if not pid or pid in seen:
            continue

        attrs = pool.get("attributes") or {}
        name = attrs.get("name") or "Unknown pair"
        created = attrs.get("pool_created_at") or "Unknown"
        liquidity = attrs.get("reserve_in_usd") or "Unknown"
        liquidity_value = float(liquidity or 0) if str(liquidity).replace(".", "", 1).isdigit() else 0.0
        address = attrs.get("address") or pid.split("_", 1)[-1]
        link = (
            "https://www.geckoterminal.com/ton/pools/"
            + urllib.parse.quote(address, safe="")
        )

        message = (
            f"🆕 New TON trading pool\n"
            f"Pair: {name}\n"
            f"Created: {created}\n"
            f"Liquidity (USD): {liquidity}\n"     
            f"{'⚠️ Low liquidity (under $500)' if liquidity_value < 500 else '✅ Liquidity above $500'}\n"
            f"Pool: {address}\n"
            f"{link}\n"
            "⚠️ Verify the token before trading."
        )
        send(message)
        seen.add(pid)

        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(sorted(seen), f)

    print(f"Checked {len(pools)} latest pools")


if __name__ == "__main__":
    main()
