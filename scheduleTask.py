# from ReadTemp import read_temp
# from setOutputs import setOutputs
# from checkPumpEfi import checkPumpEfi
# import globals as g

# def scheduleTask():
#     g.c = read_temp()
#     checkPumpEfi(g.tz1, g.readTemp[3], g.pumpTempOfset, g.pumpInterval)
#     g.BaseEfiInPercent = setOutputs(g.mainState, g.c, g.pumpEfi)
#     print("This test runs every 3 seconds")