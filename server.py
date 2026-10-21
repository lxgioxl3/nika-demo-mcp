import sys, json
import handlers
TOOLS = json.loads(r'''[{"name": "suma", "description": "Suma dos numeros enteros y devuelve el resultado.", "inputSchema": {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}}, {"name": "hora", "description": "Devuelve la hora local del equipo.", "inputSchema": {"type": "object", "properties": {}}}]''')
NAME = "nika-demo"
VERSION = "0.1.0"


def send(o):
    sys.stdout.write(json.dumps(o) + "\n")
    sys.stdout.flush()


def main():
    nombres = [t["name"] for t in TOOLS]
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except ValueError:
            continue
        mid, met = m.get("id"), m.get("method")
        if met == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": NAME, "version": VERSION}}})
        elif met == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
        elif met == "tools/call":
            p = m.get("params") or {}
            if p.get("name") not in nombres:
                send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "herramienta desconocida"}})
                continue
            try:
                r = getattr(handlers, p["name"])(**(p.get("arguments") or {}))
                send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": str(r)}], "isError": False}})
            except Exception as e:
                send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": type(e).__name__}], "isError": True}})
        elif mid is not None:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "metodo no soportado"}})


main()
