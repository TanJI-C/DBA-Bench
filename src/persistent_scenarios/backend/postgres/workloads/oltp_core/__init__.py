"""Shared OLTP substrate for the pg5 business-priority and online-change instances.

Owns the commerce schema contract, the external trusted business ledger, the
bounded application-side connection pool with retry-merging logical
transactions, traffic tiers and the public control-table readers. This module
is instance-owned; the persistent-scenario core package does not import it.
"""
