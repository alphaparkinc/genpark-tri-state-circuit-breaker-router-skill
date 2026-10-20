"""MCP Server for Tri-State Circuit Breaker Router.
100% Python Standard Library JSON-RPC.
"""
import sys
import json
import time
from client import TriStateCircuitBreakerRouter

router = TriStateCircuitBreakerRouter()

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "route_request",
                                "description": "Route API request through tri-state circuit breaker with fallback cascade",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "primary": {"type": "string", "description": "Primary provider name"},
                                        "fallback_chain": {"type": "array", "description": "Ordered fallback providers list"}
                                    },
                                    "required": ["primary", "fallback_chain"]
                                }
                            },
                            {
                                "name": "record_result",
                                "description": "Record provider execution success or failure into circuit breaker",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "provider": {"type": "string"},
                                        "success": {"type": "boolean"}
                                    },
                                    "required": ["provider", "success"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                call_name = req.get("params", {}).get("name")
                args = req.get("params", {}).get("arguments", {})
                now = time.time()
                if call_name == "route_request":
                    res = router.route_request(args.get("primary"), args.get("fallback_chain", []), now)
                elif call_name == "record_result":
                    router.record_result(args.get("provider"), args.get("success"), now)
                    res = {"status": "recorded", "provider": args.get("provider")}
                else:
                    res = {"error": "Unknown tool name"}
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
