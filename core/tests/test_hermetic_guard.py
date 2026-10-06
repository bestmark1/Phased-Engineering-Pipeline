"""Reference hermetic guard for executable specs (trial finding F12)."""
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
        guard.violations.clear()
        guard.install()

    def tearDown(self):
        guard.uninstall()
        guard.violations.clear()

    def test_loopback_and_remote_connects_are_blocked(self):
        for call in (lambda: socket.create_connection(('127.0.0.1', 9)),
                     lambda: socket.socket().connect(('example.com', 443)),
                     lambda: socket.socket().connect_ex(('127.0.0.1', 9))):
            with self.assertRaises(guard.GuardViolation):
                call()
        self.assertEqual(len(guard.violations), 3)

    def test_blocked_tools_cannot_spawn_in_any_form(self):
        for args, kw in ((['curl', '--version'], {}), (['/usr/bin/ssh', '-V'], {}),
                         ('codex exec hi', {'shell': True}), ('cd /tmp && curl x', {'shell': True}),
                         ('docker ps', {})):
            with self.subTest(args=args), self.assertRaises(guard.GuardViolation):
                subprocess.Popen(args, **kw)

    def test_harmless_processes_still_run(self):
        out = subprocess.run([sys.executable, '-c', 'print(1)'], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), '1')
        self.assertEqual(guard.violations, [])

    def test_extra_blocked_tools_from_env(self):
        os.environ['HERMETIC_GUARD_BLOCK'] = 'mytool'
        try:
            with self.assertRaises(guard.GuardViolation):
                subprocess.Popen(['mytool'])
        finally:
            del os.environ['HERMETIC_GUARD_BLOCK']

    def test_swallowed_violation_still_fails_the_session(self):
        try:
            socket.create_connection(('127.0.0.1', 9))
        except guard.GuardViolation:
            pass  # the product swallows it
        session = types.SimpleNamespace(exitstatus=0)
        guard.pytest_sessionfinish(session, 0)
        self.assertEqual(session.exitstatus, 1)

    def test_uninstall_restores_originals(self):
        guard.uninstall()
        self.assertIs(socket.create_connection.__module__, 'socket')
        guard.install()


if __name__ == '__main__':
    unittest.main()
