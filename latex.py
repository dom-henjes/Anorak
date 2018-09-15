import numpy

class Latexer(object):

    def set_chars(self, chars):
        self.coll = chars
        # convert internal pieces
        # self.flatten()
        # prep internal values
        self.av_h = numpy.median([i[1][1] for i in chars])
        self.av_s = self.get_demiper()


    # format is list of characters
    # each list is a column, showing characters from top to bottom
    # each character is a tuple (number, (centre-x, centre-y), (height, width))
    def to_latex(self):
        # wrap equation in correct delimiter
        out = "$$"
        out += self.latexify(self.coll)
        # wrap equation in correct delimiter
        out += "$$"
        return out

    def flatten(self):
        new_char_coll = []
        for col in self.coll:
            try:
                new_char_coll += col
            except:
                new_char_coll += [col]
        self.coll = new_char_coll

    def latexify(self, coll):
        if len(coll) == 0:
            return ""
        if coll[0] == 71: # sum
            return "\\prod_\{" + self.latex_char(coll[2]) + "\}\^\{" + self.latex_char(coll[1]) + "\} " + self.latexify(coll[3:])
        if coll[0] == 48: # integral
            return "\\int_\{" + self.latex_char(coll[2]) + "\}\^\{" + self.latex_char(coll[1]) + "\} " + self.latexify(coll[3:])
        if coll[0] == 55:  # limit
            return "\\lim_\{" + self.latex_char(coll[1]) + "\\to" + self.latex_char(coll[3]) + "\} " + self.latexify(coll[4:])
        
        return self.latex_char(coll[0]) + self.latexify(coll[1:])


    def get_demiper(self):
        # find average demi-perimeter of image
        sum_size = 0
        for char in self.coll:
            x, y = char[1]
            sum_size += x + y
        av_size = sum_size // len(char)
        return av_size
        

    def latex_char(self, char):
        latex_arr = [
            '!',
            '\\left \\(',
            '\\right \\)',
            '+',
            ',',
            '\\-',
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '=',
            'A',
            'B',
            'C',
            '\\Delta',
            'G',
            'H',
            'M',
            'N',
            'R',
            'S',
            'T',
            'X',
            '\\[',
            '\\]',
            '\\alpha',
            '\\ascii_124',
            'b',
            '\\beta',
            '\\cos',
            'd',
            '\\div',
            'e',
            '\\exists',
            'f',
            '\\forall',
            '\\forward_slash',
            '\\gamma',
            '\\geq',
            '\\gt',
            'i',
            '\\in',
            '\\infty',
            '\\int',
            'j',
            'k',
            'l',
            '\\lambda',
            '\\ldots',
            '\\leq',
            '\\lim',
            '\\log',
            '\\lt',
            '\\mu',
            '\\neq',
            'o',
            'p',
            '\\phi',
            '\\pi',
            '\\pm',
            '\\prime',
            'q',
            '\\rightarrow',
            '\\sigma',
            '\\sin',
            '\\sqrt',
            '\\sum',
            '\\tan',
            '\\test',
            '\\theta',
            '\\times',
            '\\train',
            'u',
            'v',
            'w',
            'y',
            'z',
            '\\left \\{',
            '\\right \\}',
        ]
        return latex_arr[char[0]]

    def print_example(self):
        out = """ 
        l = Latexer()
        l.set_chars([[0,(10,10), (10, 10)], [10, (10, 30), (10, 10)]])
        print l.to_latex()
        """

        print out

l = Latexer()
l.print_example()