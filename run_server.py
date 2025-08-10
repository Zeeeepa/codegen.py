#!/usr/bin/env python3
"""
FastAPI Server Runner for Codegen API
"""

import os
import sys
import uvicorn
from codegen_api import create_app, FASTAPI_AVAILABLE

def main():
    """Run the FastAPI server"""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
        sys.exit(1)
    
    # Set environment variables
    os.environ.setdefault("CODEGEN_ORG_ID", "323")
    os.environ.setdefault("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    
    print("🚀 Starting Codegen FastAPI Server...")
    print(f"📊 Organization ID: {os.environ.get('CODEGEN_ORG_ID')}")
    print(f"🔑 API Token: {os.environ.get('CODEGEN_API_TOKEN')[:20]}...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Alternative docs: http://localhost:8000/redoc")
    print("❤️  Health check: http://localhost:8000/health")
    
    # Create and run the app
    app = create_app(title="Codegen API Server", version="1.0.0")
    
    # Add health check endpoint manually since file size limit prevents adding it to main file
    @app.get("/health", tags=["System"])
    async def health_check():
        """Health check endpoint"""
        from datetime import datetime
        try:
            from codegen_api import CodegenClient, ClientConfig
            config = ClientConfig(
                api_token=os.environ.get("CODEGEN_API_TOKEN"),
                org_id=os.environ.get("CODEGEN_ORG_ID")
            )
            client = CodegenClient(config)
            health = client.health_check()
            return {
                "status": health["status"],
                "response_time_seconds": health["response_time_seconds"],
                "user_id": health.get("user_id"),
                "timestamp": health["timestamp"],
                "version": "1.0.0"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_seconds": 0.0,
                "user_id": None,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
