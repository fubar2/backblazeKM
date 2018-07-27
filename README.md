# backblazeKM
Updated July 27 2018
Smart hours raw or normalised are so manufacturer/drive specific that I can't think they're much use.
Lots of drives have a fail followed by up to thousands more records indicating still alive. Clearly a data 
problem. Can't seem to get any help from the Backblaze folks.

Updated June 10 2017: removed my ggsurv functions because
GGally is now patched to include them


Updated June 8 2017:

New data added. Code updated. images stowed here.
Now run a series of time restricted models to allow exploration of 
newer drives over shorter time spans - all observations are adjusted 
to represent what would have been known at the end of the particular 
shorter period


Started February 2016
Ross Lazarus

Kaplan-Meier survival analysis for the Backblaze hard disk failure time data - see 
https://www.backblaze.com/blog/hard-drive-reliability-q4-2015/ and raw data at 
https://www.backblaze.com/hard-drive-test-data.html

R script does the modelling.


![KM curves by model][km1]


![KM curves by manufacturer][km2]


Python for transforming the fugly data into a format suitable for npsurv in the survival library

Blog at http://bioinformare.blogspot.com


[km2]: km_manufacturer_feb2015_rl.png   "KM curves by manufacturer"
[km1]: km_model_feb2015_rl.png   "KM curves by model"
