"""
Test script for the Research Literature Navigator system
"""
import sys
import os
from pathlib import Path

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemTester:
    """Test suite for the Research Literature Navigator"""
    
    def __init__(self):
        """Initialize test components"""
        logger.info("Initializing Research Literature Navigator test suite...")
        
        # Ensure configuration is valid
        try:
            Config.ensure_directories()
            Config.validate_config()
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            logger.info("Please ensure your .env file is configured with required API keys")
            return
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.chunking_pipeline = ChunkingAndEmbeddingPipeline()
        self.vector_store = VectorStore()
        self.retriever = SectionAwareRetriever(self.vector_store)
        self.answer_generator = AnswerGenerator(self.retriever)
        self.duplicate_detector = DuplicateDetector(self.vector_store)
        
        logger.info("✅ System components initialized successfully")
    
    def test_document_processing(self):
        """Test document processing pipeline"""
        logger.info("🧪 Testing document processing...")
        
        # Check if there are any PDF files to process
        papers_dir = Path(Config.PAPERS_DIR)
        pdf_files = list(papers_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning("❌ No PDF files found in papers directory")
            logger.info(f"Please add PDF files to: {papers_dir}")
            return False
        
        # Process first PDF file
        test_file = pdf_files[0]
        logger.info(f"Processing test file: {test_file.name}")
        
        try:
            # Process document
            processed_doc = self.document_processor.process_document(str(test_file))
            
            if processed_doc:
                logger.info(f"✅ Successfully processed document: {processed_doc.metadata.title}")
                logger.info(f"   - Document ID: {processed_doc.id}")
                logger.info(f"   - Number of chunks: {len(processed_doc.chunks)}")
                logger.info(f"   - Authors: {', '.join(processed_doc.metadata.authors)}")
                return True
            else:
                logger.error("❌ Failed to process document")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing document: {e}")
            return False
    
    def test_chunking_and_embedding(self):
        """Test chunking and embedding pipeline"""
        logger.info("🧪 Testing chunking and embedding...")
        
        # Check if we have any processed documents
        papers_dir = Path(Config.PAPERS_DIR)
        pdf_files = list(papers_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning("❌ No PDF files available for testing")
            return False
        
        try:
            # Process a document
            test_file = pdf_files[0]
            processed_doc = self.document_processor.process_document(str(test_file))
            
            if not processed_doc:
                logger.error("❌ Could not process document for chunking test")
                return False
            
            # Test chunking and embedding
            chunks = self.chunking_pipeline.process_single_document(processed_doc)
            
            if chunks:
                logger.info(f"✅ Successfully created {len(chunks)} chunks with embeddings")
                
                # Show sample chunk info
                sample_chunk = chunks[0]
                logger.info(f"   - Sample chunk text length: {len(sample_chunk['text'])}")
                logger.info(f"   - Embedding dimension: {len(sample_chunk['embedding'])}")
                logger.info(f"   - Metadata keys: {list(sample_chunk['metadata'].keys())}")
                return True
            else:
                logger.error("❌ No chunks created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in chunking/embedding: {e}")
            return False
    
    def test_vector_store(self):
        """Test vector store operations"""
        logger.info("🧪 Testing vector store...")
        
        try:
            # Get collection stats
            stats = self.vector_store.get_collection_stats()
            logger.info(f"✅ Vector store initialized")
            logger.info(f"   - Total chunks: {stats.get('total_chunks', 0)}")
            logger.info(f"   - Unique documents: {stats.get('unique_documents', 0)}")
            
            # If empty, try to add a test document
            if stats.get('total_chunks', 0) == 0:
                logger.info("📝 Collection is empty, adding test document...")
                
                papers_dir = Path(Config.PAPERS_DIR)
                pdf_files = list(papers_dir.glob("*.pdf"))
                
                if pdf_files:
                    test_file = pdf_files[0]
                    processed_doc = self.document_processor.process_document(str(test_file))
                    
                    if processed_doc:
                        chunks = self.chunking_pipeline.process_single_document(processed_doc)
                        success = self.vector_store.add_documents(chunks)
                        
                        if success:
                            logger.info(f"✅ Successfully added {len(chunks)} chunks to vector store")
                        else:
                            logger.error("❌ Failed to add chunks to vector store")
                            return False
                    else:
                        logger.error("❌ Could not process document for vector store test")
                        return False
                else:
                    logger.warning("❌ No PDF files available for vector store test")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error testing vector store: {e}")
            return False
    
    def test_retrieval(self):
        """Test retrieval system"""
        logger.info("🧪 Testing retrieval system...")
        
        try:
            # Test queries
            test_queries = [
                "What methods were used?",
                "What were the main results?",
                "How was the evaluation performed?"
            ]
            
            for query in test_queries:
                logger.info(f"   Testing query: '{query}'")
                
                results = self.retriever.retrieve(query, top_k=3)
                
                if results:
                    logger.info(f"   ✅ Retrieved {len(results)} results")
                    logger.info(f"   - Top similarity score: {results[0].similarity_score:.3f}")
                else:
                    logger.warning(f"   ⚠️ No results for query: '{query}'")
            
            logger.info("✅ Retrieval system test completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error testing retrieval: {e}")
            return False
    
    def test_answer_generation(self):
        """Test answer generation"""
        logger.info("🧪 Testing answer generation...")
        
        try:
            test_query = "What are the main findings of this research?"
            
            logger.info(f"Generating answer for: '{test_query}'")
            
            result = self.answer_generator.generate_answer(
                query=test_query,
                top_k=3
            )
            
            if result and result.answer:
                logger.info("✅ Successfully generated answer")
                logger.info(f"   - Answer length: {len(result.answer)} characters")
                logger.info(f"   - Number of citations: {len(result.citations)}")
                logger.info(f"   - Confidence score: {result.confidence_score:.3f}")
                logger.info(f"   - Answer preview: {result.answer[:100]}...")
                return True
            else:
                logger.error("❌ Failed to generate answer")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing answer generation: {e}")
            return False
    
    def test_duplicate_detection(self):
        """Test duplicate detection"""
        logger.info("🧪 Testing duplicate detection...")
        
        try:
            # Get duplicate statistics
            stats = self.duplicate_detector.get_duplicate_statistics()
            
            logger.info("✅ Duplicate detection system working")
            logger.info(f"   - Total duplicate clusters: {stats.get('total_duplicate_clusters', 0)}")
            logger.info(f"   - Total duplicate chunks: {stats.get('total_duplicate_chunks', 0)}")
            logger.info(f"   - Duplicate percentage: {stats.get('duplicate_percentage', 0):.1f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error testing duplicate detection: {e}")
            return False
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        logger.info("🚀 Running Research Literature Navigator test suite...")
        logger.info("=" * 60)
        
        tests = [
            ("Document Processing", self.test_document_processing),
            ("Chunking & Embedding", self.test_chunking_and_embedding),
            ("Vector Store", self.test_vector_store),
            ("Retrieval System", self.test_retrieval),
            ("Answer Generation", self.test_answer_generation),
            ("Duplicate Detection", self.test_duplicate_detection)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Running {test_name} test...")
            try:
                success = test_func()
                results[test_name] = success
                status = "✅ PASSED" if success else "❌ FAILED"
                logger.info(f"{test_name}: {status}")
            except Exception as e:
                logger.error(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            logger.info(f"{test_name:.<30} {status}")
        
        logger.info("-" * 40)
        logger.info(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! System is ready to use.")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Please check the logs above.")
            
        return passed == total

def main():
    """Main test runner"""
    print("🔬 Research Literature Navigator - System Test")
    print("=" * 50)
    
    # Check environment
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    try:
        tester = SystemTester()
        return tester.run_full_test_suite()
    except Exception as e:
        logger.error(f"Test suite crashed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)