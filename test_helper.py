#!/usr/bin/env python3
"""
Test Helper Script - Makes manual testing and feedback sharing easier
Usage: python test_helper.py [command]

Commands:
  start       - Start a test session (launches improved_ollama_system.py)
  analyze     - Analyze the most recent session log
  compare     - Compare last 2 sessions
  feedback    - Generate feedback template with log excerpts
  issues      - Extract potential issues from log
"""

import sys
import os
import json
import glob
from datetime import datetime

def get_latest_log():
    """Get the most recent session log file"""
    log_files = glob.glob("logs/improved_manual_*.json")
    if not log_files:
        return None
    return max(log_files, key=os.path.getmtime)

def get_last_n_logs(n=2):
    """Get the last N session log files"""
    log_files = glob.glob("logs/improved_manual_*.json")
    if not log_files:
        return []
    return sorted(log_files, key=os.path.getmtime, reverse=True)[:n]

def analyze_session(log_file):
    """Analyze a session log and extract key information"""
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)

        print("=" * 70)
        print(f"SESSION ANALYSIS: {os.path.basename(log_file)}")
        print("=" * 70)

        # Basic stats
        print(f"\n📊 BASIC STATS")
        print(f"   Session ID: {data.get('session_id', 'N/A')}")
        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"   Total Turns: {data.get('turns', 0)}")
        print(f"   Final State: {data.get('final_state', 'N/A')}")
        print(f"   Body Questions Asked: {data.get('body_questions_asked', 0)}/3")

        # Completion status
        completion = data.get('completion', {})
        completed = [k for k, v in completion.items() if v]
        print(f"\n✅ COMPLETION STATUS ({len(completed)}/11)")
        for key, value in completion.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}")

        # Conversation flow
        conversation = data.get('conversation', [])
        print(f"\n💬 CONVERSATION FLOW")

        # Track state transitions
        states_visited = []
        loops_detected = []

        for i, turn in enumerate(conversation, 1):
            substate = turn.get('navigation', {}).get('current_substate', 'unknown')
            decision = turn.get('navigation', {}).get('navigation_decision', 'unknown')

            if substate not in states_visited:
                states_visited.append(substate)

            # Detect potential loops (same decision 3+ times in a row)
            if i >= 3:
                last_3_decisions = [
                    conversation[i-3].get('navigation', {}).get('navigation_decision'),
                    conversation[i-2].get('navigation', {}).get('navigation_decision'),
                    turn.get('navigation', {}).get('navigation_decision')
                ]
                if len(set(last_3_decisions)) == 1 and last_3_decisions[0]:
                    if last_3_decisions[0] not in loops_detected:
                        loops_detected.append((i-2, last_3_decisions[0]))

            print(f"\n   Turn {i}: [{substate}]")
            print(f"   Client: \"{turn.get('client_input', '')}\"")
            print(f"   Decision: {decision}")
            print(f"   Therapist: \"{turn.get('therapist_response', '')[:80]}...\"")

        # States visited
        print(f"\n🗺️  STATES VISITED ({len(states_visited)} unique)")
        print(f"   {' → '.join(states_visited)}")

        # Issues detected
        print(f"\n⚠️  POTENTIAL ISSUES")

        issues_found = 0

        # Check for loops
        if loops_detected:
            issues_found += len(loops_detected)
            print(f"   🔴 LOOPS DETECTED: {len(loops_detected)}")
            for turn_num, decision in loops_detected:
                print(f"      - Turn {turn_num}: '{decision}' repeated 3+ times")

        # Check if completed Stage 1
        if data.get('final_state') != '4.1':
            issues_found += 1
            print(f"   🟡 DID NOT COMPLETE STAGE 1 (stopped at {data.get('final_state')})")

        # Check body question counter
        if data.get('body_questions_asked', 0) == 0 and len(conversation) > 5:
            issues_found += 1
            print(f"   🟡 BODY QUESTION COUNTER NOT INCREMENTING (stayed at 0)")

        # Check for very long sessions (might indicate stuck)
        if data.get('turns', 0) > 40:
            issues_found += 1
            print(f"   🟡 VERY LONG SESSION ({data.get('turns')} turns) - Possible stuck behavior")

        if issues_found == 0:
            print(f"   ✅ No obvious issues detected")

        print(f"\n{'=' * 70}")

        return data

    except FileNotFoundError:
        print(f"❌ Error: Log file not found: {log_file}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in log file: {log_file}")
        return None
    except Exception as e:
        print(f"❌ Error analyzing log: {e}")
        return None

