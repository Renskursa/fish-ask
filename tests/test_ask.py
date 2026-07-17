from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch


ASK = Path(__file__).resolve().parents[1] / "bin" / "ask"
ASK_CMD = ASK.with_suffix(".cmd")
ASK_MODULE = runpy.run_path(str(ASK))


class OllamaHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []

    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if self.path != "/api/tags":
            self.send_error(404)
            return
        self._send_json({"models": [{"name": "test-local:latest"}]})

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length))
        self.requests.append(body)
        chunks = [
            {"message": {"role": "assistant", "content": "pacman"}, "done": False},
            {"message": {"role": "assistant", "content": " -Ss test"}, "done": False},
            {"message": {"role": "assistant", "content": ""}, "done": True},
        ]
        encoded = b"".join(json.dumps(chunk).encode() + b"\n" for chunk in chunks)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class AskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), OllamaHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.host = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=1)

    def run_ask(self, *args: str, **extra_env: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(extra_env)
        return subprocess.run(
            [sys.executable, str(ASK), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_local_provider_detects_model_and_streams_command(self) -> None:
        result = self.run_ask(
            "--provider",
            "ollama-local",
            "search pacman",
            ASK_OLLAMA_HOST=self.host,
            ASK_OLLAMA_MODEL="",
            OLLAMA_HOST="",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "pacman -Ss test\n")
        request = OllamaHandler.requests[-1]
        self.assertEqual(request["model"], "test-local:latest")
        self.assertEqual(request["messages"][0]["role"], "system")

    def test_cloud_provider_uses_cloud_model_through_local_daemon(self) -> None:
        result = self.run_ask(
            "--provider",
            "ollama-cloud",
            "search pacman",
            ASK_OLLAMA_HOST=self.host,
            ASK_OLLAMA_CLOUD_HOST=self.host,
            ASK_OLLAMA_CLOUD_MODEL="test:cloud",
            OLLAMA_API_KEY="",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "pacman -Ss test\n")
        self.assertEqual(OllamaHandler.requests[-1]["model"], "test:cloud")

    def test_ollama_alias(self) -> None:
        result = self.run_ask(
            "--provider",
            "ollama",
            "--model",
            "explicit-model",
            "search pacman",
            ASK_OLLAMA_HOST=self.host,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(OllamaHandler.requests[-1]["model"], "explicit-model")

    def test_api_key_selects_direct_cloud_and_bearer_auth(self) -> None:
        with patch.dict(os.environ, {"OLLAMA_API_KEY": "test-secret"}, clear=True):
            host, model = ASK_MODULE["ollama_config"]("ollama-cloud", None)
            headers = ASK_MODULE["request_headers"](host)
        self.assertEqual(host, "https://ollama.com")
        self.assertEqual(model, "gpt-oss:120b")
        self.assertEqual(headers["Authorization"], "Bearer test-secret")

    def test_prompt_detects_linux_flavour_and_shell(self) -> None:
        release = {"PRETTY_NAME": "Fedora Linux 42", "NAME": "Fedora Linux"}
        with patch.object(sys, "platform", "linux"):
            with patch("platform.freedesktop_os_release", return_value=release):
                with patch.dict(os.environ, {"SHELL": "/usr/bin/fish"}, clear=False):
                    instructions = ASK_MODULE["system_instructions"]()
        self.assertIn("Fedora Linux 42", instructions)
        self.assertIn("interactive shell is fish", instructions)
        self.assertNotIn("Arch Linux", instructions)

    def test_prompt_defaults_to_cmd_on_windows(self) -> None:
        environment = {"ASK_SHELL": "", "SHELL": "", "COMSPEC": r"C:\Windows\System32\cmd.exe"}
        with patch.object(sys, "platform", "win32"):
            with patch.dict(os.environ, environment, clear=False):
                instructions = ASK_MODULE["system_instructions"]()
        self.assertIn("for Windows", instructions)
        self.assertIn("interactive shell is cmd", instructions)
        self.assertIn("one cmd-compatible command line", instructions)

    @unittest.skipUnless(sys.platform == "win32", "Windows CMD launcher test")
    def test_cmd_launcher(self) -> None:
        result = subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(ASK_CMD), "--version"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "ask 1.1.0")

    def test_missing_prompt_is_usage_error(self) -> None:
        result = self.run_ask("--provider", "codex")
        self.assertEqual(result.returncode, 2)
        self.assertIn("a prompt is required", result.stderr)


if __name__ == "__main__":
    unittest.main()
