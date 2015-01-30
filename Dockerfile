# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2015 CERN.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

FROM python:2.7
ADD . /code
WORKDIR /code
RUN pip install pep257
RUN pip install sphinx
RUN python setup.py develop
