import argparse
import yaml
from core import scorer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profiles/felicity.yaml",
                        help="Path to user profile YAML")
    args = parser.parse_args()

    profile = scorer.load_profile(args.profile)
    print("Loaded profile:", profile["name"])
    print("Career focus:", ", ".join(profile.get("career_focus", [])))
    print("Values:", ", ".join(profile.get("values", [])))
    print("Excludes:", ", ".join(profile.get("exclude", [])))

if __name__ == "__main__":
    main()
