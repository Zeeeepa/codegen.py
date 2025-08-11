"""
Config command implementation
Handles configuration management
"""

import json
import os
from typing import Any, Dict


class ConfigCommand:
    """Command to manage configuration"""

    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.expanduser("~/.codegen/config.json")
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")

        return {
            "org_id": os.getenv("CODEGEN_ORG_ID"),
            "token": os.getenv("CODEGEN_API_TOKEN"),
            "default_timeout": 300,
            "poll_interval": 5.0,
            "preset": "production",
        }

    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def show(self):
        """Show current configuration"""
        print("🔧 Current configuration:")
        for key, value in self.config.items():
            if key == "token" and value:
                # Mask token for security
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")

    def set_value(self, key: str, value: str):
        """Set a configuration value"""
        self.config[key] = value
        self.save_config()
        print(f"✅ Set {key} = {value}")

    def set_preset(self, preset: str):
        """Set configuration preset"""
        available_presets = [
            "development",
            "production",
            "high_throughput",
            "low_latency",
            "batch_processing",
        ]
        if preset not in available_presets:
            print(f"❌ Invalid preset. Available: {', '.join(available_presets)}")
            return False

        self.config["preset"] = preset
        self.save_config()
        print(f"✅ Set preset to {preset}")
        return True

    def initialize(self):
        """Initialize configuration interactively"""
        print("🔧 Initializing Codegen configuration...")

        org_id = input("Organization ID: ").strip()
        token = input("API Token: ").strip()

        if org_id:
            self.config["org_id"] = org_id
        if token:
            self.config["token"] = token

        self.save_config()
        print("✅ Configuration saved!")

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
