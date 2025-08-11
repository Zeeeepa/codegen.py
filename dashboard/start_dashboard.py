#!/usr/bin/env python3
"""
Codegen Dashboard Startup Script
Launches the Streamlit dashboard with proper configuration and validation.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("✅ All required dependencies are installed")
    return True

def validate_dashboard():
    """Run dashboard validation before starting"""
    logger.info("🔍 Running dashboard validation...")
    
    try:
        # Add current directory to Python path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        from validation.dashboard_validator import DashboardValidator
        
        validator = DashboardValidator()
        summary = validator.run_comprehensive_validation()
        
        if summary['success_rate'] >= 80:
            logger.info(f"✅ Dashboard validation passed ({summary['success_rate']:.1f}% success rate)")
            return True
        else:
            logger.warning(f"⚠️ Dashboard validation failed ({summary['success_rate']:.1f}% success rate)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Validation failed: {str(e)}")
        return False

def start_streamlit_app():
    """Start the Streamlit dashboard application"""
    logger.info("🚀 Starting Codegen Dashboard...")
    
    # Set environment variables for Streamlit
    env = os.environ.copy()
    env.update({
        'STREAMLIT_SERVER_PORT': '8501',
        'STREAMLIT_SERVER_ADDRESS': '0.0.0.0',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_SERVER_HEADLESS': 'true'
    })
    
    # Get the path to the dashboard app
    app_path = Path(__file__).parent / 'app.py'
    
    try:
        # Start Streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', str(app_path)]
        logger.info(f"Executing: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=Path(__file__).parent
        )
        
        logger.info("🌐 Dashboard starting up...")
        logger.info("📱 Access the dashboard at: http://localhost:8501")
        logger.info("⏹️ Press Ctrl+C to stop the dashboard")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("🛑 Dashboard stopped by user")
        if process:
            process.terminate()
    except Exception as e:
        logger.error(f"❌ Failed to start dashboard: {str(e)}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 Codegen Agent Run Management Dashboard")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages.")
        return False
    
    # Validate dashboard (optional, can be skipped with --skip-validation)
    if '--skip-validation' not in sys.argv:
        if not validate_dashboard():
            response = input("⚠️ Validation failed. Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("❌ Startup cancelled due to validation failure.")
                return False
    else:
        logger.info("⏭️ Skipping validation (--skip-validation flag provided)")
    
    # Start the dashboard
    success = start_streamlit_app()
    
    if success:
        logger.info("✅ Dashboard startup completed successfully")
    else:
        logger.error("❌ Dashboard startup failed")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

