#! /usr/bin/env python3
# @file parseE3SMTiming.py
# @brief parser for E3SM timing file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import unittest

# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/Users/4g5/Desktop/ornl/pace/portal/pace/e3sm/e3smParser')

import parseBuildTime, parseE3SMTiming, parseMemoryProfile, parseModelVersion, parseNameList, parseRC, parseReadMe, parseScorpioStats, parseXML

class testE3SMParse(unittest.TestCase):

    def test_e3sm_buildTime(self):
        filename = 'build_times.txt.303313.220628-152730.gz'
        data, total_computecost,total_elapsed_time = parseBuildTime.loaddb_buildTimesFile(filename)

        self.assertEqual(total_computecost,1946.7374160000015,"Should be 1946.7374160000015")
        self.assertEqual(total_elapsed_time,450.49,"Should be 450.49")

    def test_e3sm_caseDocs(self):
        pass

    def test_e3sm_timing(self):
        pass

    def test_e3sm_memoryProfile(self):
        pass

    def test_e3sm_modelVersion(self):
        expectedData = 'v2.0.0-beta.3-3091-g3219b44fc'
        filename = 'GIT_DESCRIBE.43235257.210608-222102.gz'
        gotData = parseModelVersion.parseModelVersion(filename)
        
        self.assertEqual(gotData, expectedData, "Should be v2.0.0-beta.3-3091-g3219b44fc")

    def test_e3sm_nameList(self):
        pass
    
    def test_e3sm_previewRun(self):
        pass

    def test_e3sm_rcFile(self):
        pass

    def test_e3sm_readMe(self):
        pass

    def test_e3sm_replaySh(self):
        pass

    def test_e3sm_runE3SMSh(self):
        pass

    def test_e3sm_scorpio(self):
        pass

    def test_e3sm_text(self):
        pass

    def test_e3sm_xmlfile(self):
        pass


if __name__ == "__main__":
    unittest.main()

    #filename = "e3sm_timing.e3sm_v1.2_ne30_noAgg-60.43235257.210608-222102.gz"
    #print(parseE3SMTiming.parseE3SMtiming(filename))
    
    #filename = "memory.3.86400.log.63117.210714-233452.gz"
    #print(parseMemoryProfile.loaddb_memfile(filename))

    #filename = 'GIT_DESCRIBE.43235257.210608-222102.gz'
    #print(parseModelVersion.parseModelVersion(filename))

    #filename = "atm_in.63117.210714-233452.gz"
    #print(parseNameList.loaddb_namelist(filename))

    #filename = "seq_maps.rc.63117.210714-233452.gz"
    #print(parseRC.loaddb_rcfile(filename))

    #filename = "README.case.43235257.210608-222102.gz"
    #print(parseReadMe.parseReadme(filename))

    #filename = "spio_stats.63117.210714-233452.tar.gz"
    #print(parseScorpioStats.loaddb_scorpio_stats(filename))

    #filename = "env_batch.xml.63117.210714-233452.gz"
    #print(parseXML.loaddb_xmlfile(filename))