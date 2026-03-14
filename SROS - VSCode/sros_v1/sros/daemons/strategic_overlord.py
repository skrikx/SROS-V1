"""
Strategic Overlord
==================

Campaign-level Volition.
Manages long-term strategic goals (Campaigns) and breaks them into Missions.
"""
import logging
import time
from typing import List, Dict, Any
from sros.kernel.event_bus import EventBus
from sros.runtime.agents.skrikx_agent import SkrikxAgent

logger = logging.getLogger(__name__)

class StrategicOverlord:
    """
    Manages long-term campaigns.
    """
    def __init__(self, agent: SkrikxAgent):
        self.agent = agent
        self.campaigns: List[Dict[str, Any]] = []

    def add_campaign(self, name: str, objective: str):
        """Start a new strategic campaign."""
        self.campaigns.append({
            "name": name,
            "objective": objective,
            "status": "active",
            "missions": []
        })
        logger.info(f"Campaign Started: {name}")

    def strategize(self):
        """
        Review campaigns and generate missions.
        """
        for campaign in self.campaigns:
            if campaign["status"] == "active":
                # Ask agent to generate next mission
                prompt = f"""
                Campaign: {campaign['name']}
                Objective: {campaign['objective']}
                
                Current Missions: {len(campaign['missions'])} completed.
                
                Task:
                Generate the NEXT tactical mission to advance this campaign.
                """
                response = self.agent.chat(prompt)
                mission = response.get("text", "No mission generated.")
                
                campaign["missions"].append({
                    "mission": mission,
                    "timestamp": time.time()
                })
                logger.info(f"New Mission for {campaign['name']}: {mission[:50]}...")
