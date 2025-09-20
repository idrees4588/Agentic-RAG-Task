"""
Quick start script for Research Literature Navigator
"""
import sys
import os
from pathlib import Path

def setup_environment():
    """Set up the environment for running the application"""
    print("🚀 Research Literature Navigator - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    required_files = ["requirements.txt", "src/app.py", ".env.example"]
    
    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please run this script from the project root directory")
        return False
    
    print("✅ Project structure verified")
    
    # Check .env file
    env_file = current_dir / ".env"
    env_example = current_dir / ".env.example"
    
    if not env_file.exists():
        print("⚠️ .env file not found")
        
        if env_example.exists():
            print("📝 Creating .env file from .env.example...")
            try:
                import shutil
                shutil.copy(env_example, env_file)
                print("✅ .env file created")
                print("🔧 Please edit .env file and add your API keys:")
                print("   - OPENAI_API_KEY (required for answer generation)")
                print("   - Other settings are optional")
            except Exception as e:
                print(f"❌ Error creating .env file: {e}")
                return False
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file found")
    
    # Check if dependencies are installed
    print("📦 Checking dependencies...")
    
    missing_deps = []
    required_packages = [
        "streamlit", "langchain", "chromadb", "sentence-transformers",
        "pdfplumber", "numpy", "pandas", "python-dotenv"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_deps.append(package)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Installing dependencies...")
        
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies installed successfully")
            else:
                print(f"❌ Error installing dependencies: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            print("Please run: pip install -r requirements.txt")
            return False
    else:
        print("✅ All dependencies are installed")
    
    return True

def create_sample_content():
    """Create sample content for testing"""
    print("\n📁 Setting up directories...")
    
    try:
        # Add src to Python path
        current_dir = Path.cwd()
        src_dir = current_dir / "src"
        sys.path.insert(0, str(src_dir))
        
        from core.config import Config
        
        # Ensure directories exist
        Config.ensure_directories()
        print("✅ Data directories created")
        
        # Check if there are any PDF files
        papers_dir = Path(Config.PAPERS_DIR)
        pdf_files = list(papers_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"📄 No PDF files found in {papers_dir}")
            print("To get started:")
            print(f"   1. Add PDF research papers to: {papers_dir}")
            print("   2. Use the 'Document Management' page in the app to upload files")
        else:
            print(f"✅ Found {len(pdf_files)} PDF files in papers directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up directories: {e}")
        return False

def run_application():
    """Run the Streamlit application"""
    print("\n🌐 Starting Research Literature Navigator...")
    
    try:
        import subprocess
        
        # Get the path to the app
        current_dir = Path.cwd()
        app_path = current_dir / "src" / "app.py"
        
        if not app_path.exists():
            print(f"❌ App file not found: {app_path}")
            return False
        
        print("🚀 Launching Streamlit application...")
        print("📱 The application will open in your default web browser")
        print("🔗 URL: http://localhost:8501")
        print("\n⏹️ Press Ctrl+C to stop the application")
        print("-" * 50)
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path)
        ])
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return False

def main():
    """Main quick start function"""
    try:
        # Setup environment
        if not setup_environment():
            print("\n❌ Environment setup failed")
            return False
        
        # Create sample content
        if not create_sample_content():
            print("\n❌ Content setup failed")
            return False
        
        print("\n✅ Setup complete!")
        print("\n🎯 What you can do now:")
        print("   1. Upload PDF research papers")
        print("   2. Ask questions about your literature")
        print("   3. Find similar content and duplicates")
        print("   4. Generate grounded answers with citations")
        
        # Ask if user wants to run the app
        response = input("\n🚀 Would you like to start the application now? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            run_application()
        else:
            print("\n📖 To start the application later, run:")
            print("   streamlit run src/app.py")
            print("\n📚 Or run system tests with:")
            print("   python test_system.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Quick start failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n🔧 Need help? Check:")
        print("   - README.md for detailed setup instructions")
        print("   - .env.example for configuration options")
        print("   - requirements.txt for dependency list")
    
    sys.exit(0 if success else 1)