import unittest
import json
from meeting_minutes_robot import (
    MeetingMinutes,
    DiscussionPoint,
    ActionItem,
    Decision,
    parse_gemini_response,
    format_minutes_to_text,
    main
)
from io import StringIO
import sys
import os

class TestMeetingMinutesRobot(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            "summary": "Test summary.",
            "discussion_points": [
                {"speaker": "Speaker1", "point": "Point 1"},
                {"speaker": "Speaker2", "point": "Point 2"}
            ],
            "action_items": [
                {"assignee": "Assignee1", "task": "Task 1", "deadline": "2024-12-31"},
                {"task": "Task 2"}
            ],
            "decisions": [
                {"decision": "Decision 1"}
            ],
            "topics": ["Topic1", "Topic2"],
            "meeting_title": "Test Meeting",
            "date": "2024-01-01",
            "time": "10:00 AM",
            "attendees": ["Attendee1", "Attendee2"]
        }
        self.sample_json_string = json.dumps(self.sample_data)

    def test_parse_gemini_response_success(self):
        minutes = parse_gemini_response(self.sample_json_string)
        self.assertIsNotNone(minutes)
        self.assertIsInstance(minutes, MeetingMinutes)
        self.assertEqual(minutes.summary, self.sample_data["summary"])
        self.assertEqual(len(minutes.discussion_points), 2)
        self.assertEqual(minutes.discussion_points[0].speaker, "Speaker1")
        self.assertEqual(minutes.action_items[0].assignee, "Assignee1")
        self.assertEqual(minutes.topics[0], "Topic1")
        self.assertEqual(minutes.meeting_title, "Test Meeting")

    def test_parse_gemini_response_invalid_json(self):
        invalid_json = "{'summary': 'bad json"
        # Suppress print statements during this test
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        minutes = parse_gemini_response(invalid_json)
        sys.stdout = old_stdout # Restore stdout
        self.assertIsNone(minutes)

    def test_parse_gemini_response_missing_fields(self):
        # Pydantic should handle missing non-optional fields by raising validation error
        # Our parser should catch this and return None
        incomplete_data = {"summary": "Only summary"}
        incomplete_json = json.dumps(incomplete_data)
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        minutes = parse_gemini_response(incomplete_json)
        sys.stdout = old_stdout
        self.assertIsNone(minutes)


    def test_format_minutes_to_text(self):
        minutes = MeetingMinutes(**self.sample_data)
        formatted_text = format_minutes_to_text(minutes)

        self.assertIn("# Meeting Minutes: Test Meeting", formatted_text)
        self.assertIn("**Date:** 2024-01-01", formatted_text)
        self.assertIn("**Time:** 10:00 AM", formatted_text)
        self.assertIn("**Attendees:** Attendee1, Attendee2", formatted_text)
        self.assertIn("## Summary", formatted_text)
        self.assertIn("Test summary.", formatted_text)
        self.assertIn("## Discussion Points", formatted_text)
        self.assertIn("- **Speaker1:** Point 1", formatted_text)
        self.assertIn("## Action Items", formatted_text)
        self.assertIn("- **Task:** Task 1 (Assigned to: Assignee1) [Deadline: 2024-12-31]", formatted_text)
        self.assertIn("- **Task:** Task 2", formatted_text) # Action item without assignee/deadline
        self.assertIn("## Decisions Made", formatted_text)
        self.assertIn("- Decision 1", formatted_text)
        self.assertIn("## Topics Discussed", formatted_text)
        self.assertIn("Topic1, Topic2", formatted_text)

    def test_format_minutes_to_text_minimal_data(self):
        minimal_data = {
            "summary": "Minimal summary.",
            "discussion_points": [],
            "action_items": [],
            "decisions": [],
            "topics": []
        }
        minutes = MeetingMinutes(**minimal_data)
        formatted_text = format_minutes_to_text(minutes)
        self.assertIn("# Meeting Minutes", formatted_text) # Default title
        self.assertIn("Minimal summary.", formatted_text)
        self.assertNotIn("## Discussion Points", formatted_text) # Should not appear if empty
        self.assertNotIn("## Action Items", formatted_text)
        self.assertNotIn("## Decisions Made", formatted_text)
        self.assertNotIn("## Topics Discussed", formatted_text)


    def test_main_function_simulated_run(self):
        # Test that main runs without error using the simulated Gemini response
        # This is a basic integration test.
        # We'll redirect stdout to check for output.
        captured_output = StringIO()
        sys.stdout = captured_output

        # Ensure GEMINI_API_KEY is not set for this test to force simulation
        original_api_key = os.environ.pop("GEMINI_API_KEY", None)

        try:
            main() # Run with default internal transcript and simulated API
            output = captured_output.getvalue()
            self.assertIn("Meeting Minutes Robot initialized.", output)
            self.assertIn("Warning: GEMINI_API_KEY environment variable not set. Using simulated Gemini response.", output)
            self.assertIn("--- Formatted Meeting Minutes (Text) ---", output)
            self.assertIn("Formatted minutes saved to meeting_minutes_output.txt", output)
            # Check if the output file was created
            self.assertTrue(os.path.exists("meeting_minutes_output.txt"))
            os.remove("meeting_minutes_output.txt") # Clean up
        finally:
            sys.stdout = sys.__stdout__ # Restore stdout
            if original_api_key is not None:
                os.environ["GEMINI_API_KEY"] = original_api_key


if __name__ == '__main__':
    unittest.main()
