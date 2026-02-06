"""
Application bootstrap and composition root.

Responsible for initializing and wiring together
all core components such as:
- configuration
- database
- repositories
- services
- Telegram handlers

This module defines the setup_bot() function,
which returns fully configured bot and dispatcher instances.
"""
