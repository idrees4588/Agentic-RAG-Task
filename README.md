# Research Literature Navigator

An AI-powered assistant for navigating and analyzing scientific literature using Retrieval-Augmented Generation (RAG). This system helps researchers, students, and academics quickly find relevant methods, results, and evidence across large sets of scientific papers.

## 🚀 Key Features

### Core Capabilities
- **📄 Section-Aware Retrieval**: Search within specific sections (abstract, methods, results, discussion)
- **🖼️ Figure/Table Linking**: Connect figure captions with surrounding textual context
- **🎯 Evidence Grounding**: Generate answers with inline citations and DOI/arXiv references
- **🔍 Duplicate Detection**: Identify overlapping findings and similar content across papers
- **⚖️ Cross-Paper Comparison**: Side-by-side analysis of methodologies and results
- **🤖 Natural Language Queries**: Ask questions in plain English about your research corpus

### Advanced Features
- **🧠 Query Type Detection**: Automatically detects whether you're asking about methods, results, or comparisons
- **📊 Confidence Scoring**: Each answer includes a confidence score based on evidence quality
- **📚 Citation Management**: Automatic generation of properly formatted citations
- **🔄 Hybrid Retrieval**: Combines multiple search strategies for comprehensive results
- **📈 Analytics Dashboard**: Track duplicate content and collection statistics

## 🎯 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python quickstart.py
```
This script will:
- Check dependencies and install missing packages
- Set up configuration files
- Create necessary directories
- Launch the application

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the Application**
   ```bash
   streamlit run src/app.py
   ```

## 📁 Project Structure

```
research-literature-navigator/
├── src/                    # Main source code
│   ├── core/              # Core models and configuration
│   │   ├── config.py      # System configuration
│   │   └── models.py      # Data models and enums
│   ├── ingestion/         # PDF processing pipeline
│   │   ├── pdf_parser.py      # PDF text extraction
│   │   ├── section_detector.py # Section identification
│   │   └── document_processor.py # Main processing logic
│   ├── retrieval/         # Vector search and retrieval
│   │   ├── vector_store.py    # Chroma database interface
│   │   └── retriever.py       # Section-aware retrieval
│   ├── generation/        # Answer generation system
│   │   ├── llm_handler.py     # LLM interaction
│   │   ├── citation_manager.py # Citation formatting
│   │   └── answer_generator.py # Main generation logic
│   ├── utils/             # Utility functions
│   │   ├── chunking.py        # Text chunking and embedding
│   │   └── duplicate_detection.py # Similarity analysis
│   └── app.py             # Streamlit web interface
├── data/                  # Data storage
│   ├── papers/           # Input PDF files
│   └── chroma_db/        # Vector database storage
├── quickstart.py         # Automated setup script
├── demo.py              # Interactive demonstration
├── test_system.py       # System validation tests
├── requirements.txt     # Python dependencies
├── .env.example        # Configuration template
└── README.md           # This file
```

## 🎮 Usage Guide

### Getting Started
1. **📁 Add Research Papers**: Upload PDF files through the web interface or place them in `data/papers/`
2. **⚙️ Process Documents**: Use the "Document Management" tab to process and index your papers
3. **❓ Ask Questions**: Use the main "Query Literature" interface for natural language questions
4. **📊 Analyze Results**: Review answers with citations, confidence scores, and supporting evidence

### Example Queries

#### 🔬 Methodology Questions
- "What deep learning architectures were used for deepfake detection?"
- "How did the authors evaluate their model's performance?"
- "What datasets were used in the training process?"

#### 📈 Results & Findings
- "What accuracy did the proposed method achieve?"
- "How does this approach compare to existing baselines?"
- "What were the main limitations identified by the authors?"

#### 🖼️ Figure & Table Analysis
- "What do Figure 3 and Table 2 show about model performance?"
- "Find all accuracy comparison charts"
- "Show me visualization of the experimental results"

#### ⚖️ Cross-Paper Comparisons
- "Compare transformer architectures across these papers"
- "What are the common themes in recent computer vision research?"
- "How do different papers approach the same problem?"

### ⚙️ Configuration Options

Edit the `.env` file to customize:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional - Processing Parameters
MAX_CHUNK_SIZE=900          # Maximum text chunk size
MIN_CHUNK_SIZE=600          # Minimum text chunk size  
CHUNK_OVERLAP=100           # Overlap between chunks

# Optional - Retrieval Settings
TOP_K_RESULTS=5             # Number of results to retrieve
SIMILARITY_THRESHOLD=0.7    # Minimum similarity for results

# Optional - System Settings
DEBUG=True                  # Enable debug logging
```

## 🧪 Testing & Validation

### Run System Tests
```bash
python test_system.py
```
This validates all components and provides a health check of your installation.

### Interactive Demo
```bash
python demo.py
```
Explore system features with guided demonstrations and interactive queries.

### Web Interface
```bash
streamlit run src/app.py
```
Access the full-featured web application at `http://localhost:8501`

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for large document collections)
- **Storage**: 1GB for system + space for your PDF collection
- **API Access**: OpenAI API key (required for answer generation)

## 📊 Performance Characteristics

- **Document Processing**: ~1-2 minutes per PDF (depending on size)
- **Query Response**: 2-5 seconds for typical queries
- **Embedding Model**: 384-dimensional vectors (all-MiniLM-L6-v2)
- **Supported Formats**: PDF files with extractable text
- **Scalability**: Tested with collections up to 1000+ papers

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`python test_system.py`)
5. Submit a pull request

### Areas for Contribution
- Additional document formats (Word, LaTeX, etc.)
- Enhanced section detection algorithms
- More sophisticated duplicate detection
- Integration with academic databases
- Multi-language support

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support & Troubleshooting

### Common Issues

1. **"No module named 'X'"**: Run `pip install -r requirements.txt`
2. **"OpenAI API key required"**: Add your API key to the `.env` file
3. **"No PDF files found"**: Add PDF files to `data/papers/` directory
4. **Poor answer quality**: Ensure PDFs have extractable text (not scanned images)

### Getting Help

- Check the demo script: `python demo.py`
- Run system tests: `python test_system.py`
- Review configuration: `.env` file settings
- Check logs: Enable debug mode in `.env`

---

**Built with**: LangChain, ChromaDB, Sentence Transformers, Streamlit, and OpenAI

**Research Areas**: Information Retrieval, Natural Language Processing, Scientific Literature Analysis