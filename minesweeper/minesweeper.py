import itertools
from os import remove
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) > 0 and len(self.cells) == self.count:
            return set(dict.fromkeys(list(self.cells)))
        return set()

    def known_safes(self):
        if self.count == 0:
            return set(dict.fromkeys(list(self.cells)))
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
    """
    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
        
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        self.mines = set(dict.fromkeys(list(self.mines)))
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        self.safes = set(dict.fromkeys(list(self.safes)))
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1
        self.moves_made.add(cell)

        # 2
        self.mark_safe(cell)

        # 3
        sentence_cells = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    sentence_cells.add((i, j))

        sentence_cells = set(sentence_cells).difference(self.moves_made)
        sentence = Sentence(sentence_cells, count)

        for cell in self.safes:
            sentence.mark_safe(cell)
        for cell in self.mines:
            sentence.mark_mine(cell)

        self.knowledge.append(sentence)
       
        # 4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        
        for sentence in self.knowledge:
            known_mines_copy = sentence.known_mines().copy()
            for safe in sentence.known_safes():
                self.mark_safe(safe)
            for mine in known_mines_copy:
                self.mark_mine(mine)

        # 5) add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge

        knowledge_copy = self.knowledge.copy()

        for sen1 in self.knowledge:
            for sen2 in self.knowledge:
                if sen1.cells.issubset(sen2.cells):
                    cells = sen2.cells - sen1.cells
                    count = sen2.count - sen1.count

                    if len(cells) > 0:
                        sentence = Sentence(set(dict.fromkeys(list(cells))), count)
                        if sentence not in knowledge_copy:
                            knowledge_copy.append(sentence)
                            if count == 0:
                                for cell in cells:
                                    self.mark_safe(cell)
                            elif count == len(cells) and count > 0:
                                for cell in cells:
                                    self.mark_mine(cell)
        
        # clean empty cell sentences
        self.knowledge = knowledge_copy
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                knowledge_copy.remove(sentence)
        self.knowledge = knowledge_copy
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes - self.moves_made
        if safe_moves:
            return safe_moves.pop()
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.moves_made) + len(self.mines) == (self.height * self.width):
            return None
        i = random.randrange(self.height)
        j = random.randrange(self.width)
        return (i, j)

