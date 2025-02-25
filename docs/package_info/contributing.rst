Contributing to Async PRAW
==========================

Async PRAW gladly welcomes new contributions. As with most larger projects, we have an
established consistent way of doing things. A consistent style increases readability,
decreases bug-potential and makes it faster to understand how everything works together.

Async PRAW follows :PEP:`8` and :PEP:`257`. `pre-commit <https://pre-commit.com>`_ is
used to manage a suite of pre-commit hooks that enforce conformance with these PEPs
along with several other checks. Additionally, the ``pre_push.py`` script can be used to
run the full pre-commit suite and the docs build prior to submitting a pull request. The
following are Async PRAW-specific guidelines in addition to those PEPs.

.. note::

    In order to use the pre-commit hooks and the ``pre_push.py`` dependencies, install
    Async PRAW's ``[lint]`` extra, followed by the appropriate pre-commit command:

    .. code-block:: bash

        pip install asyncpraw[lint]
        pre-commit install

    If you are using ``zsh`` for your shell, you will need to double-quote
    ``"asyncpraw[lint]"`` like so:

    .. code-block:: zsh

        pip install "asyncpraw[lint]"
        pre-commit install

Code
----

- Within a single file classes are sorted alphabetically where inheritance permits.
- Within a class, methods are sorted alphabetically within their respective groups with
  the following as the grouping order:

  - Static methods
  - Class methods
  - Cached properties
  - Properties
  - Instance Methods

- Use descriptive names for the catch-all keyword argument. E.g., ``**other_options``
  rather than ``**kwargs``.

Testing
-------

Contributions to Async PRAW requires 100% test coverage as reported by `Coveralls
<https://coveralls.io/github/praw-dev/asyncpraw>`_. If you know how to add a feature,
but aren't sure how to write the necessary tests, please open a pull request anyway so
we can work with you to write the necessary tests.

Running the Test Suite
~~~~~~~~~~~~~~~~~~~~~~

`GitHub Actions <https://github.com/praw-dev/asyncpraw/actions>`_ automatically runs all
updates to known branches and pull requests. However, it's useful to be able to run the
tests locally. The simplest way is via:

.. code-block:: bash

    pytest

Without any configuration or modification, all the tests should pass. If they do not,
please file a bug report.

.. note::

    Async PRAW uses a fork of `vcrpy` before you can run tests locally you must install
    the forked version.

    .. code-block:: bash

        pip install https://github.com/LilSpazJoekp/vcrpy/archive/asyncpraw.zip

Adding and Updating Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Async PRAW's integration tests utilize `vcrpy
<https://vcrpy.readthedocs.io/en/latest/>`_ to record an interaction with Reddit. The
recorded interaction is then replayed for subsequent test runs.

To safely record a cassette without leaking your account credentials, Async PRAW
utilizes a number of environment variables which are replaced with placeholders in the
cassettes. The environment variables are (listed in bash export format):

.. code-block:: bash

    export prawtest_client_id=myclientid
    export prawtest_client_secret=myclientsecret
    export prawtest_password=mypassword
    export prawtest_test_subreddit=test
    export prawtest_username=myusername
    export prawtest_user_agent=praw_pytest

By setting these environment variables prior to running ``pytest``, when adding or
updating cassettes, instances of ``mypassword`` will be replaced by the placeholder text
``<PASSWORD>`` and similar for the other environment variables.

To use a refresh token instead of username/password set ``prawtest_refresh_token``
instead of ``prawtest_password`` and ``prawtest_username``.

When adding or updating a cassette, you will likely want to force requests to occur
again rather than using an existing cassette. The simplest way to rebuild a cassette is
to first delete it, and then rerun the test suite.

Please always verify that only the requests you expect to be made are contained within
your cassette.

Documentation
-------------

- All publicly available functions, classes, and modules should have a docstring.
- All documentation files and docstrings should be linted and formatted by
  ``docstrfmt``.
- Use correct terminology. A subreddit's fullname is something like ``t5_xyfc7``. The
  correct term for a subreddit's "name" like `python <https://www.reddit.com/r/python>`_
  is its display name.

Static Checker
~~~~~~~~~~~~~~

Async PRAW's test suite comes with a checker tool that can warn you of using incorrect
documentation styles (using ``.. code::`` instead of ``.. code-block::``, using ``/r/``
instead of ``r/``, etc.). This is run automatically by the pre-commit hooks and the
``pre_push.py`` script.

.. autoclass:: tools.static_word_checks.StaticChecker
    :inherited-members:

Files to Update
---------------

AUTHORS.rst
~~~~~~~~~~~

For your first contribution, please add yourself to the end of the respective list in
the ``AUTHORS.rst`` file.

CHANGES.rst
~~~~~~~~~~~

For feature additions, bugfixes, or code removal please add an appropriate entry to
``CHANGES.rst``. If the ``Unreleased`` section does not exist at the top of
``CHANGES.rst`` please add it. See `commit 280525c16ba28cdd69cdbb272a0e2764b1c7e6a0
<https://github.com/praw-dev/praw/commit/280525c16ba28cdd69cdbb272a0e2764b1c7e6a0>`_ for
an example.

See Also
--------

Please also read through:
https://github.com/praw-dev/asyncpraw/blob/master/.github/CONTRIBUTING.rst
