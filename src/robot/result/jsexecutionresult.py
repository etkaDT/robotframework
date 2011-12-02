#  Copyright 2008-2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time

from robot import utils
from robot.reporting.parsingcontext import TextIndex


class JsExecutionResult(object):

    def __init__(self, suite, statistics, errors, strings, basemillis,
                 split_results=None):
        self.suite = suite
        self.strings = strings
        self.data = self._get_data(statistics, errors, basemillis)
        self.split_results = split_results or []

    def _get_data(self, statistics, errors, basemillis):
        gentime = time.localtime()
        return {
            'stats': statistics,
            'errors': errors,
            'baseMillis': basemillis,
            'generatedMillis': long(time.mktime(gentime) * 1000) - basemillis,
            'generatedTimestamp': utils.format_time(gentime, gmtsep=' ')
        }

    # TODO: Combine remove_keywords and remove_errors
    # into remove_data_not_needed_in_report or something similar.
    # The code related to removing should also be moved into a separate object.

    def remove_keywords(self):
        self._remove_keywords_from_suite(self.suite)
        self._prune_unused_indices()

    def remove_errors(self):
        self.data.pop('errors')

    def _remove_keywords_from_suite(self, suite):
        suite[8] = []
        for subsuite in suite[6]:
            self._remove_keywords_from_suite(subsuite)
        for test in suite[7]:
            test[-1] = []

    def _prune_unused_indices(self):
        used = self._collect_used_indices(self.suite, set())
        remap = {}
        self.strings = \
            list(self._prune(self.strings, used, remap))
        self._remap_indices(self.suite, remap)

    def _prune(self, data, used, index_remap):
        offset = 0
        for index, text in enumerate(data):
            if index in used:
                index_remap[index] = index - offset
                yield text
            else:
                offset += 1

    def _remap_indices(self, data, remap):
        for i, item in enumerate(data):
            if isinstance(item, TextIndex):
                data[i] = remap[item]
            elif isinstance(item, list):
                self._remap_indices(item, remap)

    def _collect_used_indices(self, data, result):
        for item in data:
            if isinstance(item, TextIndex):
                result.add(item)
            elif isinstance(item, list):
                self._collect_used_indices(item, result)
        return result