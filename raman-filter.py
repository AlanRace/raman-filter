
import csv
import os
import numpy as np
from common import calculateSpectrumStats, loadDataset


(savGolFilterSize, topHatFilterSize, peakThreshold, stdThreshold,
 spectrumWidthThreshold, numPeaks) = (51, 21, 0.001, 0.001, 2, 5)

homeFolder = '/home/alan/Documents/Work/Jasmin/Test'

with open(os.path.join(homeFolder, 'filtering-summary.csv'), 'w', newline='') as validation_csvfile:
    val_writer = csv.writer(validation_csvfile, delimiter=',')

    val_writer.writerow(['Filename', 'savGolFilterSize', 'topHatFilterSize', 'peakThreshold',
                        'stdThreshold', 'spectrumWidthThreshold', 'numPeaks', '# Keep', '# Discard'])

    for root, dirs, files in os.walk(homeFolder):
        for filename in files:
            if filename.endswith(".txt"):
                file = os.path.join(root, filename)

                print(file)
                row = []

                fileSpectra, wavenumbers, numLines = loadDataset(file)

                spectraStats, processedBurntData = calculateSpectrumStats(
                    fileSpectra, wavenumbers, savGolFilterSize, topHatFilterSize, spectrumWidthThreshold, peakThreshold)
                qualityPeaks = (spectraStats[:, 0] > peakThreshold) * \
                    (spectraStats[:, 2] > stdThreshold) * \
                    (spectraStats[:, 3] >= numPeaks)

                realSpectra = fileSpectra[qualityPeaks, :]
                burntSpectra = fileSpectra[~qualityPeaks, :]

                with open(file[:-4] + '_discard.csv', 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=',')

                    csvwriter.writerow(wavenumbers)
                    csvwriter.writerows(burntSpectra)

                with open(file[:-4] + '_keep.csv', 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, delimiter=',')

                    csvwriter.writerow(wavenumbers)
                    csvwriter.writerows(realSpectra)

                row.append(filename)
                row.append(savGolFilterSize)
                row.append(topHatFilterSize)
                row.append(peakThreshold)
                row.append(stdThreshold)
                row.append(spectrumWidthThreshold)
                row.append(numPeaks)
                row.append(sum(qualityPeaks))
                row.append(sum(~qualityPeaks))
                row.extend(np.mean(realSpectra, axis=0))

                val_writer.writerow(row)
