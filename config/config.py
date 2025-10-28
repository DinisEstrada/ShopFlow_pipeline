import os
import yaml
from dotenv import load_dotenv

class ConfigError(Exception):
    pass

def load_config(env="dev"):
    """Load YAML config, resolve ${VAR}, and validate sections."""
    load_dotenv()  # load .env if it exists

    config_file = os.path.join(os.path.dirname(__file__), f"{env}.yaml")
    if not os.path.exists(config_file):
        raise ConfigError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    # Substitute environment variables
    for section, values in config.items():
        if isinstance(values, dict):
            for key, value in values.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var = value[2:-1]
                    val = os.getenv(var)
                    if not val:
                        raise ConfigError(f"Missing environment variable: {var}")
                    config[section][key] = val

    # Basic validation
    for key in ["user", "password", "host", "port", "name"]:
        if key not in config.get("database", {}):
            raise ConfigError(f"Missing database config key: {key}")

    for key in ["region", "bucket"]:
        if key not in config.get("aws", {}):
            raise ConfigError(f"Missing AWS config key: {key}")

    return config
