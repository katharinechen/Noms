"""
Test-running tool.
------------------------------------------------------------------------        
- If no tool options are specified at all, run all tools with all default
options.
                                                                                
- Otherwise, run the specified tools only, with the specified options.
------------------------------------------------------------------------        
TIP: The parameters above take the extra args you want to pass into the tool
as a string, but using one will run ONLY that tool. If you want to run several
with the defaults and one without, try this syntax:
                                                                                
$ testit -p "noms.foo" -kk -cc
""" # note - preserve whitespace in the docstring above.

import shlex
import subprocess
import webbrowser

from twisted.python.procutils import which

from codado.tx import Main


# The tools we will run. This also specifies the order they will run.
ALL_TOOLS = ['python', 'pyflakes', 'coverage']


class TestIt(Main):
    """
    Run tests of various kinds.
    """
    synopsis = "testit [individual command params]"

    optParameters = [
        ['python', 'p', None, 'Run python tests with args (or -pp)'],
        ['pyflakes', 'k', None, 'Run pyflakes with args (or -kk)'],
        ['coverage', 'c', None, 'Generate pretty coverage with args (HTML by default) (or -cc)'],
    ]

    def __init__(self):
        """
        Initialize the tool dictionary. Empty dictionary means all tools.
        """
        super(TestIt, self).__init__() # we need to run the superclass's init before overwriting it
        self.tools = {}

    def postOptions(self):
        """
        Decide what tools to run and then run them
        """
        self.tools = {}
        for t in ALL_TOOLS:
            if self[t] is None:
                continue
            else:
                # make -kk -pp etc. work...
                if self.synonyms.get(self[t]) == t:
                    self[t] = ""

                self.tools[t] = self[t]

        if len(self.tools) == 0:
            self.tools = {t: None for t in ALL_TOOLS}

        toolResults = {}

        toolOrder = [(t, self.tools[t]) for t in ALL_TOOLS if t in self.tools]

        for tool, extra in toolOrder:
            extra = shlex.split(extra or '')
            print '\n', '#' * 10, tool
            rc = getattr(self, 'run_' + tool)(extra)
            toolResults[tool] = rc

        print '\n\n', '#' * 80, '\n'
        for tool, _ in toolOrder:
            if toolResults[tool] == 0:
                print tool.ljust(20), 'ok'
            else:
                print '**', tool.ljust(17), 'FAIL'

    def run_python(self, extra):
        """
        Run python unit tests, with trial, using coverage tracking
        """
        trial = which('trial')[0]
        coverage = which('coverage')[0]
        # we want to run trial with python coverage
        _args = [coverage, 'run', trial]
        args = _args + (extra or ['noms'])
        return subprocess.call(args)

    def run_coverage(self, extra):
        """
        Run Python coverage
        """
        coverage = which('coverage')[0]
        _args = [coverage, 'html', '--fail-under=100']
        args = _args + (extra or [])
        rc = subprocess.call(args)

        if rc == 2:
            print "** Coverage is incomplete"
            webbrowser.open("htmlcov/index.html")

        elif rc == 0:
            print "Coverage is 100%"

        # Other rcs are errors unrelated to coverage completion
        else:
            print "** Coverage runtime error"

        return rc

    def run_pyflakes(self, extra):
        """
        Run pyflakes on Python code
        """
        pyflakes = which('pyflakes')[0]
        _args = [pyflakes, 'noms']
        args = _args + (extra or [])
        rc = subprocess.call(args)
        if rc == 0:
            print 'pyflakes passes'
        return rc

