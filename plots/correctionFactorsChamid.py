import os
from topSupport.tools.logger import getLogger
from topSupport.tools.style import drawTex
log = getLogger()
import pickle
import ROOT
from array import array
ROOT.TH2.SetDefaultSumw2()
ROOT.TH1.SetDefaultSumw2()

import pdb


ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPaintTextFormat("3.2f")


# TODO DON"T FORGET TO UPDATE!
path = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-chamidClosureData-FINAL/ee/onZ-nLep2-SS/totYield.pkl'


def sumHists(dict, sumkeys = [], antiSumKeys = []):
  sumHist = None
  for name, hist in dict.iteritems():
    if (any((name.count(key) for key in sumkeys)) or not sumkeys) and (not any((name.count(key) for key in antiSumKeys)) or not antiSumKeys):
      if not sumHist: sumHist = hist.Clone()
      else: sumHist.Add(hist)
  return sumHist



for year in ['2016', '2017' , '2018']:
  direct    = sumHists(pickle.load(open(path.replace('YEAR', year), 'r'))['totYield'], [] , ['chamidEstimate'])
  estimate  = sumHists(pickle.load(open(path.replace('YEAR', year), 'r'))['totYield'], ['chamidEstimate'] , )
  # total prediction needs to be estimate * CF, so here it's direct / estimate
  print year + ' CF: ' + str(round(direct.Integral() / estimate.Integral(), 3))
