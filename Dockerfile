# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2015 CERN.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

# Use Python-2.7:
FROM python:2.7

# Install some prerequisites ahead of `setup.py` in order to profit
# from the docker build cache:
RUN pip install 'coverage<4.0a1' \
                flask \
                pydocstyle \
                pytest \
                pytest-cov \
                pytest-pep8 \
                sphinx

# Add sources to `code` and work there:
WORKDIR /code
ADD . /code

# Install Flask-Menu:
RUN pip install -e .[docs]

# Run container as user `flaskmenu` with UID `1000`, which should match
# current host user in most situations:
RUN adduser --uid 1000 --disabled-password --gecos '' flaskmenu && \
    chown -R flaskmenu:flaskmenu /code

# Start simple example application:
USER flaskmenu
CMD  ["python", "examples/simple/app.py"]
