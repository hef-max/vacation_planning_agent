"""
LangChain Agent untuk Vacation Planning.
Menggunakan LLM Google Gemini via API.
"""
import json
from typing import Optional

# Impor untuk Agent modern LangChain (0.2.x)
from langchain.agents.agent import AgentExecutor
from langchain.agents import create_react_agent
from langchain.tools import Tool, StructuredTool
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pydantic import BaseModel, Field

from app.config import settings
from app.tools.search import search_hotels, search_flights, search_activities, get_destination_info
from app.tools.calendar import get_free_dates, find_best_travel_window
from app.utils.logger import audit, logger

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI


# === Tool Input Schemas ===
class HotelSearchInput(BaseModel):
    destination: str = Field(description="Destination city name")
    checkin: str = Field(description="Check-in date in YYYY-MM-DD format")
    checkout: str = Field(description="Check-out date in YYYY-MM-DD format")
    preferences: Optional[str] = Field(default=None, description="User preferences like 'homestay', 'budget', 'luxury'")
    max_price: Optional[int] = Field(default=None, description="Maximum price per night in IDR")

class FlightSearchInput(BaseModel):
    destination: str = Field(description="Destination city")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    origin: str = Field(default="Jakarta", description="Origin city")

class ActivitySearchInput(BaseModel):
    destination: str = Field(description="Destination city")
    travel_type: Optional[str] = Field(default=None, description="Type of travel: culture, adventure, beach, nature")

class CalendarCheckInput(BaseModel):
    user_id: str = Field(description="User ID to check calendar")
    range_start: str = Field(description="Start date in YYYY-MM-DD format")
    range_end: str = Field(description="End date in YYYY-MM-DD format")


# === Tool Functions with Wrappers ===
def _search_hotels_wrapper(destination: str, checkin: str, checkout: str, preferences: str = None, max_price: int = None) -> str:
    results = search_hotels(destination, checkin, checkout, preferences, max_price)
    return json.dumps(results, indent=2, ensure_ascii=False)

def _search_flights_wrapper(destination: str, departure_date: str, origin: str = "Jakarta") -> str:
    results = search_flights(destination, departure_date, origin)
    return json.dumps(results, indent=2, ensure_ascii=False)

def _search_activities_wrapper(destination: str, travel_type: str = None) -> str:
    results = search_activities(destination, travel_type)
    return json.dumps(results, indent=2, ensure_ascii=False)

def _get_calendar_free_dates(user_id: str, range_start: str, range_end: str) -> str:
    free_dates = get_free_dates(user_id, range_start, range_end)
    window = find_best_travel_window(user_id, range_start, range_end)
    return json.dumps({"free_dates": free_dates, "analysis": window}, indent=2, ensure_ascii=False)

def _get_destination_info_wrapper(destination: str) -> str:
    info = get_destination_info(destination)
    return json.dumps(info, indent=2, ensure_ascii=False)

# === Define Tools ===
tools = [
    StructuredTool.from_function(
        func=_search_hotels_wrapper,
        name="search_hotels",
        description="Search for hotels at a destination. Returns list of available hotels with prices and ratings.",
        args_schema=HotelSearchInput
    ),
    StructuredTool.from_function(
        func=_search_flights_wrapper,
        name="search_flights",
        description="Search for flights to a destination. Returns available flights with prices.",
        args_schema=FlightSearchInput
    ),
    StructuredTool.from_function(
        func=_search_activities_wrapper,
        name="search_activities",
        description="Search for activities and attractions at a destination. Can filter by travel type (culture, adventure, beach, nature).",
        args_schema=ActivitySearchInput
    ),
    StructuredTool.from_function(
        func=_get_calendar_free_dates,
        name="check_calendar",
        description="Check user's calendar for free dates within a range. Returns available dates and suggests best travel window.",
        args_schema=CalendarCheckInput
    ),
    Tool(
        name="get_destination_info",
        func=_get_destination_info_wrapper,
        description="Get general information about a destination including highlights, best time to visit, and budget ranges."
    )
]

