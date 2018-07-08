"""
 
July 2018
All sorts of odd data anomalies where a drive fails but subsequently reappears as not failed.
Added code to allow this "resurrection" or not - for sensitivity analyses
Added an output based on survival in SMART9 "hours" terms instead of date
 
Feb 29 2016
Ross added "fix" for ST500LM012 HN entries in 2014


Feb 26 2016
read raw backblaze csv data like
rlazarus@rosshp:~/drivefail$ head 2013/2013-09-29.csv
date,serial_number,model,capacity_bytes,failure,smart_1_normalized,smart_1_raw,smart_2_normalized,smart_2_raw,smart_3_normalized,smart_3_raw,smart_4_normalized,smart_4_raw,smart_5_normalized,smart_5_raw,smart_7_normalized,smart_7_raw,smart_8_normalized,smart_8_raw,smart_9_normalized,smart_9_raw,smart_10_normalized,smart_10_raw,smart_11_normalized,smart_11_raw,smart_12_normalized,smart_12_raw,smart_13_normalized,smart_13_raw,smart_15_normalized,smart_15_raw,smart_183_normalized,smart_183_raw,smart_184_normalized,smart_184_raw,smart_187_normalized,smart_187_raw,smart_188_normalized,smart_188_raw,smart_189_normalized,smart_189_raw,smart_190_normalized,smart_190_raw,smart_191_normalized,smart_191_raw,smart_192_normalized,smart_192_raw,smart_193_normalized,smart_193_raw,smart_194_normalized,smart_194_raw,smart_195_normalized,smart_195_raw,smart_196_normalized,smart_196_raw,smart_197_normalized,smart_197_raw,smart_198_normalized,smart_198_raw,smart_199_normalized,smart_199_raw,smart_200_normalized,smart_200_raw,smart_201_normalized,smart_201_raw,smart_223_normalized,smart_223_raw,smart_225_normalized,smart_225_raw,smart_240_normalized,smart_240_raw,smart_241_normalized,smart_241_raw,smart_242_normalized,smart_242_raw,smart_250_normalized,smart_250_raw,smart_251_normalized,smart_251_raw,smart_252_normalized,smart_252_raw,smart_254_normalized,smart_254_raw,smart_255_normalized,smart_255_raw
2013-09-29,W300D3HY,ST4000DM000,4000787030016,0,,165366816,,,,,,,,0,,,,,,2537,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,21,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,MJ1323YNG1MB4C,Hitachi HDS5C3030ALA630,3000592982016,0,,0,,,,,,,,0,,,,,,17567,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,30,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,W300BR20,ST4000DM000,4000787030016,0,,213485592,,,,,,,,0,,,,,,1835,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,23,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,W300CJ6Y,ST4000DM000,4000787030016,0,,213596136,,,,,,,,0,,,,,,2386,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,21,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,PL1331LAGB4EVH,Hitachi HDS5C4040ALE630,4000787030016,0,,0,,,,,,,,0,,,,,,3331,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,28,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,Z300MGNF,ST4000DM000,4000787030016,0,,207347848,,,,,,,,0,,,,,,1150,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,26,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,W30068RN,ST4000DM000,4000787030016,0,,124416800,,,,,,,,0,,,,,,1123,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,26,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,W300D3HL,ST4000DM000,4000787030016,0,,11744152,,,,,,,,0,,,,,,390,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,26,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2013-09-29,Z300GQ68,ST4000DM000,4000787030016,0,,42326864,,,,,,,,0,,,,,,1835,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,25,,,,,,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,


"""

import os
import sys
import datetime
import time
runtag = 'july6_no_resurrection'

allowResurrection = False # controls treatment of drives that reappear unfailed after a fail record
# if True pretends the fail was not seen, else first fail is taken as gospel. 
# this is a data problem I need to talk to them about...

started = time.time()
sdirs = sorted(os.listdir('.'))
dirs = [x for x in sdirs if os.path.isdir(x)]
#dirs = ['2018',] # testing
print 'dfail.py processing',' '.join(dirs)
ndone = 0
testing = False
outfn = 'drivefail_res%s.xls' % runtag
if testing:
    outfn = 'drivefail_resMay2017_testing.xls'
