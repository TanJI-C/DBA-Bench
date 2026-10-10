# Online Unsafe Recovery state and validation boundary

TiDB 8.1 Online Unsafe Recovery is a lossy PD-owned recovery operation for
TiKV Stores that are permanently damaged or cannot be recovered. It is not a
normal Store drain and it does not establish a lossless RPO.

The request must include every currently unrecoverable Store in the affected
scope and must not include a Store that is up and connected. Derive the set
from current PD Store state and Region peer evidence. A single Store mentioned
by an error is not necessarily the complete recovery scope, and a healthy
neighbor must remain outside it.

A successful request registers an asynchronous task. It does not mean that
recovery has finished. Observe the product progress endpoint until a terminal
finished state is present; a terminal failed state is failure. During recovery,
the affected Stores enter the product's terminal Store state and must not be
restarted as healthy Stores before the task and Region scheduling have settled.

After terminal recovery, wait for affected Regions to converge, verify the
remaining peers and Store states, run `ADMIN CHECK TABLE` for affected
record/index data, and perform a bounded surviving-endpoint write/read-back
probe. Preserve the pre-outage business boundary and explicitly describe any
unconfirmed write interval. A command exit status, readable data, or one
unchanged aggregate is not enough to prove recovery or zero data loss.

