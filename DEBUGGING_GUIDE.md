# LangGraph Debugging Guide for AI Travel Agent

## Method 1: Using the Debug Script (Recommended for Quick Testing)

### Step 1: Run the debug script
```bash
python debug_langgraph.py
```

This will:
- Show you each node execution step-by-step
- Display errors immediately when they occur
- Print the final state summary
- Show the generated itinerary if successful

---

## Method 2: LangGraph Studio (Visual Debugging)

### Step 1: Install LangGraph CLI
```bash
pip install langgraph-cli
```

### Step 2: Start LangGraph Studio
```bash
langgraph dev
```

This will:
- Open a web interface (usually at http://localhost:8123)
- Show a visual representation of your graph
- Allow you to run the graph step-by-step
- Inspect state at each node
- Set breakpoints

### Step 3: Access LangGraph Studio
- Open your browser to http://localhost:8123
- You'll see your travel_agent graph
- Click "New Thread" to start a debug session
- Input your test data (city, days, interests, budget)
- Step through each node execution

---

## Method 3: Python Debugger (PDB)

### Step 1: Add breakpoints in your code
```python
# Add this line where you want to pause
import pdb; pdb.set_trace()
```

### Step 2: Run your application
```bash
python debug_langgraph.py
```

When it hits the breakpoint:
- `n` = next line
- `s` = step into function
- `c` = continue
- `p variable_name` = print variable
- `q` = quit

---

## Method 4: LangSmith (Cloud Tracing)

### Step 1: Sign up for LangSmith
Visit: https://smith.langchain.com/

### Step 2: Add to .env file
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key_here
LANGCHAIN_PROJECT=ai-travel-agent
```

### Step 3: Run your application
All executions will be logged to LangSmith dashboard with:
- Full execution trace
- Input/output for each node
- Timing information
- Error details

---

## Method 5: Manual Testing with Logging

### Add logging to each node:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def planner_node(state: TravelState):
    logger.info(f"PLANNER INPUT: city={state.city}, days={state.days}")
    # ... rest of code
    logger.info(f"PLANNER OUTPUT: plan_outline={bool(result.get('plan_outline'))}")
    return result
```

---

## Debugging Checklist

### Common Issues to Check:

1. **Environment Variables**
   - [ ] GROQ_API_KEY is set
   - [ ] OPENTRIPMAP_KEY is set
   - [ ] .env file is loaded

2. **State Flow**
   - [ ] Each node returns a dict with expected keys
   - [ ] State fields match TravelState model
   - [ ] No typos in field names (attractions vs attraction)

3. **API Calls**
   - [ ] API keys are valid
   - [ ] Network connectivity
   - [ ] API rate limits not exceeded

4. **Data Validation**
   - [ ] Input data is valid (city name exists, days > 0, etc.)
   - [ ] JSON parsing succeeds in planner
   - [ ] Coordinates are retrieved for city

---

## Quick Test Commands

### Test individual nodes:
```bash
# Test planner only
python -c "from src.agents.planner import planner_node; from model import TravelState; state = TravelState(city='Paris', days=2, interests=['culture'], budget='medium'); print(planner_node(state))"

# Test with full graph
python debug_langgraph.py
```

### Check graph structure:
```bash
python -c "from graph import trip_graph; print(trip_graph.get_graph().draw_ascii())"
```

---

## Recommended Workflow

1. **Start with debug_langgraph.py** to see overall flow
2. **Use LangGraph Studio** for visual debugging
3. **Add LangSmith** for production monitoring
4. **Use PDB** for deep dive into specific node issues

---

## Need Help?

If you see errors:
1. Run `python debug_langgraph.py` first
2. Note which node fails
3. Check that node's input state
4. Verify API keys for that service
5. Test the external API directly (Groq, OpenTripMap, etc.)
