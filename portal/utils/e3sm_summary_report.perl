#!/usr/bin/perl

#  Perl 5 required.
require 5.004;

#  Strict syntax checking.
use strict;

#  Modules.
use Cwd;
use Time::Local;

=head1 NAME

e3sm_summary_report

=head1 SYNOPSIS

summarize job information in a performance_archive 
at NERSC, at ALCF, at OLCF, on Anvil, or on Compy

=head1 DESCRIPTION

Summarize e3sm job statistics in a performance_archive
for jobs at NERSC run on Cori-Haswell, Cori-KNL, or Edison,
jobs at ALCF run on Theta, jobs at OLCF run on Summit
or Titan, jobs run on Anvil, or jobs run on Compy.
Meant to be used with biweekly archive of the 
performance_archive.

Usage:

perl e3sm_summary_report.perl

within the top level of a performance_archive at NERSC,
at ALCF, at OLCF, on Anvil, or on Compy

Optional arguments:
  -h, --help      show this help message and exit 
  -u, --user [user name]
                  limit summary to jobs submitted by indicated user
  -a, --account [account name]
                  limit summary to jobs charged against indicated account
  -s, --system [{anvil, compy, cori-haswell, cori-knl, edison, summit, theta, titan}]
                  limit summary to jobs run on indicated system
  -r, --runlength [number of simulation days]
                  limit summary to jobs requesting to run more than
                  indicated number of simulation days
  -d, --detail [{0,1,2,3}]
                   0: basic summary (default)
                   1: also summarize by (compset,resolution,number of nodes)
                   2: also summarize by compset for each user
                  >2: also summarize per job
  -m, --medminratio [ratio of dt median to dt min]
                  output job information when median time
                  to calculate a simulation day exceeds the
                  minimum time by more than the indicated ratio
  -p, --avgmedratio [ratio of dt average to dt median]
                  output job information when average time
                  to calculate a simulation day exceeds the
                  median time by more than the indicated ratio
  -c, --highcostdef [dt cost relative to minimum]
                  increase in simulation day cost as compared
                  to the minimum that defines a high cost 
                  simulation day (default is 2.0)
  -n, --highcostnum [{0,1,2,...,31}]
                  number of high cost days in 31 consecutive days
                  that will trigger output of job information
                  (default is 32)

=head1 AUTHOR

Pat Worley E<lt>F<worleyph@ornl.gov>E<gt>

=cut

###############################################################################
#
#  Miscellaneous global flags and variables.
#
###############################################################################

###############################################################################
#
#  This is the call to main.
#
###############################################################################

    &main();

exit 0;

###############################################################################
#
#  This is main.
#
###############################################################################

