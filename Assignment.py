# CSP Assignment
# Original code by Håkon Måløy
# Updated by Xavier Sánchez Díaz

import copy
from itertools import product as prod
from tkinter import *




class CSP:
 

    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains is a dictionary of domains (lists)
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

        self.backtrack_counter = 0

        self.backtrack_failure_counter = 0

    def add_variable(self, name: str, domain: list):
        """Add a new variable to the CSP.

        Parameters
        ----------
        name : str
            The name of the variable to add
        domain : list
            A list of the legal values for the variable
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a: list, b: list) -> list[tuple]:
        """Get a list of all possible pairs (as tuples) of the values in
        lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.

        Parameters
        ----------
        a : list
            First list of values
        b : list
            Second list of values

        Returns
        -------
        list[tuple]
            List of tuples in the form (a, b)
        """
        return prod(a, b)

    def get_all_arcs(self) -> list[tuple]:
        """Get a list of all arcs/constraints that have been defined in
        the CSP.

        Returns
        -------
        list[tuple]
            A list of tuples in the form (i, j), which represent a
            constraint between variable `i` and `j`
        """
        return [(i, j) for i in self.constraints for j in self.constraints[i]]

    def get_all_neighboring_arcs(self, var: str) -> list[tuple]:
        """Get a list of all arcs/constraints going to/from variable 'var'.

        Parameters
        ----------
        var : str
            Name of the variable

        Returns
        -------
        list[tuple]
            A list of all arcs/constraints in which `var` is involved
        """
        return [(i, var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i: str, j: str,
                               filter_function: callable):
        """Add a new constraint between variables 'i' and 'j'. Legal
        values are specified by supplying a function 'filter_function',
        that should return True for legal value pairs, and False for
        illegal value pairs.

        NB! This method only adds the constraint one way, from i -> j.
        You must ensure to call the function the other way around, in
        order to add the constraint the from j -> i, as all constraints
        are supposed to be two-way connections!

        Parameters
        ----------
        i : str
            Name of the first variable
        j : str
            Name of the second variable
        filter_function : callable
            A callable (function name) that needs to return a boolean.
            This will filter value pairs which pass the condition and
            keep away those that don't pass your filter.
        """
        if j not in self.constraints[i]:
            # First, get a list of all possible pairs of values
            # between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(
                self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = list(filter(lambda
                                             value_pair:
                                             filter_function(*value_pair),
                                             self.constraints[i][j]))

    def add_all_different_constraint(self, var_list: list):
        """Add an Alldiff constraint between all of the variables in the
        list provided.

        Parameters
        ----------
        var_list : list
            A list of variable names
        """
        for (i, j) in self.get_all_possible_pairs(var_list, var_list):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        self.backtrack_counter = 1
        self.backtrack_failure_counter = 0

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    def backtrack(self, assignment):
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """
        # TODO: YOUR CODE HERE
        if sum(len(domain) for domain in assignment.values()) == len(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in assignment[var]:
            new_assignment = copy.deepcopy(assignment)
            new_assignment[var] = value
            if self.inference(new_assignment, self.get_all_arcs()):
				# Found inference calling backtrack recursively
                self.backtrack_counter += 1
                result = self.backtrack(new_assignment)
                if result:
                    return result

		# Backtracking failed
        self.backtrack_failure_counter += 1
        return

    def select_unassigned_variable(self, assignment):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        # TODO: YOUR CODE HERE
        # for n in assignment:
        #     # print(n)
        #     if len(assignment[n]) > 1:
        #         # print(assignment[n])
        #         return n
        # return False

        return min(assignment.keys(), 
                   key=lambda var: float("inf") 
                   if len(assignment[var]) < 2 
                   else len(assignment[var]))
    
    

    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
        # TODO: YOUR CODE HERE
        
        while len(queue) != 0:
            i, j = queue.pop()
            if (self.revise(assignment, i, j) == True):
                if not assignment[i]:
                    return False
                for k, _ in self.get_all_neighboring_arcs(i):
                    if k != j:
                        queue.append((k,i))
        return True

    def revise(self, assignment, i, j):
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.
        """
        # TODO: YOUR CODE HERE
        revised = False
        for x in assignment[i]:
            arcs = list(self.get_all_possible_pairs([x], assignment[j]))
            if not sum(arc in self.constraints[i][j] for arc in arcs):
                revised = True
                # print(assignment[i], x)
                if x in assignment[i] and len(assignment[i]) > 1:
                    assignment[i].remove(x)
                    
        return revised

def create_map_coloring_csp():
    """Instantiate a CSP representing the map coloring problem from the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    edges = {'SA': ['WA', 'NT', 'Q', 'NSW', 'V'],
             'NT': ['WA', 'Q'], 'NSW': ['Q', 'V']}
    colors = ['red', 'green', 'blue']
    for state in states:
        csp.add_variable(state, colors)
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)
    return csp


