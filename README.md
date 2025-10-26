# Agentic Travel Assistant (AI Travel Agent)

Plan smarter trips with an agentic workflow that combines LLM planning, real-time attractions, weather, routing, and a polished PDF itinerary — all in a single Streamlit app.

## Summary
- Enter your destination, trip length, interests, and budget to get a curated, day-by-day plan.
- The app fetches nearby attractions, forecasts, and computes an efficient route, then summarizes everything into a clean, downloadable PDF.

---

## Features
- Interactive Streamlit UI with tabs for Plan, Map, Weather, and Attractions
- LangGraph-powered pipeline for reliable step-by-step orchestration
- LLM (Groq) for converting plans into human-friendly itineraries
- Attractions from OpenTripMap with intelligent fallbacks (OSM/Overpass)
- Weather from Open-Meteo (daily: code, temp max/min)
- Route ordering from OSRM (public demo server) for stop sequencing
- Polished PDF export with headings, bullet lists, and pagination
- Lightweight caching to speed up repeated runs

---

## Architecture & Workflow
This project uses LangGraph to orchestrate a linear pipeline that turns your inputs into a complete travel plan.

```mermaid
flowchart LR
    A[START] --> B[planner]
    B --> C[attraction]
    C --> D[weather]
    D --> E[route]
    E --> F[summarizer]
    F --> G[reporter]
    G --> H[END]
```

- planner: build a coarse day-by-day outline based on city, days, interests, budget
- attraction: fetch points of interest near the city (with coordinate and provider fallbacks)
- weather: fetch daily forecasts from Open-Meteo
- route: compute a reasonable visiting order using OSRM table distances
- summarizer: create readable itinerary text (Groq LLM)
- reporter: generate a paginated, well-formatted PDF itinerary

Core types live in `model.py` (notably `TravelState`), and the compiled graph is exported as `trip_graph` from `graph.py`.

---

## Data sources
- Groq LLM via `langchain_groq` (default model: `llama-3-8b-8192`)
- OpenTripMap POIs with progressive broadening and Overpass fallback
- OpenStreetMap/Nominatim for city geocoding (first choice)
- Open-Meteo for weather (free, daily)
- OSRM public demo for route distance matrix and naive ordering

---

## Requirements
- Python 3.10+
- See `requirements.txt` for libraries:
  - streamlit, langgraph, langchain, langchain_groq, reportlab, folium, requests, requests-cache, pydantic, etc.

---

## Installation (local)
1. Clone the repository.
2. Create and activate a virtual environment (recommended).
3. Install dependencies:

```powershell
# Optional (create venv)
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install
pip install -r requirements.txt
```

4. Set environment variables (PowerShell):

```powershell
# Required for LLM
$env:GROQ_API_KEY = "<your_groq_api_key>"

# Optional: improves POI coverage (fallbacks still work without this)
$env:OPENTRIPMAP_KEY = "<your_opentripmap_key>"
```

---

## Quickstart
Run the Streamlit app:

```powershell
streamlit run app.py
```

In the UI, provide:
- Destination city (e.g., "Jaipur" or "Jaipur, India")
- Number of days
- Interests (comma-separated, e.g., culture, food)
- Budget (low/medium/high)

You’ll receive:
- A formatted itinerary (and a PDF download link)
- A map with route order
- A daily weather preview and chart
- A table of nearby attractions

---

## Usage details
- Plan tab: Shows the LLM-generated itinerary text and the PDF download link.
- Map tab: Ordered stops based on OSRM’s distance matrix (naive greedy ordering).
- Weather tab: Daily cards (emoji + temps), a temperature line chart, and a full table.
- Attractions tab: Top POIs found near your destination.

The app installs an HTTP cache (24h) automatically to speed up repeated runs for the same city.

---

## PDF export
The reporter formats PDFs using ReportLab Platypus:
- Wraps text properly with margins and pagination
- Highlights day headings
- Renders bullet lists (supports -, •, *)
- Produces a clean, printable document

---

## Configuration
Environment variables:
- `GROQ_API_KEY` (required): API key for Groq LLM
- `OPENTRIPMAP_KEY` (optional): API key for OpenTripMap; improves POI availability

Change defaults:
- LLM model/temperature in `src/utils/groq_client.py`
- Attraction radius/kinds and fallbacks in `src/utils/opentripmap.py`
- Route computation in `src/utils/osrm_client.py`

---

## Project structure
```
app.py                  # Streamlit UI; invokes the LangGraph pipeline and renders tabs
graph.py                # Builds and compiles the LangGraph state graph
model.py                # Pydantic models; shared TravelState
src/
  agents/
    planner.py          # Draft a plan outline
    attraction.py       # Fetch POIs (OpenTripMap + fallbacks)
    weather.py          # Weather via Open-Meteo
    route.py            # Route ordering via OSRM
    summarizer.py       # LLM: plan -> itinerary text
    reporter.py         # PDF generator (ReportLab Platypus)
  utils/
    groq_client.py      # Groq client with simple TTL cache
    opentripmap.py      # City → coords; POIs with progressive fallback
    open_meteo.py       # Weather helper
    osrm_client.py      # OSRM table-based ordering
    cache.py            # Optional HTTP caching via requests-cache
requirements.txt
setup.py
```

---

## Troubleshooting
- “No attractions found”:
  - Try setting `OPENTRIPMAP_KEY`.
  - Check network connectivity; Overpass API can rate-limit or be slow.
  - The app progressively broadens queries and falls back to OSM when needed.
- Route tab is empty:
  - Requires attractions to be available first.
- LLM issues (timeouts/empty output):
  - Verify `GROQ_API_KEY` and that your account has access to the selected model.
- Import errors (langgraph, streamlit, etc.):
  - Ensure you’re in the right virtual environment and ran `pip install -r requirements.txt`.

---

## Notes & Limitations
- OSRM public server is best-effort; for production, host your own OSRM or use a paid routing API.
- Overpass API has community rate limits; handle heavy usage carefully.
- City names are geocoded via Nominatim first; ambiguous names may resolve unexpectedly.
- The greedy route ordering is a heuristic; it’s fast but not guaranteed optimal.

---

## Acknowledgements
- [Groq](https://groq.com/) for fast LLM inference
- [OpenTripMap](https://opentripmap.io/) for places of interest
- [OpenStreetMap](https://www.openstreetmap.org/) & Overpass API for geodata
- [Open‑Meteo](https://open-meteo.com/) for weather
- [OSRM](http://project-osrm.org/) for routing
- [Streamlit](https://streamlit.io/) for the app framework
- [LangGraph](https://www.langchain.com/langgraph) for agentic orchestration
