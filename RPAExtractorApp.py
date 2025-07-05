import tkinter as tk
from tkinter import filedialog, ttk
import sys
from unrpa import UnRPA
from pathlib import Path
import threading
import time

class RPAExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RPA Extractor by 0xcds4r")
        self.root.geometry("666x300")

        self.rpa_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.status = tk.StringVar(value="Select an RPA file and output directory")
        self.progress = tk.DoubleVar(value=0)

        tk.Label(root, text="RPA File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(root, textvariable=self.rpa_file, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(root, text="Browse", command=self.browse_rpa).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(root, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(root, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=10, pady=10)

        tk.Button(root, text="Extract", command=self.start_extraction).grid(row=2, column=0, columnspan=3, pady=20)

        self.progress_bar = ttk.Progressbar(root, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.status_text = tk.Text(root, height=3, wrap="word", width=70)
        self.status_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        self.status_text.insert("1.0", self.status.get())
        self.status_text.config(state="disabled")

        def update_status(*args):
            self.status_text.config(state="normal")
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", self.status.get())
            self.status_text.config(state="disabled")

        self.status.trace("w", update_status)

    def browse_rpa(self):
        file_path = filedialog.askopenfilename(filetypes=[("RPA Files", "*.rpa")])
        if file_path:
            self.rpa_file.set(file_path)
            self.status.set("RPA file selected. Choose output directory.")

    def browse_output(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)
            self.status.set("Output directory selected. Ready to extract.")

    def start_extraction(self):
        if not self.rpa_file.get() or not self.output_dir.get():
            self.status.set("Error: Please select both an RPA file and an output directory.")
            return

        self.status.set("Starting extraction...")
        self.progress.set(0)
        self.extract_button = tk.Button(self.root, text="Extract", state="disabled")
        self.extract_button.grid(row=2, column=0, columnspan=3, pady=20)

        threading.Thread(target=self.extract_rpa, daemon=True).start()

    def extract_rpa(self):
        try:
            rpa_path = Path(self.rpa_file.get())
            output_path = Path(self.output_dir.get())
            output_path.mkdir(parents=True, exist_ok=True)

            extractor = UnRPA(filename=str(rpa_path), path=str(output_path), mkdir=True)

            self.progress.set(10)
            self.root.update()
            time.sleep(0.1)
            extractor.extract_files()
            for i in range(10, 101, 10):
                self.progress.set(i)
                self.root.update()
                time.sleep(0.1)

            self.status.set(f"Extraction complete! Files saved to {output_path}")
        except ValueError as e:
            self.status.set(f"Error: Invalid RPA file or unsupported format - {e}")
        except IOError as e:
            self.status.set(f"Error: Could not access file - {e}")
        except Exception as e:
            self.status.set(f"Unexpected error: {e}")
        finally:
            self.extract_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = RPAExtractorApp(root)
    root.mainloop()