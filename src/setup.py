#!/usr/bin/env python3
"""
TRT AI Therapy System - Setup and Maintenance Script
Provides easy commands for common operations
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if virtual environment is activated"""
    if not sys.prefix != sys.base_prefix:
        print("❌ Virtual environment not activated")
        print("Run: source therapy_env/bin/activate")
        return False
    print("✅ Virtual environment active")
    return True

def check_directory_structure():
    """Verify optimized directory structure exists"""
    required_dirs = [
        "core_system",
        "data/raw_transcripts",
        "data/processed_exchanges",
        "data/embeddings",
        "examples",
        "therapy_env"
    ]

    print("\nChecking directory structure:")
    all_good = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (missing)")
            all_good = False

    return all_good

def check_core_files():
    """Check if core system files exist"""
    core_files = [
        "core_system/optimized_master_agent.txt",
        "core_system/simplified_navigation.json",
        "core_system/input_classification_patterns.json",
        "data/embeddings/trt_rag_index.faiss",
        "data/embeddings/trt_rag_metadata.json"
    ]

    print("\nChecking core files:")
    all_good = True
    for file_path in core_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
            print(f"✅ {file_path} ({size_str})")
        else:
            print(f"❌ {file_path} (missing)")
            all_good = False

    return all_good

def test_rag_system():
    """Quick test of RAG system"""
    print("\nTesting RAG system...")
    try:
        result = subprocess.run([
            sys.executable, "test_rag_validation.py"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ RAG system test passed")
            return True
        else:
            print("❌ RAG system test failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")
        return False

def process_new_transcripts():
    """Process new transcripts and rebuild embeddings"""
    print("\nProcessing transcripts...")

    # Check for new transcript files
    transcript_dir = Path("data/raw_transcripts")
    txt_files = list(transcript_dir.glob("session_*.txt"))

    if len(txt_files) < 3:
        print(f"❌ Found only {len(txt_files)} transcript files, expected at least 3")
        return False

    print(f"Found {len(txt_files)} transcript files")

    # Run processing pipeline
    try:
        print("Running transcript processing...")
        result = subprocess.run([
            sys.executable, "transcript_processing_pipeline.py"
        ], timeout=300)

        if result.returncode != 0:
            print("❌ Transcript processing failed")
            return False

        print("Running embedding creation...")
        result = subprocess.run([
            sys.executable, "embedding_and_retrieval_setup.py"
        ], timeout=600)

        if result.returncode != 0:
            print("❌ Embedding creation failed")
            return False

        print("✅ Processing completed successfully")
        return True

    except subprocess.TimeoutExpired:
        print("❌ Processing timed out")
        return False
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False

def show_system_status():
    """Show comprehensive system status"""
    print("TRT AI THERAPY SYSTEM - STATUS CHECK")
    print("=" * 50)

    # Check environment
    env_ok = check_environment()

    # Check structure
    struct_ok = check_directory_structure()

    # Check files
    files_ok = check_core_files()

    # Overall status
    print("\n" + "=" * 50)
    if env_ok and struct_ok and files_ok:
        print("🎉 SYSTEM STATUS: READY")
        print("\nQuick commands:")
        print("• Test system: python3 test_rag_validation.py")
        print("• Process new transcripts: python3 setup.py --process")
        print("• Full status check: python3 setup.py --status")
    else:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        if not env_ok:
            print("• Activate virtual environment")
        if not struct_ok:
            print("• Restore directory structure")
        if not files_ok:
            print("• Regenerate missing files")

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            show_system_status()
        elif sys.argv[1] == "--test":
            if check_environment():
                test_rag_system()
        elif sys.argv[1] == "--process":
            if check_environment():
                process_new_transcripts()
        elif sys.argv[1] == "--help":
            print("TRT AI Therapy System Setup")
            print("Commands:")
            print("  --status   : Check system status")
            print("  --test     : Test RAG system")
            print("  --process  : Process new transcripts")
            print("  --help     : Show this help")
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Use --help for available commands")
    else:
        show_system_status()

if __name__ == "__main__":
    main()