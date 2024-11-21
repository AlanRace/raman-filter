
import csv
import glob
import numpy as np
import scipy
from scipy.signal import savgol_filter


def loadDataset(filepath, dialect="excel-tab", intensityStart=2):
    fileSpectra = []

    with open(filepath) as tsv:
        numLines = -1

        # You can also use delimiter="\t" rather than giving a dialect.
        for line in csv.reader(tsv, dialect=dialect):
            if line[0] == '':
                line[0] = '-1'
            if line[1] == '':
                line[1] = '-1'

            line = np.array(line).astype(float)

            numLines += 1

            fileSpectra.append(line)

        fileSpectra = np.array(fileSpectra)

    return fileSpectra[1:, intensityStart:], fileSpectra[0, intensityStart:], numLines


def loadDatasetsInFolder(measurementFolder):
    filesToProcess = glob.glob(os.path.join(measurementFolder, '*.txt'))
    fileNumbers = []
    wavenumbers = None

    fullData = None

    for fileIndex in range(len(filesToProcess)):
        print(filesToProcess[fileIndex])

        fileSpectra, wavenumbers, numLines = loadDataset(
            filesToProcess[fileIndex])

        # Discard the wavenumbers and the coordinates
        if fullData is None:
            fullData = fileSpectra
            fileNumbers = np.ones(numLines) * fileIndex
        else:
            fullData = np.concatenate((fullData, fileSpectra), axis=0)
            fileNumbers = np.concatenate(
                (fileNumbers, np.ones(numLines) * fileIndex))

    return fullData, wavenumbers, fileNumbers


def preprocessSpectra(spectra, savGolFilterSize, topHatFilterSize, normalisation=True):
    processedData = savgol_filter(
        spectra, savGolFilterSize, 2, mode='nearest', axis=1)

    if normalisation:
        processedData = (processedData.transpose() /
                         np.max(processedData, axis=1)).transpose()

    # processedData = savgol_filter(processedData, savGolFilterSize, 2)
    # processedData = savgol_filter(processedData, savGolFilterSize, 2)
    processedData -= scipy.ndimage.grey_opening(
        processedData, size=(1, topHatFilterSize), mode='nearest')

    return processedData


def peakPick(spectra, x):
    firstDeriv = np.gradient(spectra, x, axis=1)
    secondDeriv = np.gradient(firstDeriv, x, axis=1)
    secondDeriv = secondDeriv[:, 1:]

    a, b = np.where((firstDeriv[:, :-1] * firstDeriv[:, 1:]) <= 0)

    c = np.where(secondDeriv[a, b] < 0)
    a = a[c]
    b = b[c]

    # It could either be the left or the right index so check which is the
    # actual maximum value
    indiciesRight = b + 1
    #     indiciesRight = indiciesRight(indiciesRight < length(counts));
    indiciesLeft = b - 1
    #     indiciesLeft = indiciesLeft(indiciesLeft > 0);

    c = np.where(np.logical_and(indiciesLeft > 0,
                 indiciesRight < spectra.shape[1]))
    a = a[c]
    b = b[c]
    indiciesRight = indiciesRight[c]
    indiciesLeft = indiciesLeft[c]

    stacked = np.stack(
        (spectra[a, b], spectra[a, indiciesLeft], spectra[a, indiciesRight]), axis=0)

    stacked_indicies = np.argmax(stacked, axis=0)

    # b = np.concatenate((b[stacked_indicies == 0],
    #                    indiciesLeft[stacked_indicies == 1], indiciesRight[stacked_indicies == 2]))

    indicies = np.zeros(b.shape, dtype=np.int32)

    for i in range(0, stacked.shape[1]):
        if stacked_indicies[i] == 0:
            indicies[i] = b[i]
        elif stacked_indicies[i] == 1:
            indicies[i] = indiciesLeft[i]
        elif stacked_indicies[i] == 2:
            indicies[i] = indiciesRight[i]

    peaks = []

    for i in range(len(a)):
        ind = indicies[i]

        left = ind - 1
        # and spectra[a[i], left]:
        while left > 0 and firstDeriv[a[i], left] >= 0:
            left -= 1
        if left < 0:
            left = 0

        right = ind + 1
        while right < firstDeriv.shape[1] and firstDeriv[a[i], right] <= 0:
            right += 1

        peaks.append([a[i], ind, left, right, spectra[a[i], ind]])

    peaks = np.array(peaks)

    return peaks


def calculateSpectrumStats(fullData, wavenumbers, savGolFilterSize, topHatFilterSize, spectrumWidthThreshold, peakThreshold):
    sizeToIgnore = int((topHatFilterSize - 1) / 2)

    processedData = preprocessSpectra(
        fullData, savGolFilterSize, topHatFilterSize)

    maxProcessedData = np.max(
        processedData[:, sizeToIgnore:-sizeToIgnore], axis=1)
    meanProcessedData = np.mean(
        processedData[:, sizeToIgnore:-sizeToIgnore], axis=1)
    stdProcessedData = np.std(
        processedData[:, sizeToIgnore:-sizeToIgnore], axis=1)

    peaks = peakPick(processedData, wavenumbers)

    spectraStats = []

    for spectrumIndex in range(fullData.shape[0]):
        peaksToConsider = peaks[peaks[:, 0] == spectrumIndex, :]
        numPeaks = np.sum(np.logical_and((peaksToConsider[:, 3] - peaksToConsider[:, 2]) >= spectrumWidthThreshold,
                                         peaksToConsider[:, 4] > peakThreshold))

        # print(spectrumIndex, maxProcessedData[spectrumIndex])

        spectraStats.append([maxProcessedData[spectrumIndex], meanProcessedData[spectrumIndex],
                             stdProcessedData[spectrumIndex], numPeaks])

    spectraStats = np.array(spectraStats)

    return spectraStats, processedData
