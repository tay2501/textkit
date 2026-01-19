# CLI Improvement Proposals

**Created**: 2026-01-14
**Status**: Proposal (Not Implemented)
**Based on**: Unix Philosophy, clig.dev, POSIX Standards, PEP 690/810

---

## Executive Summary

| Issue | Current | Target | Improvement |
|-------|---------|--------|-------------|
| Typing overhead | 40+ chars | 10-15 chars | 60-75% reduction |
| Output verbosity | Always verbose | Silent by default | Unix compliance |
| Startup time | 2-5 sec (est.) | <500ms | 80%+ reduction |

---

## Issue 1: Typing Overhead Reduction

### Current Problem
```bash
# 47 characters - too verbose for daily use
uv run .\main.py text transform /t -c -C
```

### Proposed Solutions (Priority Order)

#### 1.1 Shell Alias (Recommended - Zero Code Change)

**Evidence**: Docker, Git, Kubernetes all rely heavily on aliases.
- `docker ps` → `dps` (common alias)
- `kubectl get pods` → `kgp` (common alias)
- `git status` → `gs` (common alias)

**Implementation**:
```bash
# ~/.bashrc or ~/.zshrc
alias tt='uv run python H:/Development/Git/textkit/bin/tt.py'
alias ttc='tt -c -C'  # clipboard workflow

# PowerShell $PROFILE
function tt { uv run python H:\Development\Git\textkit\bin\tt.py $args }
function ttc { tt -c -C $args }  # clipboard workflow
```

**Result**: `tt '/t/l' -c -C` → `ttc '/t/l'` (15 chars, 68% reduction)

**Pros**:
- Zero code change required
- Industry standard approach (Docker, Git, k8s)
- User-configurable per environment
- No maintenance burden

**Cons**:
- Requires user setup
- Not portable across machines without dotfiles sync

---

#### 1.2 PATH Registration with Symlink

**Evidence**: Standard Unix practice (`/usr/local/bin`)

**Implementation**:
```bash
# Unix/Linux/macOS
ln -s /path/to/textkit/bin/tt.py /usr/local/bin/tt
chmod +x /usr/local/bin/tt

# Windows (requires Admin)
mklink C:\tools\tt.bat H:\Development\Git\textkit\bin\tt.bat
# Add C:\tools to PATH
```

**Result**: `tt '/t/l'` anywhere (no `uv run` prefix)

**Pros**:
- System-wide availability
- Standard Unix approach
- Works without shell configuration

**Cons**:
- Requires admin/sudo
- Bypasses `uv` environment management
- May cause dependency issues

---

#### 1.3 UV Tool Installation (Modern Python Approach)

