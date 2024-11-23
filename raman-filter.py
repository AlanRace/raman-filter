
import csv
import os
import numpy as np
from common import calculateSpectrumStats, loadDataset
import argparse






# (savGolFilterSize, topHatFilterSize, peakThreshold, stdThreshold,
#  spectrumWidthThreshold, numPeaks) = (51, 21, 0.001, 0.001, 2, 5)

# homeFolder = '/home/alan/Documents/Work/Jasmin/Test'

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--data-folder", help="Folder containing data", required=True)
    parser.add_argument('--savitzky-golay-filter', type=int, default=51)
    parser.add_argument('--top-hat-filter', type=int, default=21)
    parser.add_argument('--peak-intensity-threshold', type=float, default=0.001)
    parser.add_argument('--std-threshold', type=float, default=0.001)
    parser.add_argument('--peak-width-threshold', type=float, default=2)
    parser.add_argument('--num-peaks', type=float, default=5)


    args = parser.parse_args()

    # (savGolFilterSize, topHatFilterSize, peakThreshold, stdThreshold,
    #     spectrumWidthThreshold, numPeaks) = (51, 21, 0.001, 0.001, 2, 5)
    
    print(args.data_folder)

    with open(os.path.join(args.data_folder, 'filtering-summary.csv'), 'w', newline='') as validation_csvfile:
        val_writer = csv.writer(validation_csvfile, delimiter=',')

        val_writer.writerow(['Filename', 'savGolFilterSize', 'topHatFilterSize', 'peakThreshold',
                            'stdThreshold', 'spectrumWidthThreshold', 'numPeaks', '# Keep', '# Discard'])

        for root, dirs, files in os.walk(args.data_folder):
            for filename in files:
                print("Processing file {}".format(filename))
                if filename.endswith(".txt"):
                    file = os.path.join(root, filename)

                    print(file)
                    row = []

                    fileSpectra, wavenumbers, numLines = loadDataset(file)

                    spectraStats, processedBurntData = calculateSpectrumStats(
                        fileSpectra, wavenumbers, 
                        savGolFilterSize=args.savitzky_golay_filter, 
                        topHatFilterSize=args.top_hat_filter, 
                        peakWidthThreshold=args.peak_width_threshold, 
                        peakThreshold=args.peak_intensity_threshold)
                    qualityPeaks = (spectraStats[:, 0] > args.peak_intensity_threshold) * \
                        (spectraStats[:, 2] > args.std_threshold) * \
                        (spectraStats[:, 3] >= args.num_peaks)

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
                    row.append(args.savitzky_golay_filter)
                    row.append(args.top_hat_filter)
                    row.append(args.peak_intensity_threshold)
                    row.append(args.std_threshold)
                    row.append(args.peak_width_threshold)
                    row.append(args.num_peaks)
                    row.append(sum(qualityPeaks))
                    row.append(sum(~qualityPeaks))
                    row.extend(np.mean(realSpectra, axis=0))

                    val_writer.writerow(row)



if __name__ == "__main__":
    main()