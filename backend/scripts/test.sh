#!/usr/bin/env bash

set -e
set -x

# Compile gettext catalogs (.mo) from source (.po) so i18n tests see translations.
# .mo is gitignored; outside the Docker image (e.g. the Test Backend CI job runs
# pytest directly on the runner) nothing else compiles it.
pybabel compile -d app/locales

coverage run -m pytest tests/
coverage report
coverage html --title "${@-coverage}"
