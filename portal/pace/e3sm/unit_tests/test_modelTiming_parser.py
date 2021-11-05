import modelTiming as mt

myjson = mt.parse('/Users/4g5/Downloads/exp-blazg-71436/timing.43235257.210608-222102/model_timing.0000')
print(myjson)
exit()
print("new timing stats")
myjson = mt.parse('modelTimingTest/gptl_timing_stats_new.txt')
# print myjson
print("old timing stats")
myjson = mt.parse('modelTimingTest/gptl_timing_stats_old.txt')
# print myjson
print("rank timing")
myjson = mt.parse('modelTimingTest/model_timing.0000')
print(myjson)

# print myjson
