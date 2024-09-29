import sys
import argparse
from gui.main_gui import ToneGeneratorGUI
from cli.main_cli import main as cli_main

def main():
    parser = argparse.ArgumentParser(description="Tone Generator Application")
    parser.add_argument("--mode", choices=["gui", "cli"], required=True, help="Select the mode to run the application: GUI or CLI")
    
    # Pass remaining arguments to the CLI parser if in CLI mode
    args, unknown = parser.parse_known_args()

    if args.mode == "gui":
        # Launch the GUI application
        app = ToneGeneratorGUI()
        app.mainloop()
    elif args.mode == "cli":
        # Pass unknown arguments to the CLI main function
        sys.argv = [sys.argv[0]] + unknown
        cli_main()

if __name__ == "__main__":
    main()


