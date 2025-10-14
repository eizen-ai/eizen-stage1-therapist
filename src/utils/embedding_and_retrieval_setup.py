"""
Embedding and RAG Retrieval Setup for TRT Therapy System
Handles embedding creation and similarity search for therapeutic exchanges
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from dataclasses import dataclass

@dataclass
class RetrievalResult:
    exchange_id: str
    content: str
    doctor_response: str
    similarity_score: float
    metadata: Dict
    retrieval_context: str

class TRTRAGSystem:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG system with sentence transformer model
        Use lightweight model for fast inference
        """
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.embedding_data = []
        self.dimension = 384  # MiniLM embedding dimension

    def load_embedding_dataset(self, dataset_path: str):
        """Load processed embedding dataset"""
        with open(dataset_path, 'r') as f:
            self.embedding_data = json.load(f)
        print(f"Loaded {len(self.embedding_data)} embedding entries")

    def create_embeddings(self):
        """Create embeddings for all therapeutic exchanges"""
        print("Creating embeddings...")

        # Prepare texts for embedding
        texts = []
        metadata = []

        for entry in self.embedding_data:
            # Create rich text representation for embedding
            text_for_embedding = self._create_embedding_text(entry)
            texts.append(text_for_embedding)
            metadata.append({
                "id": entry["id"],
                "content": entry["content"],
                "metadata": entry["metadata"],
                "tags": entry["tags"],
                "retrieval_contexts": entry["retrieval_contexts"]
            })

        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # Create FAISS index for fast similarity search
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))

        self.metadata = metadata
        print(f"Created embeddings and index with {len(embeddings)} entries")

    def _create_embedding_text(self, entry: Dict) -> str:
        """Create rich text representation for better embedding"""
        content = entry["content"]
        metadata = entry["metadata"]
        tags = " ".join(entry["tags"])
        contexts = " ".join(entry["retrieval_contexts"])

        # Create comprehensive text for embedding
        embedding_text = f"""
        Therapeutic Exchange: {content}

        TRT Context: {metadata.get('trt_stage', '')} {metadata.get('trt_substate', '')}
        Situation: {metadata.get('situation_type', '')}
        Technique: {metadata.get('dr_q_technique', '')}

        Tags: {tags}
        Contexts: {contexts}
        """.strip()

        return embedding_text

    def retrieve_similar_exchanges(self, query: str, top_k: int = 3, context_filter: str = None) -> List[RetrievalResult]:
        """
        Retrieve most similar therapeutic exchanges for a query

        Args:
            query: Search query (e.g., "client mentions body pain and stress")
            top_k: Number of results to return (default 3 for few-shot)
            context_filter: Filter by specific retrieval context
        """
        if self.index is None:
            raise ValueError("Index not created. Run create_embeddings() first.")

        # Create query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Search
        similarities, indices = self.index.search(query_embedding.astype('float32'), top_k * 2)  # Get more for filtering

        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if idx < len(self.metadata):
                metadata_entry = self.metadata[idx]

                # Apply context filter if specified
                if context_filter:
                    # Handle both old format (retrieval_contexts) and new format (contexts)
                    contexts = metadata_entry.get("contexts", metadata_entry.get("retrieval_contexts", []))
                    if context_filter not in contexts:
                        continue

                # Extract doctor response - handle both old and new metadata formats
                if "content" in metadata_entry:
                    # Old format
                    content = metadata_entry["content"]
                    doctor_response = self._extract_doctor_response(content)
                    exchange_id = metadata_entry["id"]
                    metadata = metadata_entry["metadata"]
                else:
                    # New format from rebuild_rag_with_all_transcripts.py
                    doctor_response = metadata_entry.get("doctor_example", "")
                    content = f"Doctor: {doctor_response}\nPatient: {metadata_entry.get('patient_response', '')}"
                    exchange_id = metadata_entry.get("exchange_id", "")
                    metadata = metadata_entry.get("labels", {})

                result = RetrievalResult(
                    exchange_id=exchange_id,
                    content=content,
                    doctor_response=doctor_response,
                    similarity_score=float(sim),
                    metadata=metadata,
                    retrieval_context=context_filter or "general"
                )
                results.append(result)

                if len(results) >= top_k:
                    break

        return results

    def _extract_doctor_response(self, content: str) -> str:
        """Extract doctor's response from exchange content"""
        if "Doctor:" in content:
            doctor_part = content.split("Doctor:")[1].split("Patient:")[0].strip()
            return doctor_part
        return content

    def retrieve_by_therapeutic_context(self,
                                       trt_stage: str,
                                       situation_type: str,
                                       client_input: str,
                                       top_k: int = 3) -> List[RetrievalResult]:
        """
        Retrieve examples for specific therapeutic context

        Args:
            trt_stage: e.g., "stage_1_safety_building"
            situation_type: e.g., "body_symptom_exploration"
            client_input: Current client message
            top_k: Number of examples to return
        """

        # Create contextual query
        query = f"""
        TRT Stage: {trt_stage}
        Situation: {situation_type}
        Client says: {client_input}

        Find Dr. Q examples for similar therapeutic situations.
        """

        return self.retrieve_similar_exchanges(query, top_k)

    def get_few_shot_examples(self,
                             navigation_output: Dict,
                             client_message: str,
                             max_examples: int = 3) -> List[Dict]:
        """
        Get few-shot examples for dialogue agent based on master planning output

        Args:
            navigation_output: Output from master planning agent
            client_message: Current client input
            max_examples: Maximum number of examples
        """

        rag_query = navigation_output.get("rag_query", "")
        situation_type = navigation_output.get("situation_type", "")
        trt_stage = navigation_output.get("current_stage", "")

        # Try specific RAG query first
        results = []
        if rag_query:
            # Use specific RAG query as context filter
            results = self.retrieve_similar_exchanges(
                f"{client_message} {situation_type}",
                top_k=max_examples,
                context_filter=rag_query
            )

        # Fallback to general similarity search
        if len(results) < max_examples:
            additional_results = self.retrieve_by_therapeutic_context(
                trt_stage, situation_type, client_message, max_examples
            )

            # Add unique results
            existing_ids = {r.exchange_id for r in results}
            for result in additional_results:
                if result.exchange_id not in existing_ids and len(results) < max_examples:
                    results.append(result)

        # Format for dialogue agent
        few_shot_examples = []
        for result in results:
            few_shot_examples.append({
                "similarity_score": result.similarity_score,
                "doctor_example": result.doctor_response,
                "full_exchange": result.content,
                "therapeutic_context": result.metadata,
                "usage_note": f"Use this Dr. Q style for {situation_type}"
            })

        return few_shot_examples

    def save_index(self, index_path: str, metadata_path: str):
        """Save FAISS index and metadata for later use"""
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f)
        print(f"Saved index to {index_path} and metadata to {metadata_path}")

    def load_index(self, index_path: str, metadata_path: str):
        """Load pre-built FAISS index and metadata"""
        self.index = faiss.read_index(index_path)
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        print(f"Loaded index from {index_path}")


