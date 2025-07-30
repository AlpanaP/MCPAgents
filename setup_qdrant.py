#!/usr/bin/env python3
"""
Setup script for Qdrant vector database
Helps users install and configure Qdrant for Delaware RAG tools
"""

import subprocess
import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def check_qdrant_installation():
    """Check if Qdrant is installed and running."""
    try:
        # Try to connect to Qdrant
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print("✅ Qdrant is running on localhost:6333")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

def install_qdrant():
    """Install Qdrant using Docker."""
    print("🐳 Installing Qdrant using Docker...")
    
    try:
        # Pull Qdrant Docker image
        subprocess.run([
            "docker", "pull", "qdrant/qdrant:latest"
        ], check=True)
        
        # Run Qdrant container
        subprocess.run([
            "docker", "run", "-d",
            "--name", "qdrant",
            "-p", "6333:6333",
            "-p", "6334:6334",
            "-v", "qdrant_storage:/qdrant/storage",
            "qdrant/qdrant:latest"
        ], check=True)
        
        print("✅ Qdrant installed and started successfully!")
        print("   - Host: localhost")
        print("   - Port: 6333")
        print("   - Web UI: http://localhost:6333/dashboard")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Qdrant: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        print("   Visit: https://docs.docker.com/get-docker/")
        return False

def setup_delaware_collection():
    """Setup the Delaware licenses collection in Qdrant."""
    try:
        client = QdrantClient(host="localhost", port=6333)
        
        # Check if collection exists
        collections = client.get_collections()
        collection_exists = any(col.name == "delaware_licenses" for col in collections.collections)
        
        if not collection_exists:
            print("📚 Creating Delaware licenses collection...")
            client.create_collection(
                collection_name="delaware_licenses",
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=Distance.COSINE
                )
            )
            print("✅ Delaware licenses collection created!")
        else:
            print("✅ Delaware licenses collection already exists!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup collection: {e}")
        return False

def test_qdrant_connection():
    """Test the Qdrant connection and basic operations."""
    try:
        client = QdrantClient(host="localhost", port=6333)
        
        # Test basic operations
        collections = client.get_collections()
        print(f"✅ Qdrant connection test passed!")
        print(f"   - Collections found: {len(collections.collections)}")
        
        # Test Delaware collection
        delaware_exists = any(col.name == "delaware_licenses" for col in collections.collections)
        print(f"   - Delaware collection: {'✅' if delaware_exists else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Qdrant connection test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Qdrant Setup for Delaware RAG Tools")
    print("=" * 50)
    
    # Check if Qdrant is already running
    if check_qdrant_installation():
        print("✅ Qdrant is already running!")
    else:
        print("📦 Qdrant not found. Installing...")
        if not install_qdrant():
            print("❌ Failed to install Qdrant. Please install manually.")
            print("   Visit: https://qdrant.tech/documentation/guides/installation/")
            return
    
    # Setup collection
    if not setup_delaware_collection():
        print("❌ Failed to setup Delaware collection.")
        return
    
    # Test connection
    if not test_qdrant_connection():
        print("❌ Failed to test Qdrant connection.")
        return
    
    print("\n" + "=" * 50)
    print("✅ Qdrant setup completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Run the Delaware RAG tools: python test_delaware_rag.py")
    print("2. Access Qdrant dashboard: http://localhost:6333/dashboard")
    print("3. Use the MCP tools with RAG capabilities")
    
    print("\n📚 Useful commands:")
    print("   - Start Qdrant: docker start qdrant")
    print("   - Stop Qdrant: docker stop qdrant")
    print("   - View logs: docker logs qdrant")
    print("   - Remove Qdrant: docker rm -f qdrant")

if __name__ == "__main__":
    main() 