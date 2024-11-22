
import numpy as np
import json
import os
import argparse
from common import calculateSpectrumStats, loadDataset

np.random.seed(1)


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
    trainingLabels = np.isin(
        np.arange(0, 100), data[fileIndicies[0]]['toKeep']) * 1

    for i in range(1, len(data)):
        curData = np.array(data[fileIndicies[i]]['fileSpectra'])

        trainingData = np.concatenate((trainingData, curData), axis=0)
        trainingLabels = np.append(trainingLabels, np.isin(
            np.arange(0, 100), data[fileIndicies[i]]['toKeep']) * 1)
        
    return wavenumbers, trainingData, trainingLabels


class Options:
    savGolFilterSizes: list[int] = [21, 51, 81]
    topHatFilterSizes: list[int] = [11, 21, 31]
    peakIntensityThresholds: list[float] = [0.0001, 0.001, 0.01]
    stdThresholds: list[float] = [0.0001, 0.001, 0.01]
    peakWidthThresholds: list[int] = [2, 5, 10]
    numPeaks: list[int] = [2, 5, 10]


def determineBestParameters(options: Options, wavenumbers, trainingData, trainingLabels):
    scores = []

    for savGolFilterSize in options.savGolFilterSizes:
        for topHatFilterSize in options.topHatFilterSizes:
            for peakIntensityThreshold in options.peakIntensityThresholds:
                for stdThreshold in options.stdThresholds:
                    for peakWidthThreshold in options.peakWidthThresholds:
                        for numPeaks in options.numPeaks:
                            print("Trying {}".format({"savGolFilterSize": savGolFilterSize, 
                                                              "topHatFilterSize": topHatFilterSize,
                                                              "peakIntensityThreshold": peakIntensityThreshold, 
                                                              "stdThreshold": stdThreshold, 
                                                              "peakWidthThreshold": peakWidthThreshold, 
                                                              "numPeaks": numPeaks}))

                            spectraStats, processedBurntData = calculateSpectrumStats(
                                trainingData, wavenumbers, savGolFilterSize, topHatFilterSize, peakWidthThreshold, peakIntensityThreshold)
                            qualityPeaks = (spectraStats[:, 0] > peakIntensityThreshold) * \
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

                            scores.append(((tp, tn, fp, fn), {"savGolFilterSize": savGolFilterSize, 
                                                              "topHatFilterSize": topHatFilterSize,
                                                              "peakIntensityThreshold": peakIntensityThreshold, 
                                                              "stdThreshold": stdThreshold, 
                                                              "peakWidthThreshold": peakWidthThreshold, 
                                                              "numPeaks": numPeaks}))


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

    return scores[index][1], f1_scores[index] 





def main():
    options = Options()

    parser = argparse.ArgumentParser()
    parser.add_argument("--data-folder", help="Folder containing data", required=True)
    parser.add_argument("--sorted-spectra", help=".json file defining the spectra classifications", required=True)
    parser.add_argument('--savitzky-golay-filters', nargs="+", type=int, default=options.savGolFilterSizes)
    parser.add_argument('--top-hat-filters', nargs="+", type=int, default=options.topHatFilterSizes)
    parser.add_argument('--peak-intensity-thresholds', nargs="+", type=float, default=options.peakIntensityThresholds)
    parser.add_argument('--std-thresholds', nargs="+", type=float, default=options.stdThresholds)
    parser.add_argument('--peak-width-thresholds', nargs="+", type=float, default=options.peakWidthThresholds)
    parser.add_argument('--num-peaks', nargs="+", type=float, default=options.numPeaks)
    
    args = parser.parse_args()

    options.savGolFilterSizes = args.savitzky_golay_filters
    options.topHatFilterSizes = args.top_hat_filters
    options.peakIntensityThresholds = args.peak_intensity_thresholds
    options.stdThresholds = args.std_thresholds
    options.peakWidthThresholds = args.peak_width_thresholds
    options.numPeaks = args.num_peaks

    wavenumbers, trainingData, trainingLabels = loadTrainingData(args.data_folder, args.sorted_spectra)
    best_parameters, f1_score = determineBestParameters(options, wavenumbers, trainingData, trainingLabels)
    print("Best parameters with an F1 score of {} are {}".format(
        f1_score, best_parameters))


if __name__ == "__main__":
    main()

