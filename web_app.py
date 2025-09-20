"""
Flask web application for Research Literature Navigator with HTML/CSS UI
"""
import sys
import os
from pathlib import Path
import json
import logging

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import google.generativeai as genai

# Import our components
from core.config import Config
from core.models import QueryType, SectionType
from ingestion.document_processor import DocumentProcessor
from utils.chunking import ChunkingAndEmbeddingPipeline
from retrieval.vector_store import VectorStore
from retrieval.retriever import SectionAwareRetriever
from utils.duplicate_detection import DuplicateDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'research_navigator_secret_key'
CORS(app)

class SimpleGeminiHandler:
    """Simple Gemini handler for web app"""
    
    def __init__(self):
        try:
            # Use the provided API key
            api_key = "AIzaSyBs6hzVlTGAu3EJprfex8l0Lb1dkMWlsbk"
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Gemini: {e}")
            self.model = None
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using Gemini"""
        try:
            if not self.model:
                return "Gemini model not available. Please check API key."
            
            prompt = f"""You are a research assistant. Based on the following research context, answer the question clearly and accurately.

Question: {question}

Research Context:
{context}

Instructions:
1. Provide a clear, evidence-based answer
2. Reference specific details from the context
3. If information is insufficient, state what's missing
4. Use academic language

Answer:"""
            
            response = self.model.generate_content(prompt)
            return response.text if response.text else "No response generated."
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

class ResearchNavigatorWebApp:
    """Web application for Research Literature Navigator"""
    
    def __init__(self):
        try:
            Config.ensure_directories()
            
            self.document_processor = DocumentProcessor()
            self.chunking_pipeline = ChunkingAndEmbeddingPipeline()
            self.vector_store = VectorStore()
            self.retriever = SectionAwareRetriever(self.vector_store)
            self.gemini_handler = SimpleGeminiHandler()
            self.duplicate_detector = DuplicateDetector(self.vector_store)
            
            logger.info("Research Navigator Web App initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing web app: {e}")
            raise

# Initialize the app
try:
    nav_app = ResearchNavigatorWebApp()
except Exception as e:
    logger.error(f"Failed to initialize app: {e}")
    nav_app = None

@app.route('/')
def index():
    """Main page"""
    try:
        # Get collection stats
        stats = nav_app.vector_store.get_collection_stats() if nav_app else {}
        return render_template('index.html', stats=stats)
    except Exception as e:
        flash(f"Error loading page: {e}", "error")
        return render_template('index.html', stats={})

@app.route('/query', methods=['POST'])
def query_literature():
    """Handle literature queries"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Please provide a question'}), 400
        
        if not nav_app:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Retrieve relevant documents
        results = nav_app.retriever.retrieve(question, top_k=5)
        
        if not results:
            return jsonify({
                'answer': 'No relevant information found in the document collection.',
                'sources': [],
                'confidence': 0.0
            })
        
        # Prepare context
        context_parts = []
        sources = []
        
        for i, result in enumerate(results):
            context_parts.append(f"Source {i+1}: {result.chunk.content}")
            sources.append({
                'title': result.document_metadata.title,
                'section': result.chunk.section_type.value,
                'similarity': f"{result.similarity_score:.3f}",
                'content': result.chunk.content[:200] + "..."
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        answer = nav_app.gemini_handler.generate_answer(question, context)
        
        # Calculate confidence (simplified)
        avg_similarity = sum(r.similarity_score for r in results) / len(results)
        confidence = min(avg_similarity * 1.2, 1.0)
        
        return jsonify({
            'answer': answer,
            'sources': sources,
            'confidence': f"{confidence:.2f}"
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        if not nav_app:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Save file
        filename = file.filename
        filepath = Config.PAPERS_DIR / filename
        file.save(str(filepath))
        
        # Process document
        processed_doc = nav_app.document_processor.process_document(str(filepath))
        
        if processed_doc:
            # Create chunks and embeddings
            chunks = nav_app.chunking_pipeline.process_single_document(processed_doc)
            
            # Add to vector store
            success = nav_app.vector_store.add_documents(chunks)
            
            if success:
                return jsonify({
                    'message': f'Successfully processed {filename}',
                    'title': processed_doc.metadata.title,
                    'chunks': len(chunks)
                })
            else:
                return jsonify({'error': 'Failed to add document to database'}), 500
        else:
            return jsonify({'error': 'Failed to process document'}), 500
            
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({'error': f'Error uploading document: {str(e)}'}), 500

@app.route('/stats')
def get_stats():
    """Get collection statistics"""
    try:
        if not nav_app:
            return jsonify({'error': 'System not initialized'}), 500
        
        stats = nav_app.vector_store.get_collection_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': f'Error getting stats: {str(e)}'}), 500

@app.route('/duplicates')
def analyze_duplicates():
    """Analyze duplicates in collection"""
    try:
        if not nav_app:
            return jsonify({'error': 'System not initialized'}), 500
        
        # Get duplicate statistics
        stats = nav_app.duplicate_detector.get_duplicate_statistics()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error analyzing duplicates: {e}")
        return jsonify({'error': f'Error analyzing duplicates: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)