def generate_feedback_template(log_file):
    """Generate a feedback template with log excerpts"""
    data = analyze_session(log_file)
    if not data:
        return

    print("\n" + "=" * 70)
    print("FEEDBACK TEMPLATE (Copy and share this with developer)")
    print("=" * 70)
    print(f"""
## TEST SESSION FEEDBACK

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Log File:** {os.path.basename(log_file)}
**Session Duration:** {data.get('turns', 0)} turns
**Final State:** {data.get('final_state', 'N/A')}
**Completed Stage 1:** {'YES' if data.get('final_state') == '4.1' else 'NO'}

---

### Overall Experience
[Rate 1-5]: _____

**What felt good:**
- [Fill in]

**What felt off:**
- [Fill in]

---

### Issues Found

#### ISSUE #1: [Title]
**Priority:** [CRITICAL / MEDIUM / MINOR]
**Turn Number:** [X]
**Current State:** [{data.get('final_state', 'X.X')}]

**What Happened:**
Client: "[paste from log]"
Therapist: "[paste from log]"

**What Should Happen:**
[Expected behavior]

**Suggested Fix:**
[If you have ideas]

---

### Positive Observations
- [What worked well]

---

### Session Log Excerpts

**First 3 Turns:**
""")

    # Print first 3 turns
    conversation = data.get('conversation', [])
    for i, turn in enumerate(conversation[:3], 1):
        print(f"Turn {i}:")
        print(f"  Client: \"{turn.get('client_input', '')}\"")
        print(f"  Therapist: \"{turn.get('therapist_response', '')}\"")
        print(f"  State: {turn.get('navigation', {}).get('current_substate', 'unknown')}")
        print()

    if len(conversation) > 3:
        print("**Last 3 Turns:**")
        for i, turn in enumerate(conversation[-3:], len(conversation)-2):
            print(f"Turn {i}:")
            print(f"  Client: \"{turn.get('client_input', '')}\"")
            print(f"  Therapist: \"{turn.get('therapist_response', '')}\"")
            print(f"  State: {turn.get('navigation', {}).get('current_substate', 'unknown')}")
            print()

    print(f"""
**Full Log:** See {os.path.basename(log_file)}

---

**Ready to share?** Copy this template and send to developer!
""")

def compare_sessions(log_files):
    """Compare two session logs"""
    if len(log_files) < 2:
        print("❌ Need at least 2 session logs to compare")
        return

    print("=" * 70)
    print("SESSION COMPARISON")
    print("=" * 70)

    sessions = []
    for log_file in log_files[:2]:
        try:
            with open(log_file, 'r') as f:
                sessions.append((os.path.basename(log_file), json.load(f)))
        except Exception as e:
            print(f"❌ Error reading {log_file}: {e}")
            return

    print(f"\n📊 COMPARING:")
    print(f"   Session 1: {sessions[0][0]}")
    print(f"   Session 2: {sessions[1][0]}")

    # Compare basic stats
    print(f"\n📈 BASIC STATS")
    print(f"{'Metric':<30} {'Session 1':<15} {'Session 2':<15} {'Change':<15}")
    print("-" * 75)

    turns_1 = sessions[0][1].get('turns', 0)
    turns_2 = sessions[1][1].get('turns', 0)
    turns_change = turns_2 - turns_1
    print(f"{'Total Turns':<30} {turns_1:<15} {turns_2:<15} {turns_change:+d}")

    body_q_1 = sessions[0][1].get('body_questions_asked', 0)
    body_q_2 = sessions[1][1].get('body_questions_asked', 0)
    body_q_change = body_q_2 - body_q_1
    print(f"{'Body Questions Asked':<30} {body_q_1:<15} {body_q_2:<15} {body_q_change:+d}")

    state_1 = sessions[0][1].get('final_state', 'N/A')
    state_2 = sessions[1][1].get('final_state', 'N/A')
    print(f"{'Final State':<30} {state_1:<15} {state_2:<15}")

    completed_1 = sum(1 for v in sessions[0][1].get('completion', {}).values() if v)
    completed_2 = sum(1 for v in sessions[1][1].get('completion', {}).values() if v)
    completed_change = completed_2 - completed_1
    print(f"{'Completion Criteria':<30} {completed_1}/11{'':<10} {completed_2}/11{'':<10} {completed_change:+d}")

    # Compare states visited
    conv_1 = sessions[0][1].get('conversation', [])
    conv_2 = sessions[1][1].get('conversation', [])

    states_1 = [turn.get('navigation', {}).get('current_substate') for turn in conv_1]
    states_2 = [turn.get('navigation', {}).get('current_substate') for turn in conv_2]

    unique_states_1 = len(set(states_1))
    unique_states_2 = len(set(states_2))

    print(f"{'Unique States Visited':<30} {unique_states_1:<15} {unique_states_2:<15} {unique_states_2 - unique_states_1:+d}")

    print("\n✅ Comparison complete!")

