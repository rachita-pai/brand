"""
Brand Demo Insights Generator
Generates aggregated consumer insights from AI twin profiles based on brand queries
"""

import os
import json
from typing import Dict, List, Any
from anthropic import Anthropic

class InsightsGenerator:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """System prompt for generating insights from AI twin profiles"""
        return """You are an AI insights analyst for PAI (Personal AI), a platform that creates digital twin personas from deep conversational interviews.

Your role is to analyze multiple AI digital twin profiles and provide aggregated consumer insights to brand researchers.

CRITICAL GUIDELINES:
1. Analyze the profiles provided to understand consumer behaviors, preferences, and decision-making patterns
2. Provide specific, actionable insights based on the profile data
3. Cite patterns you observe (e.g., "3 out of 5 twins mentioned...")
4. Include percentage breakdowns when relevant
5. Highlight key trends and surprising findings
6. Keep responses concise but insightful (150-250 words)
7. Use natural, professional language - as if briefing a brand manager
8. Reference specific quotes or behaviors from the profiles when relevant

Remember: These are real AI digital twins built from 15-20 minute interviews, not hypothetical personas. The insights should feel data-driven and authentic."""

    def generate_insights(self, question: str, profiles: List[Dict[str, Any]], product: str) -> str:
        """Generate aggregated consumer insights from multiple AI twin profiles

        Args:
            question: The brand's research question
            profiles: List of AI twin profile data dictionaries
            product: Product category (pickles/oats)

        Returns:
            Aggregated insights response
        """
        try:
            # Format profiles for analysis
            profiles_text = self._format_profiles(profiles)

            # Create the prompt
            user_prompt = f"""PRODUCT CATEGORY: {product.title()}

BRAND RESEARCH QUESTION:
{question}

AI DIGITAL TWIN PROFILES:
{profiles_text}

Analyze these {len(profiles)} digital twin profiles and provide aggregated consumer insights that answer the brand's question. Focus on:
- Clear patterns and trends across the profiles
- Specific percentages and counts
- Actionable insights for product development/marketing
- Surprising or noteworthy findings

Provide your response as if briefing a brand manager."""

            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                temperature=0.7,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            # Extract text response
            insights = response.content[0].text

            # Add sample size context
            insights += f"\n\n*Analysis based on {len(profiles)} AI digital twin profiles*"

            return insights

        except Exception as e:
            print(f"Error generating insights: {e}")
            raise

    def _format_profiles(self, profiles: List[Dict[str, Any]]) -> str:
        """Format profile data for analysis"""
        formatted = []

        for i, profile in enumerate(profiles, 1):
            # Extract relevant profile fields
            profile_data = profile.get('profile_data', {})

            # Format profile summary
            summary = f"Twin {i}:"

            # Add demographics if available
            if 'demographics' in profile_data:
                demo = profile_data['demographics']
                if demo.get('age'): summary += f"\n  Age: {demo['age']}"
                if demo.get('location'): summary += f"\n  Location: {demo['location']}"

            # Add key insights from profile
            if 'summary' in profile_data:
                summary += f"\n  Summary: {profile_data['summary']}"

            # Add relevant behavioral patterns
            if 'eating_habits' in profile_data:
                summary += f"\n  Eating Habits: {json.dumps(profile_data['eating_habits'])}"

            if 'purchase_behavior' in profile_data:
                summary += f"\n  Purchase Behavior: {json.dumps(profile_data['purchase_behavior'])}"

            if 'health_wellness' in profile_data:
                summary += f"\n  Health & Wellness: {json.dumps(profile_data['health_wellness'])}"

            formatted.append(summary)

        return "\n\n".join(formatted)
