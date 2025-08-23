#!/usr/bin/env python3
"""
Test script for importing ConfigPresets.
"""

from backend.core.config.client_config import ClientConfig, ConfigPresets

def main():
    """Test importing and using ConfigPresets."""
    print("Testing ConfigPresets import...")
    
    # Create a client config
    config = ClientConfig()
    
    # Print the default config
    print("Default config:")
    print(config.to_dict())
    
    # Load a preset
    config.load_preset(ConfigPresets.DEVELOPMENT)
    
    # Print the development config
    print("\nDevelopment config:")
    print(config.to_dict())
    
    print("\nTest successful!")

if __name__ == "__main__":
    main()

