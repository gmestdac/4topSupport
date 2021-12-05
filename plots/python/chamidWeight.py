#
# nonprompt photon background estimation weights
#

import os
from topSupport.tools.logger import getLogger
log = getLogger()
import pickle
import ROOT
ROOT.TH2.SetDefaultSumw2()
ROOT.TH1.SetDefaultSumw2()

sourceHists ={'2016':  '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/chamid2016ptEtaTTbinning.pkl',
              '2017' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/chamid2017ptEtaTTbinning.pkl',
              '2018' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/chamid2018ptEtaTTbinning.pkl'}

class chamidWeight:
  def __init__(self, year):
    try:
      weightHist = pickle.load(open(sourceHists[year], 'r'))
      self.weightHist = weightHist
      assert self.weightHist
    except:
      log.warning('No charge misID ratios avaialable, no problem if not used later')

  def getWeight(self, pt1, eta1, pt2, eta2):
    # if tree.chamidEstimate:
    eta1 = abs(eta1)
    eta2 = abs(eta2)
    if pt1>= 200: pt1 = 199 # last bin is valid to infinity
    if pt2>= 200: pt2 = 199 # last bin is valid to infinity
    w1 = self.weightHist.GetBinContent(self.weightHist.GetXaxis().FindBin(pt1), self.weightHist.GetYaxis().FindBin(eta1))
    w2 = self.weightHist.GetBinContent(self.weightHist.GetXaxis().FindBin(pt2), self.weightHist.GetYaxis().FindBin(eta2))
    return w1+w2
    # else: return 1.