# Example usage and testing
def test_rag_system():
    """Test the RAG system with sample queries"""

    # Initialize system
    rag_system = TRTRAGSystem()

    # Load dataset (assumes processed data exists)
    rag_system.load_embedding_dataset("data/processed_exchanges/complete_embedding_dataset.json")

    # Create embeddings
    rag_system.create_embeddings()

    # Test queries
    test_cases = [
        {
            "client_message": "I want to feel peaceful but work is stressing me out",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.1_goal_and_vision",
                "situation_type": "initial_goal_inquiry",
                "rag_query": "dr_q_goal_clarification"
            }
        },
        {
            "client_message": "My chest feels tight when I think about deadlines",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.2_problem_and_body",
                "situation_type": "body_symptom_exploration",
                "rag_query": "dr_q_body_symptom_present_moment_inquiry"
            }
        },
        {
            "client_message": "Yes, that sounds exactly what I want",
            "navigation_output": {
                "current_stage": "stage_1_safety_building",
                "current_substate": "1.1_goal_and_vision",
                "situation_type": "future_vision_building",
                "rag_query": "dr_q_future_self_vision_building"
            }
        }
    ]

    print("Testing RAG retrieval...")
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Client: {test_case['client_message']}")
        print(f"Navigation: {test_case['navigation_output']['situation_type']}")

        examples = rag_system.get_few_shot_examples(
            test_case['navigation_output'],
            test_case['client_message']
        )

        print(f"Retrieved {len(examples)} examples:")
        for j, example in enumerate(examples):
            print(f"  {j+1}. Dr. Q: {example['doctor_example'][:100]}...")
            print(f"     Similarity: {example['similarity_score']:.3f}")

    # Save index for production use
    rag_system.save_index("data/embeddings/trt_rag_index.faiss", "data/embeddings/trt_rag_metadata.json")


if __name__ == "__main__":
    test_rag_system()