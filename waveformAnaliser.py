#!/bin/env/python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.integrate import simps
import ipdb

XMIN = 450
XMAX = 550

def main():
    df = pd.read_hdf('output.h5','df')
    #df = pd.read_hdf('output-wave1-SingleTrig-V2-10k.h5','df')
    #df = pd.read_hdf('output-wave1-DoubleTrig.h5','df')

    invert = True
    xmin=400
    xmax=600
    conv = 1.0

    ipdb.set_trace()

    df['Baseline'] = 0
    df['Integral'] = 0
    df['Mean'] = 0
    df['Max'] = 0
    for i in range( df.shape[0] ):
        event = df.loc[i,'Vals']

        baseline = GetBaseLine(event, 200)
        event -= baseline
        if invert: event *= -1

        xmin, xmax = findPulseWidth(event, 1/3)

        df.loc[i,'Baseline'] = baseline
        df.loc[i,'Integral'] = integrate(event,xmin,xmax,conv)
        df.loc[i,'Mean']  = mean(event,xmin,xmax,conv)
        df.loc[i,'Max']  = GetMax(event)

    fig, axes = plt.subplots(2)

    axes[0].hist( df['Mean'], bins=50 )
    axes[1].hist( df['Integral'], bins=200, range=(0,10000) )

    plt.show()

def findPulseWidth(event, threshold):
    if (threshold > 1):
        return 0

    center = int(np.argmax(event))
    thresholdvalue = threshold * np.max(event)
    enumerateEvent = list(zip(range(event[1:center].size), event[1:center]))
    firstThreshold = bisearchLeft( enumerateEvent, thresholdvalue)
    if firstThreshold == None:
        firstThreshold = XMIN

    enumerateEvent = list(zip(range(event[center : event.size].size), event[center : event.size]))
    secondThreshold = bisearchRight(enumerateEvent, thresholdvalue)
    if secondThreshold == None:
        secondThreshold = XMAX
    else:
        secondThreshold += center

    #assimetrico por causa do formato do pico ter maior tempo de queda que de subida
    return (firstThreshold - 10, secondThreshold + 150)

def bisearchLeft(array, value):
    x = int(len(array) / 2)

    if array[x][1] > value and array[x - 1][1] < value:
        return array[x][0]
    elif array[x][1] > value :
        return bisearchLeft(array[0 : x], value)
    elif array[x][1] < value :
        return bisearchLeft(array[x : len(array)], value)

def bisearchRight(array, value):
    x = int(len(array) / 2)

    if array[x][1] < value and array[x - 1][1] > value:
        return array[x][0]
    elif array[x][1] > value :
        return bisearchRight(array[x : len(array)], value)
    elif array[x][1] < value :
        return bisearchRight(array[0 : x], value)

def integrate(event, xmin, xmax, conv=1.0):
    event_r = event[xmin:xmax]
    xdata = np.arange(xmin, (xmax if xmax < event.size else event.size) ) * conv
    return simps(event_r, xdata)

def mean(event, xmin, xmax, conv=1.0):
    x = np.arange(xmin, (xmax if xmax < event.size else event.size) ) * conv
    event_r = event[xmin:xmax]
    mean = np.sum( event_r * x ) / np.sum( event_r )
    return mean

def GetBaseLine(event, _range):
    baseline = 0
    for i in range(0, _range - 1):
        baseline += event[i]

    return baseline / _range

def GetMax(event):
    return np.nanmax(event)


if __name__ == '__main__':
    main()
