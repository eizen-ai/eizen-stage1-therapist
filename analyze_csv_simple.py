#!/usr/bin/env python3
"""
Comprehensive CSV Analysis Script (No Pandas)
Analyzes STAGE1_COMPLETE.csv structure, states, patterns
"""

import csv
from collections import Counter, defaultdict

def analyze_csv(csv_path):
    """Comprehensive CSV analysis"""

    print("="*80)
    print("STAGE1_COMPLETE.CSV - COMPREHENSIVE ANALYSIS")
    print("="*80)
    print()

    # Load CSV
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Basic Info
    print("📊 BASIC INFORMATION")
    print("-"*80)
    print(f"Total States: {len(rows)}")
    print(f"Total Columns: {len(rows[0].keys() if rows else 0)}")
    print(f"Columns: {', '.join(rows[0].keys() if rows else [])}")
    print()

    # State Categories
    print("🏷️  STATE CATEGORIES")
    print("-"*80)

    categories = defaultdict(list)
    for row in rows:
        state_id = row['State_ID']
        if '.' in state_id:
            prefix = state_id.split('.')[0]
            categories[f"Section {prefix}"].append(state_id)
        else:
            categories["Priority/Special"].append(state_id)

    for category, states in sorted(categories.items()):
        print(f"\n{category}: {len(states)} states")
        for state in states:
            state_name = [r['State_Name'] for r in rows if r['State_ID'] == state][0]
            print(f"  - {state}: {state_name}")

    print()

    # Intent Analysis
    print("🎯 CLIENT INTENT ANALYSIS")
    print("-"*80)
    intents = Counter([r['Client_Intent'] for r in rows])
    print(f"Unique Intents: {len(intents)}")
    print("\nAll Client Intents:")
    for intent, count in intents.most_common():
        print(f"  {intent}: {count} state(s)")
    print()

    # Detection Checks
    print("🔍 DETECTION CHECKS ANALYSIS")
    print("-"*80)
    all_detections = []
    for row in rows:
        detections = row.get('Detection_Checks', '')
        if detections and detections.strip():
            all_detections.extend([d.strip() for d in detections.split(',')])

    detection_counts = Counter(all_detections)
    print(f"Unique Detection Types: {len(detection_counts)}")
    print("\nAll Detection Types:")
    for detection, count in detection_counts.most_common():
        print(f"  {detection}: {count} occurrences")
    print()

    # Actions Analysis
    print("⚙️  THERAPIST ACTION ANALYSIS")
    print("-"*80)
    actions = Counter([r['Therapist_Action'] for r in rows])
    print(f"Unique Actions: {len(actions)}")
    print("\nAll Therapist Actions:")
    for action, count in actions.most_common():
        print(f"  {action}: {count} state(s)")
    print()

    # RAG Query Analysis
    print("📚 RAG QUERY ANALYSIS")
    print("-"*80)
    rag_queries = [r['RAG_Query'] for r in rows if r.get('RAG_Query') and r['RAG_Query'].strip() and r['RAG_Query'] != 'none']
    print(f"Unique RAG Queries: {len(set(rag_queries))}")
    print(f"States with RAG: {len(rag_queries)}/{len(rows)}")
    print(f"States without RAG: {len(rows) - len(rag_queries)}")

    print("\nRAG Query Tags:")
    for query in sorted(set(rag_queries)):
        count = rag_queries.count(query)
        print(f"  {query}: {count} state(s)")
    print()

    # Framework Trigger Analysis
    print("⚡ FRAMEWORK TRIGGER ANALYSIS")
    print("-"*80)
    frameworks = [(r['State_ID'], r['State_Name'], r['Framework_Trigger']) for r in rows if r.get('Framework_Trigger') and r['Framework_Trigger'].strip() and r['Framework_Trigger'] != 'none']
    print(f"States with Framework Triggers: {len(frameworks)}/{len(rows)}")

    print("\nFramework Triggers:")
    framework_types = defaultdict(list)
    for state_id, state_name, trigger in frameworks:
        if 'alpha_sequence' in trigger.lower():
            framework_types['alpha_sequence'].append((state_id, state_name, trigger))
        elif 'no_harm' in trigger.lower():
            framework_types['no_harm'].append((state_id, state_name, trigger))
        elif 'card_game' in trigger.lower():
            framework_types['card_game'].append((state_id, state_name, trigger))
        elif 'metaphors' in trigger.lower():
            framework_types['metaphors'].append((state_id, state_name, trigger))
        else:
            framework_types['other'].append((state_id, state_name, trigger))

    for framework, states in framework_types.items():
        print(f"\n  {framework.upper()}:")
        for state_id, state_name, trigger in states:
            print(f"    - {state_id} ({state_name})")
            print(f"      Trigger: {trigger}")
    print()

    # State Routing Analysis
    print("🔀 STATE ROUTING ANALYSIS")
    print("-"*80)

    has_if = len([r for r in rows if r.get('Next_State_If') and r['Next_State_If'].strip()])
    has_else = len([r for r in rows if r.get('Next_State_Else') and r['Next_State_Else'].strip()])
    both = len([r for r in rows if r.get('Next_State_If') and r['Next_State_If'].strip() and r.get('Next_State_Else') and r['Next_State_Else'].strip()])

    print(f"States with 'Next_State_If': {has_if}")
    print(f"States with 'Next_State_Else': {has_else}")
    print(f"States with both (conditional routing): {both}")
    print(f"States with neither (terminal/framework): {len(rows) - max(has_if, has_else)}")
    print()

    # Priority/Special States
    print("🚨 PRIORITY & SPECIAL STATES")
    print("-"*80)
    priority_states = [r for r in rows if not any(c.isdigit() for c in r['State_ID'].split('.')[0])]
    print(f"Non-numbered (Priority/Special) States: {len(priority_states)}")

    for row in priority_states:
        print(f"\n  {row['State_ID']}: {row['State_Name']}")
        print(f"    Intent: {row['Client_Intent']}")
        print(f"    Action: {row['Therapist_Action']}")
        if row.get('Framework_Trigger') and row['Framework_Trigger'].strip() and row['Framework_Trigger'] != 'none':
            print(f"    Framework: {row['Framework_Trigger']}")
    print()

    # Implementation Notes Analysis
    print("📝 IMPLEMENTATION NOTES SUMMARY")
    print("-"*80)
    notes_with_max = [r for r in rows if 'MAX' in r.get('Implementation_Notes', '').upper() or 'max' in r.get('Implementation_Notes', '').lower()]
    notes_with_trigger = [r for r in rows if 'TRIGGER' in r.get('Implementation_Notes', '').upper()]
    notes_with_priority = [r for r in rows if 'PRIORITY' in r.get('Implementation_Notes', '').upper()]

    print(f"States with MAX attempts mentioned: {len(notes_with_max)}")
    for r in notes_with_max:
        print(f"  - {r['State_ID']}: {r['State_Name']}")

    print(f"\nStates with TRIGGER mentioned: {len(notes_with_trigger)}")
    print(f"States with PRIORITY mentioned: {len(notes_with_priority)}")
    for r in notes_with_priority:
        print(f"  - {r['State_ID']}: {r['State_Name']}")
    print()

    # State Flow Sequence
    print("📈 MAIN STATE FLOW SEQUENCE (Section 1-4)")
    print("-"*80)
    numbered_states = [r for r in rows if '.' in r['State_ID'] and r['State_ID'][0].isdigit()]
    for row in sorted(numbered_states, key=lambda x: (int(x['State_ID'].split('.')[0]), x['State_ID'])):
        state_id = row['State_ID']
        state_name = row['State_Name']
        next_if = row.get('Next_State_If', '')
        print(f"  {state_id} {state_name}")
        if next_if and next_if.strip():
            print(f"    → If: {next_if}")
    print()

    # Problem Detection
    print("⚠️  POTENTIAL ISSUES & RECOMMENDATIONS")
    print("-"*80)

    issues = []

    # Check for states without fallback
    no_fallback = [r for r in rows if not r.get('Fallback_Response') or not r['Fallback_Response'].strip() or r['Fallback_Response'] == 'none']
    if len(no_fallback) > 0:
        issues.append(f"⚠️  {len(no_fallback)} states without fallback response:")
        for r in no_fallback:
            issues.append(f"    - {r['State_ID']}: {r['State_Name']}")

    # Check for states without RAG and without fallback
    no_rag_no_fallback = [r for r in rows if
                          (not r.get('RAG_Query') or not r['RAG_Query'].strip() or r['RAG_Query'] == 'none') and
                          (not r.get('Fallback_Response') or not r['Fallback_Response'].strip() or r['Fallback_Response'] == 'none')]
    if len(no_rag_no_fallback) > 0:
        issues.append(f"\n⚠️  {len(no_rag_no_fallback)} states with NEITHER RAG nor fallback:")
        for r in no_rag_no_fallback:
            issues.append(f"    - {r['State_ID']}: {r['State_Name']}")

    # Check for duplicate State_IDs
    state_ids = [r['State_ID'] for r in rows]
    duplicates = [sid for sid in set(state_ids) if state_ids.count(sid) > 1]
    if len(duplicates) > 0:
        issues.append(f"\n⚠️  {len(duplicates)} duplicate State_IDs found: {', '.join(duplicates)}")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ No major issues detected!")

    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    csv_path = "docs/planning/rasa_system/STAGE1_COMPLETE.csv"
    analyze_csv(csv_path)
