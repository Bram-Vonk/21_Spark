import argparse

from envyaml import EnvYAML


def parse_config(abs_path) -> EnvYAML:
    """Parse the configuration in EnvYAML format."""
    return EnvYAML(abs_path, strict=False)


def parse_args() -> dict:
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser()
    args, _ = parser.parse_known_args()
    return vars(args)
