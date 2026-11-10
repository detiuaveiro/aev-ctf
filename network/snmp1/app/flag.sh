#!/bin/sh
# labstatus -- the status hook the SNMP agent exposes at the private OID
# 1.3.6.1.4.1.99999.1.1.0. The agent runs this script and returns its stdout
# to whoever GETs/GETNEXTs that OID.
#
# In the lab the LIVE flag is /flag/flag (a read-only bind mount of the host
# flag file, atomically rewritten on rotation) -- read per invocation, so a
# rotation is visible without a restart. The env FLAG (podman secret) is the
# fallback for local/docker-compose runs where no mount exists. If neither is
# available we print a fallback so the agent never hands back an empty node.
if [ -r /flag/flag ]; then
    cat /flag/flag
    exit 0
fi
echo "${FLAG:-flag{snmp1_unset}}"
