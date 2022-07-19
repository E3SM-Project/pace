#! /usr/bin/env python3
# @file parseE3SMTiming.py
# @brief parser for E3SM timing file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import unittest, gzip, json
'''
# use this for local because my PATH was not setup correctly
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/Users/4g5/Desktop/ornl/pace/portal/pace/e3sm/e3smParser')
import parseRunE3SMsh, parseBuildTime, parseE3SMTiming, parseMemoryProfile, parseModelVersion, parseNameList, parseRC, parseReadMe, parseScorpioStats, parseXML, parsePreviewRun, parseReplaysh
'''
from pace.e3sm.e3smParser import parseE3SMTiming
from pace.e3sm.e3smParser import parseModelVersion
from pace.e3sm.e3smParser import parseReadMe
from pace.e3sm.e3smParser import parseMemoryProfile
from pace.e3sm.e3smParser import parseScorpioStats
from pace.e3sm.e3smParser import parseXML
from pace.e3sm.e3smParser import parseRC
from pace.e3sm.e3smParser import parseNameList
from pace.e3sm.e3smParser import parseBuildTime
from pace.e3sm.e3smParser import parsePreviewRun
from pace.e3sm.e3smParser import parseReplaysh
from pace.e3sm.e3smParser import parseRunE3SMsh

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
        file = "atm_modelio.nml.303313.220628-152730.gz"
        dataExpected = json.dumps({"modelio": {"diri": "/compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/build/atm", "diro": "/compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/tests/S_1x5_ndays/run", "logfile": "atm.log.303313.220628-152730"}, "pio_inparm": {"pio_netcdf_format": "64bit_offset", "pio_numiotasks": -99, "pio_rearranger": 1, "pio_root": 0, "pio_stride": 40, "pio_typename": "pnetcdf"}})
        
        data = parseNameList.loaddb_namelist(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_previewRun(self):
        file = 'preview_run.log.303313.220628-152730.gz'
        dataExpected = {
                        "nodes":10,
                        "total_tasks":400,
                        "tasks_per_node":40,
                        "thread_count":1,
                        "ngpus_per_node":0,
                        "env":{
                            "I_MPI_ADJUST_ALLREDUCE":"1",
                            "LD_LIBRARY_PATH":"/share/apps/gcc/8.1.0/lib:/share/apps/gcc/8.1.0/lib64:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/tbb/lib/intel64_lin/gcc4.7:/share/apps/pnetcdf/1.9.0/intel/19.0.5/intelmpi/2019u4/lib:/share/apps/netcdf/4.6.3/intel/19.0.5/lib:/share/apps/hdf5/1.10.5/serial/lib:/share/apps/intel/2019u4/compilers_and_libraries_2019.4.243/linux/mpi/intel64/libfabric/lib:/share/apps/intel/2019u4/compilers_and_libraries_2019.4.243/linux/mpi/intel64/lib/release:/share/apps/intel/2019u4/compilers_and_libraries_2019.4.243/linux/mpi/intel64/lib:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/compiler/lib/intel64_lin:/share/apps/intel/2019u5/comepilers_and_libraries_2019.5.281/linux/mpi/intel64/libfabric/lib:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/mpi/intel64/lib/release:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/mpi/intel64/lib:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/ipp/lib/intel64:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/compiler/lib/intel64_lin:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/mkl/lib/intel64_lin:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/tbb/lib/intel64/gcc4.7:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/tbb/lib/intel64/gcc4.7:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/daal/lib/intel64_lin:/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/daal/../tbb/lib/intel64_lin/gcc4.4",
                            "MKL_PATH":"/share/apps/intel/2019u5/compilers_and_libraries_2019.5.281/linux/mkl",
                            "NETCDF_HOME":"/share/apps/netcdf/4.6.3/intel/19.0.5/",
                            "OMP_NUM_THREADS":"1"
                        },
                        "submit_cmd":"sbatch --time 00:20:00 -p short --account e3sm .case.run --resubmit",
                        "mpirun":"srun --mpi=pmi2 --ntasks=400 --nodes=10 --kill-on-bad-exit -l --cpu_bind=cores -c 1 -m plane=40 /compyfs/kezi456/E3SM_simulations/v2.master.mam5.PD/build/e3sm.exe   >> e3sm.log.$LID 2>&1",
                        "omp_threads":"1"
                        }
        data = parsePreviewRun.load_previewRunFile(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_rcFile(self):
        file = "seq_maps.rc.63117.210714-233452.gz"
        dataExpected = json.dumps({"atm2ice_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_EC30to60E2r2_mono.201005.nc","atm2ice_fmaptype":"X","atm2ice_smapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_EC30to60E2r2_bilin.201005.nc","atm2ice_smaptype":"X","atm2ice_vmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_EC30to60E2r2_bilin.201005.nc","atm2ice_vmaptype":"X","atm2lnd_fmapname":"idmap","atm2lnd_fmaptype":"X","atm2lnd_smapname":"idmap","atm2lnd_smaptype":"X","atm2ocn_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_EC30to60E2r2_mono.201005.nc","atm2ocn_fmaptype":"X","atm2ocn_smapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_EC30to60E2r2_bilin.201005.nc","atm2ocn_smaptype":"X","atm2ocn_vmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_EC30to60E2r2_bilin.201005.nc","atm2ocn_vmaptype":"X","atm2rof_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_mono.200220.nc","atm2rof_fmaptype":"X","atm2rof_smapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_mono.200220.nc","atm2rof_smaptype":"X","atm2wav_smapname":"idmap","atm2wav_smaptype":"X","glc2ice_fmapname":"idmap_ignore","glc2ice_fmaptype":"X","glc2ice_rmapname":"idmap_ignore","glc2ice_rmaptype":"X","glc2ice_smapname":"idmap_ignore","glc2ice_smaptype":"X","glc2lnd_fmapname":"idmap","glc2lnd_fmaptype":"X","glc2lnd_smapname":"idmap","glc2lnd_smaptype":"X","glc2ocn_fmapname":"idmap_ignore","glc2ocn_fmaptype":"X","glc2ocn_ice_rmapname":"idmap_ignore","glc2ocn_ice_rmaptype":"X","glc2ocn_liq_rmapname":"idmap_ignore","glc2ocn_liq_rmaptype":"X","glc2ocn_smapname":"idmap_ignore","glc2ocn_smaptype":"X","iac2atm_fmapname":"idmap","iac2atm_fmaptype":"X","iac2atm_smapname":"idmap","iac2atm_smaptype":"X","iac2lnd_fmapname":"idmap","iac2lnd_fmaptype":"X","iac2lnd_smapname":"idmap","iac2lnd_smaptype":"X","ice2atm_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/EC30to60E2r2/map_EC30to60E2r2_to_ne30pg2_mono.201005.nc","ice2atm_fmaptype":"X","ice2atm_smapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/EC30to60E2r2/map_EC30to60E2r2_to_ne30pg2_mono.201005.nc","ice2atm_smaptype":"X","ice2wav_smapname":"idmap","ice2wav_smaptype":"X","lnd2atm_fmapname":"idmap","lnd2atm_fmaptype":"X","lnd2atm_smapname":"idmap","lnd2atm_smaptype":"X","lnd2glc_fmapname":"idmap","lnd2glc_fmaptype":"X","lnd2glc_smapname":"idmap","lnd2glc_smaptype":"X","lnd2rof_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_mono.200220.nc","lnd2rof_fmaptype":"X","ocn2atm_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/EC30to60E2r2/map_EC30to60E2r2_to_ne30pg2_mono.201005.nc","ocn2atm_fmaptype":"X","ocn2atm_smapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/EC30to60E2r2/map_EC30to60E2r2_to_ne30pg2_mono.201005.nc","ocn2atm_smaptype":"X","ocn2glc_fmapname":"idmap_ignore","ocn2glc_fmaptype":"X","ocn2glc_smapname":"idmap_ignore","ocn2glc_smaptype":"X","ocn2wav_smapname":"idmap","ocn2wav_smaptype":"X","rof2lnd_fmapname":"/lcrc/group/e3sm/data/inputdata/cpl/gridmaps/ne30pg2/map_r05_to_ne30pg2_mono.200220.nc","rof2lnd_fmaptype":"X","rof2ocn_fmapname":"idmap_ignore","rof2ocn_fmaptype":"X","rof2ocn_ice_rmapname":"/lcrc/group/e3sm/data/inputdata/cpl/cpl6/map_r05_to_EC30to60E2r2_smoothed.r150e300.201005.nc","rof2ocn_ice_rmaptype":"X","rof2ocn_liq_rmapname":"/lcrc/group/e3sm/data/inputdata/cpl/cpl6/map_r05_to_EC30to60E2r2_smoothed.r150e300.201005.nc","rof2ocn_liq_rmaptype":"X","wav2ocn_smapname":"idmap","wav2ocn_smaptype":"X"}, separators=(',', ':'))
        data = parseRC.loaddb_rcfile(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_readMe(self):
        file = 'README.case.43235257.210608-222102.gz'
        dataExpected = {
                        "name":"create_newcase",
                        "date":"2021-06-07 10:17:07",
                        "case":"/global/cscratch1/sd/blazg/e3sm_scratch/e3sm_v1.2_ne30_noAgg-60",
                        "mach":"cori-knl",
                        "res":"ne30_ne30",
                        "compset":"F2010",
                        "compiler":"intel"
                        }
        data = parseReadMe.parseReadme(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_replaySh(self):
        file = 'replay.sh.303313.220628-152730.gz'
        with gzip.open(file, 'rt') as f:
            dataExpected = f.read()
        data = parseReplaysh.load_replayshFile(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_runE3SMSh(self):
        file = 'run_e3sm.sh.20220506-193932.556061.220506-194028.gz'
        with gzip.open(file, 'rt') as f:
            dataExpected = f.read()
        data = parseRunE3SMsh.load_rune3smshfile(file)
        self.assertEqual(data,dataExpected,dataExpected)

    def test_e3sm_scorpio(self):
        file = 'spio_stats.303313.220628-152730.tar.gz'
        data = parseScorpioStats.loaddb_scorpio_stats(file,360.212)
        self.assertEqual(data[0]['name'],'EAM-410856','EAM-410856')
        self.assertEqual(data[0]['iopercent'],64.17,64.17)
        self.assertEqual(data[0]['iotime'],231.149313,231.149313)
        self.assertEqual(data[0]['version'],'1.0.0','1.0.0')

    def test_e3sm_xmlfile(self):
        file = "env_batch.xml.63117.210714-233452.gz"
        dataExpected = json.dumps({"file": {"@id": "env_batch.xml", "@version": "2.0", "header": "These variables may be changed anytime during a run, they\n      control arguments to the batch submit command.", "group": [{"@id": "config_batch", "entry": {"@id": "BATCH_SYSTEM", "@value": "slurm", "type": "char", "valid_values": "nersc_slurm,lc_slurm,moab,pbs,lsf,slurm,cobalt,cobalt_theta,none", "desc": "The batch system type to use for this machine."}}, {"@id": "job_submission", "entry": {"@id": "PROJECT_REQUIRED", "@value": "FALSE", "type": "logical", "valid_values": "TRUE,FALSE", "desc": "whether the PROJECT value is required on this machine"}}], "batch_system": [{"@type": "slurm", "batch_query": {"@per_job_arg": "-j", "#text": "squeue"}, "batch_submit": "sbatch", "batch_cancel": "scancel", "batch_directive": "#SBATCH", "jobid_pattern": "(\\d+)$", "depend_string": "--dependency=afterok:jobid", "depend_allow_string": "--dependency=afterany:jobid", "depend_separator": ":", "walltime_format": "%H:%M:%S", "batch_mail_flag": "--mail-user", "batch_mail_type_flag": "--mail-type", "batch_mail_type": "none, all, begin, end, fail", "submit_args": {"arg": [{"@flag": "--time", "@name": "$JOB_WALLCLOCK_TIME"}, {"@flag": "-p", "@name": "$JOB_QUEUE"}, {"@flag": "--account", "@name": "$PROJECT"}]}, "directives": {"directive": ["--job-name={{ job_id }}", "--nodes={{ num_nodes }}", "--output={{ job_id }}.%j", "--exclusive"]}}, {"@MACH": "chrysalis", "@type": "slurm", "directives": {"directive": "--switches=$SHELL{echo \"(`./xmlquery --value NUM_NODES` + 19) / 20\" |bc}"}, "queues": {"queue": [{"@walltimemax": "48:00:00", "@strict": "true", "@nodemin": "1", "@nodemax": "492", "#text": "compute"}, {"@walltimemax": "04:00:00", "@strict": "true", "@nodemin": "1", "@nodemax": "20", "@default": "true", "#text": "debug"}]}}]}})
        data = parseXML.loaddb_xmlfile(file)

        self.assertEqual(data,dataExpected,dataExpected)

if __name__ == "__main__":
    unittest.main()