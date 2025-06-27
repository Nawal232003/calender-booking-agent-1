# =========================
# 🚀 backend/main.py (enhanced with clean formatting and better messaging)
# =========================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dateutil import parser as dt_parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    available_slots: List[str] = []
    booking_confirmed: bool = False

sessions = {}

WEEKDAYS = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU
}

class CalendarBookingAgent:
    def __init__(self):
        self.mock_calendar = {
            "busy_slots": ["2025-06-28T10:00:00", "2025-06-28T14:00:00"]
        }

    def parse_date(self, message: str):
        now = datetime.now()
        message_lower = message.lower()

        for name, weekday in WEEKDAYS.items():
            if name in message_lower:
                return now + relativedelta(weekday=weekday(+1))

        if "tomorrow" in message_lower:
            return now + timedelta(days=1)

        try:
            return dt_parser.parse(message, fuzzy=True)
        except:
            return now + timedelta(days=1)

    def get_available_slots(self, date: datetime) -> List[str]:
        slots = []
        for hour in range(9, 18):
            slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_str = slot_time.strftime("%Y-%m-%dT%H:%M:%S")
            if slot_str not in self.mock_calendar["busy_slots"]:
                slots.append(slot_time.strftime("%B %d, %Y at %I:%M %p"))
        return slots[:5]

    def book_appointment(self, time_slot):
        print(f"📌 Booking confirmed: {time_slot}")
        return True

    def process_message(self, message: str, session_id: str) -> ChatResponse:
        if session_id not in sessions:
            sessions[session_id] = {"state": "greeting", "proposed_slots": [], "selected_slot": None}
        session = sessions[session_id]
        message_lower = message.lower()

        if session["state"] == "greeting":
            if any(word in message_lower for word in ["book", "meeting", "schedule"]):
                date = self.parse_date(message)
                slots = self.get_available_slots(date)
                session["proposed_slots"] = slots
                session["state"] = "slot_selection"
                pretty_slots = "\n".join([f"**{i+1}.** {s}" for i, s in enumerate(slots)])
                return ChatResponse(
                    response=f"""
📅 **Here are your available time slots:**

{pretty_slots}

👉 _Please reply with a slot number (e.g., 1, 2, 3)..._""",
                    available_slots=slots)
            return ChatResponse(response="👋 Hello! I'm your scheduling assistant. Just tell me when you'd like to book a meeting!")

        elif session["state"] == "slot_selection":
            try:
                idx = int(re.search(r"\d", message).group()) - 1
                slot = session["proposed_slots"][idx]
                session["selected_slot"] = slot
                session["state"] = "confirmation"
                return ChatResponse(response=f"✅ Great! I will book your appointment for: **{slot}**\n\nPlease confirm by replying 'yes'.")
            except:
                return ChatResponse(response="⚠️ Please reply with a valid slot number (1–5).")

        elif session["state"] == "confirmation":
            if any(word in message_lower for word in ["yes", "confirm", "okay", "book"]):
                booked = self.book_appointment(session["selected_slot"])
                session["state"] = "done"
                return ChatResponse(response="🎉 **Appointment Confirmed!** I’ve scheduled your meeting. Let me know if you want to book another!", booking_confirmed=True)
            else:
                session["state"] = "slot_selection"
                return ChatResponse(response="👌 No worries. Please pick another slot number.")

        return ChatResponse(response="Let's start over. Just tell me when you'd like to book a meeting.")

agent = CalendarBookingAgent()

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    return agent.process_message(message.message, message.session_id)

@app.get("/health")
async def health():
    return {"status": "healthy"}