sub main {

  # System specific
  my %maxnodes;
  $maxnodes{'anvil'} = 240;
  $maxnodes{'compy'} = 460;
  $maxnodes{'cori-haswell'} = 2388;
  $maxnodes{'cori-knl'} = 9688;
  $maxnodes{'edison'} = 5586;
  $maxnodes{'theta'} = 4392;
  $maxnodes{'titan'} = 18688;
  $maxnodes{'summit'} = 4608;

  # define variables
  my %month_to_number;
  my $arg_flag;
  my $user = "*";
  my $account = "*";
  my $system = "*";
  my $runlength = 0;
  my $detail = 0;
  my $ratio_med_min = 10000.;
  my $ratio_avg_med = 10000.;
  my $highcost_def = 2.0;
  my $highcost_num = 32;
  my $curtime;
  my $cursec;
  my $curmin;
  my $curhour;
  my $curmday;
  my $curmon;
  my $curyear;
  my $curwday;
  my $curyday;
  my $curisdst;
  my $performance_archive;
  my @users;
  my %totalcompletedjobswithperfsummary;
  my %totalcompletedjobsnoperfsummary;
  my %totalfailedjobs;
  my %totaloutoftimejobs;
  my %totalfailedjobswithsimdays;
  my %totalcompletedsimdays;
  my %totalfailedsimdays;
  my %totalcompletednodeseconds;
  my %totalfailednodeseconds;
  my %period;
  my $thisuser;
  my $thisuser_directory;
  my @cases;
  my $thiscase;
  my $thiscase_directory;
  my @lids;
  my $lid;
  my $lid_directory;
  my $thissystem;
  my $envbatchf;
  my $envbatchf_readable;
  my %systems;
  my $thisrun_length_target;
  my $env_runf;
  my $env_runf_readable;
  my $thisstop_option;
  my $thisstop_n;
  my $thisdin_loc_root;
  my $thissyslog_n;
  my $job_statsf_string;
  my $job_statsf;
  my $job_statsf_readable;
  my $bjobs_submit_jobid;
  my $bjobs_submit_time;
  my $found_bjobs_submit;
  my $bjobs_start_time;
  my $found_bjobs_start;
  my $bjobs_submit_year;
  my $bjobs_submit_month;
  my $bjobs_submit_day;
  my $bjobs_submit_hour;
  my $bjobs_submit_minute;
  my $bjobs_submit_second;
  my $bjobs_start_year;
  my $bjobs_start_month;
  my $bjobs_start_day;
  my $bjobs_start_hour;
  my $bjobs_start_minute;
  my $bjobs_start_second;
  my $thisjobid;
  my $thisqueue;
  my $thisaccount;
  my %thisjob_limit;
  my %thisjob_submit;
  my %thisjob_start;
  my $thisnumnodes;
  my $thisfeatures;
  my @squeueall_field;
  my $thisjob_waittime;
  my @thisjob_waittime;
  my $thiscompset_alias;
  my $thisres_alias;
  my $READMEcasef;
  my $READMEcasef_readable;
  my $GIT_DESCRIBEf;
  my $GIT_DESCRIBEf_readable;
  my $thisgit_describe;
  my $seconds_until_finished;
  my @thesedt;
  my @sorted_thesedt;
  my @thishighcost_gap;
  my $thisjob_time;
  my $daycount;
  my $thiswalltime;
  my $thisstring;
  my $thisratio_medmin;
  my $thisratio_avgmed;
  my $thisratio_maxmin;
  my $thisdt_maxreg;
  my $thishighcost_num;
  my $thisgap_maxcnt;
  my $cpllogf;
  my $cpllogf_readable;
  my $firstsimdate;
  my $thissimdate;
  my $thiswallyear;
  my $thiswallmonth;
  my $thiswallday;
  my $thiswallhour;
  my $thiswallminute;
  my $thiswallsecond;
  my $thisdt_avg;
  my $thisdt;
  my $thisdt_min;
  my $thisdt_med;
  my $thisdt_max;
  my $thishighcost_curr;
  my $thishighcost_next;
  my $thishighcost_gaps;
  my $thisgap_curr;
  my $thisgap_cnt;
  my $thisgap_size;
  my $thisgap_next;
  my $thiscompleted;
  my $thisperfsummary;
  my $found_caserun_start;
  my $found_caserun_success;
  my $CaseStatusf;
  my %caserun_start;
  my %caserun_success;
  my $thisjob_inittime;
  my $thiscase_runtime;
  my $acme_timingf;
  my $e3sm_timingf;
  my $thiscasename;
  my $thislid;
  my %curr_date;
  my $thisgrid;
  my $thiscompset;
  my $thisrun_length;
  my $thisrun_length_unit;
  my $thisinit_time;
  my $thisinit_time_unit;
  my $thisrun_time;
  my $thisrun_time_unit;
  my $thisfinal_time;
  my $thisfinal_time_unit;
  my $thistot_sypd;
  my $thisrun_total;
  my $thiscase_ovhdtime;
  my $thisjob_runtime;
  my $thistime_remaining;
  my $cpllogstepf;
  my $cpllogstepf_readable;
  my %completedsypd;
  my %completedsimdays;
  my %failedsimdays;
  my %completedjobswithperfsummary;
  my %completedjobsnoperfsummary;
  my %failedjobs;
  my %outoftimejobs;
  my %failedjobswithsimdays;
  my $failedjobsnosimdays;
  my $totalnodehours;
  my $maxnodehours;
  my $totalnodehourspercentage;
  my %summary;
  my $max_sypd;
  my $max_sypd_lid;
  my $max_sypd_user;
  my $max_sypd_case;
  my $min_sypd;
  my $min_sypd_lid;
  my $min_sypd_user;
  my $min_sypd_case;
  my $avg_sypd;
  my $thisfailed_jobs;
  my $thisoutoftime_jobs;
  my $cnt;
  my $simdays;

  %month_to_number = qw(
    jan 01  feb 02  mar 03  apr 04  may 05  jun 06
    jul 07  aug 08  sep 09  oct 10  nov 11  dec 12
  );

  for (my $i=0; $i <= $#ARGV; $i+=2){
    $arg_flag = $ARGV[$i];
    if (($arg_flag =~ m/^-h$/) || ($arg_flag =~ m/^--help$/)){
      print
"Usage:

perl e3sm_summary_report.perl

within the top level of a performance_archive at NERSC, 
at ALCF, at OLCF, on Anvil, or on Compy

Purpose:
Script to summarize throughput for E3SM jobs at NERSC 
run on Cori-Haswell, Cori-KNL, or Edison, jobs at ALCF run 
on Theta, jobs at OLCF run on Summit or Titan, jobs run 
on Anvil, or jobs run on Compy.

Optional arguments:
  -h, --help      show this help message and exit 
  -u, --user [user name]
                  limit summary to jobs submitted by indicated user
  -a, --account [account name]
                  limit summary to jobs charged against indicated account
  -s, --system [{anvil, compy, cori-haswell, cori-knl, edison, summit, theta, titan}]
                  limit summary to jobs run on indicated system
  -r, --runlength [number of simulation days]
                  limit summary to jobs requesting to run more than
                  indicated number of simulation days
  -d, --detail [{0,1,2,3}]
                   0: basic summary (default)
                   1: also summarize by (compset,resolution,number of nodes)
                   2: also summarize by compset for each user
                  >2: also summarize per job
  -m, --medminratio [ratio of dt median to dt min]
                  output job information when median time
                  to calculate a simulation day exceeds the
                  minimum time by more than the indicated ratio
  -p, --avgmedratio [ratio of dt average to dt median]
                  output job information when average time
                  to calculate a simulation day exceeds the
                  median time by more than the indicated ratio
  -c, --highcostdef [dt cost relative to minimum]
                  increase in simulation day cost as compared
                  to the minimum that defines a high cost 
                  simulation day (default is 2.0)
  -n, --highcostnum [{0,1,2,...,31}]
                  number of high cost days in 31 consecutive days
                  that will trigger output of job information
                  (default is 32)
\n";
      exit;
    }elsif(($arg_flag =~ m/^--user$/) || ($arg_flag =~ m/^-u$/)){
      $user = $ARGV[$i+1];
    }elsif(($arg_flag =~ m/^--account$/) || ($arg_flag =~ m/^-a$/)){
      $account = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--system$/) || ($arg_flag =~ m/^-s$/)){
      $system = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--runlength$/) || ($arg_flag =~ m/^-r$/)){
      $runlength = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--detail$/) || ($arg_flag =~ m/^-d$/)){
      $detail = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--medminratio$/) || ($arg_flag =~ m/^-m$/)){
      $ratio_med_min = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--avgmedratio$/) || ($arg_flag =~ m/^-p$/)){
      $ratio_avg_med = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--highcostdef$/) || ($arg_flag =~ m/^-c$/)){
      $highcost_def = $ARGV[$i+1];
    }elsif (($arg_flag =~ m/^--highcostnum$/) || ($arg_flag =~ m/^-n$/)){
      $highcost_num = $ARGV[$i+1];
    }
  }

  $curtime = time;
  ($cursec,$curmin,$curhour,$curmday,$curmon,$curyear,$curwday,$curyday,$curisdst) = localtime($curtime);
  $curyear += 1900;

  $performance_archive = cwd();

  opendir USERS, $performance_archive;
  @users = grep { -d $_ && -r _ && /^(?!\.).*$/ } readdir USERS;

  $period{'start'} = -1;
  $period{'end'} = -1;
  USERLOOP: for ( @users ){
    $thisuser = $_;
    if ($detail > 1){
      if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
        print "USER: $thisuser\n";
      }
    }

    chdir "$performance_archive/$thisuser";
    $thisuser_directory = cwd();

    opendir CASES, $thisuser_directory;
    @cases = grep { -d $_ && -r _ && /^(?!\.).*$/ } readdir CASES;

    for ( @cases ){
      $thiscase = $_;

      if ($detail > 1){
        if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
          print "  CASE: $thiscase\n";
        }
      }

      chdir "$thisuser_directory/$thiscase";
      $thiscase_directory = cwd();

      opendir LIDS, $thiscase_directory;
      @lids = grep { -d $_ && -r _ && /^(?!\.).*$/ } readdir LIDS;

      LIDSLOOP: for ( @lids ){
        $lid = $_;

        chdir "$thiscase_directory/$lid";
        $lid_directory = cwd();

        # Get system name from env_batch.xml file.
        $thissystem = "unknown";
        $envbatchf = "$lid_directory/CaseDocs.$lid/env_batch.xml.$lid.gz";

        $envbatchf_readable = "false";
        if (-f $envbatchf && -r _ ){
          open(ENVBATCH, "gunzip -c $envbatchf |") || die "can't open pipe to $envbatchf";
          $envbatchf_readable = "true";
        }else{
          $envbatchf = "$lid_directory/CaseDocs.$lid/env_batch.xml.$lid";
          if (-f $envbatchf && -r _ ){
            open(ENVBATCH, "$envbatchf");
            $envbatchf_readable = "true";
          }else{
            $envbatchf = "$lid_directory/CaseDocs.$lid/env_batch.xml";
            if (-f $envbatchf && -r _ ){
              open(ENVBATCH, "$envbatchf");
              $envbatchf_readable = "true";
            }
          }
        }

        if ($envbatchf_readable =~ m/true/){
          while (<ENVBATCH>){
            if (m/.*MACH=\"(\S+)\"/){
              $thissystem = $1;
              $systems{$thissystem} = 1;
            }
          }
          close ENVBATCH;

        }

        # If available, get requested runlength, frequency of checkpointing,
        # and location of inputdata from env_run.xml file
        $thisrun_length_target = 0;
        $thisstop_option = "unknown";
        $thisstop_n = 0;
        $thisdin_loc_root = "unknown";
        $thissyslog_n = -3600;
        $env_runf = "$lid_directory/CaseDocs.$lid/env_run.xml.$lid.gz";

        $env_runf_readable = "false";
        if (-f $env_runf && -r _ ){
          open(ENVRUNF, "gunzip -c $env_runf |") || die "can't open pipe to $env_runf";
          $env_runf_readable = "true";
        }else{
          $env_runf = "$lid_directory/CaseDocs.$lid/env_run.xml.$lid";
          if (-f $env_runf && -r _ ){
            open(ENVRUNF, "$env_runf");
            $env_runf_readable = "true";
          }else{
            $env_runf = "$lid_directory/CaseDocs.$lid/env_run.xml";
            if (-f $env_runf && -r _ ){
              open(ENVRUNF, "$env_runf");
              $env_runf_readable = "true";
            }
          }
        }

        if ($env_runf_readable =~ m/true/){

          ENVRUNFLOOP: while (<ENVRUNF>){
            if (m/^\s*<entry id=\"STOP_OPTION\"\s+value=\"(\S+)\">\s*/){
              $thisstop_option = $1;
            }
            elsif (m/^\s*<entry id=\"STOP_N\"\s+value=\"(\S+)\">\s*/){
              $thisstop_n = $1;
            }
            elsif (m/^\s*<entry id=\"SYSLOG_N\"\s+value=\"(\d+)\">\s*/){
              $thissyslog_n = $1;
            }
            elsif (m/^\s*<entry id=\"DIN_LOC_ROOT\"\s+value=\"(\S+)\">\s*/){
              $thisdin_loc_root = $1;
              last ENVRUNFLOOP;
            }
          }
          close ENVRUNF;

        }

        if ($thisstop_option =~ /^nday/){
          $thisrun_length_target = $thisstop_n;
        }
        elsif ($thisstop_option =~ /^nmonth/){
          $thisrun_length_target = 31*$thisstop_n;
        }
        elsif ($thisstop_option =~ /^nyear/){
          $thisrun_length_target = 366*$thisstop_n;
        }

        # Get case information from job_statsf file
        if ($system =~ m/anvil|compy/){
          $job_statsf_string = "squeueall_jobid";
        }elsif ($thissystem =~ m/theta|titan/){
          $job_statsf_string = "qstatf_jobid";
        }elsif ($thissystem =~ m/cori-haswell|cori-knl|edison/){
          $job_statsf_string = "sqsf_jobid";
        }elsif ($thissystem =~ m/summit/){
          $job_statsf_string = "bjobslUF_jobid";
	}else{
          $job_statsf_string = "squeueall_jobid";
        }
        $job_statsf = "$lid_directory/$job_statsf_string.$lid.gz";
        $job_statsf_readable = "false";
        if (-f $job_statsf && -r _ ){
          open(JOBSTATSF, "gunzip -c $job_statsf |") || die "can't open pipe to $job_statsf";
          $job_statsf_readable = "true";
        }else{
          $job_statsf = "$lid_directory/$job_statsf_string.$lid";
          if (-f $job_statsf && -r _ ){
            open(JOBSTATSF, "$job_statsf");
            $job_statsf_readable = "true";
          }
        }

        if ($job_statsf_readable =~ m/true/){

          # bjobs ouput does not include year in its timestamps. If the CaseStatus file
          # is available, get year for submit and start from there, but only these for
          # now. CaseStatus is read again later, for all job_statsf_strings, and other 
          # data is extracted then.
          if ($job_statsf_string =~ m/bjobslUF_jobid/){

            $bjobs_submit_jobid = -1;
            $bjobs_submit_time = -1;
            $found_bjobs_submit = "false";
            $bjobs_start_time  = -1;
            $found_bjobs_start = "false";
            $CaseStatusf = "$lid_directory/CaseStatus.$lid.gz";
            if (-f $CaseStatusf){
              open(CASESTATUSF, "gunzip -c $CaseStatusf |") || die "can't open pipe to $CaseStatusf";
              while (<CASESTATUSF>){
                if (m/^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+):\s+case.submit success case.run:\s*(\d+)\s*$/){
                  $bjobs_submit_year = $1;
                  $bjobs_submit_month = $2;
                  $bjobs_submit_day = $3;
                  $bjobs_submit_hour = $4;
                  $bjobs_submit_minute = $5;
                  $bjobs_submit_second = $6;
                  $bjobs_submit_jobid = $7;
                  $found_bjobs_submit = "true";
                }elsif (m/^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+):\s+case.run starting/){
                  $bjobs_start_year = $1;
                  $bjobs_start_month = $2;
                  $bjobs_start_day = $3;
                  $bjobs_start_hour = $4;
                  $bjobs_start_minute = $5;
                  $bjobs_start_second = $6;
                  $found_bjobs_start = "true";
                }
              }

              close CASESTATUSF;

              if ($found_bjobs_submit =~ m/true/){
                $bjobs_submit_time = timelocal($bjobs_submit_second,$bjobs_submit_minute,
                                         $bjobs_submit_hour,$bjobs_submit_day,
                                         $bjobs_submit_month-1,$bjobs_submit_year);
              }else{
                $bjobs_submit_time = -1;
              }

              if (($bjobs_submit_time >= 0) && ($found_bjobs_start =~ m/true/)){
                $bjobs_start_time  = timelocal($bjobs_start_second,$bjobs_start_minute,
                                             $bjobs_start_hour,$bjobs_start_day,
                                             $bjobs_start_month-1,$bjobs_start_year);
              }else{
                $bjobs_start_time  = -1;
              }

              if ($bjobs_start_time < $bjobs_submit_time){
                $bjobs_start_time  = -1;
              }

            }

          }

          $thisjobid = -2;
          JOBFLOOP: while (<JOBSTATSF>){
            if ($job_statsf_string =~ m/sqsf_jobid/){
              if (m/^JobId=(\d+)\s*JobName=(\S*)\s*$/){
                $thisjobid = $1;
              }elsif (m/^\s*Priority=(\d+)\s+Nice=(\S+)\s+Account=(\S+)\s+QOS=(\S+)/){
                $thisaccount = $3;
                $thisqueue = $4;
              }elsif (m/^\s*RunTime=(\d+):(\d+):(\d+)\s+TimeLimit=(\S+)\s+TimeMin=/){
                $thisjob_limit{'string'} = $4;
                if ($thisjob_limit{'string'} =~ m/^\s*(\d+):(\d+):(\d+)\s*$/){
                  $thisjob_limit{'days'} = 0;
                  $thisjob_limit{'hours'} = $1;
                  $thisjob_limit{'minutes'} = $2;
                  $thisjob_limit{'seconds'} = $3;
                }elsif($thisjob_limit{'string'} =~ m/^\s*(\d+)-(\d+):(\d+):(\d+)\s*$/){
                  $thisjob_limit{'days'} = $1;
                  $thisjob_limit{'hours'} = $2;
                  $thisjob_limit{'minutes'} = $3;
                  $thisjob_limit{'seconds'} = $4;
	        }
                $thisjob_limit{'time'} = 60*(60*(24*$thisjob_limit{'days'} + $thisjob_limit{'hours'}) + $thisjob_limit{'minutes'})+ $thisjob_limit{'seconds'};
              }elsif (m/^\s*SubmitTime=(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\s+/){
                $thisjob_submit{'year'} = $1;
                $thisjob_submit{'month'} = $2;
                $thisjob_submit{'day'} = $3;
                $thisjob_submit{'hour'} = $4;
                $thisjob_submit{'minute'} = $5;
                $thisjob_submit{'second'} = $6;
                $thisjob_submit{'string'} = "$1\-$2\-$3 $4\:$5\:$6";
                $thisjob_submit{'time'} = timelocal($thisjob_submit{'second'},$thisjob_submit{'minute'},
                                                    $thisjob_submit{'hour'},$thisjob_submit{'day'},
                                                    $thisjob_submit{'month'}-1,$thisjob_submit{'year'});
              }elsif (m/^\s*StartTime=(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\s+/){
                $thisjob_start{'year'} = $1;
                $thisjob_start{'month'} = $2;
                $thisjob_start{'day'} = $3;
                $thisjob_start{'hour'} = $4;
                $thisjob_start{'minute'} = $5;
                $thisjob_start{'second'} = $6;
                $thisjob_start{'string'} = "$1\-$2\-$3 $4\:$5\:$6";
                $thisjob_start{'time'} = timelocal($thisjob_start{'second'},$thisjob_start{'minute'},
                                                   $thisjob_start{'hour'},$thisjob_start{'day'},
                                                   $thisjob_start{'month'}-1,$thisjob_start{'year'});
              }elsif (m/^\s*NumNodes=(\S+)/){
                $thisnumnodes = $1;
              }elsif (m/^\s*Features=(\S+)\s+/){
                $thisfeatures = $1;
                if    ($thisfeatures =~ m/ivybridge/){
                  $thissystem = "edison";
                  $systems{$thissystem} = 1;
                }
                elsif ($thisfeatures =~ m/haswell/){
                  $thissystem = "cori-haswell";
                  $systems{$thissystem} = 1;
                }
                elsif ($thisfeatures =~ m/knl/){
                  $thissystem = "cori-knl";
                  $systems{$thissystem} = 1;
                }
                last JOBFLOOP;
              }
            }elsif ($job_statsf_string =~ m/squeueall_jobid/){
              @squeueall_field = split(/\|/,$_);
              $thisaccount = $squeueall_field[0];
              if ($thisaccount =~ m/ACCOUNT/){
                next JOBFLOOP;
              }
              $thisjobid = $squeueall_field[8];
              $thisjob_limit{'string'} = $squeueall_field[11];
              if ($thisjob_limit{'string'} =~ m/^\s*(\d+):(\d+)\s*$/){
                $thisjob_limit{'days'} = 0;
                $thisjob_limit{'hours'} = 0;
                $thisjob_limit{'minutes'} = $1;
                $thisjob_limit{'seconds'} = $2;
              }elsif ($thisjob_limit{'string'} =~ m/^\s*(\d+):(\d+):(\d+)\s*$/){
                $thisjob_limit{'days'} = 0;
                $thisjob_limit{'hours'} = $1;
                $thisjob_limit{'minutes'} = $2;
                $thisjob_limit{'seconds'} = $3;
              }elsif($thisjob_limit{'string'} =~ m/^\s*(\d+)-(\d+):(\d+):(\d+)\s*$/){
                $thisjob_limit{'days'} = $1;
                $thisjob_limit{'hours'} = $2;
                $thisjob_limit{'minutes'} = $3;
                $thisjob_limit{'seconds'} = $4;
              }else{
                $thisjob_limit{'days'} = 0;
                $thisjob_limit{'hours'} = 0;
                $thisjob_limit{'minutes'} = 0;
                $thisjob_limit{'seconds'} = -1;
              }
              $thisjob_limit{'time'} = 60*(60*(24*$thisjob_limit{'days'} + $thisjob_limit{'hours'}) + $thisjob_limit{'minutes'})+ $thisjob_limit{'seconds'};
              $thisqueue = $squeueall_field[16];
              $thisnumnodes = $squeueall_field[29];
              $thisjob_start{'string'} = $squeueall_field[44];
              if ($thisjob_start{'string'} =~ m/^\s*(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\s*/){
                $thisjob_start{'year'} = $1;
                $thisjob_start{'month'} = $2;
                $thisjob_start{'day'} = $3;
                $thisjob_start{'hour'} = $4;
                $thisjob_start{'minute'} = $5;
                $thisjob_start{'second'} = $6;
                $thisjob_start{'string'} = "$1\-$2\-$3 $4\:$5\:$6";
                $thisjob_start{'time'} = timelocal($thisjob_start{'second'},$thisjob_start{'minute'},
                                                   $thisjob_start{'hour'},$thisjob_start{'day'},
                                                   $thisjob_start{'month'}-1,$thisjob_start{'year'});
              }
              $thisjob_submit{'string'} = $squeueall_field[47];
              if ($thisjob_submit{'string'}=~ m/^\s*(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)\s*/){
                $thisjob_submit{'year'} = $1;
                $thisjob_submit{'month'} = $2;
                $thisjob_submit{'day'} = $3;
                $thisjob_submit{'hour'} = $4;
                $thisjob_submit{'minute'} = $5;
                $thisjob_submit{'second'} = $6;
                $thisjob_submit{'string'} = "$1\-$2\-$3 $4\:$5\:$6";
                $thisjob_submit{'time'} = timelocal($thisjob_submit{'second'},$thisjob_submit{'minute'},
                                                    $thisjob_submit{'hour'},$thisjob_submit{'day'},
                                                    $thisjob_submit{'month'}-1,$thisjob_submit{'year'});
              }
            }elsif ($job_statsf_string =~ m/qstatf_jobid/){
              if     ((m/^Job Id:\s*(\d+)\S*\s*$/) || 
                      (m/^JobID:\s*(\d+)\S*\s*$/)){
                $thisjobid = $1;
              }elsif ((m/^\s*queue =\s*(\S+)\s*/) || 
                      (m/^\s*Queue\s*:\s*(\S+)\s*/)){
                $thisqueue = $1;
              }elsif ((m/^\s*Account_Name =\s*(\S+)\s*/) || 
                      (m/^\s*Project\s*:\s*(\S+)\s*/)){
                $thisaccount = $1;
              }elsif ((m/^\s*ctime =\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)\s*/) ||
                      (m/^\s*SubmitTime\s*:\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)\s*/)){
                $thisjob_submit{'dayname'} = $1;
                $thisjob_submit{'month'} = $month_to_number{ lc substr($2, 0, 3) };
                $thisjob_submit{'day'} = $3;
                $thisjob_submit{'hour'} = $4;
                $thisjob_submit{'minute'} = $5;
                $thisjob_submit{'second'} = $6;
                $thisjob_submit{'year'} = $7;
                $thisjob_submit{'string'} = "$7\-$thisjob_submit{'month'}\-$3 $4\:$5\:$6";
                $thisjob_submit{'time'} = timelocal($thisjob_submit{'second'},$thisjob_submit{'minute'},
                                                    $thisjob_submit{'hour'},$thisjob_submit{'day'},
                                                    $thisjob_submit{'month'}-1,$thisjob_submit{'year'});
              }elsif ((m/^\s*Resource_List.nodes = (\d+):ppn=(\d+)\s*/)||
                      (m/^\s*Nodes\s*:\s*(\d+)\s*/)){
                $thisnumnodes = $1;
              }elsif ((m/^\s*Resource_List.walltime = (\S+)\s*/) ||
                      (m/^\s*WallTime\s*:\s*(\S+)\s*/)){
                $thisjob_limit{'string'} = $1;
                if ($thisjob_limit{'string'} =~ m/^\s*(\d+):(\d+):(\d+)$/){
                  $thisjob_limit{'hours'} = $1;
                  $thisjob_limit{'minutes'} = $2;
                  $thisjob_limit{'seconds'} = $3;
                }else{
                  $thisjob_limit{'hours'} = 0;
                  $thisjob_limit{'minutes'} = 0;
                  $thisjob_limit{'seconds'} = 0;
                }
                $thisjob_limit{'time'} = 60*(60*($thisjob_limit{'hours'}) + $thisjob_limit{'minutes'})+ $thisjob_limit{'seconds'};
              }elsif ((m/^\s*start_time =\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)\s*/) ||
                      (m/^\s*StartTime\s*:\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)\s*/)){
                $thisjob_start{'dayname'} = $1;
                $thisjob_start{'month'} = $month_to_number{ lc substr($2, 0, 3) };
                $thisjob_start{'day'} = $3;
                $thisjob_start{'hour'} = $4;
                $thisjob_start{'minute'} = $5;
                $thisjob_start{'second'} = $6;
                $thisjob_start{'year'} = $7;
                $thisjob_start{'string'} = "$7\-$thisjob_start{'month'}\-$3 $4\:$5\:$6";
                $thisjob_start{'time'} = timelocal($thisjob_start{'second'},$thisjob_start{'minute'},
                                                   $thisjob_start{'hour'},$thisjob_start{'day'},
                                                   $thisjob_start{'month'}-1,$thisjob_start{'year'});
              }
            }elsif ($job_statsf_string =~ m/bjobslUF_jobid/){
              if     (m/^Job\s*<(\S+)?>,.*?Project\s*<(\S+)?>,.*?Queue\s*<(\S+)?>,.*?nnodes\s*(\d+)\s+.*$/){
                $thisjobid = $1;
                $thisaccount = $2;
                $thisqueue = $3;
                $thisnumnodes = $4;
              }elsif (m/^\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+):\s+Submitted.*$/){
                $thisjob_submit{'dayname'} = $1;
                $thisjob_submit{'month'} = $month_to_number{ lc substr($2, 0, 3) };
                $thisjob_submit{'day'} = $3;
                $thisjob_submit{'hour'} = $4;
                $thisjob_submit{'minute'} = $5;
                $thisjob_submit{'second'} = $6;
                # As bjobs timestamps do not include the year, use year from CaseStatus if available.
                # Otherwise, use the current year if month is the same or earlier than the current 
                # month, and the year before if it is a later month. Note that $curmon is 0..11
                # while $thisjob_start{'month'} is 1..12 .
                if (($bjobs_submit_jobid == $thisjobid) && ($bjobs_submit_time >= 0)){
                  $thisjob_submit{'year'} = $bjobs_submit_year;
                }else{
                  if ($thisjob_submit{'month'} <= $curmon+1){
                    $thisjob_submit{'year'} = $curyear;
                  }else{
                    $thisjob_submit{'year'} = $curyear-1;
                  }
                }
                $thisjob_submit{'string'} = "$thisjob_submit{'year'}\-$thisjob_submit{'month'}\-$3 $4\:$5\:$6";
                $thisjob_submit{'time'} = timelocal($thisjob_submit{'second'},$thisjob_submit{'minute'},
                                                    $thisjob_submit{'hour'},$thisjob_submit{'day'},
                                                    $thisjob_submit{'month'}-1,$thisjob_submit{'year'});
              }elsif (m/^\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+):\s+Started.*$/){
                $thisjob_start{'dayname'} = $1;
                $thisjob_start{'month'} = $month_to_number{ lc substr($2, 0, 3) };
                $thisjob_start{'day'} = $3;
                $thisjob_start{'hour'} = $4;
                $thisjob_start{'minute'} = $5;
                $thisjob_start{'second'} = $6;
                # As bjobs timestamps do not include the year, use year from CaseStatus if available.
                # Otherwise, use the current year if month is the same or earlier than the current 
                # month, and the year before if it is a later month. Note that $curmon is 0..11
                # while $thisjob_start{'month'} is 1..12 .
                if (($bjobs_submit_jobid == $thisjobid) && ($bjobs_start_time >= 0)){
                  $thisjob_start{'year'} = $bjobs_start_year;
                }else{
                  if ($thisjob_start{'month'} <= $curmon+1){
                    $thisjob_start{'year'} = $curyear;
                  }else{
                    $thisjob_start{'year'} = $curyear-1;
                  }
                }
                $thisjob_start{'string'} = "$thisjob_start{'year'}\-$thisjob_start{'month'}\-$3 $4\:$5\:$6";
                $thisjob_start{'time'} = timelocal($thisjob_start{'second'},$thisjob_start{'minute'},
                                                    $thisjob_start{'hour'},$thisjob_start{'day'},
                                                    $thisjob_start{'month'}-1,$thisjob_start{'year'});
              }elsif (m/^\s*(\S+)\s+min\s*$/){
                $thisjob_limit{'seconds'} = 0;
                $thisjob_limit{'minutes'} = $1;
                $thisjob_limit{'hours'} = 0;
                $thisjob_limit{'time'} = 60*(60*($thisjob_limit{'hours'}) + $thisjob_limit{'minutes'})+ $thisjob_limit{'seconds'};
	      }
	    }
          }

          close JOBSTATSF;

          if (not ($thissystem =~ m/anvil|compy|cori-haswell|cori-knl|edison|summit|theta|titan/)){
            if (not ($thissystem =~ /unknown/)){
              delete $systems{$thissystem};
            }
            if ($detail > 1){
              if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
                print "\n";
                if ($thissystem =~ /unknown/){
                  print "    LID $lid: System name is not available.\n";
                }else{
                  print "    LID $lid: summarizing job data for system $thissystem is not supported.\n";
                }
                print "    Skipping processing data for this job.\n";
              }
            }
            next LIDSLOOP;
          }

          if ($period{'start'} < 0){
            $period{'start'} = $thisjob_start{'time'};
            $period{'startstring'} = $thisjob_start{'string'};
          }elsif ($period{'start'} > $thisjob_start{'time'}){
            $period{'start'} = $thisjob_start{'time'};
            $period{'startstring'} = $thisjob_start{'string'};
          }

          $thisjob_waittime = $thisjob_start{'time'} - $thisjob_submit{'time'};
          @thisjob_waittime = gmtime($thisjob_waittime);

          # If available, get compset and resolution aliases from README.case file
          $thiscompset_alias = "unknown";
          $thisres_alias = "unknown";
          $READMEcasef = "$lid_directory/CaseDocs.$lid/README.case.$lid.gz";

          $READMEcasef_readable = "false";
          if (-f $READMEcasef && -r _ ){
            open(READMECASEF, "gunzip -c $READMEcasef |") || die "can't open pipe to $READMEcasef";
            $READMEcasef_readable = "true";
          }else{
            $READMEcasef = "$lid_directory/CaseDocs.$lid/README.case.$lid";
            if (-f $READMEcasef && -r _ ){
              open(READMECASEF, "$READMEcasef");
              $READMEcasef_readable = "true";
            }else{
              $READMEcasef = "$lid_directory/CaseDocs.$lid/README.case";
              if (-f $READMEcasef && -r _ ){
                open(READMECASEF, "$READMEcasef");
                $READMEcasef_readable = "true";
              }
            }
          }

          if ($READMEcasef_readable =~ m/true/){

            READMECASEFLOOP: while (<READMECASEF>){
              if (m/.*\-compset\s+(\S+)\s+/){
                $thiscompset_alias = $1;
              }
              if (m/.*\-res\s+(\S+)\s+/){
                $thisres_alias = $1;
                last READMECASEFLOOP;
              }
            }
            close READMECASEF;

          }

          # If available, get git version number for E3SM from GIT_DESCRIBE file
          $thisgit_describe = "unknown";
          $GIT_DESCRIBEf = "$lid_directory/GIT_DESCRIBE.$lid.gz";

          $GIT_DESCRIBEf_readable = "false";
          if (-f $GIT_DESCRIBEf && -r _ ){
            open(GITDESCRIBEF, "gunzip -c $GIT_DESCRIBEf |") || die "can't open pipe to $GIT_DESCRIBEf";
            $GIT_DESCRIBEf_readable = "true";
          }else{
            $GIT_DESCRIBEf = "$lid_directory/GIT_DESCRIBE.$lid";
            if (-f $GIT_DESCRIBEf && -r _ ){
              open(GITDESCRIBEF, "$GIT_DESCRIBEf");
              $GIT_DESCRIBEf_readable = "true";
            }else{
              $GIT_DESCRIBEf = "$lid_directory/GIT_DESCRIBE";
              if (-f $GIT_DESCRIBEf && -r _ ){
                open(GITDESCRIBEF, "$GIT_DESCRIBEf");
                $GIT_DESCRIBEf_readable = "true";
              }
            }
          }

          if ($GIT_DESCRIBEf_readable =~ m/true/){

            GITDESCRIBEFLOOP: while (<GITDESCRIBEF>){
              if (m/^\s*(\S+)\s*/){
                $thisgit_describe = $1;
                last GITDESCRIBEFLOOP;
              }
            }
            close GITDESCRIBEF;

          }

          $seconds_until_finished = ($thisjob_start{'time'} + $thisjob_limit{'time'}) - $curtime;
