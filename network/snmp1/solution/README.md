# snmp1 — intended solution

The host runs an SNMPv2c agent on UDP 161 with the default `public` community
(world-readable). The leak is two-fold: the agent answers the open community,
and its private enterprise tree carries the flag.

## Steps

1. **Enumerate the tree** with a walk:
   ```
   snmpwalk -v2c -c public snmp1.chal.deti 1.3.6.1
   ```
   This returns the MIB-II system group (`sysDescr`, `sysObjectID`, `sysUpTime`,
   `sysContact`, `sysName`, `sysLocation`, `sysServices`) and the interface
   table (`ifNumber`, `ifIndex`/`ifDescr`/`ifSpeed`/`ifAdminStatus`/
   `ifOperStatus`), then the private tree `1.3.6.1.4.1.99999.1.1.*`.

2. **Read the flag.** The first private node, `1.3.6.1.4.1.99999.1.1.0`, is the
   stdout of a status script the agent runs on demand — it carries the flag:
   ```
   snmpget -v2c -c public snmp1.chal.deti 1.3.6.1.4.1.99999.1.1.0
   ```

## Reference solve

`solve.py` speaks raw SNMPv2c over UDP (a GETNEXT walk from `sysDescr` plus a
direct GET) using the shared codec in `app/snmpcodec.py` — no external
dependencies. It prints the flag to stdout.

```
python solution/solve.py                     # 127.0.0.1:8024
python solution/solve.py snmp1.chal.deti:8024
```
