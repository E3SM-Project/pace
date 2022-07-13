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

import parseBuildTime, parseE3SMTiming, parseMemoryProfile, parseModelVersion, parseNameList, parseRC, parseReadMe, parseScorpioStats, parseXML, parsePreviewRun, parseReplaysh

class testE3SMParse(unittest.TestCase):

    def test_e3sm_buildTime(self):
        filename = 'build_times.txt.303313.220628-152730.gz'
        data, total_computecost,total_elapsed_time = parseBuildTime.loaddb_buildTimesFile(filename)

        self.assertEqual(total_computecost,1946.7374160000015,"Should be 1946.7374160000015")
        self.assertEqual(total_elapsed_time,450.49,"Should be 450.49")

    def test_e3sm_timing(self):
        filename = 'e3sm_timing.e3sm_v1.2_ne30_noAgg-60.43235257.210608-222102'
        successFlag, timingProfileInfo, componentTable, runTimeTable = parseE3SMTiming.parseE3SMtiming(filename)
        timingProfileInfoData = {'case': 'e3sm_v1.2_ne30_noAgg-60', 'lid': '43235257.210608-222102', 'machine': 'cori-knl', 'caseroot': '/global/cscratch1/sd/blazg/e3sm_scratch/e3sm_v1.2_ne30_noAgg-60', 'timeroot': '/global/cscratch1/sd/blazg/e3sm_scratch/e3sm_v1.2_ne30_noAgg-60/Tools', 'user': 'blazg', 'curr': 'Wed Jun  9 01:07:55 2021', 'long_res': 'a%ne30np4_l%ne30np4_oi%ne30np4_r%r05_g%null_w%null_z%null_m%gx1v6', 'long_compset': '2010_EAM%CMIP6_ELM%SPBC_CICE%PRES_DOCN%DOM_MOSART_SGLC_SWAV_SIAC_SESP', 'stop_option': 'nmonths', 'stop_n': '6', 'run_length': '184', 'total_pes': '5400', 'mpi_task': '32', 'pe_count': '1376', 'model_cost': '7473.60', 'model_throughput': '4.42', 'init_time': '81.132', 'run_time': '9856.861', 'final_time': '0.325', 'actual_ocn': '39.855'}
        componentTableData = ['cpl', '5400', '0', '1350', '4', '1', '1', 'atm', '5400', '0', '1350', '4', '1', '1', 'lnd', '5400', '0', '1350', '4', '1', '1', 'ice', '1200', '0', '1200', '1', '1', '1', 'ocn', '1200', '0', '1200', '1', '1', '1', 'rof', '1350', '0', '1350', '1', '1', '1', 'glc', '32', '0', '32', '1', '1', '1', 'wav', '32', '0', '32', '1', '1', '1', 'iac', '1', '0', '1', '1', '1', '1']
        runTimeTableData = ['TOT', '9856.861', '53.570', '4.42', 'CPL', '167.454', '0.910', '260.10', 'ATM', '8757.355', '47.594', '4.97', 'LND', '609.132', '3.310', '71.50', 'ICE', '72.266', '0.393', '602.70', 'OCN', '13.568', '0.074', '3210.13', 'ROF', '89.037', '0.484', '489.18', 'GLC', '0.000', '0.000', '0.00', 'WAV', '0.000', '0.000', '0.00', 'IAC', '0.000', '0.000', '0.00', 'ESP', '0.000', '0.000', '0.00']
        
        self.assertEqual(timingProfileInfo,timingProfileInfoData,timingProfileInfoData)
        self.assertEqual(componentTable,componentTableData,componentTableData)
        self.assertEqual(runTimeTable,runTimeTableData,runTimeTableData)

    def test_e3sm_memoryProfile(self):
        need_data = '#TOD, VSZ_CPL_N_0, RSS_CPL_N_0, VSZ_ATM_N_0, RSS_ATM_N_0, VSZ_LND_N_0, RSS_LND_N_0, VSZ_ICE_N_0, RSS_ICE_N_0, VSZ_OCN_N_0, RSS_OCN_N_0, VSZ_GLC_N_0, RSS_GLC_N_0, VSZ_ROF_N_0, RSS_ROF_N_0, VSZ_WAV_N_0, RSS_WAV_N_0, VSZ_IAC_N_0, RSS_IAC_N_0\n19890912.00000,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566,   125305.090,    25347.566\n19890914.00000,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953,   131423.867,    27270.953\n'
        actual_data = parseMemoryProfile.loaddb_memfile('memory.3.86400.log.61012576.220711-001958.gz')
        self.assertEqual(need_data,actual_data,"Should be"+need_data)

    def test_e3sm_modelVersion(self):
        expectedData = 'v2.0.0-beta.3-3091-g3219b44fc'
        filename = 'GIT_DESCRIBE.43235257.210608-222102.gz'
        gotData = parseModelVersion.parseModelVersion(filename)
        
        self.assertEqual(gotData, expectedData, "Should be v2.0.0-beta.3-3091-g3219b44fc")

    def test_e3sm_nameList(self):
        pass
    
    def test_e3sm_previewRun(self):
        file = 'preview_run.log.303313.220628-152730.gz'
        dataExpected = {'nodes': 10, 'total_tasks': 400, 'tasks_per_node': 40, 'thread_count': 1, 'ngpus_per_node': 0, 'mpirun': 'srun --mpi=pmi2 --ntasks=400 --nodes=10 --kill-on-bad-exit -l --cpu_bind=cores -c 1 -m plane=40 /compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/build/e3sm.exe   >> e3sm.log.$LID 2>&1'}
        data = parsePreviewRun.load_previewRunFile(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_rcFile(self):
        pass

    def test_e3sm_readMe(self):
        pass

    def test_e3sm_replaySh(self):
        file = 'replay.sh.303313.220628-152730.gz'
        data = parseReplaysh.load_replayshFile(file)
        #print(data)
        #dataExpected = '#!/bin/bash\r\n\r\nset -e\r\n\r\n# Created 2022-06-28 14:25:03\r\n\r\nCASEDIR=\"/compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/tests/S_1x5_ndays/case_scripts\"\r\n\r\n/qfs/people/kezi456/E3SM_code/v2-master/cime/scripts/create_newcase --case v2.master.mam5.PD --output-root /compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD --script-root \"${CASEDIR}\" --handle-preexisting-dirs u --compset F2010 --res ne30pg2_EC30to60E2r2 --machine compy --project e3sm --walltime 00:20:00 --pecount custom-10\r\n\r\ncd \"${CASEDIR}\"\r\n\r\n./xmlchange NTASKS=400\r\n\r\n./xmlchange NTHRDS=1\r\n\r\n./xmlchange MAX_MPITASKS_PER_NODE=40\r\n\r\n./xmlchange MAX_TASKS_PER_NODE=40\r\n\r\n./xmlchange EXEROOT=/compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/build\r\n\r\n./xmlchange RUNDIR=/compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/tests/S_1x5_ndays/run\r\n\r\n./xmlchange DOUT_S=FALSE\r\n\r\n./xmlchange DOUT_S_ROOT=/compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/archive\r\n\r\n./xmlchange --id CAM_CONFIG_OPTS --append --val=-chem linoz_mam5_resus_mom_soag -usr_mech_infile /qfs/people/kezi456/codes/compy.mam5/chem/chem_mech_MAM5_SC_E90.in\r\n\r\n./case.setup --reset\r\n\r\n./case.build\r\n\r\n./case.build\r\n\r\n./case.build --clean-all\r\n\r\n./case.build\r\n\r\n./case.submit\r\n\r\n./case.submit\r\n\r\n./case.submit\r\n\r\n./case.submit'
        
        #self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_runE3SMSh(self):
        pass

    def test_e3sm_scorpio(self):
        file = 'spio_stats.303313.220628-152730.tar.gz'
        data = parseScorpioStats.loaddb_scorpio_stats(file,360.212)
        print(data[0]['data'])

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