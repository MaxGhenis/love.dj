"""Prevent accidental network use, including during test collection."""

from unittest.mock import patch


def pytest_sessionstart(session):
    session.network_guard = patch(
        "socket.socket.connect",
        side_effect=AssertionError("Tests must not access the network"),
    )
    session.network_guard.start()


def pytest_sessionfinish(session, exitstatus):
    session.network_guard.stop()
