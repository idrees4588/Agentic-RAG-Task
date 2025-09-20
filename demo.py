"""
Demo script for Research Literature Navigator
This script demonstrates the key features of the system
"""
import sys
import os
from pathlib import Path
import time

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

import logging
from core.config import Config
from ingestion.document_processor import DocumentProcessor
from utils.chunking import ChunkingAndEmbeddingPipeline
from retrieval.vector_store import VectorStore
from retrieval.retriever import SectionAwareRetriever
from generation.answer_generator import AnswerGenerator
from utils.duplicate_detection import DuplicateDetector

# Configure logging for demo
logging.basicConfig(level=logging.WARNING)  # Reduce log noise for demo

class ResearchNavigatorDemo:
    """Demonstration of Research Literature Navigator capabilities"""
    
    def __init__(self):
        print("🚀 Research Literature Navigator - Interactive Demo")
        print("=" * 60)
        
        # Initialize system
        print("📚 Initializing system components...")
        
        try:
            Config.ensure_directories()
            
            self.document_processor = DocumentProcessor()
            self.chunking_pipeline = ChunkingAndEmbeddingPipeline()
            self.vector_store = VectorStore()
            self.retriever = SectionAwareRetriever(self.vector_store)
            self.answer_generator = AnswerGenerator(self.retriever)
            self.duplicate_detector = DuplicateDetector(self.vector_store)
            
            print("✅ System initialized successfully!")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            print("Please ensure .env file is configured with API keys")
            sys.exit(1)
    
    def show_system_status(self):
        """Display current system status"""
        print("\n📊 System Status")
        print("-" * 30)
        
        try:
            stats = self.vector_store.get_collection_stats()
            print(f"📄 Documents in collection: {stats.get('unique_documents', 0)}")
            print(f"📝 Total chunks: {stats.get('total_chunks', 0)}")
            
            if stats.get('section_distribution'):
                print("📂 Section distribution:")
                for section, count in stats['section_distribution'].items():
                    print(f"   - {section.title()}: {count}")
            
            # Check available PDFs
            papers_dir = Path(Config.PAPERS_DIR)
            pdf_files = list(papers_dir.glob("*.pdf"))
            print(f"🗂️ PDF files available: {len(pdf_files)}")
            
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
    
    def demo_document_processing(self):
        """Demonstrate document processing"""
        print("\n🔄 Document Processing Demo")
        print("-" * 40)
        
        papers_dir = Path(Config.PAPERS_DIR)
        pdf_files = list(papers_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found for processing demo")
            print(f"Please add PDF files to: {papers_dir}")
            return False
        
        # Process first available PDF
        test_file = pdf_files[0]
        print(f"📖 Processing: {test_file.name}")
        
        try:
            # Process document
            processed_doc = self.document_processor.process_document(str(test_file))
            
            if processed_doc:
                print(f"✅ Successfully processed document")
                print(f"   📝 Title: {processed_doc.metadata.title}")
                print(f"   👥 Authors: {', '.join(processed_doc.metadata.authors[:3])}...")
                print(f"   📄 Chunks created: {len(processed_doc.chunks)}")
                
                # Create embeddings and add to vector store
                print("🔢 Creating embeddings...")
                chunks = self.chunking_pipeline.process_single_document(processed_doc)
                
                print("💾 Adding to vector database...")
                success = self.vector_store.add_documents(chunks)
                
                if success:
                    print(f"✅ Added {len(chunks)} chunks to database")
                    return True
                else:
                    print("❌ Failed to add to database")
                    return False
            else:
                print("❌ Document processing failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            return False
    
    def demo_retrieval_system(self):
        """Demonstrate retrieval capabilities"""
        print("\n🔍 Retrieval System Demo")
        print("-" * 40)
        
        # Test different types of queries
        test_queries = [
            ("General Query", "What is this research about?"),
            ("Methods Query", "What methodology was used?"),
            ("Results Query", "What were the main findings?"),
            ("Figures Query", "What do the figures show?")
        ]
        
        for query_type, query in test_queries:
            print(f"\n📋 {query_type}: '{query}'")
            
            try:
                results = self.retriever.retrieve(query, top_k=3)
                
                if results:
                    print(f"   ✅ Found {len(results)} results")
                    
                    # Show top result
                    top_result = results[0]
                    print(f"   🏆 Top result (similarity: {top_result.similarity_score:.3f}):")
                    print(f"      📖 From: {top_result.document_metadata.title[:50]}...")
                    print(f"      📝 Section: {top_result.chunk.section_type.value}")
                    print(f"      💬 Content: {top_result.chunk.content[:100]}...")
                else:
                    print("   ❌ No results found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
    
    def demo_answer_generation(self):
        """Demonstrate answer generation with citations"""
        print("\n💡 Answer Generation Demo")
        print("-" * 40)
        
        # Test comprehensive answer generation
        test_query = "What are the key contributions and findings of this research?"
        
        print(f"❓ Question: {test_query}")
        print("\n🤖 Generating comprehensive answer...")
        
        try:
            result = self.answer_generator.generate_answer(
                query=test_query,
                top_k=5,
                include_evidence_grounding=True
            )
            
            if result and result.answer:
                print("\n📝 Generated Answer:")
                print("-" * 20)
                print(result.answer)
                
                print(f"\n📊 Answer Statistics:")
                print(f"   🎯 Confidence Score: {result.confidence_score:.3f}")
                print(f"   📚 Citations: {len(result.citations)}")
                print(f"   🔍 Evidence Chunks: {len(result.evidence_chunks)}")
                
                if result.citations:
                    print(f"\n📖 Citations:")
                    for i, citation in enumerate(result.citations[:3], 1):
                        print(f"   [{i}] {citation.get('title', 'Unknown')[:50]}...")
                        print(f"       Section: {citation.get('section', 'N/A')}")
                        print(f"       Similarity: {citation.get('similarity_score', 0):.3f}")
                
                return True
            else:
                print("❌ Failed to generate answer")
                return False
                
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return False
    
    def demo_duplicate_detection(self):
        """Demonstrate duplicate detection"""
        print("\n🔄 Duplicate Detection Demo")
        print("-" * 40)
        
        try:
            print("🔍 Analyzing collection for duplicates...")
            
            # Get duplicate statistics
            stats = self.duplicate_detector.get_duplicate_statistics()
            
            print(f"📊 Duplicate Analysis Results:")
            print(f"   🔢 Total clusters: {stats.get('total_duplicate_clusters', 0)}")
            print(f"   📝 Duplicate chunks: {stats.get('total_duplicate_chunks', 0)}")
            print(f"   📄 Affected documents: {stats.get('affected_documents', 0)}")
            print(f"   📈 Duplicate percentage: {stats.get('duplicate_percentage', 0):.1f}%")
            
            if stats.get('section_breakdown'):
                print(f"   📂 By section type:")
                for section, data in stats['section_breakdown'].items():
                    print(f"      - {section}: {data['clusters']} clusters")
            
            # Try to detect actual duplicates
            duplicates = self.duplicate_detector.detect_duplicates_in_collection()
            
            if duplicates:
                print(f"\n🔍 Found {len(duplicates)} duplicate clusters:")
                
                for i, cluster in enumerate(duplicates[:3], 1):  # Show first 3
                    print(f"\n   Cluster {i}:")
                    print(f"   📏 Size: {cluster.cluster_size} chunks")
                    print(f"   📊 Avg similarity: {cluster.avg_similarity:.3f}")
                    print(f"   📄 Documents: {len(cluster.document_ids)}")
                    print(f"   💬 Sample: {cluster.representative_chunk.content[:80]}...")
            else:
                print("\n✅ No significant duplicates found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in duplicate detection: {e}")
            return False
    
    def interactive_query_session(self):
        """Interactive query session"""
        print("\n💬 Interactive Query Session")
        print("-" * 40)
        print("Ask questions about your research literature!")
        print("Type 'quit', 'exit', or 'q' to end the session")
        print()
        
        while True:
            try:
                query = input("❓ Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q', '']:
                    print("👋 Ending interactive session")
                    break
                
                print("\n🤖 Thinking...")
                
                result = self.answer_generator.generate_answer(
                    query=query,
                    top_k=3
                )
                
                if result and result.answer:
                    print(f"\n💡 Answer (confidence: {result.confidence_score:.2f}):")
                    print("-" * 30)
                    print(result.answer)
                    
                    if result.citations:
                        print(f"\n📚 Based on {len(result.citations)} sources")
                    
                    print("\n" + "="*50)
                else:
                    print("❌ Sorry, I couldn't generate an answer for that question.")
                
            except KeyboardInterrupt:
                print("\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run_complete_demo(self):
        """Run the complete demonstration"""
        print("\n🎬 Starting Complete Demo")
        print("=" * 60)
        
        demos = [
            ("System Status", self.show_system_status),
            ("Document Processing", self.demo_document_processing),
            ("Retrieval System", self.demo_retrieval_system),
            ("Answer Generation", self.demo_answer_generation),
            ("Duplicate Detection", self.demo_duplicate_detection)
        ]
        
        for demo_name, demo_func in demos:
            print(f"\n▶️ Running {demo_name} Demo...")
            
            try:
                success = demo_func()
                if success:
                    print(f"✅ {demo_name} demo completed successfully")
                else:
                    print(f"⚠️ {demo_name} demo had issues")
                
                # Wait for user input
                input(f"\n⏸️ Press Enter to continue to next demo...")
                
            except Exception as e:
                print(f"❌ {demo_name} demo failed: {e}")
                continue
        
        print("\n🎉 All demos completed!")
        
        # Offer interactive session
        response = input("\n💬 Would you like to try the interactive query session? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            self.interactive_query_session()

def main():
    """Main demo function"""
    print("🔬 Research Literature Navigator - Interactive Demo")
    print("This demo showcases the key features of the system")
    print()
    
    # Check environment
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please run quickstart.py first.")
        return False
    
    try:
        demo = ResearchNavigatorDemo()
        
        print("\n🎯 Demo Options:")
        print("1. Complete demo (all features)")
        print("2. Quick interactive session")
        print("3. System status only")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            demo.run_complete_demo()
        elif choice == "2":
            demo.show_system_status()
            demo.interactive_query_session()
        elif choice == "3":
            demo.show_system_status()
        else:
            print("Invalid choice. Running complete demo...")
            demo.run_complete_demo()
        
        print("\n🏁 Demo completed successfully!")
        print("\n📚 To use the full web interface, run: streamlit run src/app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)