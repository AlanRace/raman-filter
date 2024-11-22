# Automatic Raman spectra filtering

## Filter spectra

### Parameters

| Parameter | Description|
|---------|-------|
| ....

## [Optional] Find optimal parameters 

As there are a number of parameters that can affect the selection of high quality spectra, an additional tool is provided to determine the optimal parameters via grid search based on pre-labelled spectra. 

To genererate labels, the tool [spectrum-sorter](https://github.com/AlanRace/spectrum-sorter) can be used. This generates the required input file `sortedSpectra.json`.


### Usage

`python optimise-parameters.py --data-folder /path/to/data --sorted-spectra /path/to/sortedSpectra.json`

#### Parameters


| Parameter | Description|
|---------|-------|
| `--data-folder` | Location of the data to be processed |
| `--sorted-spectra` | Location of the `sortedSpectra.json` generated from the [spectrum-sorter](https://github.com/AlanRace/spectrum-sorter) tool. |
| `--savitzky-golay-filters` | List of Savitzky-Golay window sizes to test. **Example:** `--savitzky-golay-filters 21 51 81` |
| `--top-hat-filters` | List of TopHat window sizes to test. **Example:** `--top-hat-filters 11 21 31` |
| `--peak-intensity-thresholds` | List of (normalised) peak intensity thresholds to test. **Example:** `--peak-intensity-thresholds 0.0001 0.001 0.01` |
| `--peak-width-thresholds` | List of peak widths (in bins/channels) to test. **Example:** `--peak-width-thresholds 2 5 10` |
| `--std-thresholds` | List of standard deviation thresholds to test. **Example:** `--std-thresholds 0.0001 0.001 0.01` |
| `--num-peaks` | List of number of peaks to test. **Example** `--num-peaks 2 5 10` |