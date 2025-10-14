#!/usr/bin/env python3
"""
Comprehensive CSV Analysis Script
Analyzes STAGE1_COMPLETE.csv structure, states, patterns
"""

import pandas as pd
import json
from collections import Counter, defaultdict

def analyze_csv(csv_path):
    """Comprehensive CSV analysis"""

    print("="*80)
    print("STAGE1_COMPLETE.CSV - COMPREHENSIVE ANALYSIS")
    print("="*80)
    print()

    # Load CSV
    df = pd.read_csv(csv_path)

    # Basic Info
    print("📊 BASIC INFORMATION")
    print("-"*80)
    print(f"Total States: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    print()

    # State Categories
    print("🏷️  STATE CATEGORIES")
    print("-"*80)

    # Categorize by State_ID prefix
    categories = defaultdict(list)
    for idx, row in df.iterrows():
        state_id = str(row['State_ID'])
        if '.' in state_id:
            prefix = state_id.split('.')[0]
            categories[f"Section {prefix}"].append(state_id)
        else:
            categories["Priority/Special"].append(state_id)

    for category, states in sorted(categories.items()):
        print(f"\n{category}: {len(states)} states")
        for state in states:
            state_name = df[df['State_ID'] == state]['State_Name'].values[0]
            print(f"  - {state}: {state_name}")

    print()

    # Intent Analysis
    print("🎯 CLIENT INTENT ANALYSIS")
    print("-"*80)
    intents = df['Client_Intent'].value_counts()
    print(f"Unique Intents: {len(intents)}")
    print("\nTop 10 Most Common Intents:")
    for intent, count in intents.head(10).items():
        print(f"  {intent}: {count} states")
    print()

    # Detection Checks
    print("🔍 DETECTION CHECKS ANALYSIS")
    print("-"*80)
    all_detections = []
    for detections in df['Detection_Checks'].dropna():
        all_detections.extend([d.strip() for d in str(detections).split(',')])

    detection_counts = Counter(all_detections)
    print(f"Unique Detection Types: {len(detection_counts)}")
    print("\nMost Common Detections:")
    for detection, count in detection_counts.most_common(10):
        print(f"  {detection}: {count} occurrences")
    print()

    # Actions Analysis
    print("⚙️  THERAPIST ACTION ANALYSIS")
    print("-"*80)
    actions = df['Therapist_Action'].value_counts()
    print(f"Unique Actions: {len(actions)}")
    print("\nMost Common Actions:")
    for action, count in actions.head(10).items():
        print(f"  {action}: {count} states")
    print()

    # RAG Query Analysis
    print("📚 RAG QUERY ANALYSIS")
    print("-"*80)
    rag_queries = df['RAG_Query'].dropna().value_counts()
    print(f"Total RAG Queries: {len(rag_queries)}")
    print(f"States with RAG: {df['RAG_Query'].notna().sum()}/{len(df)}")
    print(f"States without RAG (using fallback only): {df['RAG_Query'].isna().sum()}")

    print("\nRAG Query Tags:")
    for query in sorted(df['RAG_Query'].dropna().unique()):
        count = (df['RAG_Query'] == query).sum()
        print(f"  {query}: {count} states")
    print()

    # Framework Trigger Analysis
    print("⚡ FRAMEWORK TRIGGER ANALYSIS")
    print("-"*80)
    frameworks = df['Framework_Trigger'].dropna()
    print(f"States with Framework Triggers: {len(frameworks)}/{len(df)}")

    print("\nFramework Types:")
    framework_types = defaultdict(list)
    for idx, row in df[df['Framework_Trigger'].notna()].iterrows():
        trigger = str(row['Framework_Trigger'])
        state_id = row['State_ID']
        state_name = row['State_Name']

        if 'alpha_sequence' in trigger:
            framework_types['alpha_sequence'].append((state_id, state_name))
        elif 'no_harm' in trigger:
            framework_types['no_harm'].append((state_id, state_name))
        elif 'card_game' in trigger:
            framework_types['card_game'].append((state_id, state_name))
        elif 'metaphors' in trigger:
            framework_types['metaphors'].append((state_id, state_name))
        else:
            framework_types['other'].append((state_id, state_name))

    for framework, states in framework_types.items():
        print(f"\n  {framework.upper()}:")
        for state_id, state_name in states:
            print(f"    - {state_id} ({state_name})")
    print()

    # State Routing Analysis
    print("🔀 STATE ROUTING ANALYSIS")
    print("-"*80)

    # Count states with conditional routing
    has_if = df['Next_State_If'].notna().sum()
    has_else = df['Next_State_Else'].notna().sum()
    both = ((df['Next_State_If'].notna()) & (df['Next_State_Else'].notna())).sum()

    print(f"States with 'Next_State_If': {has_if}")
    print(f"States with 'Next_State_Else': {has_else}")
    print(f"States with both (conditional routing): {both}")
    print(f"States with neither (terminal/framework): {len(df) - max(has_if, has_else)}")
    print()

    # Priority/Special States
    print("🚨 PRIORITY & SPECIAL STATES")
    print("-"*80)
    priority_states = df[~df['State_ID'].astype(str).str.contains(r'^\d+\.')]
    print(f"Non-numbered (Priority/Special) States: {len(priority_states)}")

    for idx, row in priority_states.iterrows():
        print(f"\n  {row['State_ID']}: {row['State_Name']}")
        print(f"    Intent: {row['Client_Intent']}")
        print(f"    Action: {row['Therapist_Action']}")
        if pd.notna(row['Framework_Trigger']):
            print(f"    Framework: {row['Framework_Trigger']}")
    print()

    # Implementation Notes Analysis
    print("📝 IMPLEMENTATION NOTES SUMMARY")
    print("-"*80)
    notes_with_max = df[df['Implementation_Notes'].str.contains('MAX|max', case=False, na=False)]
    notes_with_trigger = df[df['Implementation_Notes'].str.contains('TRIGGER|trigger', case=False, na=False)]
    notes_with_priority = df[df['Implementation_Notes'].str.contains('PRIORITY|priority', case=False, na=False)]

    print(f"States with MAX attempts mentioned: {len(notes_with_max)}")
    print(f"States with TRIGGER mentioned: {len(notes_with_trigger)}")
    print(f"States with PRIORITY mentioned: {len(notes_with_priority)}")
    print()

    # State Flow Sequence
    print("📈 MAIN STATE FLOW SEQUENCE")
    print("-"*80)
    numbered_states = df[df['State_ID'].astype(str).str.match(r'^\d+\.')]
    print("Sequential Flow (Section order):")
    for idx, row in numbered_states.iterrows():
        state_id = row['State_ID']
        state_name = row['State_Name']
        next_if = row['Next_State_If']
        print(f"  {state_id} {state_name}")
        if pd.notna(next_if):
            print(f"    → {next_if}")
    print()

    # Problem Detection
    print("⚠️  POTENTIAL ISSUES & RECOMMENDATIONS")
    print("-"*80)

    issues = []

    # Check for states without fallback
    no_fallback = df[df['Fallback_Response'].isna()]
    if len(no_fallback) > 0:
        issues.append(f"⚠️  {len(no_fallback)} states without fallback response")
        for idx, row in no_fallback.iterrows():
            issues.append(f"    - {row['State_ID']}: {row['State_Name']}")

    # Check for states without RAG and without fallback
    no_rag_no_fallback = df[(df['RAG_Query'].isna()) & (df['Fallback_Response'].isna())]
    if len(no_rag_no_fallback) > 0:
        issues.append(f"⚠️  {len(no_rag_no_fallback)} states with NEITHER RAG nor fallback!")

    # Check for duplicate State_IDs
    duplicates = df['State_ID'].value_counts()
    duplicates = duplicates[duplicates > 1]
    if len(duplicates) > 0:
        issues.append(f"⚠️  {len(duplicates)} duplicate State_IDs found!")

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
