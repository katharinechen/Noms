"""
Test-running tool
"""
import shlex
import subprocess

from twisted.python.procutils import which

from noms import Main


# The tools we will run. This also specifies the order they will run.
ALL_TOOLS = ['python', 'pyflakes', 'coverage']


class TestIt(Main):
    """
    Command-line options for the test-running tool
    """
    synopsis = "testit [individual command params]"

    optParameters = [
        ['python', 'p', None, 'Run python tests (use -p="" for defaults)'],
        ['pyflakes', 'k', None, 'Run pyflakes (use -k="" for defaults)'],
        ['coverage', 'c', None, 'Run the coverage tool (generates HTML by default) (use -c="" for defaults)'],
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
        for tool in ALL_TOOLS:
            if self[tool]:
                self.tools[tool] = self[tool]

        if not self.tools:
            self.tools = {t: None for t in ALL_TOOLS}

        toolResults = {}

        toolOrder = [(t, self.tools[t]) for t in ALL_TOOLS if t in self.tools]

        for tool, extra in toolOrder:
            extra = shlex.split(extra or '')
            rc = getattr(self, 'run_' + tool)(extra)
            toolResults[tool] = rc

        print '#' * 80
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
        _args = [coverage, 'run', trial, 'noms']
        args = _args + (extra or [])
        return subprocess.call(args)

    def run_coverage(self, extra):
        """
        Run Python coverage
        """
        coverage = which('coverage')[0]
        _args = [coverage, 'html']
        args = _args + (extra or [])
        return subprocess.call(args)

    def run_pyflakes(self, extra):
        """
        Run pyflakes on Python code
        """
        pyflakes = which('pyflakes')[0]
        _args = [pyflakes, 'noms']
        args = _args + (extra or [])
        return subprocess.call(args)
