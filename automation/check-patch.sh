#!/bin/bash -xe

pyflakes `find . -name "*.py"`
pep8 `find . -name "*.py"`
