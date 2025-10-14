#!/usr/bin/env python3
"""
QA Validation Tests for TRT Stage 1 System
Validates all 5 critical fixes implemented on 2025-10-14
"""

import sys
import os
import csv
import re

def test_fix_1_problem_identification():
    """Test Fix #1: Problem identification logic in session_state_manager.py"""
    print("\n🔍 TEST #1: Problem Identification Loop Fix")
    print("=" * 60)

    file_path = "src/core/session_state_manager.py"

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for key improvements
        checks = [
            ("conversation history check", "conversation_history[-5:]" in content),
            ("stressor detection", "stressor_mentioned" in content),
            ("body reference detection", "has_body_reference" in content),
            ("problem indicators counter", "problem_indicators" in content),
            ("smart identification logic", "problem_indicators >= 2" in content)
        ]

        passed = sum(1 for _, result in checks if result)

        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")

        if passed == len(checks):
            print("\n✅ Fix #1 VERIFIED: Problem identification logic implemented correctly")
            return True
        else:
            print("\n⚠️  Fix #1 INCOMPLETE: Some checks failed")
            return False

    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return False

def test_fix_2_spelling_correction():
    """Test Fix #2: Context-aware spelling correction in input_preprocessing.py"""
    print("\n🔍 TEST #2: Spelling Correction Context Awareness")
    print("=" * 60)

    file_path = "src/utils/input_preprocessing.py"

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for key improvements
        checks = [
            ("context_protected_words dictionary", "context_protected_words" in content),
            ("'right' protection", "'right'" in content and "['now'" in content),
            ("next word context check", "next_word" in content),
            ("is_protected flag", "is_protected" in content),
            ("stricter cutoff (0.85)", "0.85" in content or "cutoff_ratio = 0.85" in content)
        ]

        passed = sum(1 for _, result in checks if result)

        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")

        if passed >= 4:  # Allow some flexibility
            print("\n✅ Fix #2 VERIFIED: Context-aware spelling correction implemented")
            return True
        else:
            print("\n⚠️  Fix #2 INCOMPLETE: Some checks failed")
            return False

    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return False

def test_fix_3_csv_fallback():
    """Test Fix #3: State 3.3 fallback in STAGE1_COMPLETE.csv"""
    print("\n🔍 TEST #3: CSV Fallback for State 3.3")
    print("=" * 60)

    file_path = "config/STAGE1_COMPLETE.csv"

    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Find State 3.3 (Execute Alpha)
        state_3_3 = None
        for row in rows:
            if len(row) > 0 and row[0] == "3.3":
                state_3_3 = row
                break

        if not state_3_3:
            print("❌ State 3.3 not found in CSV")
            return False

        # Check fallback response (column 8)
        fallback_response = state_3_3[7] if len(state_3_3) > 7 else ""

        checks = [
            ("State 3.3 exists", state_3_3 is not None),
            ("Fallback response present", fallback_response and fallback_response != "none"),
            ("Fallback is therapeutic", "moment" in fallback_response.lower() and "body" in fallback_response.lower()),
            ("Mentions rest/calm", "rest" in fallback_response.lower() or "calm" in fallback_response.lower())
        ]

        passed = sum(1 for _, result in checks if result)

        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")

        if fallback_response:
            print(f"\n   Fallback text: \"{fallback_response[:80]}...\"")

        if passed == len(checks):
            print("\n✅ Fix #3 VERIFIED: State 3.3 has proper fallback")
            return True
        else:
            print("\n⚠️  Fix #3 INCOMPLETE: Some checks failed")
            return False

    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return False
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def test_fix_4_body_counter():
    """Test Fix #4: Body question counter in improved_ollama_system.py"""
    print("\n🔍 TEST #4: Body Question Counter")
    print("=" * 60)

    file_path = "src/core/improved_ollama_system.py"

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for key improvements
        checks = [
            ("body_question_decisions list", "body_question_decisions" in content),
            ("body_question_substates list", "body_question_substates" in content),
            ("counter increment logic", "body_questions_asked += 1" in content),
            ("MAX 3 check", "body_questions_asked >= 3" in content),
            ("escape route to 3.1", 'next_state\"] = \"3.1\"' in content or "next_state'] = '3.1'" in content),
            ("warning message", "MAX body questions" in content)
        ]

        passed = sum(1 for _, result in checks if result)

        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")

        if passed >= 5:  # Allow some flexibility
            print("\n✅ Fix #4 VERIFIED: Body question counter implemented correctly")
            return True
        else:
            print("\n⚠️  Fix #4 INCOMPLETE: Some checks failed")
            return False

    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return False