**Evidence**: [UV Tool Documentation](https://docs.astral.sh/uv/guides/tools/)

**Implementation**:
```bash
# Install as global tool
uv tool install --from . textkit

# Or publish to PyPI and install
uv tool install textkit
```

**Result**: `tt '/t/l'` globally available

**Pros**:
- Modern Python best practice
- Automatic dependency isolation
- Easy updates via `uv tool upgrade`

**Cons**:
- Requires package restructuring
- May need PyPI publication

---

#### 1.4 Compound Command Shortcuts

**Evidence**: Git's `git stash pop`, `git commit -am`

**Implementation Options**:

```python
# Option A: Dedicated shortcut commands
@app.command("tc")  # transform-clipboard
def transform_clipboard(rules: str):
    """Shortcut: transform from/to clipboard."""
    # Equivalent to: tt <rules> -c -C
    ...

# Option B: Rule aliases in config
# ~/.textkit.toml
[aliases]
trim = "/t"
lower = "/l"
tl = "/t/l"  # combined
```

**Result**: `tt tc '/t/l'` or `tt tl`

---

#### 1.5 Fish/Zsh Abbreviations (Shell-Specific)

**Evidence**: Fish shell abbreviations, Zsh `abbr` plugin

```fish
# Fish shell
abbr -a tt 'uv run python bin/tt.py'
abbr -a ttc 'uv run python bin/tt.py -c -C'
```

**Pros**:
- Expands on type (visible to user)
- Combines speed with learnability

---

### Recommendation Matrix

| Solution | Effort | Impact | Portability | Recommended For |
|----------|--------|--------|-------------|-----------------|
| Shell Alias | Low | High | Medium | All users |
| UV Tool | Medium | High | High | Distribution |
| Symlink | Low | Medium | Low | Personal use |
| Command Shortcuts | Medium | Medium | High | Power users |

**Primary Recommendation**: Shell Alias (1.1) + UV Tool (1.3) for distribution

---

## Issue 2: Output Verbosity (Unix Rule of Silence)

### Current Problem
```bash
$ tt '/t/l' -c -C
Processing...
Transformed: "hello world"
Copied to clipboard!
```

### Unix Philosophy Reference

> "When a program has nothing surprising to say, it should say nothing."
> — Eric S. Raymond, The Art of Unix Programming

**Evidence**:
- `cp`, `mv`, `rm` - no output on success
- `grep` - only matching lines
- `git add` - silent on success
- `docker pull` - progress only when useful

### Proposed Solutions

#### 2.1 Silent Mode by Default (Recommended)

**Implementation**:
```python
# Default behavior: silent on success
def output_text(result: str, quiet: bool = True) -> None:
    if not quiet:
        console.print(f"Transformed: {result}")
    print(result)  # Always output the actual data
```

**Result**:
```bash
# Default: only data output
$ tt '/t/l' -c -C
hello world

# Verbose when requested
$ tt '/t/l' -c -C -v
[info] Input: "  HELLO WORLD  "
[info] Applied: trim, lowercase
hello world
[info] Copied to clipboard
```

---

#### 2.2 Verbosity Levels (Industry Standard)

**Evidence**: GNU coreutils, curl, wget, rsync

| Level | Flag | Output |
|-------|------|--------|
| Silent | `-q, --quiet` | Errors only |
| Normal | (default) | Result only |
| Verbose | `-v, --verbose` | Progress + result |
| Debug | `-vv` or `--debug` | Full trace |

**Implementation**:
```python
class VerbosityLevel(IntEnum):
    QUIET = 0    # Errors only (stderr)
    NORMAL = 1   # Result only (stdout)
    VERBOSE = 2  # Progress + result
    DEBUG = 3    # Full diagnostic

# Environment variable override
TEXTKIT_VERBOSITY = os.getenv("TEXTKIT_VERBOSITY", "1")
```

---

#### 2.3 TTY Detection (Smart Default)

**Evidence**: Git, Docker, npm - all detect TTY

**Implementation**:
```python
import sys

def should_show_progress() -> bool:
    """Show progress only in interactive terminal."""
    return sys.stdout.isatty() and sys.stderr.isatty()

def output_result(result: str) -> None:
    # Progress to stderr (won't break pipes)
    if should_show_progress():
        print("Processing...", file=sys.stderr)
    
    # Data to stdout (pipeable)
    print(result)
```

**Result**:
```bash
# Interactive: shows progress
$ tt '/t/l'
Processing...
hello world

# Piped: clean output only
$ tt '/t/l' | wc -c
11
```

---

#### 2.4 clig.dev Compliance Checklist

Based on [clig.dev Guidelines](https://clig.dev/):

| Guideline | Current | Target |
|-----------|---------|--------|
| stdout for data | Partial | Full |
| stderr for messages | No | Yes |
| Non-zero exit on error | Yes | Yes |
| --quiet flag | No | Yes |
| --verbose flag | Partial | Full |
| TTY detection | No | Yes |
| NO_COLOR support | No | Yes |
| Progress to stderr | No | Yes |

---

### Recommendation

**Primary**: Implement 2.3 (TTY Detection) + 2.2 (Verbosity Levels)

```python
# Pseudocode
if sys.stdout.isatty():
    # Interactive mode: minimal feedback
    print(result)
    if not quiet:
        print("Copied.", file=sys.stderr)
else:
    # Pipe mode: data only
    print(result)
```

---

## Issue 3: Performance Optimization

### Current Bottlenecks (from profiling_analysis.txt)

| Component | Time | % of Total |
|-----------|------|------------|
| Cryptography | 75s | 36% |
| Regex compilation | 25s | 12% |
| Thread locks | 57s | 27% |
| Sleep operations | 17s | 8% |

### Proposed Solutions

#### 3.1 Lazy Imports (PEP 690/810)

**Evidence**: 
- [PEP 690](https://peps.python.org/pep-0690/) - Accepted for Python 3.12+
- Instagram Server: 40% startup improvement
- Meta CLI tools: 50-80% startup improvement

**Implementation**:
```python
# Option A: Python 3.12+ with -L flag
python -L -m textkit

# Option B: importlib.util.LazyLoader
import importlib.util
import sys

def lazy_import(name: str):
    """Defer module loading until first attribute access."""
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module

# Usage
typer = lazy_import("typer")
rich = lazy_import("rich")
```

**Option C: Manual Deferred Import (Most Compatible)**
```python
# bin/tt.py - Fast path
def main():
    # Only import heavy modules when needed
    if "--help" in sys.argv:
        import typer  # Import only for help
        ...
    else:
        # Minimal imports for transform
        from components.text_core import TextTransformationEngine
        ...
```

**Expected Impact**: 50-80% startup time reduction

---

#### 3.2 StringZilla Integration (SIMD Optimization)

**Evidence**: [StringZilla](https://github.com/ashvardanian/StringZilla)
- Up to 10x faster string operations
- SIMD-accelerated (AVX2, AVX-512, NEON)
- Drop-in replacement for many str methods

**Implementation**:
```python
# Replace hot path string operations
from stringzilla import Str

def transform_text(text: str) -> str:
    sz_text = Str(text)
    # SIMD-accelerated operations
    result = sz_text.lower()  # 10x faster
    return str(result)
```

**Benchmark Target**:
| Operation | Python str | StringZilla | Speedup |
|-----------|------------|-------------|---------|
| lower() | 100ms | 10ms | 10x |
| find() | 50ms | 5ms | 10x |
| replace() | 200ms | 20ms | 10x |

**Note**: Already documented in `stringzilla_integration` memory.

---

#### 3.3 Regex Compilation Cache

**Evidence**: profiling shows 25s (12%) in regex compilation

**Implementation**:
```python
import functools
import re

@functools.lru_cache(maxsize=128)
def get_compiled_pattern(pattern: str, flags: int = 0) -> re.Pattern:
    """Cache compiled regex patterns."""
    return re.compile(pattern, flags)

# Or use regex module with built-in caching
import regex  # pip install regex
# regex module has superior caching and Unicode support
```

**Expected Impact**: Near-zero regex compilation on repeated operations

---

#### 3.4 Pre-compiled Binary Distribution

**Evidence**: 
- Rust CLI tools (ripgrep, fd) - instant startup
- Go CLI tools (gh, docker) - instant startup

**Options**:

| Tool | Pros | Cons |
|------|------|------|
| PyInstaller | Easy, well-documented | Large binary (~50MB) |
| Nuitka | Smaller, faster | Complex build |
| cx_Freeze | Cross-platform | Less maintained |
| PyOxidizer | Modern, Rust-based | Steep learning curve |

**Implementation (PyInstaller)**:
```bash
# Build standalone executable
pyinstaller --onefile --name tt bin/tt.py

# Result: dist/tt.exe (~50MB) - instant startup
```

**Implementation (Nuitka)**:
```bash
# More optimized build
nuitka --standalone --onefile bin/tt.py

# Result: tt.exe (~20MB) - near-native speed
```

---

#### 3.5 Startup Time Profiling Tools

**Evidence**: Standard Python profiling

```bash
# Measure import time
python -X importtime -c "import textkit" 2>&1 | head -20

# Profile startup
python -m cProfile -s cumtime bin/tt.py --help
```

**Current Estimated Breakdown** (needs measurement):
| Component | Est. Time | % |
|-----------|-----------|---|
| Python interpreter | 50ms | 10% |
| typer import | 200ms | 40% |
| rich import | 150ms | 30% |
| components import | 100ms | 20% |

---

### Performance Recommendation Matrix

| Solution | Effort | Impact | Risk |
|----------|--------|--------|------|
| Lazy imports | Low | High | Low |
| Regex cache | Low | Medium | Low |
| StringZilla | Medium | High | Medium |
| Binary dist | High | Very High | Medium |

**Priority Order**:
1. Lazy imports (immediate win, low risk)
2. Regex cache (quick fix)
3. Binary distribution (for end users)
4. StringZilla (for heavy text processing)

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 days)
- [ ] Add shell alias documentation
- [ ] Implement `-q/--quiet` flag
- [ ] Add TTY detection for output
- [ ] Add regex compilation cache

### Phase 2: Core Improvements (1 week)
- [ ] Implement lazy imports
- [ ] Add verbosity levels
- [ ] Update clig.dev compliance

### Phase 3: Distribution (2 weeks)
- [ ] UV tool packaging
- [ ] PyInstaller build pipeline
- [ ] Performance benchmarks

### Phase 4: Advanced (Future)
- [ ] StringZilla integration
- [ ] Nuitka optimization
- [ ] Async processing for large files

---

## References

### Standards & Guidelines
- [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)
- [GNU Coding Standards - CLI](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html)
- [clig.dev - CLI Guidelines](https://clig.dev/)
- [The Art of Unix Programming - Rule of Silence](https://www.linuxtopia.org/online_books/programming_books/art_of_unix_programming/ch01s06_10.html)

### Python Performance
- [PEP 690 - Lazy Imports](https://peps.python.org/pep-0690/)
- [PEP 810 - Explicit Lazy Imports](https://peps.python.org/pep-0810/)
- [StringZilla](https://github.com/ashvardanian/StringZilla)

### CLI Design Examples
- Git aliases: `git config --global alias.co checkout`
- Docker aliases: [gist.github.com/jgrodziski/docker-aliases](https://gist.github.com/jgrodziski/docker-aliases)
- kubectl aliases: [kubectl-aliases](https://github.com/ahmetb/kubectl-aliases)

---

## Benchmark Results (2026-01-18)

### Startup Time Breakdown

| Component | Time (ms) | Notes |
|-----------|-----------|-------|
| Python interpreter | 45 | Baseline |
| uv run overhead | 430 | Package resolution |
| tt --version | 507 | Typer import (~77ms) |
| tt transform | 751 | Full processing (~244ms) |

### Import Time Analysis (Top Contributors)

```
import time:  31645 |  click.core
import time:  25895 |  typer.main
import time:  11302 |  click._winconsole
import time:  10505 |  inspect
import time:   9989 |  site
```

### Command Comparison

| Command | Before | After | Improvement |
|---------|--------|-------|-------------|
| `uv run python bin/tt.py` | 47 chars | - | Baseline |
| `uv run tt` | 9 chars | 522ms | **81% fewer chars** |
| Shell alias `tt` | 2 chars | ~80ms* | **96% fewer chars** |

*Estimated without uv overhead

### Recommendations for Further Optimization

1. **Remove uv overhead**: Use shell alias pointing directly to venv Python
2. **Nuitka compilation**: Could reduce to ~100ms startup
3. **Lazy Typer**: Defer Typer import for --version only

---

## Implementation Status

### Phase 1: Quick Wins ✅ Complete
- [x] Shell alias documentation (bin/README.md)
- [x] `-q/--quiet` flag implementation
- [x] TTY detection for output control
- [x] structlog suppression

### Phase 2: Core Improvements ✅ Complete
- [x] Lazy imports (typer, rich, structlog, components)
- [x] Verbosity levels (-v, -vv)
- [x] clig.dev compliance (NO_COLOR, stderr separation)
- [x] Version callback fix

### Phase 3: Distribution ✅ Complete
- [x] UV tool packaging (`uv run tt`)
- [x] Startup time benchmark
- [ ] PyInstaller build (skipped - path issues on Windows)

### Phase 4: Advanced (Future)
- [ ] StringZilla integration
- [ ] Nuitka optimization
- [ ] Async processing for large files

---

## Changelog

### 2026-01-18 - Phase 1-3 Implementation
- Implemented lazy imports reducing startup overhead
- Added `-v/-vv` verbosity levels
- Added NO_COLOR environment variable support
- Configured UV tool packaging (`uv run tt`)
- Documented startup benchmark results

### 2026-01-14 - Initial Proposal
- Documented 3 improvement areas with evidence-based solutions
- Added industry standard references (Git, Docker, Unix)
- Created implementation roadmap
