# 10 june 2017 - removed my versions of ggsurv because GGally has now been patched
# updated june 2017 to generate km curves for restricted periods to make sense of
# drives with short observation periods
# for data from https://www.backblaze.com/hard-drive-test-data.html
# ross lazarus me fecit february 18 2016
# ggsurv modified from
# http://www.r-statistics.com/2013/07/creating-good-looking-survival-curves-the-ggsurv-function/
# the legend now corresponds to the order of the very last survival point so
# it's easier to see which is which...

library(survival)
library(rms)
library(GGally)
library(gdata)


setwd('/data/drivefail')


fixres = function(modkm)
{
  ## reformat and reorder the km model results
  oediff = modkm$obs - modkm$exp
  oesign = sign(oediff)
  oegood = oesign < 0
  oechi = (oediff) ^ 2 / modkm$exp
  oesort = oechi * oesign
  resd = data.frame(
    modkm$n,
    'Observed' = modkm$obs,
    'Expected' = modkm$exp,
    'chisq' = oechi,
    'sort' = oesort
  )
  rownames(resd) = names(modkm$n)
  sresd = resd[order(resd$sort), ]
  sresd$rank = c(1:nrow(resd))
  return(sresd)
}

# changeme!!!
setwd('/data/drivefail') 
options(width=512)
runtag = 'july6'
fn = paste('drivefail_res',runtag,sep='')
titl = 'KM plots - Backblaze drive data to end Q1 2018'
subtitl = paste('Run on',runtag,sep=' ')
# changeme!!!


f = paste(fn, 'xls', sep = '.')
d = read.delim(f, sep = '\t', head = T)
tm = table(d$manufact)
ds = subset(d, tm[d$manufact] > 200)
s = with(ds, Surv(time = obsdays, event = status))
km.manu = npsurv(s ~ manufact, data = ds)
ofnpdf = paste(fn, '_manufacturer.pdf', sep = '')
ofnpng = paste(fn, '_manufacturer.png', sep = '')
ofnsvg = paste(fn, '_manufacturer.svg', sep = '')
svg(ofnsvg)
ggsurv(km.manu, main = titl)
dev.off()
png(ofnpng, height = 1000, width = 1600)
ggsurv(km.manu, main = titl)
dev.off()
pdf(ofnpdf, height = 10, width = 20)
ggsurv(km.manu, main = titl)
dev.off()
tmo = table(d$model)
dm = subset(d, tmo[d$model] > 500)
# dm = subset(dm,)
sm = with(dm, Surv(time = obsdays, event = status))
km.mod = npsurv(sm ~ model, data = dm)
ofnpdf = paste(fn, '_model.pdf', sep = '')
ofnpng = paste(fn, '_model.png', sep = '')
ofnsvg = paste(fn, '_model.svg', sep = '')
svg(ofnsvg)
ggsurv(km.mod, main = titl)
dev.off()
png(ofnpng, height = 1000, width = 1600)
ggsurv(km.mod, main = titl)
dev.off()
pdf(ofnpdf, height = 10, width = 20)
ggsurv(km.mod, main = titl)
dev.off()
survdiff(sm ~ model, data = dm, rho = 0)
survdiff(s ~ manufact, data = ds, rho = 0)
# km assumes similar observation duration records for all strata	
# some drives (eg seagate 8TB) only have 30 days at best with Q2 2016 data.
# this makes the right hand side of the usual full period KM plots misleading,
# because there's no new information being added about some of the drives over time
# so try only modelling the first week and so on
# some interesting urban myths about early vs late failures?
#
cutps = c(3, 7, 15, 30, 60, 90, 120, 360, 720, 1080, 1440, 1800)

ncut = length(cutps)
for (i in c(1:ncut))
{
  nmax = cutps[i]
  titl = paste('KM first',
               nmax,
               'days of observation curves from Backblaze drive data to Q1 2017')
  dti = dm
  fixme = (dti$obsdays > nmax) # ignore all data, failing or not beyond nmax, by censoring at nmax.
  okmodels = subset(dti,fixme,select=c(model))
  models = levels(factor(as.character(okmodels$model)))
  modcol = models[order(models)]
  if (i == 1) {
    mdf = data.frame('model' = modcol)
  }
  dti$status[fixme] = 0
  dti$obsdays[fixme] = nmax
  inmodels = (dti$model %in% models)
  dt = subset(dti, inmodels)
  stm = with(dt, Surv(time = obsdays, event = status))
  km.mod = npsurv(stm ~ model, data = dt)
  kmmod = survdiff(stm ~ model, data = dt, rho = 0)
  pres = fixres(kmmod)
  rnk = data.frame(rank=pres[order(pres$groups), ]$rank)
  mdf = cbindX(mdf, rnk)# cbind(mdf, rnk)
  s = paste('*** KM statistics for first',nmax,'days')
  print.noquote(s)
  print(pres)
  ofnroot = paste('km_first',
                 nmax,
                 '_days_model_',
                 runtag,
                 sep = '')
  ofnpdf = paste(ofnroot,'.pdf',sep = '')
  ofnpng = paste(ofnroot,'.png',sep = '')
  png(ofnpng, height = 1000, width = 1600)
  print(ggsurv(km.mod, main = titl))
  ## ggplot requires explicit printing inside loops
  dev.off()
  pdf(ofnpdf, height = 10, width = 20)
  print(ggsurv(km.mod, main = titl))
  dev.off()
}

colnames(mdf) = c('Model', paste('Rank_day', cutps, sep = '_'))
mdfs = mdf[, 2:ncut]
vmdf = apply(mdfs, 1, var,na.rm=TRUE)
mmdf = apply(mdfs, 1, mean,na.rm=TRUE)
mdfo = cbind(mdf, 'mean' = mmdf, 'var' = vmdf)
mdfo = mdfo[order(mdfo$mean), ]
print(mdfo)

