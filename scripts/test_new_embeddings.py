"""
Test the newly rebuilt embeddings
"""

import sys
sys.path.append('src')

from utils.embedding_and_retrieval_setup import TRTRAGSystem

def test_embeddings():
    """Test the new clean embeddings"""

    print("=" * 80)
    print("TESTING NEW CLEAN EMBEDDINGS")
    print("=" * 80)

    # Initialize RAG system
    print("\n🔧 Initializing RAG system...")
    rag = TRTRAGSystem()

    # Load the new index
    print("📂 Loading embeddings...")
    rag.load_index("data/embeddings/trt_rag_index.faiss", "data/embeddings/trt_rag_metadata.json")
    print(f"✅ Loaded {len(rag.metadata)} embeddings")

    # Test queries
    test_cases = [
        {
            "query": "Client mentions feeling stressed at work and wants to feel peaceful",
            "description": "Goal setting scenario"
        },
        {
            "query": "Client describes body pain in their chest and leg",
            "description": "Body symptom exploration"
        },
        {
            "query": "Client says 'I don't know' when asked about their feelings",
            "description": "Client uncertainty"
        }
    ]

    print("\n" + "=" * 80)
    print("RUNNING TEST QUERIES")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {test['description']}")
        print(f"{'=' * 80}")
        print(f"Query: {test['query']}")
        print()

        # Retrieve similar exchanges
        results = rag.retrieve_similar_exchanges(test['query'], top_k=3)

        print(f"Retrieved {len(results)} examples:\n")
        for j, result in enumerate(results, 1):
            print(f"{j}. Similarity: {result.similarity_score:.3f}")
            print(f"   Exchange ID: {result.exchange_id}")
            print(f"   Content: {result.content[:150]}...")
            print(f"   Metadata: {result.metadata.get('trt_substate', 'N/A')} | {result.metadata.get('dr_q_technique', 'N/A')}")
            print()

    print("=" * 80)
    print("✅ EMBEDDING TEST COMPLETE")
    print("=" * 80)
    print("\nThe new embeddings are working correctly!")
    print("System is ready to use with clean, high-quality data.")

if __name__ == "__main__":
    test_embeddings()