def create_sudoku_csp(filename: str) -> CSP:
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.

    Parameters
    ----------
    filename : str
        Filename of the Sudoku board to solve

    Returns
    -------
    CSP
        A CSP instance
    """
    csp = CSP()
    board = list(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), list(map(str,
                                                                range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col)
                                          for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col)
                                         for row in range(9)])
    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    return csp


def print_sudoku_solution(solution):
    """Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    for row in range(9):
        for col in range(9):
            print(solution['%d-%d' % (row, col)][0], end=" "),
            if col == 2 or col == 5:
                print('|', end=" "),
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')


def draw_board(solution, backtrack_counter, backtrack_failure_counter, boardname=""):
	"""
	Method for drawing sudoku board with solution from CSP-backtracking with kTinker
	"""
	rec_size = 35
	width = 9 * rec_size + 3
	height = 9 * rec_size + 3

	drawer = Tk()
	drawer.winfo_toplevel().title("Solved {}".format(boardname))
	window = Canvas(drawer, width=width, height=height)

	def exit_tkinter():
		drawer.destroy()

	def stop_solving():
		global solving
		solving = False
		drawer.destroy()

	for row in range(9):
		for col in range(9):
			x = row + 0.1
			y = col + 0.1

			# Drawing thicker lines on certain rows and columns
			col_space = 1 if col == 3 or col == 6 else 0
			row_space = 1 if row == 3 or row == 6 else 0

			window.create_rectangle(y * rec_size + col_space, x * rec_size + row_space, y * rec_size + rec_size,
									x * rec_size + rec_size,
									fill="white")

			window.create_text(y * rec_size + 0.5 * rec_size, x * rec_size + 0.5 * rec_size,
							   fill="black", font="Times 20 italic bold", text=(solution['{}-{}'.format(row, col)][0]))

	next_button = Button(drawer, text="Solve next board",
						 width=30, command=exit_tkinter, height=2)
	stop_button = Button(drawer, text="Stop solving",
						 width=30, command=stop_solving, height=2)

	label1 = Label(drawer, text="Number of backtracks: {}".format(backtrack_counter))
	label2 = Label(drawer, text="Number of failed backtracks: {}".format(backtrack_failure_counter))

	window.pack()
	label1.pack()
	label2.pack()
	next_button.pack()
	stop_button.pack()

	drawer.mainloop()

def main():
	board_paths = [("Easy", "easy.txt"),
				 ("Medium", "medium.txt"),
				 ("Hard", "hard.txt"),
				 ("Very hard", "veryhard.txt")]
	for filepath in board_paths:
		if solving:
			print(">  Solving {}".format(filepath[0]), end="\n\n")
			csp = create_sudoku_csp(filepath[1])
			solution = csp.backtracking_search()
			draw_board(solution, csp.backtrack_counter, csp.backtrack_failure_counter, filepath[0])

	if not solving:
		print("Stopped solving")

solving = True
main()