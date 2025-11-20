"""
Brand Demo Query API
Handles brand research questions using multi-query pattern from main PAI project
Decomposes questions, queries AI twins in batches, analyzes responses
"""

import os
import sys
import json
import concurrent.futures
from http.server import BaseHTTPRequestHandler

# Add lib directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.supabase import SupabaseClient


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for brand queries"""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            product = data.get('product')
            question = data.get('question')

            # Validate input
            if not product or not question:
                self.send_error(400, "Missing product or question")
                return

            if product not in ['pickles', 'oats']:
                self.send_error(400, "Invalid product")
                return

            # Get API keys
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_key:
                self.send_error(500, "Missing ANTHROPIC_API_KEY")
                return

            # Get AI digital twin profiles from Supabase
            supabase = SupabaseClient(use_service_role=False)
            profile_ids = self._get_relevant_profile_ids(supabase, product)

            if not profile_ids:
                # Fallback message if no profiles
                response_text = self._generate_fallback_message(product)
                response = {
                    'response': response_text,
                    'profiles_analyzed': 0,
                    'product': product,
                    'total_twins_queried': 0,
                    'confidence': 0
                }
            else:
                # Use multi-query approach from main project
                # Step 1: Decompose question into sub-questions
                sub_questions = self._decompose_research_question(question, anthropic_key)
                print(f"DEBUG: Decomposed into {len(sub_questions)} sub-questions")

                # Step 2: Query all twins with sub-questions in parallel
                all_survey_results = self._process_sub_questions_parallel(
                    profile_ids, sub_questions, anthropic_key, supabase
                )

                # Step 3: Generate overall insights
                key_insights = self._generate_overall_insights(
                    all_survey_results, question, anthropic_key
                )

                # Calculate average confidence
                avg_confidence = sum(r.get('confidence', 0) for r in all_survey_results) // len(all_survey_results) if all_survey_results else 0

                # Return structured response
                response = {
                    'query': question,
                    'product': product,
                    'total_twins_queried': len(profile_ids),
                    'profiles_analyzed': len(profile_ids),
                    'confidence': avg_confidence,
                    'key_insights': key_insights,
                    'survey_results': all_survey_results,
                    'privacy_note': 'Individual responses kept confidential for privacy protection'
                }

            # Send successful response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"Error in query API: {e}")
            import traceback
            traceback.print_exc()

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            error_response = {
                'error': str(e),
                'response': "I encountered an error processing your question. Please try again or rephrase your question."
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _get_relevant_profile_ids(self, supabase: SupabaseClient, product: str) -> list:
        """Get profile IDs for AI twins relevant to the product category"""
        try:
            # Get all active profiles
            all_profiles = supabase.get_active_profiles()

            if not all_profiles:
                return []

            # Filter profiles with relevant data and extract profile_ids
            profile_ids = []
            for profile in all_profiles[:10]:  # Check first 10 active profiles
                profile_data = profile.get('profile_data', {})

                # Check if profile has useful data for food-related queries
                has_food_data = (
                    'eating_habits' in profile_data or
                    'health_wellness' in profile_data or
                    'purchase_behavior' in profile_data or
                    'lifestyle' in profile_data
                )

                if has_food_data:
                    profile_ids.append(profile.get('profile_id'))

                if len(profile_ids) >= 5:
                    break

            # If no profiles with food data, just use first 5 active profile IDs
            if not profile_ids and all_profiles:
                profile_ids = [p.get('profile_id') for p in all_profiles[:5] if p.get('profile_id')]

            return profile_ids

        except Exception as e:
            print(f"Error getting profiles: {e}")
            return []

    def _decompose_research_question(self, query: str, api_key: str) -> list:
        """Decompose a broad research question into 3 specific sub-questions"""
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        decompose_prompt = f"""You are a market research expert. Your task is to break down a broad research question into exactly 3 specific, actionable sub-questions that will provide the most valuable consumer insights.

RESEARCH QUESTION: {query}

Create 3 sub-questions that:
1. Are specific and answerable by consumers
2. Cover different aspects (e.g., preferences, concerns, willingness-to-pay, usage patterns)
3. Will yield quantifiable insights when asked to consumers
4. Are phrased naturally, as if asking a real person

Return your response in this exact JSON format - no extra text:

{{
  "sub_questions": [
    {{
      "question": "First specific sub-question here?",
      "insight_type": "preferences|concerns|pricing|usage|barriers"
    }},
    {{
      "question": "Second specific sub-question here?",
      "insight_type": "preferences|concerns|pricing|usage|barriers"
    }},
    {{
      "question": "Third specific sub-question here?",
      "insight_type": "preferences|concerns|pricing|usage|barriers"
    }}
  ]
}}"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.5,
                messages=[{
                    "role": "user",
                    "content": decompose_prompt
                }]
            )

            response_text = response.content[0].text
            print(f"DEBUG: Question decomposition response: {response_text}")

            result = json.loads(response_text)
            return result.get('sub_questions', [])

        except Exception as e:
            print(f"DEBUG: Error decomposing question: {e}")
            # Fallback to generic sub-questions
            return [
                {"question": f"What are your preferences regarding {query}?", "insight_type": "preferences"},
                {"question": f"What concerns do you have about {query}?", "insight_type": "concerns"},
                {"question": f"How would you rate your interest in {query}?", "insight_type": "usage"}
            ]

    def _process_sub_questions_parallel(self, profile_ids: list, sub_questions: list, api_key: str, supabase: SupabaseClient) -> list:
        """Process all sub-questions in parallel"""
        all_survey_results = [None] * len(sub_questions)

        def process_sub_question(sub_q, index):
            print(f"DEBUG: Processing sub-question {index + 1}: {sub_q['question']}")
            responses = self._query_multiple_twins(profile_ids, sub_q['question'], api_key, supabase)
            survey_result = self._analyze_survey_responses(responses, sub_q, api_key)
            return (index, survey_result)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_index = {
                executor.submit(process_sub_question, sub_q, i): i
                for i, sub_q in enumerate(sub_questions)
            }

            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    index, survey_result = future.result()
                    all_survey_results[index] = survey_result
                    print(f"DEBUG: Sub-question {index + 1} completed")
                except Exception as e:
                    index = future_to_index[future]
                    print(f"DEBUG: Error processing sub-question {index + 1}: {e}")
                    all_survey_results[index] = {
                        "question": sub_questions[index]['question'],
                        "insight_type": sub_questions[index]['insight_type'],
                        "top_insight": "Analysis failed",
                        "data_points": [],
                        "confidence": 0
                    }

        return all_survey_results

    def _query_multiple_twins(self, profile_ids: list, query: str, api_key: str, supabase: SupabaseClient) -> list:
        """Query multiple digital twins using batch processing"""
        responses = []

        try:
            # Load all profiles
            loaded_profiles = []
            for profile_id in profile_ids:
                profile_data = supabase.get_profile_version(profile_id)
                if profile_data:
                    loaded_profiles.append({
                        'profile_id': profile_id,
                        'person_name': profile_data.get('person_name', 'Unknown'),
                        'profile_data': profile_data
                    })

            # Query in batches of 10
            BATCH_SIZE = 10
            profile_batches = [loaded_profiles[i:i + BATCH_SIZE] for i in range(0, len(loaded_profiles), BATCH_SIZE)]

            for batch in profile_batches:
                batch_responses = self._query_batch_of_twins(batch, query, api_key)
                responses.extend(batch_responses)

        except Exception as e:
            print(f"DEBUG: Error in multi-query: {e}")

        return responses

    def _query_batch_of_twins(self, profiles: list, query: str, api_key: str) -> list:
        """Query a batch of digital twins in a single API call"""
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        # Build batch prompt
        profiles_text = ""
        for i, profile in enumerate(profiles, 1):
            profile_json = profile['profile_data'].get('profile_data', {})
            person_name = profile['person_name']
            profiles_text += f"\n\nPERSON {i} - {person_name}:\n{json.dumps(profile_json, indent=2)}"

        batch_prompt = f"""You are analyzing how multiple people would respond to a question based on their personality profiles.

PERSONALITY PROFILES:{profiles_text}

QUESTION: {query}

For each person, respond as THEY would, using first person ("I", "my", "me"). Base responses on their personality traits, attitudes, and decision-making patterns. Keep each response to 2-3 sentences.

Return your responses in this exact JSON format - no extra text:

{{
  "responses": [
    {{"person_number": 1, "person_name": "{profiles[0]['person_name']}", "response": "Their authentic response here"}},
    {{"person_number": 2, "person_name": "{profiles[1]['person_name'] if len(profiles) > 1 else ''}", "response": "Their authentic response here"}},
    ... (continue for all {len(profiles)} people)
  ]
}}"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": batch_prompt
                }]
            )

            batch_response_text = response.content[0].text
            batch_data = json.loads(batch_response_text)
            batch_responses = []

            for resp in batch_data.get('responses', []):
                person_num = resp.get('person_number', 0) - 1
                if 0 <= person_num < len(profiles):
                    profile = profiles[person_num]
                    batch_responses.append({
                        'profile_id': profile['profile_id'],
                        'person_name': profile['person_name'],
                        'response': resp.get('response', 'No response provided'),
                        'error': False
                    })

            return batch_responses

        except Exception as e:
            print(f"DEBUG: Error in batch query: {e}")
            return [{
                'profile_id': profile['profile_id'],
                'person_name': profile['person_name'],
                'response': f'Error generating response: {str(e)}',
                'error': True
            } for profile in profiles]

    def _analyze_survey_responses(self, responses: list, sub_question: dict, api_key: str) -> dict:
        """Analyze responses and extract quantifiable insights with percentages"""
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        valid_responses = [r for r in responses if not r.get('error', False)]

        if len(valid_responses) == 0:
            return {
                "question": sub_question['question'],
                "insight_type": sub_question['insight_type'],
                "top_insight": "Insufficient data",
                "data_points": [],
                "confidence": 0
            }

        responses_text = "\n\n".join([
            f"Participant {i+1}: {r['response']}"
            for i, r in enumerate(valid_responses)
        ])

        analysis_prompt = f"""You are a market research analyst analyzing consumer responses to extract quantifiable insights.

