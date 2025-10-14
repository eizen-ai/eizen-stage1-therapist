"""
Comprehensive Test Cases for Lightweight LLM-Enhanced TRT System
Modified to work with the enhanced lightweight system
"""

import json
from datetime import datetime
from improved_lightweight_llm_system import ImprovedLLMTRTSystem
from session_state_manager import TRTSessionState

class LightweightTRTTestSuite:
    """Comprehensive test suite for lightweight enhanced TRT system"""

    def __init__(self):
        print("🧪 Initializing Lightweight Enhanced TRT Test Suite...")
        self.system = ImprovedLLMTRTSystem()
        self.test_results = []

    def run_all_tests(self):
        """Run all test scenarios"""
        print("\n🚀 RUNNING COMPREHENSIVE LIGHTWEIGHT TRT SYSTEM TESTS")
        print("=" * 80)

        test_scenarios = [
            self.test_normal_progression,
            self.test_edge_cases,
            self.test_spelling_mistakes,
            self.test_emotional_variations,
            self.test_resistance_patterns,
            self.test_confusion_states,
            self.test_positive_responses,
            self.test_repetitive_inputs,
            self.test_body_awareness_focus,
            self.test_goal_clarification_variations,
            self.test_enhanced_reasoning_factors
        ]

        for i, test_func in enumerate(test_scenarios, 1):
            print(f"\n🔬 TEST {i}: {test_func.__name__.replace('test_', '').replace('_', ' ').title()}")
            print("-" * 60)

            try:
                result = test_func()
                self.test_results.append(result)
                success_rate = result['success_rate']
                status = "✅ PASS" if success_rate >= 0.8 else "⚠️  PARTIAL" if success_rate >= 0.6 else "❌ FAIL"
                print(f"{status} - Success Rate: {success_rate:.1%}")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.test_results.append({'test_name': test_func.__name__, 'success_rate': 0.0, 'error': str(e)})

        self._generate_test_report()

    def test_normal_progression(self):
        """Test normal therapeutic progression through Stage 1"""
        session = TRTSessionState("normal_progression_test")

        test_inputs = [
            "I've been feeling really anxious and stressed lately",
            "I want to feel calm and peaceful",
            "Yes, that vision sounds exactly right to me",
            "It's mainly work stress, I get tightness in my chest",
            "I can feel that tightness right now as we talk",
            "It usually starts when I check my email in the morning",
            "I think I understand the pattern now, I'm ready to work on it"
        ]

        expected_substates = ["1.1", "1.1", "1.2", "1.2", "1.2", "1.3", "stage_1_complete"]
        results = []

        for i, client_input in enumerate(test_inputs):
            output = self.system.process_client_input(client_input, session)
            current_substate = output['navigation']['current_substate']

            # Check if progression matches expectation (more flexible)
            expected = expected_substates[i]
            success = expected in current_substate or (expected == "1.2" and "1.2" in current_substate)
            results.append(success)

            print(f"   Turn {i+1}: \"{client_input[:40]}...\" → {current_substate} {'✅' if success else '❌'}")

        return {
            'test_name': 'normal_progression',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_edge_cases(self):
        """Test challenging edge cases with enhanced reasoning"""
        session = TRTSessionState("edge_cases_test")

        edge_cases = [
            # Ambiguous inputs
            "I don't know",
            "Maybe",
            "Sort of",
            "It's complicated",

            # Contradictory statements
            "I want to feel better but I don't want to change",
            "This is helping but it's not working",

            # Meta-therapeutic comments
            "Are you a real therapist?",
            "How long will this take?",
            "I don't think this is working",

            # Extreme emotional states
            "I want to disappear completely",
            "Nothing matters anymore",
            "I feel completely numb"
        ]

        results = []
        for client_input in edge_cases:
            try:
                output = self.system.process_client_input(client_input, session)
                response = output['dialogue']['therapeutic_response']
                enhanced = output['navigation'].get('enhanced_reasoning', False)

                # Check if response is therapeutic and uses enhanced reasoning
                is_therapeutic = self._evaluate_response_quality(client_input, response)
                results.append(is_therapeutic and enhanced)

                print(f"   \"{client_input}\" → {'✅' if (is_therapeutic and enhanced) else '❌'}")
                print(f"      Enhanced: {'✅' if enhanced else '❌'} Response: \"{response[:60]}...\"")

            except Exception as e:
                results.append(False)
                print(f"   \"{client_input}\" → ❌ ERROR: {e}")

        return {
            'test_name': 'edge_cases',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_spelling_mistakes(self):
        """Test handling of spelling mistakes and typos"""
        session = TRTSessionState("spelling_test")

        misspelled_inputs = [
            "iam feelig realy sad",
            "i want to fel beter",
            "yes thats wat i want",
            "its my bos at wrk",
            "i fel it in my ches",
            "its hevy and tigt"
        ]

        results = []
        for client_input in misspelled_inputs:
            output = self.system.process_client_input(client_input, session)
            processing = output['navigation']['input_processing']

            # Check if spelling was corrected
            corrections_made = len(processing.get('spelling_corrections', []))
            corrected_properly = corrections_made > 0
            results.append(corrected_properly)

            print(f"   \"{client_input}\" → {processing['corrected_input']} {'✅' if corrected_properly else '❌'}")

        return {
            'test_name': 'spelling_mistakes',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_emotional_variations(self):
        """Test different emotional expressions with enhanced detection"""
        session = TRTSessionState("emotional_test")

        emotional_inputs = [
            # Sadness variations
            "I feel so depressed",
            "I'm feeling down today",
            "I feel melancholy",

            # Anxiety variations
            "I'm having panic attacks",
            "I feel overwhelmed",
            "I'm stressed out",

            # Anger variations
            "I'm furious about this",
            "I feel so frustrated",
            "I'm angry all the time",

            # Mixed emotions
            "I feel sad but also relieved",
            "I'm angry but I know I shouldn't be"
        ]

        results = []
        for client_input in emotional_inputs:
            output = self.system.process_client_input(client_input, session)
            processing = output['navigation']['input_processing']
            factors = output['navigation'].get('reasoning_factors', {})

            # Check if emotional state was detected and enhanced reasoning applied
            emotional_state = processing.get('emotional_state', 'neutral')
            detected_emotion = emotional_state != 'neutral'
            has_emotional_intensity = 'emotional_intensity' in factors

            success = detected_emotion and has_emotional_intensity
            results.append(success)

            print(f"   \"{client_input}\" → {emotional_state} (intensity: {factors.get('emotional_intensity', 'N/A')}) {'✅' if success else '❌'}")

        return {
            'test_name': 'emotional_variations',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_resistance_patterns(self):
        """Test handling of therapeutic resistance with enhanced adaptation"""
        session = TRTSessionState("resistance_test")

        resistance_inputs = [
            "I don't want to talk about that",
            "This isn't helping",
            "I don't see the point",
            "You don't understand",
            "I've tried everything",
            "Nothing works for me",
            "I don't believe in therapy",
            "This is too hard"
        ]

        results = []
        for client_input in resistance_inputs:
            output = self.system.process_client_input(client_input, session)
            response = output['dialogue']['therapeutic_response']
            factors = output['navigation'].get('reasoning_factors', {})
            adaptation_used = output['dialogue'].get('adaptation_used', False)

            # Check if resistance was detected and adaptation was used
            resistance_detected = factors.get('resistance_indicators', False)
            is_validating = self._check_validation(response)

            success = resistance_detected and adaptation_used and is_validating
            results.append(success)

            print(f"   \"{client_input}\" → Resistance: {'✅' if resistance_detected else '❌'} Adapted: {'✅' if adaptation_used else '❌'}")
            print(f"      Response: \"{response[:60]}...\"")

        return {
            'test_name': 'resistance_patterns',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_confusion_states(self):
        """Test handling of client confusion with enhanced clarification"""
        session = TRTSessionState("confusion_test")

        confusion_inputs = [
            "I'm not sure what you mean",
            "Can you explain that again?",
            "I don't understand",
            "What do you want me to say?",
            "I'm confused",
            "Could you repeat that?",
            "I lost track of what we were talking about"
        ]

        results = []
        for client_input in confusion_inputs:
            output = self.system.process_client_input(client_input, session)
            response = output['dialogue']['therapeutic_response']
            factors = output['navigation'].get('reasoning_factors', {})
            adaptation_used = output['dialogue'].get('adaptation_used', False)

            # Check if confusion was detected and appropriate clarification provided
            confusion_detected = factors.get('confusion_indicators', False)
            is_clarifying = self._check_clarification(response)

            success = confusion_detected and adaptation_used and is_clarifying
            results.append(success)

            print(f"   \"{client_input}\" → Confusion: {'✅' if confusion_detected else '❌'} Adapted: {'✅' if adaptation_used else '❌'}")

        return {
            'test_name': 'confusion_states',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_positive_responses(self):
        """Test handling of positive client responses with enhanced acknowledgment"""
        session = TRTSessionState("positive_test")

        positive_inputs = [
            "I feel much better now",
            "That's really helpful",
            "I understand now",
            "That makes sense",
            "I feel good about that",
            "I'm feeling more relaxed",
            "That resonates with me"
        ]

        results = []
        for client_input in positive_inputs:
            output = self.system.process_client_input(client_input, session)
            response = output['dialogue']['therapeutic_response']
            factors = output['navigation'].get('reasoning_factors', {})
            adaptation_used = output['dialogue'].get('adaptation_used', False)

            # Check if positivity was detected and acknowledged appropriately
            positive_detected = factors.get('positive_indicators', False)
            acknowledges_positive = self._check_positive_acknowledgment(response)

            success = positive_detected and acknowledges_positive
            results.append(success)

            print(f"   \"{client_input}\" → Positive: {'✅' if positive_detected else '❌'} Acknowledged: {'✅' if acknowledges_positive else '❌'}")

        return {
            'test_name': 'positive_responses',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_repetitive_inputs(self):
        """Test handling of repetitive client inputs with enhanced variation"""
        session = TRTSessionState("repetitive_test")

        # Repeat the same input multiple times
        repetitive_input = "I feel sad"
        responses = []
        adaptations = []

        for i in range(5):
            output = self.system.process_client_input(repetitive_input, session)
            response = output['dialogue']['therapeutic_response']
            adaptation_used = output['dialogue'].get('adaptation_used', False)

            responses.append(response)
            adaptations.append(adaptation_used)
            print(f"   Iteration {i+1}: Adapted: {'✅' if adaptation_used else '❌'} \"{response[:50]}...\"")

        # Check if responses vary over time and adaptations are used
        unique_responses = len(set(responses))
        variation_rate = unique_responses / len(responses)
        adaptation_rate = sum(adaptations) / len(adaptations)

        success = variation_rate >= 0.6 and adaptation_rate >= 0.4

        return {
            'test_name': 'repetitive_inputs',
            'success_rate': 1.0 if success else 0.0,
            'details': {
                'variation_rate': variation_rate,
                'adaptation_rate': adaptation_rate,
                'unique_responses': unique_responses
            }
        }

    def test_body_awareness_focus(self):
        """Test body awareness and somatic focus with enhanced detection"""
        session = TRTSessionState("body_awareness_test")

        body_related_inputs = [
            "I feel tension in my shoulders",
            "My chest feels tight",
            "I have a knot in my stomach",
            "My head is pounding",
            "I feel heavy all over",
            "There's pressure in my throat",
            "My hands are shaking"
        ]

        results = []
        for client_input in body_related_inputs:
            output = self.system.process_client_input(client_input, session)
            response = output['dialogue']['therapeutic_response']
            factors = output['navigation'].get('reasoning_factors', {})

            # Check if body awareness was detected and response focuses on it
            body_detected = factors.get('body_awareness_present', False)
            focuses_on_body = self._check_body_awareness_focus(response)

            success = body_detected and focuses_on_body
            results.append(success)

            print(f"   \"{client_input}\" → Body: {'✅' if body_detected else '❌'} Focus: {'✅' if focuses_on_body else '❌'}")

        return {
            'test_name': 'body_awareness_focus',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_goal_clarification_variations(self):
        """Test different ways clients express goals with enhanced recognition"""
        session = TRTSessionState("goal_clarification_test")

        goal_expressions = [
            "I just want to be happy",
            "I need to stop feeling anxious",
            "I want my life back",
            "I need to feel normal again",
            "I want to be myself",
            "I need to feel confident",
            "I want peace of mind",
            "I need to stop worrying"
        ]

        results = []
        for client_input in goal_expressions:
            output = self.system.process_client_input(client_input, session)
            completion = output['navigation']['completion_status']
            factors = output['navigation'].get('reasoning_factors', {})

            # Check if goal was recognized and goal language detected
            goal_recognized = completion.get('goal_stated', False)
            goal_language_detected = factors.get('goal_language', False)

            success = goal_recognized or goal_language_detected  # Either should work
            results.append(success)

            print(f"   \"{client_input}\" → Goal: {'✅' if goal_recognized else '❌'} Language: {'✅' if goal_language_detected else '❌'}")

        return {
            'test_name': 'goal_clarification_variations',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def test_enhanced_reasoning_factors(self):
        """Test the enhanced reasoning factors specifically"""
        session = TRTSessionState("reasoning_factors_test")

        test_cases = [
            # Test emotional intensity detection
            {
                'input': "I'm extremely depressed and feel completely hopeless",
                'expected_factors': ['emotional_intensity', 'body_awareness_present'],
                'expected_intensity': 'high'
            },
            {
                'input': "I don't want to do this anymore",
                'expected_factors': ['resistance_indicators'],
                'expected_intensity': 'moderate'
            },
            {
                'input': "I feel much better and that really helped",
                'expected_factors': ['positive_indicators', 'body_awareness_present'],
                'expected_intensity': 'moderate'
            },
            {
                'input': "I want to feel confident and happy",
                'expected_factors': ['goal_language', 'positive_indicators'],
                'expected_intensity': 'low'
            }
        ]

        results = []
        for test_case in test_cases:
            output = self.system.process_client_input(test_case['input'], session)
            factors = output['navigation'].get('reasoning_factors', {})

            # Check if expected factors were detected
            detected_factors = [factor for factor in test_case['expected_factors'] if factors.get(factor, False)]
            factor_success = len(detected_factors) >= len(test_case['expected_factors']) * 0.5

            # Check emotional intensity if specified
            intensity_success = True
            if 'expected_intensity' in test_case:
                actual_intensity = factors.get('emotional_intensity', 'unknown')
                intensity_success = actual_intensity == test_case['expected_intensity']

            success = factor_success and intensity_success
            results.append(success)

            print(f"   \"{test_case['input'][:40]}...\"")
            print(f"      Expected: {test_case['expected_factors']} → Detected: {detected_factors} {'✅' if factor_success else '❌'}")
            if 'expected_intensity' in test_case:
                print(f"      Intensity: {test_case['expected_intensity']} → {factors.get('emotional_intensity', 'N/A')} {'✅' if intensity_success else '❌'}")

        return {
            'test_name': 'enhanced_reasoning_factors',
            'success_rate': sum(results) / len(results),
            'details': results
        }

    def _evaluate_response_quality(self, client_input: str, response: str) -> bool:
        """Evaluate if response is therapeutically appropriate"""
        if not response or len(response.strip()) < 10:
            return False

        therapeutic_indicators = [
            "what", "how", "feel", "understand", "notice", "experience",
            "body", "moment", "happening", "sense", "awareness"
        ]

        response_lower = response.lower()
        has_therapeutic_language = any(word in response_lower for word in therapeutic_indicators)

        analytical_flags = [
            "because you", "the reason", "this means", "what this tells me",
            "obviously", "clearly", "you should", "you must"
        ]

        is_not_analytical = not any(flag in response_lower for flag in analytical_flags)

        return has_therapeutic_language and is_not_analytical

    def _check_validation(self, response: str) -> bool:
        """Check if response is validating"""
        validating_phrases = [
            "i hear", "i understand", "that makes sense", "i can see",
            "sounds like", "it seems", "i notice", "that's", "feels"
        ]

        response_lower = response.lower()
        return any(phrase in response_lower for phrase in validating_phrases)

    def _check_clarification(self, response: str) -> bool:
        """Check if response provides clarification"""
        clarifying_phrases = [
            "what i mean", "let me", "another way", "what i'm asking",
            "to clarify", "what's", "help me understand", "different way",
            "more specific", "asking about"
        ]

        response_lower = response.lower()
        return any(phrase in response_lower for phrase in clarifying_phrases)

    def _check_positive_acknowledgment(self, response: str) -> bool:
        """Check if response acknowledges positive feelings appropriately"""
        positive_acknowledgments = [
            "that's good", "i'm glad", "that's helpful", "that's wonderful",
            "good to hear", "that's great", "what's different", "making the difference",
            "sounds positive", "feels right"
        ]

        response_lower = response.lower()
        return any(phrase in response_lower for phrase in positive_acknowledgments)

    def _check_body_awareness_focus(self, response: str) -> bool:
        """Check if response focuses on body awareness"""
        body_focus_phrases = [
            "notice in your body", "body feeling", "what's happening",
            "right now", "present moment", "body", "sensation",
            "feeling like", "notice", "experiencing", "talking about that right now"
        ]

        response_lower = response.lower()
        return any(phrase in response_lower for phrase in body_focus_phrases)

    def _generate_test_report(self):
        """Generate comprehensive test report"""

        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success_rate'] >= 0.8)
        partial_tests = sum(1 for result in self.test_results if 0.6 <= result['success_rate'] < 0.8)
        failed_tests = sum(1 for result in self.test_results if result['success_rate'] < 0.6)
        overall_success_rate = sum(result['success_rate'] for result in self.test_results) / total_tests

        print(f"\n📊 COMPREHENSIVE LIGHTWEIGHT ENHANCED TRT TEST REPORT")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Successful Tests (≥80%): {successful_tests}")
        print(f"Partial Tests (60-79%): {partial_tests}")
        print(f"Failed Tests (<60%): {failed_tests}")
        print(f"Overall Success Rate: {overall_success_rate:.1%}")
        print()

        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success_rate'] >= 0.8 else "⚠️" if result['success_rate'] >= 0.6 else "❌"
            print(f"{status} {result['test_name']}: {result['success_rate']:.1%}")

        # Performance classification
        if overall_success_rate >= 0.9:
            performance = "🏆 EXCELLENT"
        elif overall_success_rate >= 0.8:
            performance = "✅ GOOD"
        elif overall_success_rate >= 0.7:
            performance = "⚠️  ACCEPTABLE"
        else:
            performance = "❌ NEEDS_IMPROVEMENT"

        print(f"\n🎯 OVERALL PERFORMANCE: {performance}")

        # Enhanced features assessment
        enhanced_features = {
            'Enhanced Reasoning': any('enhanced_reasoning_factors' in r['test_name'] for r in self.test_results),
            'Resistance Handling': any('resistance_patterns' in r['test_name'] for r in self.test_results),
            'Confusion Handling': any('confusion_states' in r['test_name'] for r in self.test_results),
            'Body Awareness': any('body_awareness_focus' in r['test_name'] for r in self.test_results),
            'Emotional Detection': any('emotional_variations' in r['test_name'] for r in self.test_results)
        }

        print(f"\n🔧 ENHANCED FEATURES TESTED:")
        for feature, tested in enhanced_features.items():
            print(f"   {'✅' if tested else '❌'} {feature}")

        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_type': 'lightweight_enhanced_llm_trt',
            'overall_success_rate': overall_success_rate,
            'performance_classification': performance,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'partial_tests': partial_tests,
            'failed_tests': failed_tests,
            'enhanced_features_tested': enhanced_features,
            'detailed_results': self.test_results
        }

        report_filename = f"logs/lightweight_enhanced_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📁 Detailed report saved to {report_filename}")

def run_comprehensive_lightweight_tests():
    """Run all comprehensive tests on lightweight enhanced system"""
    test_suite = LightweightTRTTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    run_comprehensive_lightweight_tests()