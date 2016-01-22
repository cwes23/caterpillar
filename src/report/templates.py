#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generates a Caterpillar conversion report.
"""

from __future__ import print_function, division, unicode_literals

import jinja2


TEMPLATE_SUMMARY = jinja2.Template("""
<section id="summary">
  <h2>Summary</h2>
  <span class="name">{{ ca_manifest.name }}</span> was
  <span class="conversion-status {{ status }}">
    {% if status == Status.TOTAL %}
      successfully
    {% elif status == Status.PARTIAL %}
      partially
    {% else %}
      not
    {% endif %}
    converted{%- if warnings -%}, with warnings{%- endif -%}.
  </span>

  <ul>
    {% for pf_name, pf_info in apis.items() | sort %}
      <li>
        <span class="ca-feature {{ pf_info.status }}">
          chrome.{{ pf_name }}
        </span>
        was {% if pf_info.status == Status.NONE %} not {% endif %} polyfilled.
      </li>
    {% endfor %}
  </ul>
</section>
""")


TEMPLATE_GENERAL_WARNINGS = jinja2.Template("""
{% if warnings %}
<section id="general-warnings">
  <h2>General Warnings</h2>
  <ul>
    {% for warning in warnings %}
      <li>{{ warning }}</li>
    {% endfor %}
  </ul>
</section>
{% endif %}
""")


TEMPLATE_POLYFILLED = jinja2.Template("""
{% if some_polyfilled %}
<section id="polyfilled">
  <h2>Polyfilled Chrome Apps APIs</h2>
  <p>
    Some Chrome Apps APIs have been polyfilled. Calls to these APIs will
    generally still work, though there may be missing functionality. You should
    check that the functionality you rely on still works.
  </p>

  {% for pf_name, pf_info in apis.items() %}
    <section class="polyfill">
      <h3 class="ca-feature {{ pf_info.status }}">
        chrome.{{ pf_name }}
      </h3>
      <p>
        <span class="ca-feature {{ pf_info.status }}">
          chrome.{{ pf_name }}
        </span> was
        {% if pf_info.status == Status.PARTIAL %} partially {% endif %}
        polyfilled.
      </p>
      {% if pf_info.relevant_warnings %}
        <p>
          <span class="name">{{ ca_manifest.name }}</span> seems to make use of
          features with missing or altered functionality in the polyfill:
        </p>
        <ul>
          {% for warning in pf_info.relevant_warnings %}
            <li>{{ warning }}</li>
          {% endfor %}
        </ul>
      {% endif %}
      {% if pf_info.other_warnings %}
        <p>
          Additionally, the
          <span class="ca-feature {{ pf_info.status }}">
            chrome.{{ pf_name }}
          </span> polyfill has the following missing or altered functionality:
        </p>
        <ul>
          {% for warning in pf_info.other_warnings %}
            <li>{{ warning }}</li>
          {% endfor %}
        </ul>
        <p>
          <span class="name">{{ ca_manifest.name }}</span> doesn't seem to use
          these features, but you should check to make sure.
        </p>
      {% endif %}
      <p>
        <span class="name">{{ ca_manifest.name }}</span> uses
        <span class="ca-feature {{ pf_info.status }}">
          {{ pf_name }}
        </span>
        in the following places:
      </p>
      {% for path, start, context, line_num in pf_info.usage %}
        <p class="code-location path">{{ path }}:{{ start+2 }}</p>
<pre>
<code class="prettyprint lang-js linenums:{{ start }}">{{ context }}</code>
</pre>
      {% endfor %}
    </section>
  {% endfor %}
</section>
{% endif %}
""")


TEMPLATE_NOT_POLYFILLED = jinja2.Template("""
{% if some_not_polyfilled %}
<section id="not-polyfilled">
  <h2>Missing Chrome Apps APIs</h2>
  <p>
    Some Chrome Apps APIs have not been polyfilled, and your application may
    rely on them. Places they are used in your application are shown below.
  </p>

  {% for pf_name, pf_info in apis.items() %}
    <section class="missing-api">
      <h3 class="ca-feature {{ pf_info.status }}">
        chrome.{{ pf_name }}
      </h3>
      <p>
        <span class="name">{{ ca_manifest.name }}</span> uses
        <span class="ca-feature {{ pf_info.status }}">
          {{ pf_name }}
        </span>
        in the following places:
      </p>
      {% for path, start, context, line_num in pf_info.usage %}
        <p class="code-location path">{{ path }}:{{ start+2 }}</p>
<pre>
<code class="prettyprint lang-js linenums:{{ start }}">{{ context }}</code>
</pre>
      {% endfor %}
    </section>
  {% endfor %}
</section>
{% endif %}
""")


TEMPLATE_FULL = jinja2.Template("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Caterpillar Conversion Report: {{ ca_manifest.name }}</title>
    <link rel="stylesheet" href="../bower_components/lato/css/lato.css">
    <link rel="stylesheet" href="css/report.css">
  <body>
    <div id="report">
      <h1>
        Caterpillar Conversion Report:
        <span class="name">{{ ca_manifest.name }}</span>
      </h1>
      {{ summary }}
      {{ general_warnings }}
      {{ polyfilled }}
      {{ not_polyfilled }}
    </div>
    <footer>
      Generated by
      <a href="https://github.com/chromium/caterpillar">Caterpillar</a>.
    </footer>
    <script src="../bower_components/code-prettify/src/run_prettify.js">
    </script>
  </body>
</html>
""")
