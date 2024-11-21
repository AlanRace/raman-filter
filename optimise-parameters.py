
import numpy as np
import json
import os
import argparse
from common import calculateSpectrumStats, loadDataset

np.random.seed(1)


data_folder = '/home/alan/Documents/Work/Jasmin/Jasmin/Messungen_180mA_alle_neu/'
json_folder = '/home/alan/Documents/Work/Jasmin/Jasmin/Messungen_180mA_alle_neu/'



def loadTrainingData(data_folder, sorted_spectra_path):
    with open(sorted_spectra_path) as json_file:
        data = json.load(json_file)


    # %% Load in all of the data to test

    for i in range(len(data)):
        dataset = os.path.join(data_folder, data[i]['dataset'])
        fileSpectra, wavenumbers, numLines = loadDataset(dataset)

        data[i]['fileSpectra'] = fileSpectra


    fileIndicies = np.arange(0, len(data))

    trainingData = np.array(data[fileIndicies[0]]['fileSpectra'])
    trainingLabels = np.in1d(
        np.arange(0, 100), data[fileIndicies[0]]['toKeep']) * 1

    for i in range(1, len(data)):
        curData = np.array(data[fileIndicies[i]]['fileSpectra'])

        trainingData = np.concatenate((trainingData, curData), axis=0)
        trainingLabels = np.append(trainingLabels, np.in1d(
            np.arange(0, 100), data[fileIndicies[i]]['toKeep']) * 1)
        
    return wavenumbers, trainingData, trainingLabels

# %%

wavenumbers, trainingData, trainingLabels = loadTrainingData(data_folder, os.path.join(json_folder, 'sortedSpectra.json'))

class Options:
    savGolFilterSizes: list[int] = [21, 51, 81]
    topHatFilterSizes: list[int] = [11, 21, 31]
    peakThresholds: list[float] = [0.0001, 0.001, 0.01]
    stdThresholds: list[float] = [0.0001, 0.001, 0.01]
    spectrumWidthThresholds: list[int] = [2, 5, 10]
    numPeaks: list[int] = [2, 5, 10]

options = Options()

scores = []

for savGolFilterSize in options.savGolFilterSizes:
    for topHatFilterSize in options.topHatFilterSizes:
        for peakThreshold in options.peakThresholds:
            for stdThreshold in options.stdThresholds:
                for spectrumWidthThreshold in options.spectrumWidthThresholds:
                    for numPeaks in options.numPeaks:

                        spectraStats, processedBurntData = calculateSpectrumStats(
                            trainingData, wavenumbers, savGolFilterSize, topHatFilterSize, spectrumWidthThreshold, peakThreshold)
                        qualityPeaks = (spectraStats[:, 0] > peakThreshold) * \
                            (spectraStats[:, 2] > stdThreshold) * \
                            (spectraStats[:, 3] >= numPeaks)

                        tp = np.sum(np.logical_and(
                            qualityPeaks, trainingLabels == 1))
                        tn = np.sum(np.logical_and(
                            ~qualityPeaks, trainingLabels == 0))
                        fp = np.sum(np.logical_and(
                            qualityPeaks, trainingLabels == 0))
                        fn = np.sum(np.logical_and(
                            ~qualityPeaks, trainingLabels == 1))

                        scores.append(((tp, tn, fp, fn), (savGolFilterSize, topHatFilterSize,
                                      peakThreshold, stdThreshold, spectrumWidthThreshold, numPeaks)))


# %%


f1_scores = []

for (result, configuration) in scores:
    # (result, configuration) = results[0]

    if (result[0] + result[3]) == 0.0 or (result[0] + result[2]) == 0.0:
        f1_score = 0.0
    else:
        recall = result[0] / (result[0] + result[3])
        precision = result[0] / (result[0] + result[2])
        f1_score = 2*(recall*precision) / (recall + precision)

    f1_scores.append(f1_score)


index = np.argmax(f1_scores)

print("Best parameters with an F1 score of {} are {}".format(
    f1_scores[index], scores[index][1]))

# %%
