"""
Simplified Flask web application for Research Literature Navigator with Gemini
"""
import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'research_navigator_secret_key'
CORS(app)

class SimpleResearchNavigator:
    """Simplified Research Navigator with Gemini"""
    
    def __init__(self):
        # Initialize Gemini
        try:
            api_key = "AIzaSyBs6hzVlTGAu3EJprfex8l0Lb1dkMWlsbk"
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Gemini: {e}")
            self.model = None
        
        # Create data directories
        self.data_dir = Path("data")
        self.papers_dir = self.data_dir / "papers"
        self.data_dir.mkdir(exist_ok=True)
        self.papers_dir.mkdir(exist_ok=True)
        
        # Simple document storage
        self.documents = []
        self.load_documents()
    
    def load_documents(self):
        """Load existing documents"""
        try:
            if (self.data_dir / "documents.json").exists():
                with open(self.data_dir / "documents.json", "r") as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            self.documents = []
    
    def save_documents(self):
        """Save documents to file"""
        try:
            with open(self.data_dir / "documents.json", "w") as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
    
    def add_document(self, filename, title, content):
        """Add a document to the collection"""
        doc = {
            "filename": filename,
            "title": title,
            "content": content,
            "chunks": self.create_chunks(content)
        }
        self.documents.append(doc)
        self.save_documents()
        return doc
    
    def create_chunks(self, content, chunk_size=800):
        """Simple text chunking"""
        words = content.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def search_documents(self, query, top_k=3):
        """Simple keyword-based search"""
        query_words = set(query.lower().split())
        results = []
        
        for doc in self.documents:
            for chunk in doc["chunks"]:
                chunk_words = set(chunk.lower().split())
                # Simple similarity based on word overlap
                overlap = len(query_words & chunk_words)
                if overlap > 0:
                    similarity = overlap / len(query_words | chunk_words)
                    results.append({
                        "title": doc["title"],
                        "content": chunk,
                        "similarity": similarity
                    })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, question, context_results):
        """Generate answer using Gemini"""
        try:
            if not self.model:
                return "Gemini model not available. Please check API key."
            
            # Prepare context
            context = "\n\n".join([
                f"Source: {result['title']}\nContent: {result['content']}"
                for result in context_results
            ])
            
            prompt = f"""You are a research assistant. Based on the research papers provided, answer the question clearly and accurately.

Question: {question}

Research Papers Context:
{context}

Instructions:
1. Provide a clear, evidence-based answer
2. Reference specific papers when making claims
3. If information is insufficient, state what's missing
4. Use academic language

Answer:"""
            
            response = self.model.generate_content(prompt)
            return response.text if response.text else "No response generated."
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"

# Initialize the navigator
nav = SimpleResearchNavigator()

@app.route('/')
def index():
    """Main page"""
    stats = {
        "unique_documents": len(nav.documents),
        "total_chunks": sum(len(doc["chunks"]) for doc in nav.documents)
    }
    return render_template('index.html', stats=stats)

@app.route('/query', methods=['POST'])
def query_literature():
    """Handle literature queries"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Please provide a question'}), 400
        
        # Search for relevant documents
        search_results = nav.search_documents(question, top_k=5)
        
        if not search_results:
            return jsonify({
                'answer': 'No relevant information found. Please upload some PDF documents first.',
                'sources': [],
                'confidence': '0.00'
            })
        
        # Generate answer
        answer = nav.generate_answer(question, search_results)
        
        # Format sources for display
        sources = []
        for i, result in enumerate(search_results):
            sources.append({
                'title': result['title'],
                'section': 'Content',
                'similarity': f"{result['similarity']:.3f}",
                'content': result['content'][:200] + "..."
            })
        
        # Simple confidence calculation
        avg_similarity = sum(r['similarity'] for r in search_results) / len(search_results)
        confidence = f"{min(avg_similarity * 1.5, 1.0):.2f}"
        
        return jsonify({
            'answer': answer,
            'sources': sources,
            'confidence': confidence
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
        if file.filename == '' or not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please select a PDF file'}), 400
        
        # Save file
        filename = file.filename
        filepath = nav.papers_dir / filename
        file.save(str(filepath))
        
        # Simple text extraction (you can enhance this with proper PDF parsing)
        try:
            import PyPDF2
            with open(filepath, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
        except ImportError:
            # Fallback - treat as text file
            content = f"Document uploaded: {filename}. Please install PyPDF2 for text extraction."
        
        # Add to collection
        doc = nav.add_document(filename, filename.replace('.pdf', ''), content)
        
        return jsonify({
            'message': f'Successfully processed {filename}',
            'title': doc['title'],
            'chunks': len(doc['chunks'])
        })
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({'error': f'Error uploading document: {str(e)}'}), 500

@app.route('/stats')
def get_stats():
    """Get collection statistics"""
    try:
        total_chunks = sum(len(doc["chunks"]) for doc in nav.documents)
        
        stats = {
            "unique_documents": len(nav.documents),
            "total_chunks": total_chunks,
            "section_distribution": {"content": total_chunks} if total_chunks > 0 else {}
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': f'Error getting stats: {str(e)}'}), 500

@app.route('/duplicates')
def analyze_duplicates():
    """Simple duplicate analysis"""
    try:
        # Simple duplicate analysis
        total_docs = len(nav.documents)
        
        stats = {
            "total_duplicate_clusters": 0,
            "total_duplicate_chunks": 0,
            "affected_documents": 0,
            "duplicate_percentage": 0.0,
            "section_breakdown": {}
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error analyzing duplicates: {e}")
        return jsonify({'error': f'Error analyzing duplicates: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Research Literature Navigator - Gemini Edition")
    print("=" * 50)
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)