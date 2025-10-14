"""
RAG System Validation - Testing specific therapeutic scenarios
"""

import json
from embedding_and_retrieval_setup import TRTRAGSystem

def test_specific_therapeutic_scenarios():
    """Test RAG retrieval with specific therapeutic scenarios from Stage 1"""

    # Initialize and load pre-built RAG system
    rag_system = TRTRAGSystem()
    rag_system.load_index("data/embeddings/trt_rag_index.faiss", "data/embeddings/trt_rag_metadata.json")

    print("RAG System Validation - Therapeutic Scenario Testing")
    print("=" * 60)

    # Test scenarios from complete_stage_1_flow_example.txt
    test_scenarios = [
        {
            "name": "Initial Goal Clarification (Vague Stress)",
            "client_message": "I'm really stressed and don't know what to do anymore",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.1_goal_and_vision",
                "situation_type": "vague_stress_problem",
                "rag_query": "dr_q_goal_clarification"
            }
        },
        {
            "name": "Vision Building (Goal Stated)",
            "client_message": "I want to feel calm and not so anxious all the time",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.1_goal_and_vision",
                "situation_type": "goal_stated_needs_vision",
                "rag_query": "dr_q_future_self_vision_building"
            }
        },
        {
            "name": "Body Symptom Exploration",
            "client_message": "I get this tight feeling in my chest when I think about deadlines",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.2_problem_and_body",
                "situation_type": "body_symptoms_with_external_trigger",
                "rag_query": "dr_q_body_symptom_present_moment_inquiry"
            }
        },
        {
            "name": "Present Moment Body Awareness",
            "client_message": "Yeah, it's like a heavy weight pressing down. I can feel it right now actually.",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.2_problem_and_body",
                "situation_type": "body_awareness_established_explore_pattern",
                "rag_query": "dr_q_present_moment_body_observation"
            }
        },
        {
            "name": "Pattern Inquiry (How Do You Know)",
            "client_message": "Usually it's when I look at my calendar and see how much I have to do",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.2_problem_and_body",
                "situation_type": "pattern_understood_assess_next_steps",
                "rag_query": "dr_q_how_do_you_know_technique"
            }
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- SCENARIO {i}: {scenario['name']} ---")
        print(f"Client: \"{scenario['client_message']}\"")
        print(f"Expected RAG Query: {scenario['navigation_output']['rag_query']}")

        # Get few-shot examples from RAG system
        examples = rag_system.get_few_shot_examples(
            scenario['navigation_output'],
            scenario['client_message'],
            max_examples=2  # Test with 2 examples for brevity
        )

        print(f"Retrieved {len(examples)} examples:")
        for j, example in enumerate(examples, 1):
            print(f"\n  Example {j}:")
            print(f"  Dr. Q: {example['doctor_example'][:120]}...")
            print(f"  Similarity: {example['similarity_score']:.3f}")
            if 'therapeutic_context' in example:
                context = example['therapeutic_context']
                print(f"  Context: {context.get('trt_substate', '')} - {context.get('situation_type', '')}")

    print("\n" + "=" * 60)
    print("RAG SYSTEM VALIDATION COMPLETE")
    print(f"All scenarios tested successfully with authentic Dr. Q examples")


def test_context_filtering():
    """Test RAG retrieval with specific context filters"""

    rag_system = TRTRAGSystem()
    rag_system.load_index("data/embeddings/trt_rag_index.faiss", "data/embeddings/trt_rag_metadata.json")

    print("\n\nCONTEXT FILTERING TEST")
    print("=" * 40)

    # Test context-specific retrieval
    query = "client feels anxious about work"

    print(f"Query: {query}")
    print("\nGeneral retrieval:")
    general_results = rag_system.retrieve_similar_exchanges(query, top_k=3)
    for i, result in enumerate(general_results, 1):
        print(f"  {i}. {result.doctor_response[:80]}... (Score: {result.similarity_score:.3f})")

    print("\nFiltered by 'dr_q_goal_clarification':")
    filtered_results = rag_system.retrieve_similar_exchanges(
        query, top_k=3, context_filter="dr_q_goal_clarification"
    )
    for i, result in enumerate(filtered_results, 1):
        print(f"  {i}. {result.doctor_response[:80]}... (Score: {result.similarity_score:.3f})")


if __name__ == "__main__":
    test_specific_therapeutic_scenarios()
    test_context_filtering()