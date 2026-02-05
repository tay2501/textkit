# Clipboard Hold (Clipboard Guard) Investigation

**Created**: 2026-02-05
**Status**: Approved - Implementing Approach B
**Platform Target**: Windows 11 (Win32 API)
**Python**: 3.13+ (ctypes, no external dependencies)

---

## Requirements

1. Set clipboard text via CLI option with a duration (seconds) during which the clipboard value is protected from overwrite
2. Cancel with Ctrl+C or timeout to release the guard
3. Fallback: If true locking is impractical, monitor and force-restore on change

---

## Approach A: True Lock via `OpenClipboard()`

**Mechanism**: Call `OpenClipboard()` and hold without calling `CloseClipboard()` for N seconds.

**Win32 API Reference**: [OpenClipboard - Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-openclipboard)

### Pros
- Prevents any other application from modifying the clipboard at the Win32 API level

### Cons
- **Blocks ALL clipboard access** including paste (Ctrl+V fails system-wide)
- Applications may crash, hang, or show error dialogs
- Microsoft documentation states: "An application should call `CloseClipboard` after every successful call to `OpenClipboard`"
- Holding the clipboard open long-term is **undefined behavior**
- Password managers, clipboard utilities, and other system tools fail

### Verdict: **Technically possible but NOT practical**

---

## Approach B: Monitor + Immediate Restore (Recommended)

**Mechanism**: Use `AddClipboardFormatListener` to receive `WM_CLIPBOARDUPDATE` notifications. On external change, immediately restore the target text.

**Win32 API Reference**: [AddClipboardFormatListener - Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-addclipboardformatlistener)

### Architecture

```
Main Thread                    Win32 Message Thread
-----------                    --------------------
1. Set clipboard text    --->  2. Register listener
3. Wait (timer/Ctrl+C)        4. Receive WM_CLIPBOARDUPDATE
                               5. Check: self-update? skip
                               6. Restore target text (~1ms)
7. Timeout/cancel        --->  8. Remove listener & quit
```

### Pros
- Other applications can still **read/paste** from clipboard normally
- No risk of application crashes or system instability
- Event-driven: **zero CPU usage** while waiting (no polling)
- Restore happens in **~1ms** (imperceptible)
- Uses documented, stable Win32 APIs (available since Windows Vista)
- No external dependencies (ctypes only)

### Cons
- Tiny window (~1ms) where clipboard has "wrong" content before restoration
- Must handle self-update loop (our own `SetClipboardData` triggers `WM_CLIPBOARDUPDATE`)

### Self-Update Loop Prevention

```python
# Use a threading flag to distinguish our own updates from external ones
self._restoring = True
try:
    set_clipboard_data(target_text)
finally:
    self._restoring = False

# In WM_CLIPBOARDUPDATE handler:
if self._restoring:
    return  # Skip our own update
```

### Verdict: **Recommended - Fully practical and effective**

---

## Approach C: Polling-Based Restore

**Mechanism**: Poll clipboard every ~100ms. If changed, restore.

### Pros
- Simple implementation
- Cross-platform compatible

### Cons
- 100ms+ delay before detection
- Higher CPU usage due to constant polling
- Less responsive than event-driven approach

### Verdict: **Works but inferior to Approach B**

---

## Comparison Matrix

| Approach | Feasible? | Practical? | Side Effects | CPU Usage | Latency |
|----------|-----------|------------|--------------|-----------|---------|
| A: OpenClipboard Lock | Yes | **No** | Paste blocked, app crashes | None | 0ms |
| **B: Monitor + Restore** | **Yes** | **Yes** | ~1ms gap (negligible) | **~0%** | **~1ms** |
| C: Polling | Yes | Okay | 100ms+ gap | ~1% | 100ms+ |

---

## Implementation Plan

### Component: `ClipboardGuard`

**Location**: `components/io_handler/clipboard_guard.py`

**Dependencies**: `ctypes` (stdlib only, no external packages)

**Win32 APIs Used** (via ctypes):
- `user32.AddClipboardFormatListener` - Register for clipboard change notifications
- `user32.RemoveClipboardFormatListener` - Unregister listener
- `user32.OpenClipboard` / `user32.CloseClipboard` - Clipboard access
- `user32.EmptyClipboard` / `user32.SetClipboardData` - Write clipboard
- `user32.GetClipboardData` - Read clipboard
- `user32.CreateWindowExW` / `user32.RegisterClassExW` - Hidden message window
- `user32.GetMessageW` / `user32.PostQuitMessage` - Win32 message pump
- `kernel32.GlobalAlloc` / `kernel32.GlobalLock` / `kernel32.GlobalUnlock` - Memory management

### CLI Command

```bash
# Basic usage
textkit clip hold "secret text" --duration 30

# With pipe
echo "secret text" | textkit clip hold --duration 30

# Cancel early
# Press Ctrl+C to release the guard
```

### Platform Compatibility

- **Windows**: Full event-driven monitoring via Win32 API
- **Other OS**: Falls back to polling-based approach using pyperclip

---

## References

- [OpenClipboard - Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-openclipboard)
- [AddClipboardFormatListener - Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-addclipboardformatlistener)
- [Clipboard API Overview - Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard)
- [Monitoring Clipboard with Python - abdus.dev](https://abdus.dev/posts/monitor-clipboard/)
- [ClipCop (Clipboard Monitor) - GitHub](https://github.com/blevok/ClipCop)
- [CopyQ (Clipboard Manager) - GitHub](https://github.com/hluk/CopyQ)
