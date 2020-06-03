#! /bin/bash -xl
cd /data/pace-exp-files;

BEGIN_EXP=25301
END_EXP=25881
for i in `seq $BEGIN_EXP $END_EXP`; 
do  
    echo *$i*.zip  
    # touch insert-input-$BEGIN_EXP-$END_EXP.log
    e3smlab pacedb *$i*.zip --db-cfg /pace/prod/portal/pace/e3smlabdb.cfg --commit 2>&1 >> insert-input-$BEGIN_EXP-$END_EXP.log
done

# for i in `seq 24929 25881`; do  echo *$i*.zip  >> ./list; done
# cat ~/list | xargs echo
# cat ~/list | xargs e3smlab pacedb --db-cfg /pace/prod/portal/pace/e3smlabdb.cfg --commit

