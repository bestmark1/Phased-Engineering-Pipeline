"""Hermetic guard for executable specs (pytest plugin) — references/specs-contract.md.

Load with `-p hermetic_guard` (this directory on PYTHONPATH) or `pytest_plugins = ["hermetic_guard"]`
in the specs' conftest. While installed, any socket connect (loopback included) and any spawn of a
blocked tool raises GuardViolation. Every violation is also recorded and fails the whole run at the
end, so a product that swallows the exception still cannot pass.

Run the spec command itself under a clean environment, e.g.
`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 TZ=UTC python3 -m pytest -p hermetic_guard ...`.
Extra blocked tools: HERMETIC_GUARD_BLOCK="tool1,tool2".
"""
import os
import shlex
import socket
import subprocess

BLOCKED_TOOLS = frozenset({'curl', 'wget', 'ssh', 'scp', 'docker', 'kubectl', 'gh', 'git-remote-https',
                           'codex', 'claude', 'ollama', 'opencode', 'openai', 'aws', 'gcloud'})
violations = []
_originals = {}


class GuardViolation(RuntimeError):
    pass


def _violate(what):
    violations.append(what)
    raise GuardViolation(f'hermetic guard: {what}')


def _program(args, shell):
    """Name of the program a Popen call would start."""
    if isinstance(args, (str, bytes)):
        text = args.decode() if isinstance(args, bytes) else args
        try:
            parts = shlex.split(text)
        except ValueError:
            parts = text.split()
        if shell:  # inspect every command of a shell line, e.g. "cd x && curl y"
            return [os.path.basename(p) for p in parts if p not in ('&&', '||', ';', '|')]
        return [os.path.basename(parts[0])] if parts else []
    args = list(args)
    return [os.path.basename(str(args[0]))] if args else []


def blocked_tools():
    extra = {t.strip() for t in os.environ.get('HERMETIC_GUARD_BLOCK', '').split(',') if t.strip()}
    return BLOCKED_TOOLS | extra


def install():
    if _originals:
        return
    _originals.update(connect=socket.socket.connect, connect_ex=socket.socket.connect_ex,
                      create_connection=socket.create_connection, popen_init=subprocess.Popen.__init__)

    def connect(self, address):
        _violate(f'socket connect {address!r}')

    def connect_ex(self, address):
        _violate(f'socket connect_ex {address!r}')

    def create_connection(address, *args, **kwargs):
        _violate(f'create_connection {address!r}')

    def popen_init(self, args, *rest, **kwargs):
        shell = kwargs.get('shell', False)
        hit = [p for p in _program(args, shell) if p in blocked_tools()]
        if hit:
            _violate(f'spawn {hit[0]!r}')
        return _originals['popen_init'](self, args, *rest, **kwargs)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.create_connection = create_connection
    subprocess.Popen.__init__ = popen_init


def uninstall():
    if not _originals:
        return
    socket.socket.connect = _originals['connect']
    socket.socket.connect_ex = _originals['connect_ex']
    socket.create_connection = _originals['create_connection']
    subprocess.Popen.__init__ = _originals['popen_init']
    _originals.clear()


# pytest hooks
def pytest_configure(config):
    install()


def pytest_sessionfinish(session, exitstatus):
    if violations:
        session.exitstatus = 1


def pytest_terminal_summary(terminalreporter):
    if violations:
        terminalreporter.write_line(f'HERMETIC GUARD: {len(violations)} violation(s): ' + '; '.join(violations[:5]),
                                    red=True)