def extract_issues(log_file):
    """Extract and highlight potential issues from log"""
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading log: {e}")
        return

    print("=" * 70)
    print("POTENTIAL ISSUES EXTRACTOR")
    print("=" * 70)

    conversation = data.get('conversation', [])

    issues = []

    # Check for loops
    for i in range(3, len(conversation)):
        last_3_decisions = [
            conversation[i-3].get('navigation', {}).get('navigation_decision'),
            conversation[i-2].get('navigation', {}).get('navigation_decision'),
            conversation[i-1].get('navigation', {}).get('navigation_decision')
        ]
        if len(set(last_3_decisions)) == 1 and last_3_decisions[0]:
            issues.append({
                'type': 'LOOP',
                'priority': 'CRITICAL',
                'turn': i-2,
                'description': f"Decision '{last_3_decisions[0]}' repeated 3+ times",
                'state': conversation[i-2].get('navigation', {}).get('current_substate')
            })

    # Check for stuck in same state
    for i in range(5, len(conversation)):
        last_5_states = [
            conversation[i-j].get('navigation', {}).get('current_substate')
            for j in range(5)
        ]
        if len(set(last_5_states)) == 1:
            issues.append({
                'type': 'STUCK',
                'priority': 'CRITICAL',
                'turn': i-4,
                'description': f"Stuck in state '{last_5_states[0]}' for 5+ turns",
                'state': last_5_states[0]
            })

    # Check for body counter not incrementing
    if data.get('body_questions_asked', 0) == 0 and len(conversation) > 8:
        # Check if any body-related decisions were made
        body_decisions = [
            turn.get('navigation', {}).get('navigation_decision')
            for turn in conversation
            if 'body' in turn.get('navigation', {}).get('navigation_decision', '').lower()
        ]
        if body_decisions:
            issues.append({
                'type': 'COUNTER',
                'priority': 'MEDIUM',
                'turn': 'N/A',
                'description': 'Body question counter stayed at 0 despite body-related decisions',
                'state': 'N/A'
            })

    # Print issues
    if not issues:
        print("\n✅ No obvious issues detected!")
        print("\n   The session appears to have run smoothly.")
        print("   If you still noticed problems, describe them manually.")
    else:
        print(f"\n⚠️  FOUND {len(issues)} POTENTIAL ISSUE(S):\n")

        for i, issue in enumerate(issues, 1):
            print(f"ISSUE #{i}: {issue['type']}")
            print(f"   Priority: {issue['priority']}")
            print(f"   Turn: {issue['turn']}")
            print(f"   State: {issue['state']}")
            print(f"   Description: {issue['description']}")

            # Show relevant conversation excerpt
            if issue['turn'] != 'N/A':
                turn_idx = issue['turn'] - 1
                if 0 <= turn_idx < len(conversation):
                    turn = conversation[turn_idx]
                    print(f"\n   Excerpt:")
                    print(f"   Client: \"{turn.get('client_input', '')}\"")
                    print(f"   Therapist: \"{turn.get('therapist_response', '')[:80]}...\"")
            print()

    print("=" * 70)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'start':
        print("🚀 Starting test session...")
        print("=" * 70)
        os.system("cd src/core && python improved_ollama_system.py")

    elif command == 'analyze':
        latest = get_latest_log()
        if not latest:
            print("❌ No session logs found in logs/ directory")
            print("   Run a test session first with: python test_helper.py start")
        else:
            analyze_session(latest)

    elif command == 'compare':
        logs = get_last_n_logs(2)
        if len(logs) < 2:
            print("❌ Need at least 2 session logs to compare")
            print(f"   Found {len(logs)} log(s)")
        else:
            compare_sessions(logs)

    elif command == 'feedback':
        latest = get_latest_log()
        if not latest:
            print("❌ No session logs found")
        else:
            generate_feedback_template(latest)

    elif command == 'issues':
        latest = get_latest_log()
        if not latest:
            print("❌ No session logs found")
        else:
            extract_issues(latest)

    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
