re-worker-noop
====================

A simple noop worker for Winternewt, our new [release engine hotness](https://github.com/RHInception/?query=re-)

[![Build Status](https://api.travis-ci.org/RHInception/re-worker-noop.png)](https://travis-ci.org/RHInception/re-worker-noop/)

# For full documentation see the [Read The Docs](http://release-engine.readthedocs.org/en/latest/workers/reworkernoop.html) documentation.

# The special 'fail' step

This worker provides **one** actual hard-coded step,
``noop:fail``. Including this step in a playbook will force a
deployment failure.
