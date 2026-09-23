"""One-time helper: exchange a TickTick OAuth authorization code for an access token.
1. Visit: https://ticktick.com/oauth/authorize?client_id=<ID>&redirect_uri=<URI>&response_type=code&scope=tasks:write%20tasks:read
2. Copy the ?code= value from the redirect URL.
3. Run: python scripts/get_ticktick_token.py <client_id> <client_secret> <redirect_uri> <code>
"""
import sys
import httpx


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    client_id, client_secret, redirect_uri, code = sys.argv[1:5]
    resp = httpx.post("https://ticktick.com/oauth/token", data={
        "client_id": client_id, "client_secret": client_secret, "code": code,
        "grant_type": "authorization_code", "redirect_uri": redirect_uri, "scope": "tasks:write tasks:read"})
    resp.raise_for_status()
    print(resp.json())


if __name__ == "__main__":
    main()
