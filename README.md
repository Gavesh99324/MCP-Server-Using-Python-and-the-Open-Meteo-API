## Weather MCP Server

Lightweight MCP server that wraps the Open-Meteo API so MCP clients can fetch weather data and forecasts.

### Setup

1. Ensure `uv` is installed (WinGet: `winget install --id=astral-sh.uv -e`).
2. From the project root:
   - `uv venv`
   - `.venv\\Scripts\\activate`
   - `uv sync` (installs dependencies from `uv.lock`).

### Running the server

- Start the MCP server (stdio transport for MCP clients like Claude Desktop):
  - `uv run mcp dev server.py`
  - Or `uv run mcp dev main.py` (main simply proxies to `server.py`).

### Available tools

- `get_current_weather(latitude, longitude)` – returns current conditions.
- `get_forecast(latitude, longitude, hours=24)` – hourly forecast up to 168 hours, trimmed to the requested window.
- `get_location(query, count=5)` – geocoding helper to resolve place names to coordinates.

### Notes

- Open-Meteo does not require an API key; requests include a small user agent for identification.
- All tools return raw JSON payloads so the client/LLM can format responses as needed.
