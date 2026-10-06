"""Hermetic guard for executable specs (pytest plugin) — references/specs-contract.md.

A test guard, not a security sandbox: it stops the usual ways a spec reaches a network service or a
paid model by accident. Load with `-p hermetic_guard` (this directory on PYTHONPATH) or
`pytest_plugins = ["hermetic_guard"]` in the specs' conftest, and run the spec command under a clean
environment: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 TZ=UTC python3 -m pytest -p hermetic_guard ...`.

While installed, these raise GuardViolation and are recorded (a recorded violation fails the run even if
the product swallows the exception):
- socket connect / connect_ex / sendto and create_connection, loopback included;
- name resolution (getaddrinfo) of any host that is not allowed;
- spawning a blocked tool through subprocess (args, shell line or `executable=`), os.system,
  os.exec*, os.spawn* and os.posix_spawn*;
- the same inside child Python processes: install() puts a sitecustomize on PYTHONPATH.

HERMETIC_GUARD_ALLOW="127.0.0.1:8000,localhost:4444" allows connections to the product under test or a
local driver started by the spec (host:port; host alone allows any port).
HERMETIC_GUARD_BLOCK="tool1,tool2" adds blocked tools.
"""
import os
from pathlib import Path
import shlex
import socket
import subprocess

BLOCKED_TOOLS = frozenset({'curl', 'wget', 'ssh', 'scp', 'docker', 'kubectl', 'gh', 'git-remote-https',
                           'codex', 'claude', 'ollama', 'opencode', 'openai', 'aws', 'gcloud'})
SITE_DIR = Path(__file__).resolve().parent / 'hermetic_guard_site'
violations = []
_originals = {}


class GuardViolation(RuntimeError):
    pass


def _violate(what):
    violations.append(what)
    raise GuardViolation(f'hermetic guard: {what}')


def allowed():
    """Set of (host, port|None) pairs from HERMETIC_GUARD_ALLOW."""
    pairs = set()
    for item in os.environ.get('HERMETIC_GUARD_ALLOW', '').split(','):
        item = item.strip()
        if not item:
            continue
        host, _, port = item.rpartition(':') if ':' in item else (item, '', '')
        pairs.add((host or item, int(port) if port.isdigit() else None))
    return pairs


def _is_allowed(address):
    if not (isinstance(address, tuple) and len(address) >= 2):
        return False  # unix sockets and odd shapes stay blocked
    host, port = str(address[0]), address[1]
    return any(h == host and (p is None or p == port) for h, p in allowed())


def blocked_tools():
    extra = {t.strip() for t in os.environ.get('HERMETIC_GUARD_BLOCK', '').split(',') if t.strip()}
    return BLOCKED_TOOLS | extra


def _programs(args, shell=False, executable=None):
    names = []
    if executable:
        names.append(os.path.basename(str(executable)))
    if isinstance(args, (str, bytes)):
        text = args.decode() if isinstance(args, bytes) else args
        try:
            parts = shlex.split(text)
        except ValueError:
            parts = text.split()
        if shell:
            names += [os.path.basename(p) for p in parts if p not in ('&&', '||', ';', '|')]
        elif parts:
            names.append(os.path.basename(parts[0]))
    elif args:
        names.append(os.path.basename(str(list(args)[0])))
    return names


def _check_spawn(args, shell=False, executable=None):
    hit = [p for p in _programs(args, shell, executable) if p in blocked_tools()]
    if hit:
        _violate(f'spawn {hit[0]!r}')


def _child_env_install():
    """Make child Python processes load the guard too."""
    paths = [p for p in os.environ.get('PYTHONPATH', '').split(os.pathsep) if p]
    for needed in (str(SITE_DIR), str(SITE_DIR.parent)):
        if needed not in paths:
            paths.insert(0, needed)
    os.environ['PYTHONPATH'] = os.pathsep.join(paths)
    os.environ['HERMETIC_GUARD'] = '1'


def install():
    if _originals:
        return
    names = ['system'] + [n for n in dir(os) if n.startswith(('execv', 'execl', 'spawn', 'posix_spawn'))]
    _originals.update(connect=socket.socket.connect, connect_ex=socket.socket.connect_ex,
                      sendto=socket.socket.sendto, create_connection=socket.create_connection,
                      getaddrinfo=socket.getaddrinfo, popen_init=subprocess.Popen.__init__,
                      os_funcs={n: getattr(os, n) for n in names if hasattr(os, n)},
                      environ={k: os.environ.get(k) for k in ('PYTHONPATH', 'HERMETIC_GUARD')})

    def connect(self, address):
        if not _is_allowed(address):
            _violate(f'socket connect {address!r}')
        return _originals['connect'](self, address)

    def connect_ex(self, address):
        if not _is_allowed(address):
            _violate(f'socket connect_ex {address!r}')
        return _originals['connect_ex'](self, address)

    def sendto(self, data, *rest):
        address = rest[-1] if rest else None
        if not _is_allowed(address):
            _violate(f'socket sendto {address!r}')
        return _originals['sendto'](self, data, *rest)

    def create_connection(address, *args, **kwargs):
        if not _is_allowed(address):
            _violate(f'create_connection {address!r}')
        return _originals['create_connection'](address, *args, **kwargs)

    def getaddrinfo(host, port, *args, **kwargs):
        if not any(h == str(host) for h, _ in allowed()):
            _violate(f'getaddrinfo {host!r}')
        return _originals['getaddrinfo'](host, port, *args, **kwargs)

    def popen_init(self, args, *rest, **kwargs):
        _check_spawn(args, kwargs.get('shell', False), kwargs.get('executable'))
        return _originals['popen_init'](self, args, *rest, **kwargs)

    def guarded(name, original):
        def wrapper(*args, **kwargs):
            if name == 'system':
                _check_spawn(args[0] if args else '', shell=True)
            elif args:
                _check_spawn([args[0]] if name.startswith(('exec', 'posix_spawn')) else [args[1]])
            return original(*args, **kwargs)
        return wrapper

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.socket.sendto = sendto
    socket.create_connection = create_connection
    socket.getaddrinfo = getaddrinfo
    subprocess.Popen.__init__ = popen_init
    for name, original in _originals['os_funcs'].items():
        setattr(os, name, guarded(name, original))
    _child_env_install()


def uninstall():
    if not _originals:
        return
    socket.socket.connect = _originals['connect']
    socket.socket.connect_ex = _originals['connect_ex']
    socket.socket.sendto = _originals['sendto']
    socket.create_connection = _originals['create_connection']
    socket.getaddrinfo = _originals['getaddrinfo']
    subprocess.Popen.__init__ = _originals['popen_init']
    for name, original in _originals['os_funcs'].items():
        setattr(os, name, original)
    for key, value in _originals['environ'].items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    _originals.clear()


# pytest hooks
def pytest_configure(config):
    violations.clear()
    install()


def pytest_unconfigure(config):
    uninstall()


def pytest_sessionfinish(session, exitstatus):
    if violations:
        session.exitstatus = 1


def pytest_terminal_summary(terminalreporter):
    if violations:
        terminalreporter.write_line(f'HERMETIC GUARD: {len(violations)} violation(s): ' + '; '.join(violations[:5]),
                                    red=True)