dfd = '/data/drivefail'
os.chdir(dfd)
tdict = {}
res_models_counts= {}
outfnrmc = 'drivefail_res_models_counts%s.xls' % runtag
rmco = open(outfnrmc,'w')
res_ids_counts = {}
outfnric = 'drivefail_res_ids_counts%s.xls' % runtag
rico = open(outfnric,'w')
res_ids_dates = {}
outfnrid = 'drivefail_res_ids_dates%s.xls' % runtag
rido = open(outfnrid,'w')
res_models_dates = {}

for targ in dirs:
    print 'in',targ
    flist = sorted(os.listdir(targ))
    flist = [os.path.join(targ,x) for x in flist if x.endswith('.csv')]
    idsep = '~~~'
    for i,fn in enumerate(flist):
        tdr = open(fn,'r',buffering=10000000).readlines()[1:] # drop header
        if testing:
            tdr = tdr[:1000]
        td = [[x.strip().split(',')[y] for y in [0,1,2,3,4,20]] for x in tdr]
        for j,row in enumerate(td):
            d,sn,mod,cap,status,hours = row
            if len(mod.split(' ')) > 1: # eg "foo bar"
                manu,model = mod.split(' ',1)
                if manu == 'ST500LM012' and model == 'HN':
                    # double bogus "ST500LM012 HN"
                    model = manu
                    manu = 'HN' # samsung - same model as a seagate - hope this is right
            else:
                manu = mod[:2]
                model = mod
            if hours > 100000:
              print '## > 10k hours at row',i,' = ',row
            obshours = hours
            obst = datetime.datetime.strptime(d, "%Y-%m-%d")
            id = '%s%s%s' % (mod,idsep,sn)
            tdict.setdefault(id,[obst,obst,'0',manu,'0']) # start,last,status,manu,hours if new
            rec = tdict[id]
            if obst < rec[1]:
               print('Earlier date %s record %s at row %d: %s' % (obst,rec[1],j,row))
            if (rec[2] == '1') or res_ids_counts.get(id,None): # failed already!
               # print('### Follow up on a failed drive id %s failed %s at row %d: %s' % (id,rec[2],j,row))          
               res_models_counts.setdefault(mod,0) # trying to identify sources of apparently bogus failures
               res_models_counts[mod] += 1 # one more
               res_ids_counts.setdefault(id,0)
               res_ids_counts[id] += 1
               res_ids_dates.setdefault(id,[])
               res_ids_dates[id].append(d)
               if allowResurrection:
                 rec[2] = status
                 rec[1] = obst
                 tdict[id] = rec
            else:
              if obst > rec[1]:
                 rec[1] = obst # update last obs
                 rec[4] = obshours
              if (status=='1'):
                 rec[2] = '1'
              tdict[id] = rec # update dict
        nrows = len(td)
        ndone += nrows
        if (((i) % 100) == 0):
             dur = time.time()-started
             print '# in directory %s with %d rows done at %f secs = %f rows/sec' % (targ,ndone,dur,ndone/dur)

outf = open(outfn,'w')
outf.write('manufact\tmodel\tserial\tobsdays\tstatus\tsmarthours\n')
kees = tdict.keys()
kees.sort()
for id in kees:
    rec = tdict[id]
    status = rec[2]
    gap = rec[1] - rec[0]
    obsd = '%d' % gap.days
    idl = id.split(idsep)
    mod = idl[0]
    ser = idl[1]
    man = rec[3]
    hours = rec[4]
    s = '\t'.join([man,mod,ser,obsd,status,hours])
    outf.write(s)
    outf.write('\n')
outf.close()
rmco.write('model\tpostfailrecs\n')
rmck = res_models_counts.keys()
s = ''.join(['%s\t%d\n' % (x,res_models_counts[x]) for x in rmck])
rmco.write(s)
rmco.write('\n')
rmco.close()

rico.write('id\tpostfailrecs\n')
ridk = res_ids_counts.keys()
ridk.sort()
s = ''.join(['%s\t%d\n' % (x,res_ids_counts[x]) for x in ridk])
rico.write(s)
rico.write('\n')
rico.close()

rido.write('id\tpostfaildates\n')
ridk = res_ids_dates.keys()
ridk.sort()
s = ''.join(['%s\t%s\n' % (x,' '.join(res_ids_dates[x])) for x in ridk])
rido.write(s)
rido.write('\n')
rido.close()
dur = time.time()-started
print '# dfail.py finished - %d rows done at %f secs = %f rows/sec' % (ndone,dur,ndone/dur)

