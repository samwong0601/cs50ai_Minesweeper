import itertools
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
        # raise NotImplementedError
        if len(self.cells) == self.count and self.count > 0:
            print("Found mine(s) : ", self.cells)
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # raise NotImplementedError
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # raise NotImplementedError
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # raise NotImplementedError
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
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
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
        # raise NotImplementedError
        # Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # Mark the cell as a safe move
        self.mark_safe(cell)

        # Find the closet cell to the current cell
        closest = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.safes and (i, j) not in self.mines:
                        closest.add((i, j))
                    elif (i, j) in self.mines:
                        count -= 1

        # Add new sentance into KB
        new_sentence = Sentence(closest, count)
        print(f'Move on cell: {cell} has added sentence to knowledge {closest} = {count}')
        self.knowledge.append(new_sentence)

        # Mark cells as safe or mines
        self.infer_safes_and_mines()

        # Infer new sentences from existing KB
        new_KB = []
        for sentence_1 in self.knowledge:
            for sentence_2 in self.knowledge:
                if sentence_1 != sentence_2 and sentence_1.cells.issubset(sentence_2.cells):
                    new = Sentence(
                        sentence_2.cells - sentence_1.cells,
                        sentence_2.count - sentence_1.count
                    )
                    if new not in self.knowledge and new not in new_KB:
                        new_KB.append(new)
                        print(f'Added new sentence: {new}')

                    # Overlap inference: detect if common cells must be mines
                    overlap = sentence_1.cells.intersection(sentence_2.cells)
                    if overlap:
                        if sentence_1.count == 0:
                            for cell in overlap:
                                self.mark_safe(cell)
                                print(f"Inferred safe from overlap: {cell}")
                        elif sentence_1.count == sentence_2.count == len(overlap):
                            for cell in overlap:
                                self.mark_mine(cell)
                                print(f"Inferred mine from overlap: {cell}")

        self.knowledge.extend(new_KB)
        self.infer_safes_and_mines()

    def infer_safes_and_mines(self):
        """
        Updates AI knowledge to mark known safes and mines from sentences.
        """
        safes = set()
        mines = set()
        for sentence in self.knowledge:
            safes = safes.union(sentence.known_safes())
            mines = mines.union(sentence.known_mines())

            for safe in safes:
                self.mark_safe(safe)
            for mine in mines:
                self.mark_mine(mine)

        print(f'Safe: {self.safes}')
        print(f'Mines: {self.mines}')

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # raise NotImplementedError
        possible_moves = list(self.safes - self.moves_made)

        valid_moves = [
            cell for cell in possible_moves
            if all(cell not in sentence.cells or sentence.count == 0 for sentence in self.knowledge)
        ]
        if valid_moves:
            cell = random.choice(valid_moves)
            print(f'Move on cell: {cell}')
            return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # raise NotImplementedError
        if len(self.mines) + len(self.moves_made) == self.height * self.width:
            return None

        all_cells = set((i, j) for i in range(self.height) for j in range(self.width))
        possible_moves = list(all_cells - self.moves_made - self.mines)

        valid_moves = [
            cell for cell in possible_moves
            if all(cell not in sentence.cells or sentence.count == 0 for sentence in self.knowledge)
        ]

        if valid_moves:
            cell = random.choice(valid_moves)
            print(f'Move on cell: {cell}')
            return cell
        return None