##        print "seconds until finished: $seconds_until_finished\n";

          # If available, get time per simulation day statistics, lower bound on number of computed
          # simulation days (in case information not available from acme/e3sm timing file), and first
          # estimate for period{'end'}.
          undef(@thesedt);
          undef(@sorted_thesedt);
          undef(@thishighcost_gap);
          $thisjob_time = 0;
          $daycount = 0;
          $thiswalltime = 0;
          $thisstring = "0\-0\-0 0\:0\:0";
          $thisratio_medmin = -1;
          $thisratio_avgmed = -1;
          $thisratio_maxmin = -1;
          $thisdt_maxreg = -1;
          $thishighcost_num = 0;
          $thisgap_maxcnt = 0;
          $cpllogf = "$lid_directory/cpl.log.$lid.gz";

          $cpllogf_readable = "false";
          if (-f $cpllogf && -r _ ){
            open(CPLLOGF, "gunzip -c $cpllogf |") || die "can't open pipe to $cpllogf";
            $cpllogf_readable = "true";
          }else{
            $cpllogf = "$lid_directory/cpl.log.$lid";
            if (-f $cpllogf && -r _ ){
              open(CPLLOGF, "$cpllogf");
              $cpllogf_readable = "true";
            }
          }

          if ($cpllogf_readable =~ m/false/){

            $cpllogf = "$lid_directory/checkpoints.$lid/cpl.log.$lid.step-all.gz";

            $cpllogf_readable = "false";
            if (-f $cpllogf && -r _ ){
              open(CPLLOGF, "gunzip -c $cpllogf |") || die "can't open pipe to $cpllogf";
              $cpllogf_readable = "true";
            }else{
              $cpllogf = "$lid_directory/checkpoints.$lid/cpl.log.$lid.step-all";
              if (-f $cpllogf && -r _ ){
                open(CPLLOGF, "$cpllogf");
                $cpllogf_readable = "true";
              }
            }
          }

          if ($cpllogf_readable =~ m/true/){

            CPLLOGFLOOP: while (<CPLLOGF>){
              if (m/^\s*tStamp_write: model date = \s*(\S+)\s*\d\s*wall clock = (\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+) avg dt =\s*(\S+) dt =\s*(\S+)\s*/){
                $thissimdate    = $1;
                $thiswallyear   = $2;
                $thiswallmonth  = $3;
                $thiswallday    = $4;
                $thiswallhour   = $5;
                $thiswallminute = $6;
                $thiswallsecond = $7;
                $thisdt_avg      = $8;
                $thisdt         = $9;
                $thisstring     = "$2\-$3\-$4 $5\:$6\:$7";
                $thiswalltime   = timelocal($thiswallsecond,$thiswallminute,
                                            $thiswallhour,$thiswallday,
                                            $thiswallmonth-1,$thiswallyear);
                if ($daycount == 0){
                  $firstsimdate    = $thissimdate;
                }
                $thesedt[$daycount] = $thisdt;
                $daycount++;
              }
            }
            close CPLLOGF;

            if ($thiswalltime > $thisjob_start{'time'}){
              $thisjob_time = $thiswalltime - $thisjob_start{'time'};
            }

            if ($period{'end'} < 0){
              $period{'end'} = $thiswalltime;
              $period{'endstring'} = $thisstring;
            }elsif ($period{'end'} < $thiswalltime){
              $period{'end'} = $thiswalltime;
              $period{'endstring'} = $thisstring;
            }

            if (@thesedt){
              @sorted_thesedt = sort {$a <=> $b} @thesedt;
              $thisdt_min = $sorted_thesedt[0];
              $thisdt_med = $sorted_thesedt[int($#thesedt/2)];
              $thisdt_max = $sorted_thesedt[-1];
              if ($thisdt_min > 0){
                $thisratio_medmin = $thisdt_med/$thisdt_min;
                $thisratio_avgmed = $thisdt_avg/$thisdt_med;
                $thisratio_maxmin = $thisdt_max/$thisdt_min;

                # count number of high cost simulation days
                $thisdt_maxreg = $#sorted_thesedt;
                while ($sorted_thesedt[$thisdt_maxreg] >= $highcost_def*$thisdt_min){
                  $thisdt_maxreg--;
                }
                $thisdt_maxreg++;
                $thishighcost_num = $daycount - $thisdt_maxreg;

                if ($thishighcost_num > 0){

                  # calculate distances (gaps) between high cost simulation days
                  $thishighcost_curr = -1;
                  $thishighcost_next = 0;
                  $thishighcost_gaps = 0;
                  while ($thishighcost_next < $#thesedt){
                    while (($thesedt[$thishighcost_next] < $highcost_def*$thisdt_min) &&
                           ($thishighcost_next < $#thesedt)){
                      $thishighcost_next++;
                    }
                    if ($thesedt[$thishighcost_next] >= $highcost_def*$thisdt_min){
                      $thishighcost_gap[$thishighcost_gaps] = ($thishighcost_next - $thishighcost_curr);
                      $thishighcost_gaps++;
                      $thishighcost_curr = $thishighcost_next;
                      $thishighcost_next++;
                    }
                  }

                  # count number of high cost simulation days in each run of 31 days
                  # (kind of - count begins again from each high cost day - but will be 
                  #  what expect if every month ends with a high cost day)
                  $thisgap_curr = 0;
                  while ($thisgap_curr <= $#thishighcost_gap){
                    $thisgap_cnt = 0; 
                    $thisgap_next = $thisgap_curr;
                    $thisgap_size = $thishighcost_gap[$thisgap_next];
                    while (($thisgap_size <= 31) || ($thisgap_next == $thisgap_curr)){
                      $thisgap_cnt++;
                      $thisgap_next++;
                      last if ($thisgap_next > $#thishighcost_gap);
                      $thisgap_size += $thishighcost_gap[$thisgap_next];
                    }
                    if ($thisgap_cnt > $thisgap_maxcnt){
                      $thisgap_maxcnt = $thisgap_cnt;
                    }
                    $thisgap_curr++;
                  }

                }

              }

            }

          }

          # If available, get start/finish times and whether completed successfully from CaseStatus file
          $thiscompleted = "false";
          $thisperfsummary = "false";
          $found_caserun_start = "false";
          $found_caserun_success = "false";
          $CaseStatusf = "$lid_directory/CaseStatus.$lid.gz";
          if (-f $CaseStatusf){
            $thiscompleted = "true";
            open(CASESTATUSF, "gunzip -c $CaseStatusf |") || die "can't open pipe to $CaseStatusf";
            while (<CASESTATUSF>){
              if (m/^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+):\s+Run started/){
                $caserun_start{'year'} = $1;
                $caserun_start{'month'} = $2;
                $caserun_start{'day'} = $3;
                $caserun_start{'hour'} = $4;
                $caserun_start{'minute'} = $5;
                $caserun_start{'second'} = $6;
                $found_caserun_start = "true";
              }elsif (m/^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+):\s+Run SUCCESSFUL/){
                $caserun_success{'year'} = $1;
                $caserun_success{'month'} = $2;
                $caserun_success{'day'} = $3;
                $caserun_success{'hour'} = $4;
                $caserun_success{'minute'} = $5;
                $caserun_success{'second'} = $6;
                $found_caserun_success = "true";
              }elsif (m/^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+):\s+case.run starting/){
                $caserun_start{'year'} = $1;
                $caserun_start{'month'} = $2;
                $caserun_start{'day'} = $3;
                $caserun_start{'hour'} = $4;
                $caserun_start{'minute'} = $5;
                $caserun_start{'second'} = $6;
                $found_caserun_start = "true";
              }elsif (m/^\s*(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+):\s+case.run success/){
                $caserun_success{'year'} = $1;
                $caserun_success{'month'} = $2;
                $caserun_success{'day'} = $3;
                $caserun_success{'hour'} = $4;
                $caserun_success{'minute'} = $5;
                $caserun_success{'second'} = $6;
                $caserun_success{'string'} = "$1\-$2\-$3 $4\:$5\:$6";
                $found_caserun_success = "true";
              }
            }

            close CASESTATUSF;

            if ($found_caserun_start =~ m/true/){
              $caserun_start{'time'}      = timelocal($caserun_start{'second'},$caserun_start{'minute'},
                                                      $caserun_start{'hour'},$caserun_start{'day'},
                                                      $caserun_start{'month'}-1,$caserun_start{'year'});
            }else{
              $caserun_start{'time'} = -1;
            }

            if ($found_caserun_success =~ m/true/){
              $caserun_success{'time'}    = timelocal($caserun_success{'second'},$caserun_success{'minute'},
                                                      $caserun_success{'hour'},$caserun_success{'day'},
                                                      $caserun_success{'month'}-1,$caserun_success{'year'});
            }else{
              $caserun_success{'time'} = -1;
            }

            if (($found_caserun_start =~ m/false/) ||
                ($found_caserun_success =~ m/false/) ||
                ($caserun_success{'time'} < $caserun_start{'time'})){
              if ($detail > 1){
                if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
                  print "\n";
                  print "    LID $lid: Missing 'case.run success' or case.run success timestamp < case.run start timestamp.\n";
                  print "    Skipping processing data for this job.\n";
                }
              }
              next LIDSLOOP;
            }

            if ($period{'end'} < 0){
              $period{'end'} = $caserun_success{'time'};
              $period{'endstring'} = $caserun_success{'string'};
            }elsif ($period{'end'} < $caserun_success{'time'}){
              $period{'end'} = $caserun_success{'time'};
              $period{'endstring'} = $caserun_success{'string'};
            }

            # Have captured end time for this job. Determine whether should ignore further processing for this job.
            if ((not (($user =~ m/\*/) || ($user =~ m/$thisuser/))) ||
                (not (($account =~ m/\*/) || ($account =~ m/$thisaccount/i))) ||
                ($runlength > $thisrun_length_target) ||
                (not (($system =~ m/\*/) || ($system =~ m/$thissystem/)))){
              next LIDSLOOP;
            }

            $thisjob_inittime  = $caserun_start{'time'} - $thisjob_start{'time'};
            $thiscase_runtime  = $caserun_success{'time'} - $caserun_start{'time'};

            # If available, get performance data, simulation duration, and other (redundant) case information
            # from acme_timing or e3sm_timing file
            $acme_timingf = "$lid_directory/acme_timing.$thiscase.$lid.gz";
            $e3sm_timingf = "$lid_directory/e3sm_timing.$thiscase.$lid.gz";
            if ((-f $acme_timingf) || (-f $e3sm_timingf)) {
              $thisperfsummary = "true";
              if (-f $acme_timingf) {
                open(TIMINGF, "gunzip -c $acme_timingf |") || die "can't open pipe to $acme_timingf";
              }else{
                open(TIMINGF, "gunzip -c $e3sm_timingf |") || die "can't open pipe to $e3sm_timingf";
              }
              TIMINGFLOOP: while (<TIMINGF>){
                if (m/^\s*Case\s*:\s*(\S+)/){
                  $thiscasename = $1;
                }elsif (m/^\s*LID\s*:\s*(\S+)/){
                  $thislid = $1;
                }elsif (m/^\s*Curr Date\s*:\s*(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)\s*/){
                  $curr_date{'dayname'} = $1;
                  $curr_date{'month'} = $month_to_number{ lc substr($2, 0, 3) };
                  $curr_date{'day'} = $3;
                  $curr_date{'hour'} = $4;
                  $curr_date{'minute'} = $5;
                  $curr_date{'second'} = $6;
                  $curr_date{'year'} = $7;
                  $curr_date{'string'} = "$7\-$curr_date{'month'}\-$3 $4\:$5\:$6";
                  $curr_date{'time'} = timelocal($curr_date{'second'},$curr_date{'minute'},
                                                 $curr_date{'hour'},$curr_date{'day'},
                                                 $curr_date{'month'}-1,$curr_date{'year'});
                }elsif (m/^\s*grid\s*:\s*(\S+)/){
                  $thisgrid = $1;
                }elsif (m/^\s*compset\s*:\s*(\S+)/){
                  $thiscompset = $1;
                }elsif (m/^\s*run.length\s*:\s*(\S+)\s*(\S+)\s+\((\S+) for ocean\)/){
                  if ($1 >= $3){
                    $thisrun_length = $1;
                  }else{
                    $thisrun_length = $3;
                  }
                  $thisrun_length_unit = $2;
                }elsif (m/^\s*run.length\s*:\s*(\S+)\s*(\S+)/){
                  $thisrun_length = $1;
                  $thisrun_length_unit = $2;
                }elsif (m/^\s*Init Time\s*:\s*(\S+)\s*(\S+)/){
                  $thisinit_time = $1;
                  $thisinit_time_unit = $2;
                }elsif (m/^\s*Run Time\s*:\s*(\S+)\s*(\S+)/){
                  $thisrun_time = $1;
                  $thisrun_time_unit = $2;
                }elsif (m/^\s*Final Time\s*:\s*(\S+)\s*(\S+)/){
                  $thisfinal_time = $1;
                  $thisfinal_time_unit = $2;
                }elsif (m/^\s*TOT Run Time:\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)/){
                  $thistot_sypd = $5;
                  last TIMINGFLOOP;
                }
              }

              close TIMINGF;

              if ($thisrun_length_unit =~ /days/){
                if (exists $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                  $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} += $thisrun_length;
                }else{
                  $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = $thisrun_length;
                }
                if (exists $totalcompletedsimdays{$thissystem}){
                  $totalcompletedsimdays{$thissystem} += $thisrun_length;
                }else{
                  $totalcompletedsimdays{$thissystem} = $thisrun_length;
                }

              }else{
                if ($detail > 1){
                  if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
                    print "\n";
                    print "    LID $lid: Simulation run_length is in $thisrun_length_unit, not days.\n";
                    print "    Skipping processing data for this job.\n";
                  }
                }
                next LIDSLOOP;
              }

              $thisrun_total = $thisinit_time + $thisrun_time + $thisfinal_time;
              $thiscase_ovhdtime = $thiscase_runtime - $thisrun_total;
              $thisjob_runtime = $thiscase_runtime + $thisjob_inittime;
              $thisjob_time = $curr_date{'time'} - $thisjob_start{'time'};
              if (exists $totalcompletednodeseconds{$thissystem}){
                $totalcompletednodeseconds{$thissystem} += $thisjob_time*$thisnumnodes;
              }else{
                $totalcompletednodeseconds{$thissystem} = $thisjob_time*$thisnumnodes;
              }

              if (exists $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                if ($completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'} > $thistot_sypd){
                  $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'} = $thistot_sypd;
                  $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minlid'} = $lid;
                }
                if ($completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'} < $thistot_sypd){
                  $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'} = $thistot_sypd;
                  $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxlid'} = $lid;
                }
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sum'} += $thistot_sypd;
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'}++; 
              }else{
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'} = $thistot_sypd;
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minlid'} = $lid;
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'} = $thistot_sypd;
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxlid'} = $lid;
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sum'} = $thistot_sypd;
                $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'} = 1;
	      }

              if (exists $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}++;
              }else{
                $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = 1;
              }
              if (exists $totalcompletedjobswithperfsummary{$thissystem}){
                $totalcompletedjobswithperfsummary{$thissystem}++;
              }else{
                $totalcompletedjobswithperfsummary{$thissystem} = 1;
              }

            }else{
              # $thisperfsummary = "false" branch, i.e. no acme_timing or e3sm_timing file

              if (exists $completedjobsnoperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                $completedjobsnoperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}++;
              }else{
                $completedjobsnoperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = 1;
              }
              if (exists $totalcompletedjobsnoperfsummary{$thissystem}){
                $totalcompletedjobsnoperfsummary{$thissystem}++;
              }else{
                $totalcompletedjobsnoperfsummary{$thissystem} = 1;
              }

              # use lower bound on number of simulation days and job execution time calculated from earlier processing of cpl.log file 
              # (since performance summary is not available)
              if (exists $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} += $daycount;
              }else{
                $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = $daycount;
              }

              if (exists $totalcompletedsimdays{$thissystem}){
                $totalcompletedsimdays{$thissystem} += $daycount;
                $totalcompletednodeseconds{$thissystem} += $thisjob_time*$thisnumnodes;
              }else{
                $totalcompletedsimdays{$thissystem} = $daycount;
                $totalcompletednodeseconds{$thissystem} = $thisjob_time*$thisnumnodes;
              }

            }

          }else{
            # $thiscompleted = "false" branch (i.e. no CaseStatus file)

            # Have captured lower bound on end time for this job, if possible, from cpl.log file. 
            # Determine whether should ignore further processing for this job.
            if ((not (($user =~ m/\*/) || ($user =~ m/$thisuser/))) ||
                (not (($account =~ m/\*/) || ($account =~ m/$thisaccount/i))) ||
                ($runlength > $thisrun_length_target) ||
                (not (($system =~ m/\*/) || ($system =~ m/$thissystem/)))){
              next LIDSLOOP;
            }

            if (exists $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
              $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}++;
            }else{
              $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = 1;
            }
            if (exists $totalfailedjobs{$thissystem}){
              $totalfailedjobs{$thissystem}++;
            }else{
              $totalfailedjobs{$thissystem} = 1;
            }

            # Have captured lower bound on number of simulaiton days calculated for this job, if possible, from cpl.log file.
            if ($daycount > 0){

              if (exists $failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                $failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} += $daycount;
              }else{
                $failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = $daycount;
              }

              if (exists $totalfailedsimdays{$thissystem}){
                $totalfailedsimdays{$thissystem} += $daycount;
                $totalfailednodeseconds{$thissystem} += $thisjob_time*$thisnumnodes;
              }else{
                $totalfailedsimdays{$thissystem} = $daycount;
                $totalfailednodeseconds{$thissystem} = $thisjob_time*$thisnumnodes;
              }

              if (exists $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}++;
              }else{
                $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = 1;
              }

              if (exists $totalfailedjobswithsimdays{$thissystem}){
                $totalfailedjobswithsimdays{$thissystem}++;
              }else{
                $totalfailedjobswithsimdays{$thissystem} = 1;
              }

            }

            # look for time remaining in cpl.log.step file, to check whether it may have run out of time
            $thistime_remaining = $thissyslog_n + 1;
            $cpllogstepf = "$lid_directory/checkpoints.$lid/cpl.log.$lid.step.gz";

            $cpllogstepf_readable = "false";
            if (-f $cpllogstepf && -r _ ){
              open(CPLLOGSTEPF, "gunzip -c $cpllogstepf |") || die "can't open pipe to $cpllogstepf";
              $cpllogstepf_readable = "true";
            }else{
              $cpllogstepf = "$lid_directory/checkpoints.$lid/cpl.log.$lid.step";
              if (-f $cpllogstepf && -r _ ){
                open(CPLLOGSTEPF, "$cpllogstepf");
                $cpllogstepf_readable = "true";
              }
            }

            if ($cpllogstepf_readable =~ m/true/){

              CPLLOGSTEPFLOOP: while (<CPLLOGSTEPF>){
                if (m/^\s*Wallclock time remaining:\s*(\d+)\s*/){
                  $thistime_remaining = $1;
                }
              }
              close CPLLOGSTEPF;

            }

            if ($thistime_remaining < $thissyslog_n){

              if (exists $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}++;
              }else{
                $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} = 1;
              }
              if (exists $totaloutoftimejobs{$thissystem}){
                $totaloutoftimejobs{$thissystem}++;
              }else{
                $totaloutoftimejobs{$thissystem} = 1;
              }
            }

          }

          if ($detail > 2){
            print "\n";
            print "    Job $thisjobid ($lid) submitted at $thisjob_submit{'string'} on $thissystem:\n";
            print "    User: $thisuser; Account: $thisaccount; Queue: $thisqueue; Case: $thiscase\n";
            print "    Nodes: $thisnumnodes; Time Limit: $thisjob_limit{'time'} seconds\n";
            print "    Compset: $thiscompset_alias; Resolution: $thisres_alias; Source: $thisgit_describe\n";
##          print "    Compset: $thiscompset; Grid: $thisgrid\n";
            print "    Run Length: $thisstop_n $thisstop_option; DIN_LOC_ROOT: $thisdin_loc_root\n";
            print "    Queue Wait: $thisjob_waittime seconds (@thisjob_waittime[7] days @thisjob_waittime[2] hours @thisjob_waittime[1] minutes @thisjob_waittime[0] seconds)\n";
            if ($thiscompleted =~ m/true/){
              if ($thisperfsummary =~ m/true/){
                print "    Simulation: $thisrun_length $thisrun_length_unit\n";
                print "    Job  Total  : $thisjob_runtime seconds\n";
##              print "Case Total  : $thiscase_runtime seconds\n";
##              print "Run  Total  : $thisrun_total $thisrun_time_unit\n";
                print "     - Job Init   : $thisjob_inittime seconds\n";
                print "     - Case Ovhd  : $thiscase_ovhdtime seconds\n";
                print "     - Run Init   : $thisinit_time $thisinit_time_unit\n";
                print "     - Run Loop   : $thisrun_time $thisrun_time_unit ($thistot_sypd SYPD)\n";
                print "     - Run Final  : $thisfinal_time $thisfinal_time_unit\n";
              }else{
                print "    Job did not generate performance summary.\n";
              }
            }else{
              if ($seconds_until_finished < 0){
                if ($thistime_remaining < $thissyslog_n){
                  print "    Job did not complete successfully. It may have run out of time. (Walltime Remaining was $thistime_remaining seconds.)\n";
                }else{
                  print "    Job did not complete successfully.\n";
                }
              }else{
                print "    Job either either did not complete successfully or is still running ($seconds_until_finished seconds until finished).\n";
              }
            }
            if (($thiscompleted =~ m/false/) || ($thisperfsummary =~ m/false/)) {
              if ($daycount > 0){
                print "    Computed at least $daycount days ($firstsimdate through $thissimdate).\n";
              }else{
                print "    Computed at least 0 days.\n";
              }
            }
            if ($thisratio_medmin > -1){
              print "    DT Performance Variability:\n";
              print "      Median/Min = $thisratio_medmin, Average/Median = $thisratio_avgmed, Max/Min = $thisratio_maxmin\n";
              print "      ($thishighcost_num out of $daycount) >= $highcost_def*Min; Largest number of high cost days in 31: $thisgap_maxcnt \n";
	    }
            if (($thisratio_medmin > $ratio_med_min) || 
                ($thisratio_avgmed > $ratio_avg_med) ||
                ($thisgap_maxcnt >= $highcost_num)  ){
              print "      Performance Variability Thresholds (Med/Min: $ratio_med_min, Avg/Med: $ratio_avg_med, High Cost Days per 31 days: $highcost_num) Exceeded\n";
              print "      DT Array: @thesedt\n";
            }
          }else{
            if (($thisratio_medmin > $ratio_med_min) || 
                ($thisratio_avgmed > $ratio_avg_med) ||
                ($thisgap_maxcnt >= $highcost_num)  ){
              print "\n";
              print "    Performance Variability Thresholds (Med/Min: $ratio_med_min, Avg/Med: $ratio_avg_med, High Cost Days per 31 days: $highcost_num) Exceeded\n";
              print "      USER: $thisuser; CASE: $thiscase; LID $lid:\n";
              print "      DT Performance Variability:\n";
              print "        Median/Min = $thisratio_medmin, Average/Median = $thisratio_avgmed, Max/Min = $thisratio_maxmin\n";
              print "        ($thishighcost_num out of $daycount) >= $highcost_def*Min; Largest number of high cost days in 31: $thisgap_maxcnt \n";
              print "      DT Array: @thesedt\n";
            }
          }

        }else{

          if (not ($thissystem =~ m/anvil|compy|cori-haswell|cori-knl|edison|summit|theta|titan/)){
            if (not ($thissystem =~ /unknown/)){
              delete $systems{$thissystem};
            }
            if ($detail > 1){
              if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
                print "\n";
                if ($thissystem =~ /unknown/){
                  print "    LID $lid: System name is not available.\n";
                }else{
                  print "    LID $lid: Summarizing job data for system $thissystem is not supported.\n";
                }
                print "    Skipping processing data for this job.\n";
              }
            }
          }else{
            if ($detail > 1){
              if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
                print "\n";
                print "    LID $lid: Missing $job_statsf_string file.\n";
                print "    Skipping processing data for this job.\n";
              }
            }
          }

	}

      }

      close LIDS;

      if ($detail > 1){
        if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){

          if (exists $completedsimdays{$thisuser}{$thiscase}){

            foreach $thissystem (keys %{$completedsimdays{$thisuser}{$thiscase}}){
              if (($system =~ m/\*/) || ($system =~ m/$thissystem/)){
                foreach $thisaccount (keys %{$completedsimdays{$thisuser}{$thiscase}{$thissystem}}){
                  if (($account =~ m/\*/) || ($account =~ m/$thisaccount/i)){
                    foreach $thiscompset_alias (keys %{$completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}}){
                      foreach $thisres_alias (keys %{$completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}}){
                        foreach $thisnumnodes (keys %{$completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}}){
                          print "\n";
                          print "    SYSTEM: $thissystem; ACCOUNT: $thisaccount; COMPSET: $thiscompset_alias; RESOLUTION: $thisres_alias;\n";
                          print "    NUMNODES: $thisnumnodes; RUNLENGTH >= $runlength days\n";
                          if (exists $completedjobsnoperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                            if (exists $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                              print "      Jobs completed with performance summary: $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                            }
                            print "      Jobs completed without performance summary: $completedjobsnoperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                          }else{
                            if (exists $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                              print "      Jobs completed: $completedjobswithperfsummary{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                            }
                          }
                          print "        Days Simulated: $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                          $max_sypd = $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'};
                          $max_sypd_lid = $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxlid'};
                          $min_sypd = $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'};
                          $min_sypd_lid = $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minlid'};
                          $avg_sypd = $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sum'}/
                                      $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'};
                          print "        SYPD for TOTAL: $avg_sypd (average) $max_sypd (max: $max_sypd_lid) $min_sypd (min: $min_sypd_lid)\n";
                        }
                      }
                    }
                  }
                }
              }
            }

          }

          if (exists $failedsimdays{$thisuser}{$thiscase}){

            foreach $thissystem (keys %{$failedsimdays{$thisuser}{$thiscase}}){
              if (($system =~ m/\*/) || ($system =~ m/$thissystem/)){
                foreach $thisaccount (keys %{$failedsimdays{$thisuser}{$thiscase}{$thissystem}}){
                  if (($account =~ m/\*/) || ($account =~ m/$thisaccount/i)){
                    foreach $thiscompset_alias (keys %{$failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}}){
                      foreach $thisres_alias (keys %{$failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}}){
                        foreach $thisnumnodes (keys %{$failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}}){
                          print "\n";
                          print "    SYSTEM: $thissystem; ACCOUNT: $thisaccount; COMPSET: $thiscompset_alias; RESOLUTION: $thisres_alias;\n";
                          print "    NUMNODES: $thisnumnodes; RUNLENGTH >= $runlength days\n";
                          $thisfailed_jobs = $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes};
                          if (exists $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                            $thisoutoftime_jobs = $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes};
                            print "      Jobs failed: $thisfailed_jobs ($thisoutoftime_jobs may have run out of time)\n";
                          }else{
                            print "      Jobs failed: $thisfailed_jobs\n";
                          }
                          if (exists $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                            if (exists $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                              $failedjobsnosimdays = ($failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes} -
                                                      $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes});
                              print "        Jobs failed with no simulation days: $failedjobsnosimdays\n";
                              print "        Jobs failed with simulation days: $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                            }else{
                              print "        Jobs failed with no simulation days: $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                              print "        Jobs failed with simulation days: 0\n";
                            }
                          }
                          elsif (exists $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                            print "        Jobs failed with no simulation days: 0\n";
                            print "        Jobs failed with simulation days: $failedjobswithsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                          }
                          print "          Days Simulated: $failedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}\n";
                        }
                      }
                    }
                  }
                }
              }
            }

          }elsif (exists $failedjobs{$thisuser}{$thiscase}){

            foreach $thissystem (keys %{$failedjobs{$thisuser}{$thiscase}}){
              if (($system =~ m/\*/) || ($system =~ m/$thissystem/)){
                foreach $thisaccount (keys %{$failedjobs{$thisuser}{$thiscase}{$thissystem}}){
                  if (($account =~ m/\*/) || ($account =~ m/$thisaccount/i)){
                    foreach $thiscompset_alias (keys %{$failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}}){
                      foreach $thisres_alias (keys %{$failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}}){
                        foreach $thisnumnodes (keys %{$failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}}){
                          print "\n";
                          print "    SYSTEM: $thissystem; ACCOUNT: $thisaccount; COMPSET: $thiscompset_alias; RESOLUTION: $thisres_alias;\n";
                          print "    NUMNODES: $thisnumnodes; RUNLENGTH >= $runlength days\n";
                          $thisfailed_jobs = $failedjobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes};
                          if (exists $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){
                            $thisoutoftime_jobs = $outoftimejobs{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes};
                            print "      Jobs failed: $thisfailed_jobs ($thisoutoftime_jobs may have run out of time)\n";
                          }else{
                            print "      Jobs failed: $thisfailed_jobs\n";
                          }
                          print "        No reported days of simulation completed.\n";
                        }
                      }
                    }
                  }
                }
              }
            }

          }

          print "\n";

        }

      }

    }

    close CASES;

  }

  close USERS;

  if ($period{'start'} < 0){
    print "No job information found - exiting\n";
    exit;
  }

  print "\n";

  SYSTEMLOOP: foreach $thissystem (sort keys %systems){

    if (not (($system =~ m/\*/) || ($system =~ m/$thissystem/))){
      next SYSTEMLOOP;
    }

    if ($user =~ m/\*/){
      if ($account =~ m/\*/){
        if ($runlength <= 0){
          print "$thissystem, all users, all accounts, all run lengths\n";
        }else{
          print "$thissystem, all users, all accounts, run length >= $runlength days\n";
        }
      }else{
        if ($runlength <= 0){
          print "$thissystem, all users, $account, all run lengths\n";
        }else{
          print "$thissystem, all users, $account, run length >= $runlength days\n";
        }
      }
    }else{
      if ($account =~ m/\*/){
        if ($runlength <= 0){
          print "$thissystem, $user, all accounts, all run lengths\n";
        }else{
          print "$thissystem, $user, all accounts, run length >= $runlength days\n";
        }
      }else{
        if ($runlength <= 0){
          print "$thissystem, $user, $account, all run lengths\n";
        }else{
          print "$thissystem, $user, $account, run length >= $runlength days\n";
        }
      }
    }
    print "($period{'startstring'}) - ($period{'endstring'})\n";
    print "----------------------------------------------\n";

    $maxnodehours = (($period{'end'} - $period{'start'})*$maxnodes{$thissystem})/3600.0;
    if (exists $totalfailednodeseconds{$thissystem}){
      $totalnodehours = $totalfailednodeseconds{$thissystem}/3600.0;
    }else{
      $totalnodehours = 0;
    }
    $totalnodehourspercentage = ($totalnodehours/$maxnodehours)*100.0;

    # print "$totalfailedjobs jobs failed or still running\n";
    if (exists $totalfailedjobs{$thissystem}){
      if (not (exists $totalfailedsimdays{$thissystem})){
        $totalfailedsimdays{$thissystem} = 0;
      }
      if (exists $totaloutoftimejobs{$thissystem}){
        print "Jobs failed or still running: $totalfailedjobs{$thissystem} ($totaloutoftimejobs{$thissystem} may have run out of time)\n";
      }else{
        print "Jobs failed or still running: $totalfailedjobs{$thissystem}\n";
      }
      printf ("  Total node hours: >= %f (%6.2f%% of maximum possible)\n",$totalnodehours,$totalnodehourspercentage);
      if (exists $totalfailedjobswithsimdays{$thissystem}){
        if ($totalfailedjobswithsimdays{$thissystem} > 0){
          printf ("  Total days simulated: >= %d (%d jobs)\n",$totalfailedsimdays{$thissystem},$totalfailedjobswithsimdays{$thissystem});
        }else{
          print "  Total days simulated: >= 0\n";
        }
      }else{
        print "  Total days simulated: >= 0\n";
      }
    }else{
      print "Jobs failed: 0\n";
    }

    print "\n";

    if (exists $totalcompletednodeseconds{$thissystem}){
      $totalnodehours = $totalcompletednodeseconds{$thissystem}/3600.0;
    }else{
      $totalnodehours = 0;
    }
    $totalnodehourspercentage = ($totalnodehours/$maxnodehours)*100.0;

    if (not (exists $totalcompletedsimdays{$thissystem})){
      $totalcompletedsimdays{$thissystem} = 0;
    }

    if (exists $totalcompletedjobsnoperfsummary{$thissystem}){
      if ($totalcompletedjobsnoperfsummary{$thissystem} > 0){
        if (exists $totalcompletedjobswithperfsummary{$thissystem}){
          print "Jobs completed with performance summary: $totalcompletedjobswithperfsummary{$thissystem}; ";
        }else{
          print "Jobs completed with performance summary: 0; ";
        }
        print "Jobs completed without performance summary: $totalcompletedjobsnoperfsummary{$thissystem}\n";
        printf ("  Total node hours: %f (%6.2f%% of maximum possible)\n",$totalnodehours,$totalnodehourspercentage);
        printf ("  Total days simulated: >= %d\n",$totalcompletedsimdays{$thissystem});
      }
      else{
        if (exists $totalcompletedjobswithperfsummary{$thissystem}){
          print "Jobs completed: $totalcompletedjobswithperfsummary{$thissystem}\n";
        }else{
          print "Jobs completed: 0\n";
        }
        printf ("  Total node hours: %f (%6.2f%% of maximum possible)\n",$totalnodehours,$totalnodehourspercentage);
        printf ("  Total days simulated: %d\n",$totalcompletedsimdays{$thissystem});
      }
    }else{
      if (exists $totalcompletedjobswithperfsummary{$thissystem}){
        print "Jobs completed: $totalcompletedjobswithperfsummary{$thissystem}\n";
      }else{
        print "Jobs completed: 0\n";
      }
      printf ("  Total node hours: %f (%6.2f%% of maximum possible)\n",$totalnodehours,$totalnodehourspercentage);
      printf ("  Total days simulated: %d\n",$totalcompletedsimdays{$thissystem});
    }

    print "\n";

    if ($detail > 0){
      foreach $thisuser (keys %completedsypd){
        if (($user =~ m/\*/) || ($user =~ m/$thisuser/)){
          foreach $thiscase (keys %{$completedsypd{$thisuser}}){
            if (exists $completedsypd{$thisuser}{$thiscase}{$thissystem}){
              foreach $thisaccount (keys %{$completedsypd{$thisuser}{$thiscase}{$thissystem}}){
                if (($account =~ m/\*/) || ($account =~ m/$thisaccount/i)){
                  foreach $thiscompset_alias (keys %{$completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}}){
                    foreach $thisres_alias (keys %{$completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}}){
                      foreach $thisnumnodes (keys %{$completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}}){
                        if (exists $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}){

                          if ($summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypd'} >
                              $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'}){
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypd'} = 
                              $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'};
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypdlid'} = 
                              $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minlid'};
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypduser'} = $thisuser;
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypdcase'} = $thiscase;
                          }

                          if ($summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypd'} <
                              $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'}){
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypd'} =
                              $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'};
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypdlid'} =
                              $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxlid'};
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypduser'} = $thisuser;
                            $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypdcase'} = $thiscase;
                          }

                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sumsypd'} += 
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sum'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'} +=
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'}; 
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'simdays'} += 
                            $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes};

                        }else{

                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypd'} =
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'min'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypdlid'} =
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minlid'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypduser'} = $thisuser;
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypdcase'} = $thiscase;

                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypd'} = 
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'max'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypdlid'} =
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxlid'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypduser'} = $thisuser;
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypdcase'} = $thiscase;

                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sumsypd'} = 
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sum'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'} = 
                            $completedsypd{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'};
                          $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'simdays'} = 
                            $completedsimdays{$thisuser}{$thiscase}{$thissystem}{$thisaccount}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes};

                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }

      if (exists $summary{$thissystem}){
        foreach $thiscompset_alias (sort keys %{$summary{$thissystem}}){
          foreach $thisres_alias (sort keys %{$summary{$thissystem}{$thiscompset_alias}}){
            foreach $thisnumnodes (sort keys %{$summary{$thissystem}{$thiscompset_alias}{$thisres_alias}}){

              $max_sypd = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypd'};
              $max_sypd_lid = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypdlid'};
              $max_sypd_user = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypduser'};
              $max_sypd_case = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'maxsypdcase'};
              $min_sypd = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypd'};
              $min_sypd_lid = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypdlid'};
              $min_sypd_user = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypduser'};
              $min_sypd_case = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'minsypdcase'};
              $avg_sypd = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'sumsypd'}/
                           $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'};
              $cnt = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'cnt'};
              $simdays = $summary{$thissystem}{$thiscompset_alias}{$thisres_alias}{$thisnumnodes}{'simdays'};
              print "  System: $thissystem; Compset: $thiscompset_alias; Resolution: $thisres_alias; Number of Nodes: $thisnumnodes\n"; 
              print "    Completed Jobs: $cnt; Total Simulation Days: $simdays\n"; 
              print "    Average SYPD for TOTAL: $avg_sypd\n";
              print "    Maximum SYPD for TOTAL: $max_sypd\n";
              print "      (User: $max_sypd_user; Case: $max_sypd_case; LID: $max_sypd_lid)\n";
              print "    Minimum SYPD for TOTAL: $min_sypd\n";
              print "      (User: $min_sypd_user; Case: $min_sypd_case; LID: $min_sypd_lid)\n";
              print "\n";

            }
          }
        }
      }

    }

    print "\n";

  }
}

1;

__END__