QUESTION ASKED: {sub_question['question']}
INSIGHT TYPE: {sub_question['insight_type']}

CONSUMER RESPONSES ({len(valid_responses)} participants):
{responses_text}

Analyze these responses and extract the most common themes or patterns. Categorize responses and provide percentages.

Return your analysis in this exact JSON format - no extra text:

{{
  "top_insight": "One-sentence summary of the key finding",
  "data_points": [
    {{"category": "Category name", "percentage": 35, "description": "Brief description"}},
    {{"category": "Category name", "percentage": 28, "description": "Brief description"}},
    {{"category": "Category name", "percentage": 22, "description": "Brief description"}},
    {{"category": "Category name", "percentage": 15, "description": "Brief description"}}
  ],
  "confidence": 94
}}

Requirements:
- Extract 3-5 distinct categories from the responses
- Percentages should add up to ~100%
- Be specific and actionable
- Confidence level based on response clarity and consistency"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": analysis_prompt
                }]
            )

            response_text = response.content[0].text
            result = json.loads(response_text)
            result['question'] = sub_question['question']
            result['insight_type'] = sub_question['insight_type']
            return result

        except Exception as e:
            print(f"DEBUG: Error analyzing survey responses: {e}")
            return {
                "question": sub_question['question'],
                "insight_type": sub_question['insight_type'],
                "top_insight": "Analysis temporarily unavailable",
                "data_points": [],
                "confidence": 0
            }

    def _generate_overall_insights(self, survey_results: list, original_query: str, api_key: str) -> list:
        """Generate concise key insights from all survey results"""
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        findings_text = ""
        for i, result in enumerate(survey_results, 1):
            findings_text += f"\n\nQuestion {i}: {result['question']}\n"
            findings_text += f"Key Finding: {result['top_insight']}\n"
            findings_text += "Top Categories:\n"
            for dp in result['data_points'][:3]:
                findings_text += f"  - {dp['category']}: {dp['percentage']}%\n"

        insights_prompt = f"""You are a market research analyst. Synthesize survey findings into 3 concise, actionable insights.

ORIGINAL RESEARCH QUESTION: {original_query}

SURVEY FINDINGS:{findings_text}

Create exactly 3 key insights that:
- Are ONE sentence each (under 100 characters)
- Include specific percentages from the data
- Are actionable and highlight the most important findings
- Are numbered 1, 2, 3

Return in this exact JSON format - no extra text:

{{
  "key_insights": [
    "62% prioritize sustained energy boost and natural ingredients",
    "Finding balance without jitters is the top concern for 41% of users",
    "59% willing to pay $3+ for premium energy drinks with functional benefits"
  ]
}}"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": insights_prompt
                }]
            )

            response_text = response.content[0].text
            result = json.loads(response_text)
            return result.get('key_insights', [])

        except Exception as e:
            print(f"DEBUG: Error generating overall insights: {e}")
            return [result['top_insight'] for result in survey_results[:3]]

    def _generate_fallback_message(self, product: str) -> str:
        """Generate fallback message when no profiles available"""
        return f"""I apologize, but we don't have AI digital twin profiles available for {product} at the moment.

In a production environment, this demo would analyze responses from our network of AI twins who have shared insights about their {product} preferences and behaviors.

For demonstration purposes, I can tell you that our AI twins typically provide insights on:
- Flavor preferences and taste profiles
- Purchase frequency and occasions
- Price sensitivity and value perception
- Brand loyalty factors
- Health and wellness considerations
- Packaging and convenience preferences

Please try the demo again later when we have active profiles available."""