# === Agent Prompt Template (ReAct Format) ===
REACT_PROMPT = """You are TravelPlannerAgent, an AI assistant that creates detailed vacation itineraries.

IMPORTANT RULES:
1. Always check the user's calendar first using the 'check_calendar' tool. Adjust dates based on calendar results.
2. Search for hotels and activities that match the user's budget and preferences.
3. Create a daily itinerary with specific activities, times, and costs.
4. The total estimated cost MUST NOT exceed the user's budget.
5. Include at least one accommodation option per night.
6. Be realistic with timing - don't over-schedule daily activities.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: Your Final Answer MUST be a valid JSON object with the following structure (no additional text before or after):
{{
    "trip_name": "Descriptive trip name",
    "destination": "City name",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD", 
    "days": [
        {{
            "date": "YYYY-MM-DD",
            "activities": [
                {{"time": "08:00", "name": "Activity name", "description": "Brief description", "estimated_cost": 50000}}
            ],
            "lodging": {{"name": "Hotel name", "price": 350000}},
            "transport": {{"type": "Grab/taxi", "estimated_cost": 50000}},
            "daily_cost": 450000
        }}
    ],
    "total_estimated_cost": 1800000,
    "recommended_hotels": [{{"id": "htl_001", "name": "Hotel A", "price_per_night": 350000, "rating": 4.5}}],
    "notes": "Additional notes or recommendations"
}}

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


# === Create Agent (Fixed Version) ===
def create_planner_agent(streaming: bool = False):
    """Create and return the planner agent."""
    
    callback_manager = None
    if streaming:
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    genai.configure(api_key=settings.GOOGLE_API_KEY)

    # PERBAIKAN 1: Hapus convert_system_message_to_human untuk menghindari warning
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        callback_manager=callback_manager
    )

    logger.warning(f"LLM agent Google Gemini initialized for planning.")

    # PERBAIKAN 2: Gunakan PromptTemplate sederhana untuk ReAct
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    
    # PERBAIKAN 3: Gunakan create_react_agent dengan prompt yang benar
    agent = create_react_agent(llm, tools, prompt)
    
    # PERBAIKAN 4: AgentExecutor dengan error handling yang lebih baik
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.DEBUG,
        handle_parsing_errors=True,
        max_iterations=20,
        early_stopping_method="generate",  # Tambahan: stop method yang lebih baik
        return_intermediate_steps=True  # Aktifkan kembali untuk debugging
    )
    
    return agent_executor


# === Main Planning Function (Fixed) ===
def generate_itinerary(
    user_id: str,
    destination: str,
    start_date: str,
    end_date: str,
    budget_idr: int,
    travel_type: str = "culture",
    travelers: int = 1,
    preferences: str = ""
) -> dict:
    """
    Generate a complete itinerary using the LangChain agent.
    """
    logger.info(f"Generating itinerary for {user_id}: {destination} ({start_date} to {end_date})")
    
    # Create the agent
    agent = create_planner_agent(streaming=False)
    
    # Construct the query
    query = f"""
    Please create a vacation itinerary with the following details:
    - User ID: {user_id}
    - Destination: {destination}
    - Dates: {start_date} to {end_date}
    - Budget: {budget_idr:,} IDR total
    - Travel type preference: {travel_type}
    - Number of travelers: {travelers}
    - Additional preferences: {preferences if preferences else 'None specified'}
    
    First check the calendar for availability, then search for suitable hotels and activities.
    Create a detailed day-by-day itinerary that fits within the budget.
    """
    
    try:
        # PERBAIKAN 5: Invoke dengan error handling yang lebih baik
        result = agent.invoke({"input": query})
        
        # PERBAIKAN 6: Extract tools dengan pengecekan yang aman
        tools_called = []
        if "intermediate_steps" in result and result["intermediate_steps"]:
            for step in result["intermediate_steps"]:
                try:
                    # step adalah tuple (AgentAction, observation)
                    if isinstance(step, tuple) and len(step) >= 1:
                        agent_action = step[0]
                        if hasattr(agent_action, 'tool'):
                            tools_called.append(agent_action.tool)
                        elif isinstance(agent_action, dict) and 'tool' in agent_action:
                            tools_called.append(agent_action['tool'])
                except (AttributeError, TypeError) as e:
                    logger.debug(f"Could not extract tool name from step: {e}")
                    continue
        
        if not tools_called:
            tools_called = ["agent_executed"]
        
        audit.log_agent_action(
            user_id=user_id,
            agent_action="generate_itinerary",
            tools_called=tools_called,
            input_summary=f"{destination} | {start_date}-{end_date} | {budget_idr} IDR"
        )
        
        # Parse the output
        output = result.get("output", "")
        
        # Try to extract JSON from output
        itinerary = _extract_json_from_output(output)
        
        if itinerary:
            return {
                "success": True,
                "itinerary": itinerary,
                "tools_used": tools_called,
                "raw_output": output
            }
        else:
            logger.warning("Failed to parse JSON from agent output, trying fallback")
            return {
                "success": False,
                "error": "Failed to parse itinerary from agent output.",
                "raw_output": output,
                "tools_used": tools_called
            }
            
    except Exception as e:
        logger.error(f"Agent error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "raw_output": None
        }


def _extract_json_from_output(output: str) -> Optional[dict]:
    """Extract JSON from agent output with improved parsing."""
    import re
    
    # Try to find JSON block with various patterns
    patterns = [
        r'```json\s*(\{[\s\S]*?\})\s*```',  # Markdown JSON block
        r'```\s*(\{[\s\S]*?\})\s*```',      # Generic code block
        r'(\{[\s\S]*?\})'                    # Raw JSON
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.DOTALL)
        for match in matches:
            json_str = match if isinstance(match, str) else match[0] if match else ""
            if json_str:
                try:
                    parsed = json.loads(json_str)
                    # Validate it looks like an itinerary
                    if isinstance(parsed, dict) and "destination" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue
    
    return None


# === Fallback: Rule-based Itinerary Generator ===
def generate_itinerary_fallback(
    user_id: str,
    destination: str,
    start_date: str,
    end_date: str,
    budget_idr: int,
    travel_type: str = "culture",
    travelers: int = 1,
    preferences: str = ""
) -> dict:
    """
    Fallback itinerary generator jika LLM agent gagal.
    Menggunakan rule-based approach.
    """
    from datetime import datetime, timedelta
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    num_days = (end - start).days + 1
    
    # Get data
    hotels = search_hotels(destination, start_date, end_date, preferences, budget_idr // num_days // 2)
    activities = search_activities(destination, travel_type)
    dest_info = get_destination_info(destination)
    
    # Select hotel (cheapest that fits)
    selected_hotel = hotels[0] if hotels else {"name": "Local Guesthouse", "price_per_night": 300000}
    hotel_total = selected_hotel.get("price_per_night", 300000) * (num_days - 1)
    
    # Remaining budget for activities
    activity_budget = budget_idr - hotel_total
    daily_activity_budget = activity_budget // num_days
    
    # Build days
    days = []
    activity_idx = 0
    running_cost = 0
    
    for i in range(num_days):
        current_date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        day_activities = []
        day_cost = 0
        
        # Morning activity
        if activity_idx < len(activities):
            act = activities[activity_idx]
            day_activities.append({
                "time": "09:00",
                "name": act["name"],
                "description": act["description"],
                "estimated_cost": act["price"]
            })
            day_cost += act["price"]
            activity_idx += 1
        
        # Afternoon activity
        if activity_idx < len(activities) and day_cost < daily_activity_budget:
            act = activities[activity_idx]
            day_activities.append({
                "time": "14:00",
                "name": act["name"],
                "description": act["description"],
                "estimated_cost": act["price"]
            })
            day_cost += act["price"]
            activity_idx += 1
        
        # Add lodging (except last day)
        lodging = None
        if i < num_days - 1:
            lodging = {"name": selected_hotel["name"], "price": selected_hotel.get("price_per_night", 300000)}
            day_cost += lodging["price"]
        
        # Transport estimate
        transport = {"type": "Local transport", "estimated_cost": 50000 * travelers}
        day_cost += transport["estimated_cost"]
        
        running_cost += day_cost
        
        days.append({
            "date": current_date,
            "activities": day_activities,
            "lodging": lodging,
            "transport": transport,
            "daily_cost": day_cost
        })
    
    itinerary = {
        "trip_name": f"{travel_type.title()} Trip to {destination}",
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "total_estimated_cost": running_cost,
        "recommended_hotels": hotels[:3],
        "notes": f"Generated using fallback planner. Adjust activities as needed. Budget remaining: {budget_idr - running_cost:,} IDR"
    }
    
    return {
        "success": True,
        "itinerary": itinerary,
        "tools_used": ["fallback_generator"],
        "raw_output": None
    }