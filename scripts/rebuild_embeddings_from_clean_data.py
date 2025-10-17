"""
Rebuild Embeddings from Clean complete_embedding_dataset.json
This uses the correctly formatted data from sessions 1, 2, 3
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

def rebuild_clean_embeddings():
    """Rebuild embeddings using complete_embedding_dataset.json"""

    print("=" * 80)
    print("REBUILDING EMBEDDINGS FROM CLEAN DATA")
    print("=" * 80)

    # 1. Load clean dataset
    print("\n📚 Loading complete_embedding_dataset.json...")
    with open('data/processed/processed_exchanges/complete_embedding_dataset.json', 'r') as f:
        data = json.load(f)

    print(f"✅ Loaded {len(data)} clean exchanges")

    # 2. Initialize embedding model
    print("\n🤖 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded")

    # 3. Prepare texts for embedding
    print("\n📝 Preparing texts for embedding...")
    texts_to_embed = []
    metadata_list = []

    for entry in data:
        # Create comprehensive text for embedding
        # Format: content + tags + retrieval contexts
        embedding_text = f"{entry['content']} "
        embedding_text += " ".join(entry['tags']) + " "
        embedding_text += " ".join(entry['retrieval_contexts'])

        texts_to_embed.append(embedding_text)

        # Store metadata (keep the structure from complete_embedding_dataset)
        metadata_list.append({
            "id": entry['id'],
            "content": entry['content'],
            "metadata": entry['metadata'],
            "tags": entry['tags'],
            "retrieval_contexts": entry['retrieval_contexts']
        })

    print(f"✅ Prepared {len(texts_to_embed)} texts")

    # 4. Generate embeddings
    print("\n🧮 Generating embeddings...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    print(f"✅ Generated embeddings with shape: {embeddings.shape}")

    # 5. Create FAISS index
    print("\n📊 Creating FAISS index...")
    dimension = embeddings.shape[1]

    # Use IndexFlatIP for cosine similarity (as in original code)
    index = faiss.IndexFlatIP(dimension)

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
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
    print("EMBEDDING REBUILD SUMMARY")
    print("=" * 80)
    print(f"Total exchanges indexed: {len(data)}")
    print(f"Source: complete_embedding_dataset.json (sessions 1, 2, 3)")
    print(f"Embedding dimension: {dimension}")
    print(f"FAISS index size: {index.ntotal} vectors")
    print(f"Average retrieval contexts per exchange: {sum(len(e['retrieval_contexts']) for e in data)/len(data):.2f}")

    # Show distribution by TRT substate
    print("\n📊 DISTRIBUTION BY TRT SUBSTATE:")
    substate_counts = {}
    for entry in data:
        substate = entry['metadata'].get('trt_substate', 'unknown')
        substate_counts[substate] = substate_counts.get(substate, 0) + 1

    for substate, count in sorted(substate_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {substate}: {count}")

    # Show distribution by technique
    print("\n📊 DISTRIBUTION BY DR. Q TECHNIQUE:")
    technique_counts = {}
    for entry in data:
        technique = entry['metadata'].get('dr_q_technique', 'unknown')
        technique_counts[technique] = technique_counts.get(technique, 0) + 1

    for technique, count in sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {technique}: {count}")

    print("\n✅ Clean embeddings rebuilt successfully!")
    print("\nCorrupted files archived to: data/archive/corrupted_embeddings_*/")
    print("System is now using clean, high-quality embeddings.")

if __name__ == "__main__":
    rebuild_clean_embeddings()