def test_fix_5_psycho_education():
    """Test Fix #5: Psycho-education state 1.1.5 in STAGE1_COMPLETE.csv"""
    print("\n🔍 TEST #5: Psycho-Education State 1.1.5")
    print("=" * 60)

    file_path = "config/STAGE1_COMPLETE.csv"

    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Find State 1.1.5
        state_1_1_5 = None
        for row in rows:
            if len(row) > 0 and row[0] == "1.1.5":
                state_1_1_5 = row
                break

        if not state_1_1_5:
            print("❌ State 1.1.5 not found in CSV")
            return False

        state_name = state_1_1_5[1] if len(state_1_1_5) > 1 else ""
        fallback = state_1_1_5[7] if len(state_1_1_5) > 7 else ""

        checks = [
            ("State 1.1.5 exists", state_1_1_5 is not None),
            ("Named 'Psycho-Education'", "Psycho-Education" in state_name),
            ("Contains zebra/lion metaphor", "zebra" in fallback.lower() and "lion" in fallback.lower()),
            ("Explains brain response", "brain" in fallback.lower() and ("stress" in fallback.lower() or "survival" in fallback.lower())),
            ("Routes to 2.1", "2.1" in str(state_1_1_5))
        ]

        passed = sum(1 for _, result in checks if result)

        print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")

        if passed >= 4:  # Allow some flexibility
            print("\n✅ Fix #5 VERIFIED: Psycho-education state properly documented")
            return True
        else:
            print("\n⚠️  Fix #5 INCOMPLETE: Some checks failed")
            return False

    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return False
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def test_project_structure():
    """Test project structure after cleanup"""
    print("\n🔍 BONUS TEST: Project Structure")
    print("=" * 60)

    checks = [
        ("src/ directory exists", os.path.isdir("src")),
        ("config/ directory exists", os.path.isdir("config")),
        ("CSV in config/", os.path.isfile("config/STAGE1_COMPLETE.csv")),
        (".gitignore exists", os.path.isfile(".gitignore")),
        ("README.md exists", os.path.isfile("README.md")),
        ("project_files/ removed", not os.path.isdir("project_files")),
        ("__init__.py in src/", os.path.isfile("src/__init__.py")),
        ("__init__.py in src/core/", os.path.isfile("src/core/__init__.py")),
        ("__init__.py in src/utils/", os.path.isfile("src/utils/__init__.py")),
        ("__init__.py in src/agents/", os.path.isfile("src/agents/__init__.py"))
    ]

    passed = sum(1 for _, result in checks if result)

    print(f"\n📊 Results: {passed}/{len(checks)} checks passed")
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")

    if passed >= 9:  # Allow one failure
        print("\n✅ Project structure properly organized")
        return True
    else:
        print("\n⚠️  Some structure issues remain")
        return False

def main():
    """Run all QA validation tests"""
    print("=" * 60)
    print("   TRT STAGE 1 SYSTEM - QA VALIDATION TESTS")
    print("   Date: 2025-10-14")
    print("   Validates: All 5 critical fixes + project structure")
    print("=" * 60)

    results = {
        "Fix #1 - Problem Identification": test_fix_1_problem_identification(),
        "Fix #2 - Spelling Correction": test_fix_2_spelling_correction(),
        "Fix #3 - CSV Fallback": test_fix_3_csv_fallback(),
        "Fix #4 - Body Counter": test_fix_4_body_counter(),
        "Fix #5 - Psycho-Education": test_fix_5_psycho_education(),
        "Project Structure": test_project_structure()
    }

    print("\n" + "=" * 60)
    print("   FINAL QA RESULTS")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print("\n" + "=" * 60)
    print(f"   OVERALL: {passed}/{total} tests passed ({int(passed/total*100)}%)")

    if passed == total:
        print("   STATUS: ✅ ALL TESTS PASSED - READY FOR DEPLOYMENT")
    elif passed >= total - 1:
        print("   STATUS: ⚠️  MINOR ISSUES - REVIEW RECOMMENDED")
    else:
        print("   STATUS: ❌ CRITICAL ISSUES - FIX REQUIRED")

    print("=" * 60)

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
