import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to sys.path
sys.path.append(os.getcwd())

class TestCrewIntegration(unittest.TestCase):

    def test_imports(self):
        """Test that the new modules can be imported without error."""
        try:
            from model.crew import TravelCrew, AddressSummaryCrew, Itinerary
            print("Successfully imported TravelCrew, AddressSummaryCrew, and Itinerary.")
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    @patch('model.crew.TravelCrew.crew')
    def test_app_integration_logic(self, mock_crew_method):
        """Test the logic inside generate_itinerary by mocking the CrewAI kickoff."""
        from app import app
        
        # Mock result object
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            'destination': 'Paris',
            'total_cost': 500.0,
            'days': [
                {
                    'day_number': 1,
                    'activities': [
                        {
                            'name': 'Eiffel Tower',
                            'time': '10:00',
                            'rating': 4.8,
                            'cost': 25.0,
                            'description': 'Visit the iconic tower'
                        }
                    ]
                }
            ]
        }
        
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_method.return_value = mock_crew_instance
        
        # Use Flask test client
        with app.test_client() as client:
            # Mock authentication
            with patch('app.token_required', lambda f: f):
                # We need to patch the actual decorator in the app module
                with patch('app.jwt.decode', return_value={'user_id': 1}):
                    # We also need a database connection mock for fallback
                    with patch('database.get_db_connection'):
                        response = client.post('/api/generate-itinerary', 
                                             json={
                                                 'destination': 'Paris',
                                                 'budget': 1000,
                                                 'duration': 1
                                             },
                                             # Need to pass a cookie if we didn't mock decorator fully
                                             cookies={'token': 'test_token'})
                        
                        self.assertEqual(response.status_code, 200)
                        data = response.get_json()
                        self.assertEqual(data['destination'], 'Paris')
                        self.assertEqual(len(data['days']), 1)
                        self.assertEqual(data['days'][0]['route'][0]['place'], 'Eiffel Tower')
                        print("Flask integration logic verified successfully.")

if __name__ == '__main__':
    unittest.main()
