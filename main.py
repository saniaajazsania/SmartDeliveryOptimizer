"""
main.py
Entry point for the Smart Delivery Route Optimizer.
Launches the Tkinter GUI application.

Usage:
    python main.py

Requirements:
    pip install numpy matplotlib
"""

import tkinter as tk
from visualization.gui import DeliveryGUI


def main() -> None:
    """Create and run the main application window."""
    # Create the root Tkinter window
    root = tk.Tk()

    # Set window icon (if available, skip gracefully)
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass

    # Instantiate and launch the GUI
    app = DeliveryGUI(root)

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()