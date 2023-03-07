
def mapValue(inputValue, minIn, maxIn, minOut, maxOut):
    inpSpan=maxIn-minIn
    outSpan=maxOut-minOut
    valueScaled = float(inputValue - minIn)/float(inpSpan)
    outputValue = minOut + (valueScaled * outSpan)
    
    return round(outputValue, 2)

