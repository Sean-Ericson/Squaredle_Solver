import tkinter as tk
from tkinter import messagebox
import random
import string

def get_word_list(four_letter_min=True) -> list[str]:
    words = []
    with open("words.txt", "r") as f:
        words = [line.strip() for line in f.readlines() if not four_letter_min or len(line.strip()) >= 4]
    return words

class SquaredleGame:
    def __init__(self, root, grid_str):
        self.root = root
        self.root.title("Squaredle")
        self.root.configure(bg='#f5f5f5')
        
        # Game state
        self.grid_size = 4
        self.grid_str = grid_str
        self.grid = []
        self.selected_cells = []
        self.found_words = set()
        self.current_word = ""
        self.score = 0
        
        # Create word list (common English words)
        self.valid_words = self.create_word_list()
        
        # UI setup
        self.setup_ui()
        self.generate_grid(grid_str)
        
    def create_word_list(self):
        """Create a set of valid words"""
        words = set(get_word_list())
        return words
    
    def setup_ui(self):
        # Top frame for score and word display
        top_frame = tk.Frame(self.root, bg='#f5f5f5')
        top_frame.pack(pady=10)
        
        score_label = tk.Label(top_frame, text="Score:", font=('Arial', 14, 'bold'), bg='#f5f5f5')
        score_label.grid(row=0, column=0, padx=5)
        
        self.score_value = tk.Label(top_frame, text="0", font=('Arial', 14), bg='#f5f5f5')
        self.score_value.grid(row=0, column=1, padx=5)
        
        words_label = tk.Label(top_frame, text="Words:", font=('Arial', 14, 'bold'), bg='#f5f5f5')
        words_label.grid(row=0, column=2, padx=5)
        
        self.words_value = tk.Label(top_frame, text="0", font=('Arial', 14), bg='#f5f5f5')
        self.words_value.grid(row=0, column=3, padx=5)
        
        # Current word display
        self.word_display = tk.Label(self.root, text="", font=('Arial', 20, 'bold'), 
                                     bg='#f5f5f5', fg='#2c3e50', height=2)
        self.word_display.pack()
        
        # Grid frame
        self.grid_frame = tk.Frame(self.root, bg='#f5f5f5')
        self.grid_frame.pack(pady=10)
        
        # Found words display
        found_frame = tk.Frame(self.root, bg='#f5f5f5')
        found_frame.pack(pady=10)
        
        found_label = tk.Label(found_frame, text="Found Words:", font=('Arial', 12, 'bold'), bg='#f5f5f5')
        found_label.pack()
        
        self.found_text = tk.Text(found_frame, width=40, height=8, font=('Arial', 10), 
                                 state='disabled', bg='white')
        self.found_text.pack()
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#f5f5f5')
        button_frame.pack(pady=10)
        
        submit_btn = tk.Button(button_frame, text="Submit Word", command=self.submit_word,
                              font=('Arial', 12), bg='#3498db', fg='white', padx=20, pady=5)
        submit_btn.grid(row=0, column=0, padx=5)
        
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_selection,
                            font=('Arial', 12), bg='#e74c3c', fg='white', padx=20, pady=5)
        clear_btn.grid(row=0, column=1, padx=5)
        
        new_game_btn = tk.Button(button_frame, text="New Game", command=self.new_game,
                               font=('Arial', 12), bg='#2ecc71', fg='white', padx=20, pady=5)
        new_game_btn.grid(row=0, column=2, padx=5)
        
    def generate_grid(self, grid_str):
        """Generate a random grid of letters"""
        # Clear existing grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        self.grid = []
        self.buttons = []
        
        for i in range(self.grid_size):
            row = []
            button_row = []
            for j in range(self.grid_size):
                # Mix of common letters, vowels, and random letters
                letter = grid_str[i * self.grid_size + j].upper()
                
                row.append(letter)
                
                btn = tk.Button(self.grid_frame, text=letter, font=('Arial', 20, 'bold'),
                              width=4, height=2, bg='#ecf0f1', fg='#2c3e50',
                              relief='raised', bd=3)
                btn.grid(row=i, column=j, padx=2, pady=2)
                btn.config(command=lambda r=i, c=j: self.cell_clicked(r, c))
                button_row.append(btn)
            
            self.grid.append(row)
            self.buttons.append(button_row)
    
    def cell_clicked(self, row, col):
        """Handle cell click"""
        # Check if this cell is adjacent to the last selected cell
        if self.selected_cells:
            last_row, last_col = self.selected_cells[-1]
            if not self.is_adjacent(last_row, last_col, row, col):
                return
        
        # Check if cell is already selected
        if (row, col) in self.selected_cells:
            return
        
        # Add to selection
        self.selected_cells.append((row, col))
        self.current_word += self.grid[row][col]
        
        # Update button appearance
        self.buttons[row][col].config(bg='#3498db', fg='white')
        
        # Update word display
        self.word_display.config(text=self.current_word)
    
    def is_adjacent(self, r1, c1, r2, c2):
        """Check if two cells are adjacent (including diagonals)"""
        return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and (r1 != r2 or c1 != c2)
    
    def submit_word(self):
        """Submit the current word"""
        if len(self.current_word) < 3:
            messagebox.showwarning("Too Short", "Words must be at least 3 letters long!")
            return
        
        word_lower = self.current_word.lower()
        
        if word_lower in self.found_words:
            messagebox.showinfo("Already Found", "You've already found this word!")
            self.clear_selection()
            return
        
        if word_lower in self.valid_words:
            # Valid word!
            self.found_words.add(word_lower)
            points = len(self.current_word)
            self.score += points
            
            # Update displays
            self.score_value.config(text=str(self.score))
            self.words_value.config(text=str(len(self.found_words)))
            
            # Add to found words list
            self.found_text.config(state='normal')
            self.found_text.insert('end', f"{self.current_word} ({points} pts)\n")
            self.found_text.config(state='disabled')
            self.found_text.see('end')
            
            # Flash success
            self.word_display.config(fg='#27ae60')
            self.root.after(500, lambda: self.word_display.config(fg='#2c3e50'))
            
            self.clear_selection()
        else:
            messagebox.showwarning("Invalid Word", f"'{self.current_word}' is not a valid word!")
            self.clear_selection()
    
    def clear_selection(self):
        """Clear the current selection"""
        for row, col in self.selected_cells:
            self.buttons[row][col].config(bg='#ecf0f1', fg='#2c3e50')
        
        self.selected_cells = []
        self.current_word = ""
        self.word_display.config(text="")
    
    def new_game(self):
        """Start a new game"""
        self.selected_cells = []
        self.found_words = set()
        self.current_word = ""
        self.score = 0
        
        self.score_value.config(text="0")
        self.words_value.config(text="0")
        self.word_display.config(text="")
        
        self.found_text.config(state='normal')
        self.found_text.delete('1.0', 'end')
        self.found_text.config(state='disabled')
        
        self.generate_grid()

if __name__ == "__main__":
    root = tk.Tk()
    game = SquaredleGame(root, "tecssneirrsnidye")
    root.mainloop()