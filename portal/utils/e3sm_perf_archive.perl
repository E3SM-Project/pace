#!/usr/bin/perl

#  Perl 5 required.
require 5.004;

#  Strict syntax checking.
use strict;

#  Modules.
use Cwd;
use Time::Local;
use Sys::Hostname;

=head1 NAME

e3sm_perf_archive

=head1 SYNOPSIS

Move performance archive data for completed or failed
jobs into time-stamped directory for permanent archiving.

=head1 DESCRIPTION

If it does not already exist, create a directory with the name 

  performance_archive_<system>_<project_space_name>_<year>_<month>_<day>_<hour>_<min>_<sec>

Next, move performance data for completed or failed jobs 
into the new directory, preserving the same directory
structure (name/case name/job id). Uses system job monitoring
tools to identify which jobs are still running (so
that associated data are not moved).

Usage:

perl e3sm_perf_archive.perl

within the top level of a performance_archive.

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

  # Define variables.
  my $timestamp;
  my $i;
  my $arg_flag;
  my $host;
  my $system;
  my $center;
  my $performance_archive;
  my @path;
  my $project_space;
  my $sec;
  my $min;
  my $hour;
  my $mday;
  my $mon;
  my $year;
  my $wday;
  my $yday;
  my $isdst;
  my $calyear;
  my $twodigitsec;
  my $twodigitmin;
  my $twodigithour;
  my $twodigitday;
  my $twodigitmonth;
  my $new_archive_name;
  my $new_archive_directory;
  my $mode;
  my @users;
  my $thisuser;
  my $new_user_directory;
  my $thisuser_directory;
  my @cases;
  my $thiscase;
  my $new_case_directory;
  my $thiscase_directory;
  my @jlids;
  my $thisjlid;
  my $thislid;
  my $thisjobid;
  my $thisjobid2;
  my $thisjlid_directory;
  my $thissystem;
  my $job_statsf_string;
  my $job_statsf;
  my $job_statsf_readable;
  my @squeueall_field;
  my $thisfeatures;
  my $thisexechost;
  my $thiscompleted;
  my $CaseStatusf;
  my @jlidfiles;
  my $thisjobstat;

  $timestamp = "unset";
  for (my $i=0; $i <= $#ARGV; $i+=2){
    $arg_flag = $ARGV[$i];
    if (($arg_flag =~ m/^-h$/) || ($arg_flag =~ m/^--help$/)){
      print
"Usage:

perl e3sm_perf_archive.perl

within the top level of a performance_archive at NERSC, 
at ALCF, at OLCF, on Anvil, on Chrysalis, or on Compy

Purpose:
Tool to aid in the permanent archiving of E3SM performance data.

If it does not already exist, create a directory with the name 

  performance_archive_<system>_<project_space_name>_<year>_<month>_<day>_<hour>_<min>_<sec>

Next, move performance data for completed or failed jobs 
into the new directory, preserving the same directory
structure (name/case name/job id). This uses system job monitoring
tools to identify which jobs are still running (so that
associated data are not moved). For centers with multiple systems, 
this tool will need to be run once on each system front end for
the given performance_archive directory if multiple
systems save performance data in the same directory.

Optional arguments:

  -h, --help      show this help message and exit 
  -t, --timestamp specify the timestamp (<year>_<month>_<day>_<hour>_<min>_<sec>)
                  to use in the name of the performance_archive directory. The
                  input is checked that it satisfies the general format, and aborts
                  otherwise. (Default is to use the script execution local time.) 
\n";
      exit;
    }elsif(($arg_flag =~ m/^--timestamp$/) || ($arg_flag =~ m/^-t$/)){
      $timestamp = $ARGV[++$i];
      if ($timestamp !~ m/^(\d+)\_(\d+)\_(\d+)\_(\d+)\_(\d+)\_(\d+)$/){
        print "Error: timestamp input (\"$timestamp\") does not match required format\n";
        exit;
      }
    }
  }

  $host = hostname;

  if    ($host =~ m/^blueslogin\S*/){
    $system = "anvil";
    $center = "anvil";
  } 
  elsif ($host =~ m/^chrlogin\S*/){
    $system = "chrysalis";
    $center = "chrysalis";
  }
  elsif ($host =~ m/^compy\S*/){
    $system = "compy";
    $center = "compy";
  } 
  elsif ($host =~ m/^cori\S*/){
    $system = "cori";
    $center = "cori";
  } 
  elsif ($host =~ m/^login\S*/){
    $system = "summit";
    $center = "summit";
  }
  elsif ($host =~ m/^theta\S*/){
    $system = "theta";
    $center = "theta";
  } 
  else{
    die "ERROR: Can only be used on a supported system: anvil, chrysalis, compy, cori-haswell, cori-knl, summit, theta";
  }

