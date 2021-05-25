Performance Analytics for Computational Experiments (PACE) Client
================================================================================

PACE client tool is a python executable which uploads and parse E3SM performance data 
into PACE server and DB.


Quick Start
--------------------------------------------------------------------------------
USAGE: pace-upload [--help/-h] [--exp-dir/-ed SOURCE] [--perf-archive/-pa SOURCE] [--application/-a {e3sm}]

optional arguments:
  -h, --help            show this help message and exit
  --exp-dir SOURCE, -ed SOURCE
                        Root directory containing experiment(s) results. Handles multiple experiment directories under root
  --perf-archive SOURCE, -pa SOURCE
                        Root directory containing performance archive. Handles multiple performance archive directories under root
  --application {e3sm}, -a {e3sm}
                        Application name, default set to e3sm.

Prerequisites
--------------------------------------------------------------------------------
* Python

