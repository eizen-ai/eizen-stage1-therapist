#!/bin/bash
# System Readiness Check - Verify everything is ready for testing

echo "=================================================="
echo "   TRT SYSTEM READINESS CHECK"
echo "=================================================="
echo ""

# Check 1: Ollama running
echo "🔍 Checking Ollama server..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama server is running on localhost:11434"
else
    echo "   ❌ Ollama server is NOT running"
    echo "   ⚠️  Start it with: ollama serve"
    echo ""
    exit 1
fi

# Check 2: LLaMA model available
echo ""
echo "🔍 Checking for LLaMA 3.1 model..."
if curl -s http://localhost:11434/api/tags | grep -q "llama3.1"; then
    echo "   ✅ llama3.1 model found"
else
    echo "   ❌ llama3.1 model not found"
    echo "   ⚠️  Install it with: ollama pull llama3.1"
    echo ""
    exit 1
fi

# Check 3: Virtual environment
echo ""
echo "🔍 Checking Python virtual environment..."
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment exists"
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "   ⚠️  Not activated yet. Run: source venv/bin/activate"
    else
        echo "   ✅ Virtual environment is activated"
    fi
else
    echo "   ❌ Virtual environment not found"
    echo "   ⚠️  Create it with: python3 -m venv venv"
    echo ""
    exit 1
fi

# Check 4: Required files
echo ""
echo "🔍 Checking required files..."
files_ok=true

if [ -f "config/STAGE1_COMPLETE.csv" ]; then
    echo "   ✅ config/STAGE1_COMPLETE.csv"
else
    echo "   ❌ config/STAGE1_COMPLETE.csv missing"
    files_ok=false
fi

if [ -f "src/core/improved_ollama_system.py" ]; then
    echo "   ✅ src/core/improved_ollama_system.py"
else
    echo "   ❌ src/core/improved_ollama_system.py missing"
    files_ok=false
fi

if [ -f "data/embeddings/trt_rag_index.faiss" ]; then
    echo "   ✅ data/embeddings/trt_rag_index.faiss"
else
    echo "   ⚠️  data/embeddings/trt_rag_index.faiss missing (RAG may not work)"
fi

if [ -f "data/embeddings/trt_rag_metadata.json" ]; then
    echo "   ✅ data/embeddings/trt_rag_metadata.json"
else
    echo "   ⚠️  data/embeddings/trt_rag_metadata.json missing (RAG may not work)"
fi

# Check 5: Logs directory
echo ""
echo "🔍 Checking logs directory..."
if [ -d "logs" ]; then
    log_count=$(ls -1 logs/*.json 2>/dev/null | wc -l)
    echo "   ✅ logs/ directory exists ($log_count existing logs)"
else
    echo "   ⚠️  logs/ directory missing, creating..."
    mkdir -p logs
    echo "   ✅ Created logs/ directory"
fi

# Check 6: Test helper scripts
echo ""
echo "🔍 Checking test helper scripts..."
if [ -f "test_helper.py" ]; then
    echo "   ✅ test_helper.py"
else
    echo "   ⚠️  test_helper.py missing"
fi

if [ -f "qa_validation_tests.py" ]; then
    echo "   ✅ qa_validation_tests.py"
else
    echo "   ⚠️  qa_validation_tests.py missing"
fi

# Summary
echo ""
echo "=================================================="
if $files_ok && [ -z "$VIRTUAL_ENV" ]; then
    echo "   STATUS: ⚠️  ALMOST READY"
    echo ""
    echo "   Next step: Activate virtual environment"
    echo "   Run: source venv/bin/activate"
elif $files_ok; then
    echo "   STATUS: ✅ READY TO TEST!"
    echo ""
    echo "   Start testing with:"
    echo "   python test_helper.py start"
    echo ""
    echo "   Or directly:"
    echo "   cd src/core && python improved_ollama_system.py"
else
    echo "   STATUS: ❌ NOT READY"
    echo "   Fix the errors above first"
fi
echo "=================================================="
echo ""
