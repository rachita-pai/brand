import os
import json
from typing import Dict, List, Optional

class SupabaseClient:
    def __init__(self, use_service_role=False):
        self.url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')

        # Use service role key for backend operations (bypasses RLS)
        # Use anon key for client-facing operations (respects RLS)
        if use_service_role:
            self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            if not self.key:
                raise Exception('SUPABASE_SERVICE_ROLE_KEY environment variable is required for service role operations')
        else:
            self.key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
            if not self.key:
                raise Exception('NEXT_PUBLIC_SUPABASE_ANON_KEY environment variable is required')

        if not self.url:
            raise Exception('NEXT_PUBLIC_SUPABASE_URL environment variable is required')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Supabase REST API"""
        import urllib.request
        import urllib.parse
        
        url = f"{self.url}/rest/v1/{endpoint}"
        
        default_headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        if headers:
            default_headers.update(headers)
        
        request_data = None
        if data:
            request_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=request_data, headers=default_headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8')
            raise Exception(f"Supabase error: {e.code} - {error_data}")
    
    # ============================================================================
    # PROFILE MANAGEMENT
    # ============================================================================
    
    def create_person(self, name: str) -> Dict:
        """Create or get a person"""
        try:
            person_data = {
                'name': name,
                'first_name': name  # Store clean first name for display and sessions
            }
            return self._make_request('POST', 'people', person_data)
        except:
            # Person might already exist, try to get them
            result = self._make_request('GET', f'people?name=eq.{name}')
            return result[0] if result else {}

    def create_person_with_uid(self, name: str, uid: str) -> Dict:
        """Create or get a person with user_id as primary identifier (user_id-first strategy)"""
        try:
            print(f"👤 USER_ID-FIRST: Looking up person by user_id: {uid}")

            # STRATEGY: Always prioritize user_id lookup since it's guaranteed unique
            existing_by_uid = self._make_request('GET', f'people?user_id=eq.{uid}')
            if existing_by_uid:
                person = existing_by_uid[0]
                print(f"✅ USER_ID-FIRST: Found existing person with user_id {uid}: {person.get('name')}")
                return person

            # If no person with this user_id exists, create new one
            # Let database auto-generate unique name if there's a conflict (due to UNIQUE constraint)
            print(f"👤 USER_ID-FIRST: Creating new person for user_id {uid} with preferred name: {name}")

            person_data = {
                'name': name,        # May become "Matte_228d1afc" if conflict (for foreign key)
                'user_id': uid,      # Guaranteed unique identifier
                'first_name': name   # Store clean first name for display and sessions
            }

            result = self._make_request('POST', 'people', person_data)
            actual_name = result.get('name') if result else 'unknown'
            print(f"✅ USER_ID-FIRST: Created person with user_id {uid}, final name: {actual_name}")
            return result

        except Exception as e:
            print(f"❌ USER_ID-FIRST: Error creating person: {e}")

            # Final fallback: check if person was created despite error
            try:
                fallback_person = self._make_request('GET', f'people?user_id=eq.{uid}')
                if fallback_person:
                    print(f"✅ USER_ID-FIRST: Fallback found person: {fallback_person[0].get('name')}")
                    return fallback_person[0]
            except:
                pass

            print(f"❌ USER_ID-FIRST: Could not create or find person for user_id: {uid}")
            return {}

    def get_person_by_uid(self, uid: str) -> Optional[Dict]:
        """Get person by user_id (Supabase auth ID)"""
        try:
            result = self._make_request('GET', f'people?user_id=eq.{uid}')
            return result[0] if result else None
        except:
            return None

    def get_latest_profile_version_by_uid(self, person_uid: str) -> Optional[Dict]:
        """Get the latest profile version for a person by UID"""
        try:
            result = self._make_request('GET', f'profile_versions?person_uid=eq.{person_uid}&order=version_number.desc&limit=1')
            return result[0] if result else None
        except:
            return None

    def insert_profile_version(self, profile_data: Dict) -> Dict:
        """Insert a new profile version"""
        return self._make_request('POST', 'profile_versions', profile_data)
    
    def get_profile_version(self, profile_id: str) -> Optional[Dict]:
        """Get a specific profile version by profile_id (e.g., 'Rachita_v2')
        Used by both admin and consumer chat"""
        try:
            result = self._make_request('GET', f'profile_versions?profile_id=eq.{profile_id}')
            return result[0] if result else None
        except:
            return None
    
    def get_active_profiles(self) -> List[Dict]:
        """Get all active profile versions"""
        try:
            return self._make_request('GET', 'profile_versions?is_active=eq.true')
        except:
            return []
    
    def get_person_profiles(self, person_name: str) -> List[Dict]:
        """Get all profile versions for a person"""
        try:
            # Use ilike for case-insensitive matching
            return self._make_request('GET', f'profile_versions?person_name=ilike.{person_name}&order=version_number.desc')
        except:
            return []

    def get_profiles_by_user_id(self, user_id: str) -> List[Dict]:
        """Get all profile versions for a user_id (both active and inactive for admin)"""
        try:
            print(f"DEBUG: Querying profile_versions for user_id: {user_id}")
            result = self._make_request('GET', f'profile_versions?user_id=eq.{user_id}&order=version_number.desc')
            print(f"DEBUG: Found {len(result) if isinstance(result, list) else 'N/A'} profiles for user_id {user_id}")
            return result
        except Exception as e:
            print(f"ERROR: Failed to get profiles for user_id {user_id}: {str(e)}")
            return []

    def update_profile_version(self, profile_id: str, profile_data: Dict) -> Dict:
        """Update an existing profile version"""
        return self._make_request('PATCH', f'profile_versions?profile_id=eq.{profile_id}', profile_data)
    
    # ============================================================================
    # INTERVIEW TEMPLATES & MANAGEMENT
    # ============================================================================
    
    def get_interview_template(self, template_name: str) -> Optional[Dict]:
        """Get interview template by name"""
        try:
            result = self._make_request('GET', f'interview_templates?template_name=eq.{template_name}')
            return result[0] if result else None
        except:
            return None
    
    def get_interview_topics(self, template_name: str) -> List[Dict]:
        """Get interview topics for a template"""
        try:
            return self._make_request('GET', f'interview_topics?template_name=eq.{template_name}&order=topic_order.asc')
        except:
            return []
    
    def get_active_interview_templates(self) -> List[Dict]:
        """Get all active interview templates"""
        try:
            return self._make_request('GET', 'interview_templates?is_active=eq.true')
        except:
            return []
    
    # ============================================================================
    # INTERVIEW SESSIONS
    # ============================================================================
    
    def insert_interview_session(self, interview_data: Dict) -> Dict:
        """Insert interview session data"""
        return self._make_request('POST', 'interview_sessions', interview_data)
    
    def get_interview_session(self, session_id: str) -> Optional[Dict]:
        """Get interview session by session_id"""
        try:
            result = self._make_request('GET', f'interview_sessions?session_id=eq.{session_id}')
            return result[0] if result else None
        except Exception as e:
            print(f"ERROR querying interview session: {e}")
            return None
    
    def complete_interview_session(self, session_id: str, profile_id: str) -> Dict:
        """Mark interview session as complete and link to profile"""
        return self._make_request('PATCH', f'interview_sessions?session_id=eq.{session_id}', {
            'is_complete': True,
            'profile_id': profile_id,
            'completed_at': 'NOW()'
        })
    
    def get_sessions_by_profile_id(self, profile_id: str) -> List[Dict]:
        """Get all interview sessions linked to a profile"""
        try:
            return self._make_request('GET', f'interview_sessions?profile_id=eq.{profile_id}')
        except Exception as e:
            print(f"ERROR getting sessions for profile {profile_id}: {e}")
            return []
    
    # ============================================================================
    # SURVEY & VALIDATION MANAGEMENT
    # ============================================================================
    
    def get_survey_template(self, survey_name: str) -> Optional[Dict]:
        """Get survey template by name"""
        try:
            import urllib.parse
            encoded_name = urllib.parse.quote(survey_name)
            result = self._make_request('GET', f'survey_templates?survey_name=eq.{encoded_name}')
            return result[0] if result else None
        except:
            return None
    
    def get_all_survey_templates(self) -> List[Dict]:
        """Get all available survey templates"""
        try:
            return self._make_request('GET', 'survey_templates?is_active=eq.true&order=created_at.desc')
        except:
            return []
    
    def create_survey_template(self, survey_data: Dict) -> Dict:
        """Create a new survey template"""
        return self._make_request('POST', 'survey_templates', survey_data)
    
    def delete_survey_template(self, survey_name: str) -> bool:
        """Delete a survey template"""
        try:
            self._make_request('DELETE', f'survey_templates?survey_name=eq.{survey_name}')
            return True
        except:
            return False
    
    def create_validation_test_session(self, test_data: Dict) -> Dict:
        """Create a new validation test session"""
        return self._make_request('POST', 'validation_test_sessions', test_data)
    
    def insert_question_response(self, response_data: Dict) -> Dict:
        """Insert a question response"""
        return self._make_request('POST', 'question_responses', response_data)
    
    def insert_validation_result(self, result_data: Dict) -> Dict:
        """Insert validation test results"""
        return self._make_request('POST', 'validation_test_results', result_data)
    
    def get_validation_results(self, profile_id: str) -> List[Dict]:
        """Get all validation results for a profile"""
        try:
            return self._make_request('GET', f'validation_test_results?profile_id=eq.{profile_id}&order=created_at.desc')
        except:
            return []
    
    def get_test_session_results(self, test_session_id: str) -> Optional[Dict]:
        """Get detailed results for a specific test session"""
        try:
            result = self._make_request('GET', f'validation_test_results?test_session_id=eq.{test_session_id}')
            return result[0] if result else None
        except:
            return None
    
    # ============================================================================
    # AI PREDICTIONS & ANALYTICS
    # ============================================================================
    
    def insert_ai_prediction(self, prediction_data: Dict) -> Dict:
        """Insert AI prediction data"""
        return self._make_request('POST', 'ai_predictions', prediction_data)
    
    def get_profile_predictions(self, profile_id: str) -> List[Dict]:
        """Get all AI predictions for a profile"""
        try:
            return self._make_request('GET', f'ai_predictions?profile_id=eq.{profile_id}')
        except:
            return []
    
    def update_test_history_summary(self, profile_id: str, summary_data: Dict) -> Dict:
        """Update or create test history summary"""
        try:
            # Try to update existing
            return self._make_request('PATCH', f'test_history_summary?profile_id=eq.{profile_id}', summary_data)
        except:
            # Create new if doesn't exist
            summary_data['profile_id'] = profile_id
            return self._make_request('POST', 'test_history_summary', summary_data)
    
    def get_test_history_summary(self, profile_id: str) -> Optional[Dict]:
        """Get test history summary for a profile"""
        try:
            result = self._make_request('GET', f'test_history_summary?profile_id=eq.{profile_id}')
            return result[0] if result else None
        except:
            return None
    
    # ============================================================================
    # CUSTOM QUESTIONNAIRES
    # ============================================================================
    
    def create_custom_questionnaire(self, questionnaire_data: Dict) -> Dict:
        """Create a new custom questionnaire"""
        return self._make_request('POST', 'custom_questionnaires', questionnaire_data)
    
    def add_questionnaire_question(self, question_data: Dict) -> Dict:
        """Add a question to a questionnaire"""
        return self._make_request('POST', 'questionnaire_questions', question_data)
    
    def get_custom_questionnaire(self, questionnaire_id: str) -> Optional[Dict]:
        """Get a custom questionnaire by ID"""
        try:
            result = self._make_request('GET', f'custom_questionnaires?questionnaire_id=eq.{questionnaire_id}')
            return result[0] if result else None
        except Exception as e:
            print(f"ERROR in get_custom_questionnaire: {e}")
            return None
    
    def get_questionnaire_questions(self, questionnaire_id: str) -> List[Dict]:
        """Get all questions for a questionnaire"""
        try:
            return self._make_request('GET', f'questionnaire_questions?questionnaire_id=eq.{questionnaire_id}&order=question_order.asc')
        except:
            return []
    
    def get_public_questionnaires(self) -> List[Dict]:
        """Get all public questionnaires"""
        try:
            return self._make_request('GET', 'custom_questionnaires?is_public=eq.true&is_active=eq.true&order=created_at.desc')
        except:
            return []
    
    def get_questionnaires_by_category(self, category: str) -> List[Dict]:
        """Get questionnaires by category"""
        try:
            return self._make_request('GET', f'custom_questionnaires?category=eq.{category}&is_active=eq.true&order=usage_count.desc')
        except:
            return []
    
    def increment_questionnaire_usage(self, questionnaire_id: str) -> Dict:
        """Increment usage count for a questionnaire"""
        return self._make_request('PATCH', f'custom_questionnaires?questionnaire_id=eq.{questionnaire_id}', {
            'usage_count': 'usage_count + 1',
            'updated_at': 'NOW()'
        })
    
    def record_questionnaire_usage(self, usage_data: Dict) -> Dict:
        """Record questionnaire usage tracking"""
        return self._make_request('POST', 'questionnaire_usage', usage_data)
    
    # ============================================================================
    # QUESTIONNAIRE COMPLETIONS (modular profile building)
    # ============================================================================
    
    def insert_questionnaire_completion(self, completion_data: Dict) -> Dict:
        """Save a completed questionnaire module"""
        return self._make_request('POST', 'questionnaire_completions', completion_data)
    
    def get_questionnaire_completions(self, profile_id: str) -> List[Dict]:
        """Get all questionnaire completions for a profile"""
        try:
            return self._make_request('GET', f'questionnaire_completions?profile_id=eq.{profile_id}&order=completed_at.asc')
        except:
            return []
    
    def get_completion_by_type(self, profile_id: str, questionnaire_type: str, questionnaire_name: str = None) -> Optional[Dict]:
        """Get specific questionnaire completion"""
        try:
            query = f'questionnaire_completions?profile_id=eq.{profile_id}&questionnaire_type=eq.{questionnaire_type}'
            if questionnaire_name:
                query += f'&questionnaire_name=eq.{questionnaire_name}'
            result = self._make_request('GET', query)
            return result[0] if result else None
        except:
            return None
    
    def update_profile_completeness(self, profile_id: str, completeness_metadata: Dict) -> Dict:
        """Update profile version with completeness tracking"""
        return self._make_request('PATCH', f'profile_versions?profile_id=eq.{profile_id}', {
            'completeness_metadata': completeness_metadata,
            'updated_at': 'NOW()'
        })
    
    # ============================================================================
    # CONVERSATION MESSAGE STORAGE (stored in interview_sessions.messages JSONB)
    # ============================================================================
    
    def get_session_messages_from_interview(self, session_id: str) -> List[Dict]:
        """Get conversation messages from interview_sessions.messages JSONB field"""
        try:
            interview_session = self.get_interview_session(session_id)
            if interview_session:
                return interview_session.get('messages', [])
            return []
        except:
            return []
    
    # ============================================================================
    # INTERVIEW SESSIONS & PROFILE MANAGEMENT
    # ============================================================================
    
    
    def get_person(self, name: str) -> Optional[Dict]:
        """Get person by name"""
        try:
            result = self._make_request('GET', f'people?name=eq.{name}')
            return result[0] if result else None
        except:
            return None

    def update_person_user_id(self, name: str, user_id: str) -> Dict:
        """Update existing person record to include user_id"""
        try:
            update_data = {'user_id': user_id, 'updated_at': 'NOW()'}
            result = self._make_request('PATCH', f'people?name=eq.{name}', update_data)
            print(f"🔄 Updated person '{name}' with user_id: {user_id}")
            return result
        except Exception as e:
            print(f"❌ Error updating person with user_id: {e}")
            return {}
    
    def create_interview_session(self, session_data: Dict) -> Dict:
        """Create a new interview session"""
        print(f"DEBUG: Creating interview session with data: {session_data}")
        try:
            result = self._make_request('POST', 'interview_sessions', session_data)
            print(f"DEBUG: Successfully created interview session: {result}")
            return result
        except Exception as e:
            print(f"DEBUG: Failed to create interview session: {e}")
            raise e
    
    def update_interview_session(self, session_id: str, updates: Dict) -> Dict:
        """Update an existing interview session"""
        return self._make_request('PATCH', f'interview_sessions?session_id=eq.{session_id}', updates)

    def upsert_interview_session(self, session_data: Dict) -> Dict:
        """Atomically insert or update interview session using PostgreSQL UPSERT"""
        # Use Supabase upsert with on_conflict parameter to handle duplicates atomically
        # This prevents race conditions when multiple webhooks arrive simultaneously
        headers = {'Prefer': 'resolution=merge-duplicates'}
        try:
            result = self._make_request('POST', 'interview_sessions', session_data, headers)
            print(f"✅ ATOMIC UPSERT: Successfully upserted interview session: {session_data.get('session_id')}")
            return result
        except Exception as e:
            print(f"❌ ATOMIC UPSERT: Failed to upsert interview session: {e}")
            print(f"❌ ATOMIC UPSERT: Session data: {session_data}")
            raise e
    
    def get_recent_interview_sessions_by_person_and_questionnaire(self, person_name: str, questionnaire_id: str) -> List[Dict]:
        """Get recent interview sessions for a person and specific questionnaire type"""
        try:
            import urllib.parse
            encoded_name = urllib.parse.quote(person_name.strip())
            encoded_questionnaire = urllib.parse.quote(questionnaire_id.strip())
            
            # Get sessions from today for this person and questionnaire
            today_start = urllib.parse.quote(self._get_today_start())
            result = self._make_request('GET', 
                f'interview_sessions?person_name=eq.{encoded_name}&questionnaire_id=eq.{encoded_questionnaire}&created_at=gte.{today_start}&order=created_at.desc')
            
            print(f"DEBUG: Found {len(result)} sessions for {person_name} + {questionnaire_id}")
            return result
        except Exception as e:
            print(f"DEBUG: Error getting recent sessions: {e}")
            return []
    
    def _get_today_start(self) -> str:
        """Get today's start timestamp in ISO format"""
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return today_start.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    
    def create_profile_version(self, profile_data: Dict) -> Dict:
        """Create a new profile version"""
        print(f"🔍 SUPABASE: Creating profile version with person_uid: {profile_data.get('person_uid')}")
        result = self._make_request('POST', 'profile_versions', profile_data)
        print(f"🔍 SUPABASE: Created profile result - person_uid in response: {result.get('person_uid') if isinstance(result, dict) else 'Not in response'}")
        return result
    
    def get_latest_profile_version(self, person_name: str) -> Optional[Dict]:
        """Get the latest profile version for a person"""
        try:
            import urllib.parse
            # URL encode the person name to handle spaces and special characters
            encoded_name = urllib.parse.quote(person_name.strip())
            print(f"DEBUG: Querying latest profile version for person: {person_name} (encoded: {encoded_name})")
            # Use ilike for case-insensitive matching to handle both "rachita_v1" and "Rachita_v1" formats
            result = self._make_request('GET', f'profile_versions?person_name=ilike.{encoded_name}&order=version_number.desc&limit=1')
            print(f"DEBUG: Latest profile query result: {result}")
            return result[0] if result else None
        except Exception as e:
            print(f"DEBUG: Error getting latest profile version: {e}")
            return None

    # ==================== PRODUCT PROFILES ====================

    def save_product_profile(self, profile_data: Dict) -> Dict:
        """
        Save a product profile to the database

        Args:
            profile_data: Dictionary containing:
                - user_id (UUID): User identifier
                - person_name (str): Person's name
                - product_category (str): Product type (e.g., "Coffee")
                - questionnaire_id (str): Questionnaire identifier (e.g., "coffee_v1")
                - session_id (str): Interview session ID
                - profile_json (dict): Extracted insights organized by tags

        Returns:
            Created product profile record
        """
        print(f"💾 SUPABASE: Saving product profile for {profile_data.get('product_category')}")
        print(f"💾 SUPABASE: user_id={profile_data.get('user_id')}, session_id={profile_data.get('session_id')}")

        result = self._make_request('POST', 'product_profiles', profile_data)
        print(f"✅ SUPABASE: Product profile saved successfully")
        # Supabase POST returns a list, return first item
        return result[0] if result and len(result) > 0 else result

    def get_product_profiles(self, user_id: str) -> List[Dict]:
        """
        Get all product profiles for a user

        Args:
            user_id: User UUID

        Returns:
            List of product profile records
        """
        import urllib.parse
        encoded_user_id = urllib.parse.quote(user_id)
        print(f"🔍 SUPABASE: Fetching all product profiles for user_id={user_id}")

        result = self._make_request('GET', f'product_profiles?user_id=eq.{encoded_user_id}&order=created_at.desc')
        print(f"✅ SUPABASE: Found {len(result) if result else 0} product profiles")
        return result if result else []

    def get_product_profile(self, user_id: str, product_category: str) -> Optional[Dict]:
        """
        Get the most recent product profile for a specific product category

        Args:
            user_id: User UUID
            product_category: Product type (e.g., "Coffee", "Face cleanser")

        Returns:
            Most recent product profile record or None
        """
        import urllib.parse
        encoded_user_id = urllib.parse.quote(user_id)
        encoded_category = urllib.parse.quote(product_category)

        print(f"🔍 SUPABASE: Fetching product profile for user_id={user_id}, product={product_category}")

        result = self._make_request(
            'GET',
            f'product_profiles?user_id=eq.{encoded_user_id}&product_category=eq.{encoded_category}&order=created_at.desc&limit=1'
        )

        if result and len(result) > 0:
            print(f"✅ SUPABASE: Found product profile")
            return result[0]
        else:
            print(f"❌ SUPABASE: No product profile found")
            return None

    def get_product_profile_by_session(self, session_id: str) -> Optional[Dict]:
        """
        Get product profile by interview session ID

        Args:
            session_id: Interview session identifier

        Returns:
            Product profile record or None
        """
        import urllib.parse
        encoded_session_id = urllib.parse.quote(session_id)

        print(f"🔍 SUPABASE: Fetching product profile for session_id={session_id}")

        result = self._make_request('GET', f'product_profiles?session_id=eq.{encoded_session_id}&limit=1')

        if result and len(result) > 0:
            print(f"✅ SUPABASE: Found product profile")
            return result[0]
        else:
            print(f"❌ SUPABASE: No product profile found for session")
            return None