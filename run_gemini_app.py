"""
Simple launcher for Research Literature Navigator with Gemini and HTML/CSS UI
"""
import sys
import os
import subprocess
from pathlib import Path

def setup_environment():
    """Set up the environment"""
    print("🚀 Research Literature Navigator - Gemini Edition")
    print("=" * 50)
    
    # Check if .env exists, if not create it
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file with Gemini API key...")
        with open(".env", "w") as f:
            f.write("GEMINI_API_KEY=AIzaSyBs6hzVlTGAu3EJprfex8l0Lb1dkMWlsbk\n")
            f.write("FLASK_PORT=5000\n")
            f.write("DEBUG=True\n")
        print("✅ .env file created")
    
    # Install required packages
    print("📦 Installing required packages...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "flask", "flask-cors", "google-generativeai", 
            "chromadb", "sentence-transformers", "pdfplumber", 
            "pymupdf", "python-dotenv", "numpy", "pandas",
            "scikit-learn", "nltk", "tqdm"
        ], check=True, capture_output=True)
        print("✅ Packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["data", "data/papers", "data/chroma_db"]
    
    for dir_path in directories:
        Path(dir_path).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def run_web_app():
    """Run the Flask web application"""
    print("\n🌐 Starting Research Literature Navigator Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "web_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running web app: {e}")

def main():
    """Main function"""
    if not setup_environment():
        print("❌ Setup failed")
        return
    
    create_directories()
    
    print("\n✅ Setup complete!")
    print("\n🎯 Features available:")
    print("   📚 Upload PDF research papers")
    print("   🔍 Ask questions about your literature")
    print("   🤖 Get AI-powered answers using Gemini")
    print("   📊 View collection statistics")
    print("   🔄 Analyze duplicate content")
    
    input("\n⚡ Press Enter to start the web application...")
    run_web_app()

if __name__ == "__main__":
    main()