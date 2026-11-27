import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class MCPStdioClient:
    """Real JSON-RPC 2.0 MCP Client communicating with MCP servers over stdio
    (e.g., mcp_servers/agentic_os_mcp/server.py configured in mcp_config.json).
    """

    def __init__(
        self,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        config_path: Optional[Path] = None,
        server_name: str = "agentic-os-engine"
    ):
        self.server_name = server_name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self._process: Optional[subprocess.Popen] = None
        self._req_id = 0

        if self.command is None:
            self._load_from_mcp_config(config_path, server_name)

    def _load_from_mcp_config(self, config_path: Optional[Path], server_name: str) -> None:
        root = Path(__file__).resolve().parent.parent.parent.parent
        cfg_file = config_path or (root / "mcp_config.json")
        if cfg_file.exists():
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
            srv = data.get("mcpServers", {}).get(server_name, {})
            if srv:
                self.command = srv.get("command", sys.executable)
                self.args = srv.get("args", ["-m", "mcp_servers.agentic_os_mcp.server"])
                self.env = srv.get("env", {})
                return

        self.command = sys.executable
        self.args = ["-m", "mcp_servers.agentic_os_mcp.server"]
        self.env = {"PYTHONPATH": str(root)}

    def start(self) -> Dict[str, Any]:
        """Spawns the MCP server subprocess and performs the initialize handshake."""
        if self._process is not None and self._process.poll() is None:
            return {"status": "already_running"}

        proc_env = os.environ.copy()
        proc_env.update(self.env)

        self._process = subprocess.Popen(
            [self.command, *self.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=proc_env,
            bufsize=1
        )

        init_resp = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "agentic-os-runtime", "version": "1.0.0"}
        })
        # Send initialized notification
        self._send_notification("notifications/initialized", {})
        return init_resp

    def list_tools(self) -> List[Dict[str, Any]]:
        """Queries tools/list from the live MCP server."""
        if self._process is None or self._process.poll() is not None:
            self.start()
        resp = self._send_request("tools/list", {})
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Invokes tools/call on the live MCP server and parses the JSON text payload."""
        if self._process is None or self._process.poll() is not None:
            self.start()
        resp = self._send_request("tools/call", {"name": name, "arguments": arguments})
        result = resp.get("result", {})
        if result.get("isError"):
            err_msg = result.get("content", [{}])[0].get("text", "Unknown MCP tool error")
            raise RuntimeError(f"MCP tool '{name}' failed: {err_msg}")

        content_blocks = result.get("content", [])
        if content_blocks and content_blocks[0].get("type") == "text":
            text = content_blocks[0].get("text", "{}")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        return result

    def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        assert self._process is not None and self._process.stdin and self._process.stdout
        self._req_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": method,
            "params": params
        }
        self._process.stdin.write(json.dumps(req) + "\n")
        self._process.stdin.flush()

        line = self._process.stdout.readline()
        if not line:
            stderr_out = self._process.stderr.read() if self._process.stderr else ""
            raise RuntimeError(f"MCP server closed stream unexpectedly. Stderr: {stderr_out}")
        return json.loads(line.strip())

    def _send_notification(self, method: str, params: Dict[str, Any]) -> None:
        assert self._process is not None and self._process.stdin
        notif = {"jsonrpc": "2.0", "method": method, "params": params}
        self._process.stdin.write(json.dumps(notif) + "\n")
        self._process.stdin.flush()

    def close(self) -> None:
        if self._process is not None:
            try:
                self._process.terminate()
                self._process.wait(timeout=3)
            except Exception:
                self._process.kill()
            finally:
                self._process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
