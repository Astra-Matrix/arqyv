"""ARQYVShare — dead-simple peer-to-peer file sharing.

No accounts. No subscriptions. No cloud middleman for LAN transfers.

  share.server      → HTTP server that serves a file for download
  share.discovery   → zeroconf LAN peer discovery
  share.qr          → QR code generator (pure Python + Pillow)
  share.transfer    → transfer state tracking & progress
  share.manager     → ShareManager: the single public API
"""
