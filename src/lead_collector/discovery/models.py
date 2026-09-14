from pydantic import BaseModel, ConfigDict, HttpUrl


class DiscoveryResult(BaseModel):
    """A single result returned by a lead discovery provider."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str
    url: HttpUrl
    snippet: str | None = None
    source: str
    position: int | None = None