"""
Data models representing cycle phases, daily logs, cycle records, and user profiles.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class PhaseType(str, Enum):
    MENSTRUAL = "menstrual"
    FOLLICULAR = "follicular"
    OVULATION = "ovulation"
    LUTEAL_EARLY = "luteal_early"
    LUTEAL_LATE_PMS = "luteal_late_pms"


@dataclass
class PhaseInfo:
    """Detailed scientific and emotional information about a cycle phase."""
    phase_type: PhaseType
    phase_name: str
    day_in_cycle: int
    cycle_length: int
    days_remaining_in_phase: int
    phase_color: str
    hormone_status: str
    mood_summary: str
    energy_level: str  # e.g., "Low (Rest Needed)", "High / Peak", "Moderate"
    physical_summary: str
    care_tip_for_partner: str
    nutrition_tip: str
    recommended_activities: List[str] = field(default_factory=list)


@dataclass
class DailyLog:
    """Log for a specific day tracking symptoms, mood, and personal notes."""
    log_date: date
    mood_score: int = 3  # 1 (lowest) to 5 (highest)
    energy_score: int = 3  # 1 to 5
    pain_level: int = 0  # 0 to 5
    symptoms: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_date": self.log_date.isoformat(),
            "mood_score": self.mood_score,
            "energy_score": self.energy_score,
            "pain_level": self.pain_level,
            "symptoms": self.symptoms,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyLog":
        raw_date = data.get("log_date")
        parsed_date = date.fromisoformat(raw_date) if isinstance(raw_date, str) else date.today()
        return cls(
            log_date=parsed_date,
            mood_score=int(data.get("mood_score", 3)),
            energy_score=int(data.get("energy_score", 3)),
            pain_level=int(data.get("pain_level", 0)),
            symptoms=list(data.get("symptoms", [])),
            notes=str(data.get("notes", "")),
        )


@dataclass
class CycleRecord:
    """Historical record of an individual cycle."""
    start_date: date
    period_duration: int
    cycle_length: int
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_date": self.start_date.isoformat(),
            "period_duration": self.period_duration,
            "cycle_length": self.cycle_length,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CycleRecord":
        raw_date = data.get("start_date")
        parsed_date = date.fromisoformat(raw_date) if isinstance(raw_date, str) else date.today()
        return cls(
            start_date=parsed_date,
            period_duration=int(data.get("period_duration", 5)),
            cycle_length=int(data.get("cycle_length", 28)),
            notes=str(data.get("notes", "")),
        )


@dataclass
class Profile:
    """User profile containing cycle settings, history, and daily logs."""
    name: str
    last_period_start_date: date
    period_duration: int = 5
    cycle_length: int = 28
    history: List[CycleRecord] = field(default_factory=list)
    daily_logs: Dict[str, DailyLog] = field(default_factory=dict)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "last_period_start_date": self.last_period_start_date.isoformat(),
            "period_duration": self.period_duration,
            "cycle_length": self.cycle_length,
            "history": [record.to_dict() for record in self.history],
            "daily_logs": {k: v.to_dict() for k, v in self.daily_logs.items()},
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profile":
        raw_date = data.get("last_period_start_date")
        if isinstance(raw_date, str):
            parsed_date = date.fromisoformat(raw_date)
        elif isinstance(raw_date, date):
            parsed_date = raw_date
        else:
            parsed_date = date.today()

        history_records = [
            CycleRecord.from_dict(item) for item in data.get("history", []) if isinstance(item, dict)
        ]

        raw_logs = data.get("daily_logs", {})
        daily_logs = {}
        if isinstance(raw_logs, dict):
            for k, v in raw_logs.items():
                if isinstance(v, dict):
                    daily_logs[k] = DailyLog.from_dict(v)

        return cls(
            name=str(data.get("name", "Unnamed")),
            last_period_start_date=parsed_date,
            period_duration=max(1, int(data.get("period_duration", 5))),
            cycle_length=max(15, int(data.get("cycle_length", 28))),
            history=history_records,
            daily_logs=daily_logs,
            notes=str(data.get("notes", "")),
            created_at=str(data.get("created_at", datetime.now().isoformat())),
        )
