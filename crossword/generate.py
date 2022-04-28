import queue
from re import T
from sre_constants import FAILURE
import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # enforce length
        for var in self.domains:
            dom = self.domains[var].copy()
            for word in self.domains[var]:
                if len(word) !=  var.length:
                    dom.remove(word)
            self.domains[var] = dom

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # overlap = self.crossword.overlaps[x, y]
        # remove_words = []

        # if overlap is None:
        #     return False

        x_domain = self.domains[x]
        
        x_domain_copy = x_domain.copy()
        revised = False
        for dx in x_domain:
            satisfies = False
            y_domain = self.domains[y]
            for dy in y_domain:
                if dx != dy:
                    assignment = {}
                    assignment[x] = dx
                    assignment[y] = dy
                    if self.consistent(assignment):
                         satisfies = True
                    if satisfies == False:
                        x_domain_copy.remove(dx)
                        revised = True
                        break
            if len(x_domain_copy) == 1:

                break
        self.domains[x] = x_domain_copy
        self.domains[x]
        return revised
            
    def ac3(self, arcs=None):

        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        consistency_enforced = True
        if arcs is None:
            arcs = []
            for i in self.crossword.variables:
                for j in self.crossword.neighbors(i):
                    if i != j:
                        arcs.append((i,j))
        
        while len(arcs) > 0:
            (x, y) = arcs.pop()

            if self.revise(x ,y) == True:
                #
                # for neighbor in self.crossword.neighbors(x):
                #     arcs.append((x, neighbor))
                #

                if len(self.domains[x]) == 0:
                    return False
                consistency_enforced = False
                if len(self.domains[y]) > 0:
                    neighbors = copy.deepcopy(self.crossword.neighbors(x))
                    
                    if y in neighbors:
                        neighbors = neighbors - {y}
                    
                    for n in neighbors:
                        arcs.append((n, x))
                        if n == y:
                            neighbors.remove(y)
                            for z in neighbors:
                                if (z,x) not in arcs:
                                    arcs.append((z, x))
        # return consistency_enforced
        return len(self.domains[x]) > 0

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        keys = [*assignment]
        if len(keys) > 1:
            var0 = keys[0]
            var1 = keys[1]
            word0 = assignment[var0]
            word1 = assignment[var1]
            
            if len(word0) != var0.length:
                return False
            if var0 != var1:
                if word0 == word1:
                    return False
                overlap = self.crossword.overlaps[(keys[0], keys[1])]
                if overlap is not None:
                    if word0[overlap[0]] != word1[overlap[1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # vals = [*self.domain[var]]
        # for val in vals:
        #     self.crossword.neighbors(var)
        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return variable
        return None


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """ 
        if self.assignment_complete(assignment) == True:
            return assignment

        unassigned = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(unassigned, assignment):
            assignment[unassigned] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                assignment[unassigned] = None
        return None




def main():

    # Check usage
    # if len(sys.argv) not in [3, 4]:
    #     sys.exit("Usage: python generate.py structure words [output]")

    # # Parse command-line arguments
    # structure = sys.argv[1]
    # words = sys.argv[2]
    # output = sys.argv[3] if len(sys.argv) == 4 else None

    structure = 'data/structure2.txt'
    words = 'data/words2.txt'
    output = None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
