"""Reference hermetic guard for executable specs (trial finding F12, PR #20 review)."""
import importlib.util
import os
from pathlib import Path
import socket
import subprocess
import sys
import types
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'hermetic_guard.py'
spec = importlib.util.spec_from_file_location('hermetic_guard', SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.saved_env = dict(os.environ)
        guard.pytest_configure(None)

    def tearDown(self):
        guard.pytest_unconfigure(None)
        guard.violations.clear()
        os.environ.clear(); os.environ.update(self.saved_env)

    def blocked(self, call):
        with self.assertRaises(guard.GuardViolation):
            call()

    def test_tcp_udp_and_dns_are_blocked_loopback_included(self):
        self.blocked(lambda: socket.create_connection(('127.0.0.1', 9)))
        self.blocked(lambda: socket.socket().connect(('example.com', 443)))
        self.blocked(lambda: socket.socket().connect_ex(('127.0.0.1', 9)))
        self.blocked(lambda: socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(b'x', ('127.0.0.1', 9)))
        self.blocked(lambda: socket.getaddrinfo('example.com', 443))
        self.assertEqual(len(guard.violations), 5)

    def test_allowlisted_local_endpoint_is_reachable(self):
        os.environ['HERMETIC_GUARD_ALLOW'] = '127.0.0.1:65530'
        s = socket.socket()
        # allowed by the guard, refused by the OS (nothing listens) — not a guard violation
        self.assertNotEqual(s.connect_ex(('127.0.0.1', 65530)), None)
        s.close()
        self.blocked(lambda: socket.socket().connect_ex(('127.0.0.1', 65531)))

    def test_blocked_tools_cannot_spawn_in_any_form(self):
        for call in (lambda: subprocess.Popen(['curl', '--version']),
                     lambda: subprocess.Popen(['/usr/bin/ssh', '-V']),
                     lambda: subprocess.Popen('cd /tmp && curl x', shell=True),
                     lambda: subprocess.Popen(['anything'], executable='/usr/bin/curl'),
                     lambda: os.system('codex exec hi'),
                     lambda: os.execv('/usr/bin/curl', ['curl']),
                     lambda: os.spawnv(os.P_NOWAIT, '/usr/bin/ssh', ['ssh'])):
            with self.subTest(call=call):
                self.blocked(call)

    def test_harmless_processes_still_run(self):
        out = subprocess.run([sys.executable, '-c', 'print(1)'], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), '1')
        self.assertEqual(os.system('true'), 0)
        self.assertEqual(guard.violations, [])

    def test_child_python_processes_are_guarded_too(self):
        code = 'import socket\ntry:\n    socket.create_connection(("127.0.0.1", 9))\nexcept Exception as e:\n    print(type(e).__name__)'
        out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), 'GuardViolation', out.stderr)

    def test_swallowed_violation_still_fails_the_session(self):
        try:
            socket.create_connection(('127.0.0.1', 9))
        except guard.GuardViolation:
            pass
        session = types.SimpleNamespace(exitstatus=0)
        guard.pytest_sessionfinish(session, 0)
        self.assertEqual(session.exitstatus, 1)

    def test_new_session_starts_clean_and_unconfigure_restores(self):
        try:
            socket.create_connection(('127.0.0.1', 9))
        except guard.GuardViolation:
            pass
        guard.pytest_unconfigure(None)
        self.assertEqual(socket.create_connection.__module__, 'socket')
        self.assertIsNone(os.environ.get('HERMETIC_GUARD'))
        guard.pytest_configure(None)
        self.assertEqual(guard.violations, [])
        session = types.SimpleNamespace(exitstatus=0)
        guard.pytest_sessionfinish(session, 0)
        self.assertEqual(session.exitstatus, 0)


if __name__ == '__main__':
    unittest.main()
