import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI


class FlashcardGenerator:
    """Main application class for generating flashcards from text using OpenAI."""
    
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORG_ID")
        )
        self.setup_gui()

    def generate_flashcards(self, input_text: str) -> Optional[str]:
        """Generate flashcards from input text using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": self._build_prompt(input_text)
                }],
                max_tokens=2000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return None

    def _build_prompt(self, text: str) -> str:
        """Construct the prompt for the OpenAI API."""
        return f"""Extract key concepts and create flashcards from the following text.
        Generate 10-15 flashcards (or more if needed).
        
        Format each flashcard as:
        Question: [Your question here]
        Answer: [Your answer here]
        
        Cover all important concepts from the text.
        
        Text to process:
        {text}
        """

    def parse_flashcards(self, flashcards: str) -> Tuple[list, list]:
        """Parse the generated flashcards into questions and answers."""
        questions, answers = [], []
        current_q, current_a = None, None

        for line in flashcards.split('\n'):
            line = line.strip()
            if line.startswith('Question:'):
                if current_q and current_a:
                    questions.append(current_q)
                    answers.append(current_a)
                current_q = line.replace('Question:', '').strip()
                current_a = None
            elif line.startswith('Answer:'):
                current_a = line.replace('Answer:', '').strip()

        if current_q and current_a:
            questions.append(current_q)
            answers.append(current_a)

        return questions, answers

    def save_flashcards(self, questions: list, answers: list, filename: str = "flashcards.csv") -> None:
        """Save flashcards to a CSV file."""
        pd.DataFrame({'Question': questions, 'Answer': answers}).to_csv(filename, index=False)

    def open_file(self) -> None:
        """Handle file opening and processing."""
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filepath:
            return

        with open(filepath, "r") as file:
            text = file.read()

        if flashcards := self.generate_flashcards(text):
            questions, answers = self.parse_flashcards(flashcards)
            self.save_flashcards(questions, answers)
            messagebox.showinfo("Success", "Flashcards generated and saved to flashcards.csv")
        else:
            messagebox.showerror("Error", "Failed to generate flashcards. Please check your input.")

    def setup_gui(self) -> None:
        """Configure and start the GUI."""
        root = tk.Tk()
        root.title("AI Flashcard Generator")
        root.geometry("600x300")
        root.configure(bg="#f0f0f0")

        self._configure_styles(root)
        self._create_widgets(root)
        root.mainloop()

    def _configure_styles(self, root: tk.Tk) -> None:
        """Configure ttk styles for the application."""
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TButton", padding=10, font=("Helvetica", 12))
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        style.map("TButton",
            background=[("active", "#2980b9"), ("!active", "#3498db")],
            foreground=[("active", "white"), ("!active", "white")])

    def _create_widgets(self, root: tk.Tk) -> None:
        """Create and place all GUI widgets."""
        ttk.Label(
            root,
            text="AI Flashcard Generator",
            font=("Helvetica", 18),
            anchor="center"
        ).pack(pady=20)

        ttk.Label(
            root,
            text="Generate flashcards from text files using AI.",
            font=("Modern", 12),
            anchor="center"
        ).pack(pady=10)

        ttk.Button(
            root,
            text="Open Text File",
            command=self.open_file,
            cursor="hand2"
        ).pack(pady=20)


if __name__ == "__main__":
    FlashcardGenerator()