# Placement-policy review scope, repair, and acceptance

## Establish the live scope

A routine health review may coexist with historical closed records and approved exceptions.
Join the live review row to the service catalog, table catalog, and partition catalog before
touching an object. A healthy custom-policy neighbor is evidence that custom policies are not
universally wrong. An approved exception with an unsatisfied placement state remains an
exception until its owner changes the decision; it is not automatically the current review.

Use the public raw cluster observations to distinguish a single-Store capacity mismatch from
a service outage: inspect service state, PD Store state and labels, Region peers, current
operators, schedulers, and the relevant PD configuration. These observations are evidence,
not a precomputed diagnosis.

## Smallest repair and final acceptance

For a review whose target object should inherit the default, reset only the target object
bindings to `DEFAULT`. If both a table and a partition have explicit bindings, reset both;
either order is valid. Do not alter a shared policy definition, assign a healthy neighbor's
policy, modify database or global placement, or change PD scheduling merely to make an
unsatisfiable request look satisfied. Close only the exact live review row after the placement
has converged.

Final acceptance is a closed review, no target custom binding or pending target placement,
unchanged protected neighbors and policy definitions, and unchanged business truth. A control
plane command returning success, a report saying "fixed", or a disappearance of one table row
is not sufficient evidence for acceptance.
