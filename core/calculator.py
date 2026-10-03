"""
Scientific cycle calculator and mood insight generator.
Calculates phases, ovulation, fertile windows, countdowns, and wellness tips.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Any
from .models import PhaseInfo, PhaseType


class CycleCalculator:
    """Encapsulates all biological cycle mathematics and mood insight algorithms."""

    # Curated palette for phases (hex format, compatible with GTK/Cairo and Tkinter)
    PHASE_COLORS = {
        PhaseType.MENSTRUAL: "#E05375",      # Warm Rose / Crimson
        PhaseType.FOLLICULAR: "#4E9FDF",     # Vibrant Sky Blue
        PhaseType.OVULATION: "#38B278",      # Fresh Emerald Green
        PhaseType.LUTEAL_EARLY: "#E5A93C",   # Golden Amber
        PhaseType.LUTEAL_LATE_PMS: "#8E54E9" # Royal Amethyst Purple
    }

    @staticmethod
    def get_cycle_day(last_period_start: date, cycle_length: int, target_date: Optional[date] = None) -> int:
        """Returns the 1-based day of the cycle for the target date."""
        if target_date is None:
            target_date = date.today()
        
        days_diff = (target_date - last_period_start).days
        if days_diff < 0:
            # Date in past relative to record, calculate modularly or treat as day 1
            return 1
        return (days_diff % max(1, cycle_length)) + 1

    @staticmethod
    def get_current_cycle_start(last_period_start: date, cycle_length: int, target_date: Optional[date] = None) -> date:
        """Returns the start date of the current active cycle."""
        if target_date is None:
            target_date = date.today()
        
        days_diff = (target_date - last_period_start).days
        if days_diff < 0:
            return last_period_start
        
        cycle_count = days_diff // max(1, cycle_length)
        return last_period_start + timedelta(days=cycle_count * cycle_length)

    @classmethod
    def calculate_phase(
        cls,
        last_period_start: date,
        period_duration: int,
        cycle_length: int,
        target_date: Optional[date] = None
    ) -> PhaseInfo:
        """Determines the current phase and generates detailed psychological and physical insights."""
        if target_date is None:
            target_date = date.today()

        cycle_length = max(15, cycle_length)
        period_duration = min(cycle_length - 1, max(1, period_duration))
        day = cls.get_cycle_day(last_period_start, cycle_length, target_date)

        # Boundary calculations
        # Ovulation typically occurs ~14 days before the next period
        ovulation_day = max(period_duration + 2, cycle_length - 14)
        fertile_start = max(period_duration + 1, ovulation_day - 4)
        fertile_end = ovulation_day + 1
        early_luteal_end = cycle_length - 5

        if day <= period_duration:
            phase_type = PhaseType.MENSTRUAL
            phase_name = "Menstrual Phase (Period)"
            remaining = (period_duration - day) + 1
            hormone_status = "Estrogen & Progesterone are at their lowest levels."
            mood_summary = "Introspective, low social energy, seeking comfort, potentially sensitive or fatigued."
            energy_level = "Low (Rest & Rejuvenation)"
            physical_summary = "Uterine shedding, cramping, lower back ache, fatigue."
            partner_tip = "Bring warmth (heating pad, hot tea), handle chores without asking, offer gentle companionship."
            nutrition_tip = "Iron-rich foods (spinach, lentils, dark chocolate), warm broths, ginger, magnesium."
            activities = ["Light walking", "Gentle stretching", "Cozy movie night", "Restful naps"]

        elif day < fertile_start:
            phase_type = PhaseType.FOLLICULAR
            phase_name = "Follicular Phase"
            remaining = (fertile_start - day)
            hormone_status = "Estrogen is steadily rising as follicles develop."
            mood_summary = "Optimistic, creative, motivated, sharp focus, eager to try new activities."
            energy_level = "High & Rising"
            physical_summary = "Skin clearing, metabolism boosting, increased stamina and endurance."
            partner_tip = "Plan exciting outings, try a new restaurant or hobby together, engage in stimulating conversations."
            nutrition_tip = "Fermented foods, sprouted grains, lean proteins, colorful fresh salads."
            activities = ["Cardio or HIIT workouts", "Brainstorming new projects", "Social gatherings", "Adventure outings"]

        elif fertile_start <= day <= fertile_end:
            phase_type = PhaseType.OVULATION
            phase_name = "Ovulation Window (Peak Fertility)"
            remaining = (fertile_end - day) + 1
            hormone_status = "Luteinizing Hormone (LH) and Estrogen reach peak levels; slight testosterone surge."
            mood_summary = "Magnetic, highly confident, communicative, affectionate, radiant mood."
            energy_level = "Peak Energy & Stamina"
            physical_summary = "Peak skin glow, heightened sensory awareness, possible mild unilateral pelvic twinge (mittelschmerz)."
            partner_tip = "Offer sincere compliments, plan a romantic date night, be attentive and receptive to intimacy."
            nutrition_tip = "Fiber-rich vegetables, antioxidant berries, healthy fats (avocado, nuts, seeds)."
            activities = ["Strength training", "Important presentations/meetings", "Romantic dates", "Social networking"]

        elif fertile_end < day <= early_luteal_end:
            phase_type = PhaseType.LUTEAL_EARLY
            phase_name = "Early Luteal Phase"
            remaining = (early_luteal_end - day) + 1
            hormone_status = "Progesterone surges to support potential nesting; estrogen dips slightly then stabilizes."
            mood_summary = "Grounded, detail-oriented, calm, nesting instinct, focused on completing tasks."
            energy_level = "Moderate & Steady"
            physical_summary = "Body temperature slightly elevated, metabolism speeding up, appetite increasing."
            partner_tip = "Support her productive flow, share home organization or cooking, provide a calm environment."
            nutrition_tip = "Complex carbohydrates (sweet potatoes, oats, brown rice), vitamin B6, roasted vegetables."
            activities = ["Pilates or yoga", "Home organizing", "Deep focused work", "Cooking nutritious meals"]

        else:
            phase_type = PhaseType.LUTEAL_LATE_PMS
            phase_name = "Late Luteal Phase (PMS)"
            remaining = (cycle_length - day) + 1
            hormone_status = "Progesterone and Estrogen drop sharply if no pregnancy occurred."
            mood_summary = "Emotionally sensitive, prone to mood swings, anxiety or irritability; low tolerance for stress."
            energy_level = "Declining (Self-Care Needed)"
            physical_summary = "Bloating, breast tenderness, carbohydrate/sugar cravings, potential headaches."
            partner_tip = "Practice extra patience, avoid starting intense debates, surprise her with favorite snacks or a gentle massage."
            nutrition_tip = "Dark chocolate (70%+), chamomile tea, foods rich in calcium and omega-3s, low sodium to prevent bloating."
            activities = ["Restorative yoga", "Warm Epsom salt bath", "Journaling", "Quiet personal time"]

        return PhaseInfo(
            phase_type=phase_type,
            phase_name=phase_name,
            day_in_cycle=day,
            cycle_length=cycle_length,
            days_remaining_in_phase=remaining,
            phase_color=cls.PHASE_COLORS[phase_type],
            hormone_status=hormone_status,
            mood_summary=mood_summary,
            energy_level=energy_level,
            physical_summary=physical_summary,
            care_tip_for_partner=partner_tip,
            nutrition_tip=nutrition_tip,
            recommended_activities=activities
        )

    @classmethod
    def get_cycle_milestones(
        cls,
        last_period_start: date,
        period_duration: int,
        cycle_length: int,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calculates key dates for the current cycle: start, ovulation, next period, countdowns."""
        if target_date is None:
            target_date = date.today()

        current_start = cls.get_current_cycle_start(last_period_start, cycle_length, target_date)
        next_period_date = current_start + timedelta(days=cycle_length)
        
        ovulation_day_index = max(period_duration + 2, cycle_length - 14)
        ovulation_date = current_start + timedelta(days=ovulation_day_index - 1)
        fertile_start_date = current_start + timedelta(days=max(period_duration, ovulation_day_index - 5))
        fertile_end_date = ovulation_date + timedelta(days=1)

        days_until_period = (next_period_date - target_date).days
        days_until_ovulation = (ovulation_date - target_date).days

        return {
            "current_cycle_start": current_start,
            "next_period_date": next_period_date,
            "days_until_next_period": days_until_period,
            "ovulation_date": ovulation_date,
            "days_until_ovulation": days_until_ovulation,
            "fertile_window_start": fertile_start_date,
            "fertile_window_end": fertile_end_date,
            "is_in_fertile_window": fertile_start_date <= target_date <= fertile_end_date,
            "cycle_day": cls.get_cycle_day(last_period_start, cycle_length, target_date),
            "cycle_length": cycle_length,
            "period_duration": period_duration,
        }

    @classmethod
    def get_future_projections(
        cls,
        last_period_start: date,
        period_duration: int,
        cycle_length: int,
        months_ahead: int = 6
    ) -> List[Dict[str, Any]]:
        """Projects upcoming cycle start dates and ovulation windows for the next N months."""
        projections = []
        current_start = cls.get_current_cycle_start(last_period_start, cycle_length)
        ovulation_offset = max(period_duration + 2, cycle_length - 14) - 1

        for i in range(months_ahead):
            cycle_start = current_start + timedelta(days=i * cycle_length)
            cycle_end = cycle_start + timedelta(days=period_duration - 1)
            ovulation_date = cycle_start + timedelta(days=ovulation_offset)
            fertile_start = ovulation_date - timedelta(days=4)
            fertile_end = ovulation_date + timedelta(days=1)
            
            projections.append({
                "cycle_index": i + 1,
                "period_start": cycle_start,
                "period_end": cycle_end,
                "ovulation_date": ovulation_date,
                "fertile_start": fertile_start,
                "fertile_end": fertile_end,
                "next_cycle_start": cycle_start + timedelta(days=cycle_length)
            })

        return projections
