import argparse
import json
import random
import string
import sys

def generate_build_number(env):
	if env == 'canary':
		return "C0" + "".join(random.choices(string.ascii_uppercase + string.digits, k = 5))
	elif env == 'release':
		return "R0" + "".join(random.choices(string.ascii_uppercase + string.digits, k = 5))
	else:
		return ValueError("Invalid environment.")

def main():
	parser = argparse.ArgumentParser(
		description="Tool for managing builds and releases."
	)

	parser.add_argument(
		'-g', '--generate',
		type=str,
		help="Generate a build number for the specified environment (e.g., 'canary', 'prod').",
		metavar='ENV'
	)

	args = parser.parse_args()

	if args.generate:
		environment = args.generate
		build_num = generate_build_number(environment)
		with open("metadata.json", "r") as metadata_file:
			metadata = json.load(metadata_file)
			metadata["build"] = build_num

		with open("metadata.json", "w") as metadata_file:
			json.dump(metadata, metadata_file, indent = 4)
		print(f"Updated build number ({build_num}).")
	else:
		print("No operation specified. Use -h for help.")
		sys.exit(1)

if __name__ == "__main__":
	main()
