"""
Example API Client for TRT AI Therapist
Demonstrates complete therapy session via REST API
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8090"


def print_separator():
    """Print visual separator"""
    print("\n" + "=" * 70 + "\n")


def health_check():
    """Check API health"""
    print("🏥 Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        health = response.json()

        if health["status"] == "healthy":
            print("✅ API is healthy")
            print(f"   Ollama: {health['services']['ollama']}")
            print(f"   RAG: {health['services']['rag']}")
            print(f"   State Machine: {health['services']['state_machine']}")
            return True
        else:
            print(f"⚠️ API status: {health['status']}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Run: ./startup.sh or docker-compose up")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def create_session(client_id="test_client"):
    """Create new therapy session"""
    print(f"📝 Creating session for client: {client_id}")

    response = requests.post(
        f"{BASE_URL}/api/v1/session/create",
        json={
            "client_id": client_id,
            "metadata": {
                "platform": "python_example",
                "version": "1.0"
            }
        }
    )

    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Session created: {session_id}")
        print(f"   Status: {session_data['status']}")
        print(f"   Created at: {session_data['created_at']}")
        return session_id
    else:
        print(f"❌ Failed to create session: {response.text}")
        return None


def send_input(session_id, user_input, turn_number):
    """Send client input and get therapist response"""
    print(f"\n🔄 Turn {turn_number}")
    print(f"👤 Client: {user_input}")

    response = requests.post(
        f"{BASE_URL}/api/v1/session/{session_id}/input",
        json={"user_input": user_input}
    )

    if response.status_code == 200:
        result = response.json()

        # Print therapist response
        print(f"🩺 Therapist: {result['therapist_response']}")

        # Print metadata
        print(f"\n   📊 Metadata:")
        print(f"      State: {result['session_progress']['current_substate']}")
        print(f"      Body Questions: {result['session_progress']['body_question_count']}/3")
        print(f"      Emotion: {result['preprocessing']['emotional_state']['primary_emotion']}")
        print(f"      Input Category: {result['preprocessing']['input_category']}")

        # Check for safety flags
        safety = result['preprocessing']['safety_checks']
        if safety['self_harm_detected']['detected']:
            print(f"      ⚠️ SAFETY: Self-harm detected!")
        if safety['past_tense_detected']['detected']:
            print(f"      ⏮️ Past tense detected: {safety['past_tense_detected']['phrases_found']}")
        if safety['thinking_mode_detected']['detected']:
            print(f"      💭 Thinking mode detected")

        # Show completion progress
        completed = sum(result['session_progress']['completion_criteria'].values())
        total = len(result['session_progress']['completion_criteria'])
        print(f"      Progress: {completed}/{total} criteria completed")

        return result
    else:
        print(f"❌ Failed to send input: {response.text}")
        return None


def get_session_status(session_id):
    """Get current session status"""
    print(f"\n📊 Getting session status...")

    response = requests.get(f"{BASE_URL}/api/v1/session/{session_id}/status")

    if response.status_code == 200:
        status = response.json()

        print(f"   Session ID: {status['session_id']}")
        print(f"   Status: {status['status']}")
        print(f"   Current State: {status['current_substate']}")
        print(f"   Turn Count: {status['turn_count']}")
        print(f"   Body Questions: {status['body_question_count']}/3")

        # Show completion criteria
        print(f"\n   ✅ Completion Criteria:")
        for criteria, completed in status['completion_criteria'].items():
            icon = "✅" if completed else "⏳"
            print(f"      {icon} {criteria}")

        return status
    else:
        print(f"❌ Failed to get status: {response.text}")
        return None


def delete_session(session_id):
    """Delete session"""
    print(f"\n🗑️ Deleting session...")

    response = requests.delete(f"{BASE_URL}/api/v1/session/{session_id}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        return True
    else:
        print(f"❌ Failed to delete session: {response.text}")
        return False


def run_therapy_session():
    """Run a complete therapy session"""
    print_separator()
    print("🧠 TRT AI Therapist - API Test Session")
    print_separator()

    # Health check
    if not health_check():
        return

    print_separator()

    # Create session
    session_id = create_session(client_id="example_client")
    if not session_id:
        return

    print_separator()

    # Conversation flow (typical Stage 1 session)
    conversation = [
        "I'm feeling really stressed and overwhelmed",  # Turn 1: Problem statement
        "I want to feel calm and peaceful",             # Turn 2: Goal clarification
        "Yes, that makes sense",                        # Turn 3: Affirmation
        "I feel it in my chest",                        # Turn 4: Body location
        "It's tight and heavy",                         # Turn 5: Body sensation
        "Right now",                                    # Turn 6: Present moment
        "Nothing more from my side",                    # Turn 7: Readiness assessment
        "Yes, I'm ready"                                # Turn 8: Permission for alpha
    ]

    # Process conversation
    results = []
    for i, user_input in enumerate(conversation, 1):
        result = send_input(session_id, user_input, i)
        if result:
            results.append(result)
        time.sleep(1)  # Small delay between turns

    print_separator()

    # Get final status
    final_status = get_session_status(session_id)

    print_separator()

    # Summary
    if final_status:
        completed = sum(final_status['completion_criteria'].values())
        total = len(final_status['completion_criteria'])

        print("📈 SESSION SUMMARY")
        print(f"   Total Turns: {final_status['turn_count']}")
        print(f"   Final State: {final_status['current_substate']}")
        print(f"   Completion: {completed}/{total} criteria ({completed/total*100:.1f}%)")

        if final_status['status'] == 'completed':
            print("\n   🎉 Stage 1 Complete! Ready for Stage 2.")
        else:
            print(f"\n   ⏳ Session Status: {final_status['status']}")

    print_separator()

    # Cleanup
    delete_session(session_id)

    print_separator()
    print("✅ Test session complete!")
    print_separator()


if __name__ == "__main__":
    try:
        run_therapy_session()
    except KeyboardInterrupt:
        print("\n\n⚠️ Session interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
