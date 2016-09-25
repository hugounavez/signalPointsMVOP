## Pulse Wave Velocity Library
This repository is a compound of modules I used to process **Arterial Pulse Wave** signals
and **ECG signals** to calculate the Pulse Wave Velocity in humans.

This project was part of my final work (Master Thesis) in a [Master in Science program
in Biomedical Engineering](http://www.ing.ula.ve/post.biomedica/) at
[Universidad of The Andes](http://www.ula.ve/), which was titled **_"Design and implementation of a photopletismographic pulse wave velocity measurement device"_**.

In the following lines shows the basic structure of the code presented.

In the lowest level of abstracction the `signals.py` module can be used. The `signals.py` file has two important classes to process the two mentioned biosignals (ECG and the Arterial Pulsw Wave).

In the `signals.py`, the classes `EcgProcessing` and `PulseProcessing` can be found.

#### `EcgProcessing(time, ecg)`

`EcgProcessing` is a class that contains a Ecg signal and some functions to reduce its noise, reduce its
baseline and also to identify reference points. It receives two input arguments. `ecg` which is an array or a list of samples of an ECG signal and `time` which is a list of values in seconds whereby each sample was taken.

  * `EcgProcessing.firFilter(self, cutoff=50, numtaps=31, pass_zero=True, fs=1800)`: This module process the signal with a low pass fir filter (Hamming Window).

      - `cutoff`:  Cut off frequency in Hz.
      - `numtaps`:  Number of coeficients of the fir filter
      - `pass_zero`: Should be always True for being a low pass filter
      - `fs`:  Sampling frequency in Hz.


  *  `removeBaseline(self, polyGrade=15)`:
      This function reduce baseline in the ECG signal. It generates a polynomium that describes the
      general behavior of the Ecg signal and then, generates a signal that is substracted to the original one.

      - `polyGrade`: Polynomium grade to generate from the linear regression.


  *   `searchPoints(self, umb=0.5, numtaps=31)`: This method search over the ECG signal the local maxima points.
      - `umb`:  Threshold.
      - `numtaps` Number of coeficients for the internal FIR filter processing


  *   `process(self, umb=0.5)`: This method remove automatically the baseline of the signal, filters the
  signal with FIR filter and then apply the searchPoints method in order to
  get reference points of the signal.

    - Returns the points identified.


####  `PulseProcessing(time, pulso)`
`PulseProcessing` contains a arterial pulse signal and several methods for its processing. Some functions for searching reference points for each period are included.
  * `time`:  Time in seconds in which each sample was sampled.
  * `pulso`: Arterial pulse wave signal (samples)

###### `PulseProcessing.firFilter(self, fs=800, cutoff=30, numtaps=51, pass_zero=True)`
 * `cutoff`: Cut off frequency in Hz.
 * `numtaps`: Number of coeficients of the fir filter
 * `pass_zero`: Should be always True for being a low pass filter.
 * `fs`: Sampling frecuency in Hz.


###### `PulseProcessing.derivate(self, signal1, fs=800)`
This functions makes a diff operation over the sinal `x(n) = x(n) - x(n - 1)`. After the diff operation the signal is filter by FIR filter.
* `signal1`: List of samples of signal to be processed.
* `fs`: Sampled frequency of the signal.

###### `PulseProcessing.maxNum(self, pulso, ecgTimeMax, simplePuntosMax=False)`
This method makes the point identification of local maxima points.


![ECG-Aterial Pulse Wave delay](https://raw.githubusercontent.com/hugounavez/signalPointsMVOP/master/resultsExamples/singleProbeSignalsPointsCarotida.png)


![Arterial pulse wave point identification](https://lh3.googleusercontent.com/RWbRb1DIbqv1VWuH_c5G4eUwZCE8fCzgwA_PWgQJNy9lj9yGV8Gs89lro2dFytUcDIY9NHcG_lnqYPiZcfDB09A7Cp8fQomHeQl7K1bPaSv49xZfx5deFhvKCVBevKNfPDxsKyxYQjVrwEbWowqpz-vJTPlMY1Ya3rDz_WSiKrPrqKqRc2cSGFP8APSQ06JLZIek0D3Ie4o7nsgsImaIL3ofv5yDy9Cml1MC06HQ9ucPwhnMOxaE3WOgzy_aur18KU70lUwh3vlSqHAq_5IgcFzPhDTQh_Ji9N-urPziXzBkoCsasC71KgBy5Q1Fw0vxjT-iZppSe9A67yVCJatI_0xzhyqeCkKvOgxrCuSyrU7xV0n_QybIDYOXQ_iZ0MjRH1neR7uQ50QW-mrmpe0O214AIfWhaSi5-YmkQOuUXWBaLnERasOkf33OC0YEbSI6J7gFGYr9VbHVUESH8PXlbLHtDXC_LzLrXyYWG3-vGHS3s59PdmShDtEnqiUtynGYcQeEX0fXLbwWoplLHObUtWO_Oh69UCgbUdLZaXuaC8eBww7y2f8Vwye_HkgxnR6qd_loDQGt4r3stlbS5XKtWugmWPKFxzWIjsMd5_3AF8CcgdJQ=w1364-h500-no)
