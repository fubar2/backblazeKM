# backblazeKM

Started February 2016
Ross Lazarus

Kaplan-Meier survival analysis for the Backblaze hard disk failure time data - see 
https://www.backblaze.com/blog/hard-drive-reliability-q4-2015/ and raw data at 
https://www.backblaze.com/hard-drive-test-data.html

R script does the modelling.


![KM curves by model][km1]


![KM curves by manufacturer][km2]


Python for transforming the fugly data into a format suitable for npsurv in the survival library

Blog at http://bioinformare.blogspot.com/2016/02/survival-analysis-of-hard-disk-drive.html


[km2]: km_manufacturer_feb2015_rl.png   "KM curves by manufacturer"
[km1]: km_model_feb2015_rl.png   "KM curves by model"
