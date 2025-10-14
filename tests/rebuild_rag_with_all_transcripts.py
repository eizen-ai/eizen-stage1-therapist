"""
Rebuild RAG System with ALL Processed Transcripts
Uses the processed exchanges from all Dr. Q sessions
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os


def rebuild_rag_from_all_transcripts():
    """Rebuild RAG system with all processed transcript exchanges"""

    print("=" * 80)
    print("REBUILDING RAG SYSTEM WITH ALL DR. Q TRANSCRIPTS")
    print("=" * 80)

    # 1. Load processed exchanges
    print("\n📚 Loading processed exchanges...")
    exchanges_file = "data/processed_exchanges/all_dr_q_exchanges.json"

    if not os.path.exists(exchanges_file):
        print(f"❌ File not found: {exchanges_file}")
        print("Please run process_all_transcripts.py first!")
        return

    with open(exchanges_file, 'r') as f:
        data = json.load(f)

    exchanges = data['exchanges']
    print(f"✅ Loaded {len(exchanges)} exchanges from {len(data['metadata']['source_files'])} files")

    # 2. Initialize embedding model
    print("\n🤖 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded")

    # 3. Prepare texts for embedding
    print("\n📝 Preparing texts for embedding...")
    texts_to_embed = []
    metadata_list = []

    for exchange in exchanges:
        # Create comprehensive text for embedding
        # Combine doctor input + patient response + tags + contexts
        embedding_text = f"{exchange['doctor_input']} {exchange['patient_response']} "
        embedding_text += " ".join(exchange['embedding_tags']) + " "
        embedding_text += " ".join(exchange['rag_retrieval_contexts'])

        texts_to_embed.append(embedding_text)

        # Store metadata
        metadata_list.append({
            "exchange_id": exchange['exchange_id'],
            "source_file": exchange['source_file'],
            "doctor_example": exchange['doctor_input'],
            "patient_response": exchange['patient_response'],
            "labels": exchange['therapeutic_labels'],
            "tags": exchange['embedding_tags'],
            "contexts": exchange['rag_retrieval_contexts']
        })

    print(f"✅ Prepared {len(texts_to_embed)} texts")

    # 4. Generate embeddings
    print("\n🧮 Generating embeddings (this may take a few minutes)...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    print(f"✅ Generated embeddings with shape: {embeddings.shape}")

    # 5. Create FAISS index
    print("\n📊 Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    print(f"✅ FAISS index created with {index.ntotal} vectors")

    # 6. Save index and metadata
    print("\n💾 Saving index and metadata...")

    # Ensure directory exists
    os.makedirs("data/embeddings", exist_ok=True)

    # Save FAISS index
    faiss.write_index(index, "data/embeddings/trt_rag_index.faiss")
    print("✅ Saved FAISS index to data/embeddings/trt_rag_index.faiss")

    # Save metadata
    with open("data/embeddings/trt_rag_metadata.json", 'w') as f:
        json.dump(metadata_list, f, indent=2)
    print("✅ Saved metadata to data/embeddings/trt_rag_metadata.json")

    # 7. Print summary
    print("\n" + "=" * 80)
    print("RAG REBUILD SUMMARY")
    print("=" * 80)
    print(f"Total exchanges indexed: {len(exchanges)}")
    print(f"Source files: {len(data['metadata']['source_files'])}")
    print(f"Embedding dimension: {dimension}")
    print(f"FAISS index size: {index.ntotal} vectors")

    # Show distribution by technique
    print("\n📊 DISTRIBUTION BY DR. Q TECHNIQUE:")
    technique_counts = {}
    for exchange in exchanges:
        technique = exchange['therapeutic_labels']['dr_q_technique']
        technique_counts[technique] = technique_counts.get(technique, 0) + 1

    for technique, count in sorted(technique_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {technique}: {count}")

    # Show distribution by substate
    print("\n📊 DISTRIBUTION BY TRT SUBSTATE:")
    substate_counts = {}
    for exchange in exchanges:
        substate = exchange['therapeutic_labels']['trt_substate']
        substate_counts[substate] = substate_counts.get(substate, 0) + 1

    for substate, count in sorted(substate_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {substate}: {count}")

    print("\n✅ RAG system rebuilt successfully!")
    print("\nYou can now use the updated system with:")
    print("  python code_implementation/test_integrated_system.py")


if __name__ == "__main__":
    rebuild_rag_from_all_transcripts()
