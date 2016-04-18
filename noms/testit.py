"""
Test-running tool 
"""
import sys 

from twisted.trial import unittest
from twisted.python import usage 


class TestIt(usage.Options): 
    """
    Command-line options for the test-running tool 
    """
    def __init__(self):
        """
        Initialize the tool dictionary. Empty dictionary means all tools. 
        """
        usage.Options.__init__(self) # we need to run the superclass's init before overwriting it 
        self.tools = {}

    def opt_python(self): 
        """
        Run python tests 
        """
        self.tools['python'] = 'python' 

    def opt_pyflakes(self):
        """
        Run pyflakes
        """
        self.tools['pyflakes'] = 'pyflakes'

    def postOptions(self): 
        """
        Decide what tools to run and then run them 
        """
        if not self.tools: 
            print "Python, Pyflakes"
        else: 
            print self.tools.values()

    # shortcuts for options 
    opt_p = opt_python 
    opt_k = opt_pyflakes 


def main(args=None):
    """
    Fill in command-line arguments from argv 
    """
    if args is None: 
        args = sys.argv[1:]

    o = TestIt()
    o.parseOptions(args)


if __name__ == "__main__": 
    main()