# print "$system\n";

  $performance_archive = cwd();

# print "$performance_archive\n";

  if ($system =~ m/cori/){
    if ($performance_archive =~ m/^\/global\/cfs\/cdirs\/\S*/){
      @path = split(/\//,$performance_archive);
      $project_space = $path[4];
    }else{
      die "ERROR: On Cori, must be in a /global/cfs/cdirs/ subdirectory for this script to work";
      exit;
    }
  }elsif ($system =~ m/anvil/){
    if ($performance_archive =~ m/^\/lcrc\/group\/\S*/){
      @path = split(/\//,$performance_archive);
      $project_space = $path[3];
    }else{
      die "ERROR: On Anvil, must be in a /lcrc/group/ subdirectory for this script to work";
      exit;
    }
  }elsif ($system =~ m/chrysalis/){
    if ($performance_archive =~ m/^\/lcrc\/group\/\S*/){
      @path = split(/\//,$performance_archive);
      $project_space = $path[3];
    }else{
      die "ERROR: On Chrysalis, must be in a /lcrc/group/ subdirectory for this script to work";
      exit;
    }
  }elsif ($system =~ m/compy/){
    if ($performance_archive =~ m/^\/compyfs\/\S*/){
      $project_space = "all";
    }else{
      die "ERROR: On Compy, must be in a /compyfs/ subdirectory for this script to work";
      exit;
    }
  }elsif ($system =~ m/summit/){
    if ($performance_archive =~ m/^\/gpfs\/alpine\/\S*/){
      @path = split(/\//,$performance_archive);
      $project_space = $path[3];
    }else{
      die "ERROR: On Summit, must be in a /gpfs/alpine/ subdirectory for this script to work";
      exit;
    }
  }elsif ($system =~ m/theta/){
    if ($performance_archive =~ m/^\/lus\/theta-fs0\/projects\/\S*/){
      @path = split(/\//,$performance_archive);
      $project_space = $path[4];
    }else{
      die "ERROR: On Theta, must be in a /lus/theta-fs0/projects/ subdirectory for this script to work";
      exit;
    }
  }

# print "$project_space\n";

  if ($timestamp =~ m/unset/){
    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
    $twodigitsec = sprintf("%02d", $sec);
    $twodigitmin = sprintf("%02d", $min);
    $twodigithour = sprintf("%02d", $hour);
    $twodigitday = sprintf("%02d", $mday);
    $twodigitmonth = sprintf("%02d", $mon+1);
    $calyear = $year + 1900;
    $timestamp = "$calyear\_$twodigitmonth\_$twodigitday\_$twodigithour\_$twodigitmin\_$twodigitsec";
  }
  $new_archive_name = "performance\_archive\_$center\_$project_space\_$timestamp";

  if (-e $new_archive_name){
    if (!(-d $new_archive_name)){
      die "ERROR: $new_archive_name must be a directory";
    }
  }else{
    mkdir "$new_archive_name";
  }

  $new_archive_directory = "$performance_archive/$new_archive_name";
  $mode = 0775;
  $mode = $mode | 02000;  # Set group sticky bit.
  chmod $mode, "$new_archive_directory";

  print "Creating/Using $new_archive_directory\n";

  opendir USERS, $performance_archive;
  @users = grep { -d $_ && -r _ && /^(?!\.).*$/ } readdir USERS;

  USERLOOP: for ( @users ){
    $thisuser = $_;
    if (!($thisuser =~ m/^performance\_archive\S*/)){

      print "USER: $thisuser\n";

      $new_user_directory = "$new_archive_directory/$thisuser";

      chdir "$performance_archive/$thisuser" || next USERLOOP;
      $thisuser_directory = cwd();

      opendir CASES, $thisuser_directory || next USERLOOP;
      @cases = grep { -d $_ && -r _ && /^(?!\.).*$/ } readdir CASES;

      CASELOOP: for ( @cases ){
        $thiscase = $_;

        print "  CASE: $thiscase\n";

        $new_case_directory = "$new_user_directory/$thiscase";

        chdir "$thisuser_directory/$thiscase" || next CASELOOP;
        $thiscase_directory = cwd();

        opendir JLIDS, $thiscase_directory || next CASELOOP;
        @jlids = grep { -d $_ && -r _ && /^(?!\.).*$/ } readdir JLIDS;

        JLIDSLOOP: for ( @jlids ){
          $thisjlid = $_;

          $thisjobid = 0;
          $thisjobid2 = 0;
          if ($thisjlid =~ m/^(\d+)\S*\.(\d+\-\d+)$/){
            $thisjobid = $1;
            $thislid   = $2;
          }

          print "    LID: $thislid JOBID: $thisjobid\n";

          chdir "$thiscase_directory/$thisjlid" || next JLIDSLOOP;
          $thisjlid_directory = cwd();
          # Verify job id from job_statsf file.
          if ($system =~ m/anvil|chrysalis/){
            $job_statsf_string = "squeueall_jobid";
            # For LCRC systems, get system name from job_statsf file.
            $thissystem = "unset";
          }elsif ($system =~ m/compy/){
            $job_statsf_string = "squeueall_jobid";
            # For non-NERSC and non-LCRC systems, already know system.
            $thissystem = $system;
          }elsif ($system =~ m/theta/){
            $job_statsf_string = "qstatf_jobid";
            # For non-NERSC and non-LCRC systems, already know system.
            $thissystem = $system;
          }elsif ($system =~ m/cori/){
            $job_statsf_string = "sqsf_jobid";
            # For NERSC, get system name from job_statsf file.
            $thissystem = "unset";
          }elsif ($system =~ m/summit/){
            $job_statsf_string = "bjobslUF_jobid";
            # For non-NERSC and non-LCRC systems, already know system.
            $thissystem = $system;
          }
          $job_statsf = "$thisjlid_directory/$job_statsf_string.$thisjlid.gz";
          $job_statsf_readable = "false";

          if (-f $job_statsf && -r _ ){
            open(JOBSTATSF, "gunzip -c $job_statsf |") || die "can't open pipe to $job_statsf";
            $job_statsf_readable = "true";
          }else{
            $job_statsf = "$thisjlid_directory/$job_statsf_string.$thisjlid";
            if (-f $job_statsf && -r _ ){
              open(JOBSTATSF, "$job_statsf");
              $job_statsf_readable = "true";
            }
          }

          if ($job_statsf_readable =~ m/true/){

            if ($job_statsf_string =~ m/sqsf_jobid/){
              JOBFLOOP1: while (<JOBSTATSF>){
                if     (m/^JobId=(\d+)\s*JobName=(\S*)\s*$/){
                  $thisjobid2 = $1;
                  if ($thisjobid =~ m/0/){
                    $thisjobid = $thisjobid2;
                  }elsif (!($thisjobid =~ m/($thisjobid2)/)){
                    print "MISMATCHED JOB IDS: $thisjlid_directory\n";
                    print "  USER: $thisuser\n";
                    print "    CASE: $thiscase\n";
                    print "      JLID: $thisjlid\n";
                    print "        JOB IDS: $thisjobid $thisjobid2\n";
                    close JOBSTATSF;
                    next JLIDSLOOP;
                  }
                }elsif (m/^\s*Features=(\S+)\s+/){
                  # In the past the Cori systems and the Edison system used the
                  # same performance_archive directory. To differentiate on which
                  # system a given job ran, we used information in the job_statsf
                  # file. While Edison has been decommissioned, this issue may
                  # reoccur when the Perlmutter system comes on-line. We retain
                  # the following logic in case it becomes useful again.
                  $thisfeatures = $1;
                  if ($thisfeatures =~ m/haswell/){
                    $thissystem = "cori";
                  }
                  elsif ($thisfeatures =~ m/knl/){
                    $thissystem = "cori";
                  }
                  last JOBFLOOP1;
                }
              }
            }elsif ($job_statsf_string =~ m/squeueall_jobid/){
              JOBFLOOP2: while (<JOBSTATSF>){
                @squeueall_field = split(/\|/,$_);
                $thisjobid2 = $squeueall_field[8];
                if ($thisjobid2 =~ m/JOBID/){
                  next JOBFLOOP2;
                }
                if ($thisjobid =~ m/0/){
                  $thisjobid = $thisjobid2;
                }elsif (!($thisjobid =~ m/($thisjobid2)/)){
                  print "MISMATCHED JOB IDS: $thisjlid_directory\n";
                  print "  USER: $thisuser\n";
                  print "    CASE: $thiscase\n";
                  print "      JLID: $thisjlid\n";
                  print "        JOB IDS: $thisjobid $thisjobid2\n";
                  close JOBSTATSF;
                  next JLIDSLOOP;
                }
                # At one point Anvil and Chrysalis used the same performance_archive
                # directory. To differentiate on which system a given job ran, use
                # information in the job_statsf file.
                if ($system =~ m/anvil|chrysalis/){
                  $thisexechost = $squeueall_field[27];
                  if     ($thisexechost =~ m/b\S+/){
                    $thissystem = "anvil";
                  }elsif ($thisexechost =~ m/chr\S+/){
                    $thissystem = "chrysalis";
                  }
                }
                last JOBFLOOP2;
              }
            }elsif ($job_statsf_string =~ m/bjobslUF_jobid/){
              JOBFLOOP3: while (<JOBSTATSF>){
                if (m/^Job\s*<(\S+)?>.*$/){
                  $thisjobid2 = $1;
                  if ($thisjobid =~ m/0/){
                    $thisjobid = $thisjobid2;
                  }elsif (!($thisjobid =~ m/($thisjobid2)/)){
                    print "MISMATCHED JOB IDS: $thisjlid_directory\n";
                    print "  USER: $thisuser\n";
                    print "    CASE: $thiscase\n";
                    print "      JLID: $thisjlid\n";
                    print "        JOB IDS: $thisjobid $thisjobid2\n";
                    close JOBSTATSF;
                    next JLIDSLOOP;
                  }
                  last JOBFLOOP3;
                }
              }
            }else{
              JOBFLOOP4: while (<JOBSTATSF>){
                if ((m/^Job Id:\s*(\d+)\S*\s*$/) || 
                    (m/^JobID:\s*(\d+)\S*\s*$/)){
                  $thisjobid2 = $1;
                  if ($thisjobid =~ m/0/){
                    $thisjobid = $thisjobid2;
                  }elsif (!($thisjobid =~ m/($thisjobid2)/)){
                    print "MISMATCHED JOB IDS: $thisjlid_directory\n";
                    print "  USER: $thisuser\n";
                    print "    CASE: $thiscase\n";
                    print "      JLID: $thisjlid\n";
                    print "        JOB IDS: $thisjobid $thisjobid2\n";
                    close JOBSTATSF;
                    next JLIDSLOOP;
                  }
                  last JOBFLOOP4;
                }
              }
            }

            close JOBSTATSF;

          }

          if ($thissystem =~ m/unset/){
            print "POTENTIAL EARLY FAILURE: $thisjlid_directory\n";
            print "  USER: $thisuser\n";
            print "    CASE: $thiscase\n";
            print "      JLID: $thisjlid\n";
            next JLIDSLOOP;
          }

          print "      JOBID: $thisjobid JOBID2: $thisjobid2\n";
          print "      SYSTEM: $thissystem  SCRIPT-SYSTEM: $system\n";

          # If a gzipped version of CaseStatus exists, then job very likely completed.
          $thiscompleted = "false";
          $CaseStatusf = "CaseStatus.$thisjlid.gz";
          if (-f $CaseStatusf){
            $thiscompleted = "true";

            # But also check that all files are gzipped in this directory.
            opendir JLIDFILES, $thisjlid_directory;

            @jlidfiles = grep { -f $_ && -r _ && /^.*(?<!\.gz)$/ } readdir JLIDFILES;
            for ( @jlidfiles ){
              $thiscompleted = "false";
            }

          }

          print "        COMPLETED: $thiscompleted\n";

          # If not obviously completed, next check whether running, but should
          # by queried only on front end of system where the job ran.
          if (($thissystem =~ m/$system/) && ($thiscompleted =~ m/false/)){

            if ($system =~ m/anvil|chrysalis|compy/){
              $thisjobstat = `/usr/bin/squeue --job $thisjobid --noheader 2>&1`;
              if (($thisjobstat =~ m/^.*(slurm_load_jobs error: Invalid job id specified).*$/) ||
                  ($thisjobstat =~ m/^\s*$/)){
                $thiscompleted = "true";
              } else {
                print "RUNNING: $thisjlid_directory\n";
                print "  USER: $thisuser\n";
                print "    CASE: $thiscase\n";
                print "      JLID: $thisjlid\n";
              }
            }elsif ($system =~ m/cori/){
              $thisjobstat = `/usr/bin/squeue --job $thisjobid --noheader 2>&1`;
              if ($thisjobstat =~ m/^.*(slurm_load_jobs error: Invalid job id specified).*$/){
                $thiscompleted = "true";
              } else {
                print "RUNNING: $thisjlid_directory\n";
                print "  USER: $thisuser\n";
                print "    CASE: $thiscase\n";
                print "      JLID: $thisjlid\n";
	      }
            }elsif ($system =~ m/summit/){
              $thisjobstat = `bjobs $thisjobid 2>&1`;
              if ($thisjobstat =~ m/^Job <$thisjobid> is not found\s*$/){
                $thiscompleted = "true";
              } else {
                print "RUNNING: $thisjlid_directory\n";
                print "  USER: $thisuser\n";
                print "    CASE: $thiscase\n";
                print "      JLID: $thisjlid\n";
	      }
            }elsif ($system =~ m/theta/){
              $thisjobstat = `/usr/bin/qstat $thisjobid 2>&1`;
              if ($thisjobstat =~ m/^\s*$/){
                $thiscompleted = "true";
              } else {
                print "RUNNING: $thisjlid_directory\n";
                print "  USER: $thisuser\n";
                print "    CASE: $thiscase\n";
                print "      JLID: $thisjlid\n";
	      }
            }

            print "        COMPLETED2: $thiscompleted\n";

	  }

          # If completed, move data for this job to the new time-stamped performance 
          # archive. While not scrictly necessary, only allow script running
          # on the front end of a system to move data for jobs running on the
          # corresponding system.
          if (($thissystem =~ m/$system/) && ($thiscompleted =~ m/true/)){

             # First, check whether need to create a new user directory.
             if (-e $new_user_directory){
               if (!(-d $new_user_directory)){
                 die "ERROR: $new_user_directory must be a directory";
               }
             }else{
               mkdir "$new_user_directory";
               chmod $mode, "$new_user_directory";
             }

             # Next, check whether need to create a new case directory.
             if (-e $new_case_directory){
               if (!(-d $new_case_directory)){
                 die "ERROR: $new_case_directory must be a directory";
               }
             }else{
               mkdir "$new_case_directory";
               chmod $mode, "$new_case_directory";
             }

             # Finally, move the job directory.
             chdir "$thiscase_directory";
print "$thiscase_directory\n";
print "mv $thisjlid_directory $new_case_directory/$thisjlid`\n";
             `mv $thisjlid $new_case_directory/$thisjlid`

          }         

        }

        # Delete the case directory if it is now empty.
        rmdir "$thiscase_directory";

      }

      # Delete the user directory if it is now empty.
      rmdir "$thisuser_directory";

    }

  }

}

1;

__END__
