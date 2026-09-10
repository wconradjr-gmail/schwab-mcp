"""Price history tools for retrieving OHLCV candle data from Schwab."""

from collections.abc import Callable
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer

from schwab_mcp.context import SchwabContext
from schwab_mcp.tools._registration import register_tool
from schwab_mcp.tools.utils import JSONType, call, parse_datetime


async def get_advanced_price_history(
    ctx: SchwabContext,
    symbol: Annotated[str, "Symbol of the security"],
    start_datetime: Annotated[str, "Start date for history (ISO format, e.g., '2023-01-01T09:30:00')"],
    frequency_type: Annotated[
        str, "Frequency type: MINUTE or DAILY",
    ],
    frequency: Annotated[
        int | str | None,
        "Number of frequencyType per candle (e.g., 1, 5, 10 for MINUTE, 1 for DAILY). Strings are coerced to int.",
    ],
    end_datetime: Annotated[str | None, "End date for history (ISO format, e.g., '2023-01-31T16:00:00')"] = None,
    extended_hours: Annotated[bool | None, "Include extended hours data"] = None,
    previous_close: Annotated[bool | None, "Include previous close data"] = None,
) -> JSONType:
    """Get price history with advanced period/frequency options. Specify period/frequency OR start/end datetimes.

    frequency 1/5/10/15/30;
    Frequency type options (by period_type):
      MINUTE, DAILY
    Dates must be in ISO format.
    """
    client = ctx.price_history

    start_dt = parse_datetime(start_datetime)
    end_dt = parse_datetime(end_datetime)

    # Automatically determine period_type based on frequency_type if not explicitly provided
    ft = frequency_type.upper()
    if ft == "MINUTE":
        period_type = "DAY"
    else:
        period_type = "YEAR"

    # Normalize enum-like strings
    period_type_enum = client.PriceHistory.PeriodType[period_type.upper()] if period_type else None
    frequency_type_enum = client.PriceHistory.FrequencyType[frequency_type.upper()] if frequency_type else None

    # Coerce frequency to int if provided as string
    if isinstance(frequency, str):
        frequency = int(frequency)

    return await call(
        client.get_price_history,
        symbol,
        period_type=period_type_enum,
        period=None,
        frequency_type=frequency_type_enum,
        frequency=frequency,
        start_datetime=start_dt,
        end_datetime=end_dt,
        need_extended_hours_data=extended_hours,
        need_previous_close=previous_close,
    )


_READ_ONLY_TOOLS = (get_advanced_price_history,)


def register(
    server: MCPServer,
    *,
    allow_write: bool,
    result_transform: Callable[[Any], Any] | None = None,
) -> None:
    """Register price history tools with the MCP server."""
    _ = allow_write
    for func in _READ_ONLY_TOOLS:
        register_tool(server, func, result_transform=result_transform)
