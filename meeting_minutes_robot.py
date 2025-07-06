# Main script for the Meeting Minutes Robot

import google.generativeai as genai
import os
import json
from typing import List, Optional
from pydantic import BaseModel, validator

# --- Data Structures ---

class DiscussionPoint(BaseModel):
    speaker: str
    point: str

class ActionItem(BaseModel):
    assignee: Optional[str] = None
    task: str
    deadline: Optional[str] = None

class Decision(BaseModel):
    decision: str

class MeetingMinutes(BaseModel):
    summary: str
    discussion_points: List[DiscussionPoint]
    action_items: List[ActionItem]
    decisions: List[Decision]
    topics: List[str]
    # Optional fields
    meeting_title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[List[str]] = None

# --- Gemini Interaction and Parsing ---

# Configure the Gemini API key
# Note: The API key should be set as an environment variable for security.
# Example: export GEMINI_API_KEY="YOUR_API_KEY"
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def parse_gemini_response(response_text: str) -> Optional[MeetingMinutes]:
    """
    Parses the JSON response from Gemini API into MeetingMinutes object.
    """
    try:
        data = json.loads(response_text)
        return MeetingMinutes(**data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Gemini response: {e}")
        print(f"Response text was: {response_text}")
        return None
    except Exception as e: # Catches Pydantic validation errors too
        print(f"Error parsing Gemini response into MeetingMinutes: {e}")
        print(f"Response data was: {data if 'data' in locals() else 'N/A'}")
        return None

def process_with_gemini(transcript: str) -> Optional[MeetingMinutes]:
    """
    Sends the transcript to the Gemini API and returns the parsed MeetingMinutes object.
    This is a placeholder and needs to be adapted based on the actual API capabilities
    and desired output structure.
    """
    response_text = ""
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY environment variable not set. Using simulated Gemini response.")
        # Simulate a structured response for now
        response_text = """
        {
            "summary": "This is a brief summary of the meeting.",
            "discussion_points": [
                {"speaker": "Alice", "point": "Discussed Q1 sales figures."},
                {"speaker": "Bob", "point": "Proposed new marketing strategy."}
            ],
            "action_items": [
                {"assignee": "Charlie", "task": "Prepare Q1 sales report", "deadline": "2024-07-15"},
                {"assignee": "Alice", "task": "Research new marketing tools", "deadline": "2024-07-20"}
            ],
            "decisions": [
                {"decision": "Approved new marketing strategy."}
            ],
            "topics": ["Q1 Sales", "Marketing Strategy"]
        }
        """
    else:
        try:
            model = genai.GenerativeModel('gemini-pro') # Or another appropriate model
            # Construct a prompt that instructs the model to extract the desired information
            # This prompt will need significant refinement.
            prompt = f"""\
Analyze the following meeting transcript and extract the following information:
- A brief summary of the meeting.
- Key discussion points, including who said what.
- Action items, including the assignee, task, and deadline (if mentioned).
- Decisions made.
- Main topics discussed.

Format the output as a JSON object with the following keys: "summary", "discussion_points", "action_items", "decisions", "topics".
"discussion_points" should be a list of objects, each with "speaker" and "point".
"action_items" should be a list of objects, each with "assignee", "task", and "deadline".
"decisions" should be a list of objects, each with "decision".
"topics" should be a list of strings.

Transcript:
{transcript}
"""
            response = model.generate_content(prompt)
            response_text = response.text
        except Exception as e:
            print(f"Error interacting with Gemini API: {e}")
            # Fallback to simulated response in case of API error
            response_text = """
            {
                "summary": "Error processing transcript. This is a fallback summary.",
                "discussion_points": [],
                "action_items": [],
                "decisions": [],
                "topics": []
            }
            """
    return parse_gemini_response(response_text)

# --- Formatting ---

def format_minutes_to_text(minutes: MeetingMinutes) -> str:
    """
    Formats the MeetingMinutes object into a structured text string.
    """
    output = []

    if minutes.meeting_title:
        output.append(f"# Meeting Minutes: {minutes.meeting_title}")
    else:
        output.append("# Meeting Minutes")

    if minutes.date:
        output.append(f"**Date:** {minutes.date}")
    if minutes.time:
        output.append(f"**Time:** {minutes.time}")

    if minutes.attendees:
        output.append(f"**Attendees:** {', '.join(minutes.attendees)}")

    output.append("\n## Summary")
    output.append(minutes.summary)

    if minutes.discussion_points:
        output.append("\n## Discussion Points")
        for dp in minutes.discussion_points:
            output.append(f"- **{dp.speaker}:** {dp.point}")

    if minutes.action_items:
        output.append("\n## Action Items")
        for ai in minutes.action_items:
            item_str = f"- **Task:** {ai.task}"
            if ai.assignee:
                item_str += f" (Assigned to: {ai.assignee})"
            if ai.deadline:
                item_str += f" [Deadline: {ai.deadline}]"
            output.append(item_str)

    if minutes.decisions:
        output.append("\n## Decisions Made")
        for dec in minutes.decisions:
            output.append(f"- {dec.decision}")

    if minutes.topics:
        output.append("\n## Topics Discussed")
        output.append(", ".join(minutes.topics))

    return "\n".join(output)

def main(transcript_filepath: Optional[str] = None):
    print("Meeting Minutes Robot initialized.")

    transcript_content = ""
    if transcript_filepath:
        try:
            with open(transcript_filepath, 'r') as f:
                transcript_content = f.read()
            print(f"Successfully read transcript from {transcript_filepath}")
        except FileNotFoundError:
            print(f"Error: Transcript file not found at {transcript_filepath}")
            return
        except Exception as e:
            print(f"Error reading transcript file: {e}")
            return
    else:
        print("No transcript file provided, using default sample transcript.")
        # Using the detailed sample transcript from sample_transcript.txt
        transcript_content = """
Project Phoenix - Weekly Sync - 2024-07-10

Attendees: Alice (Project Manager), Bob (Lead Developer), Charlie (QA Engineer), David (UX Designer)

Alice: Alright team, let's kick off the weekly sync for Project Phoenix. Bob, can you start with the development updates?
Bob: Sure, Alice. This week, we completed the user authentication module. All core features are implemented and unit tests are passing. We also started work on the dashboard integration. I'd say we're about 30% done with that. We hit a small snag with a third-party library compatibility, but it's resolved now.
Alice: Great progress, Bob! Any blockers?
Bob: Not at the moment. We should be on track to complete the dashboard integration by the end of next week.
Alice: Excellent. Charlie, how are things on the QA front?
Charlie: Thanks, Alice. We've started drafting test cases for the authentication module based on the specs. We plan to begin exploratory testing tomorrow. I'll need Bob to deploy the latest build to the staging environment.
Bob: Will do, Charlie. I'll get that done by end of day today.
Alice: Perfect. David, any updates from UX?
David: Yes, I've finalized the mockups for the new reporting feature. I've shared them on the drive. I'd like to schedule a review session with everyone, perhaps early next week?
Alice: Sounds good, David. Please send out a calendar invite. I also want to remind everyone that the client demo is scheduled for July 25th. We need to ensure all critical features are stable by then.
Charlie: Understood. We'll prioritize testing for the demo features.
Bob: We'll focus on getting the dashboard and reporting basics solid for the demo.
Alice: Okay, any other business?
David: Just a quick one - I was thinking about user feedback post-launch. Should we plan for an in-app feedback mechanism?
Alice: That's a good point, David. Let's add it to the backlog for now and discuss it in more detail after the initial launch. For now, the priority is the upcoming demo. Any objections?
(Silence)
Alice: Alright. So, to recap the main action items: Bob to deploy auth module to staging EOD today. Charlie to start auth testing tomorrow. David to send invite for UX review. Everyone to keep the July 25th demo in mind.
Alice: Thanks, everyone. Let's have a productive week!
"""
    if not transcript_content.strip():
        print("Transcript content is empty. Exiting.")
        return

    print("\\nProcessing transcript...")
    meeting_minutes_data = process_with_gemini(transcript_content)

    if meeting_minutes_data:
        # Optionally pre-fill some metadata if not in Gemini response
        # For example, if the filename implies the date or title
        if not meeting_minutes_data.date and "2024-07-10" in transcript_content: # Basic check
            meeting_minutes_data.date = "2024-07-10"
        if not meeting_minutes_data.meeting_title and "Project Phoenix" in transcript_content:
            meeting_minutes_data.meeting_title = "Project Phoenix - Weekly Sync"
        if not meeting_minutes_data.attendees and "Attendees:" in transcript_content:
            try:
                attendees_line = next(line for line in transcript_content.splitlines() if "Attendees:" in line)
                attendees_str = attendees_line.split("Attendees:")[1].strip()
                meeting_minutes_data.attendees = [a.split('(')[0].strip() for a in attendees_str.split(',')]
            except StopIteration:
                pass # Attendees line not found or format is different

        print("\\n--- Raw Parsed Data (from Gemini or simulation) ---")
        print(meeting_minutes_data.model_dump_json(indent=2))

        print("\\n\\n--- Formatted Meeting Minutes (Text) ---")
        formatted_text = format_minutes_to_text(meeting_minutes_data)
        print(formatted_text)

        # Placeholder for exporting to other formats (e.g., PDF, structured data)
        # For now, we can save the text output to a file.
        output_filename = "meeting_minutes_output.txt"
        if transcript_filepath:
            base, ext = os.path.splitext(transcript_filepath)
            output_filename = f"{base}_minutes.txt"

        try:
            with open(output_filename, 'w') as f:
                f.write(formatted_text)
            print(f"\\nFormatted minutes saved to {output_filename}")
        except Exception as e:
            print(f"Error saving formatted minutes to file: {e}")

    else:
        print("Failed to process or parse meeting transcript.")

if __name__ == "__main__":
    # Example: Run with a specific transcript file
    # main("sample_transcript.txt")
    # Or run with the default internal transcript:
    main()
