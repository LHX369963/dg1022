class Dg1022Error(Exception):
    """Base error shown to CLI users."""


class TransportError(Dg1022Error):
    """USBTMC discovery or I/O failure."""


class ProtocolError(Dg1022Error):
    """Invalid command or instrument response."""
