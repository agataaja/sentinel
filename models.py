from dataclasses import dataclass


@dataclass
class TunnelEvent:

    status: str
    public_url: str | None