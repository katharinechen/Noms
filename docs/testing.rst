Testing
=======

We currently use pytest as a tool to run test, but use with pytest and pyUnit/trial style for writing tests.

How to run test on your local branch?

To run test on your local machine, use pytest. To see whether or not your test passes on the CI server, you can go to github and view travis. pytest is a tool to run tests. pytest also have a style of writing test. There are a few different ways to use pytest.

To run a specific test, use: pytest noms/test/test_rendering.py
To run all of the test, use: pytest
To run only the failing test, use pytest --lf
Why did we change from trial to pytest? What are the pros and cons?

pytest and trial are both compatible with twisted. pytest can be integrated with pyflakes and is faster than trail.