import modelTiming as mt

print "new timing stats"
myjson = mt.parse('modelTimingTest/gptl_timing_stats_new.txt')
# print myjson
print "old timing stats"
myjson = mt.parse('modelTimingTest/gptl_timing_stats_old.txt')
# print myjson
print "rank timing"
myjson = mt.parse('modelTimingTest/model_timing.0000')
print myjson

# print myjson
