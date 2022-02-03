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

sourceHists ={'2016MC':  '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2016ptetasum2D_MC.pkl',
              '2017MC' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2017ptetasum2D_MC.pkl',
              '2018MC' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2018ptetasum2D_MC.pkl',
              '2016Da':  '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2016ptetasum2D_data.pkl',
              '2017Da' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2017ptetasum2D_data.pkl',
              '2018Da' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2018ptetasum2D_data.pkl'}

class ssosWeight:
  def __init__(self, year, isData):
    try:
      self.weightHist = pickle.load(open(sourceHists[year + ('Da' if isData else 'MC')], 'r'))
      assert self.weightHist
    except:
      log.warning('No charge misID ratios avaialable, no problem if not used later')


# NOTE OVERFLOW ADDING DONE IN CREATING THESE WEIGHTS?

  def getWeight(self, pt1, etaSC1, pt2, etaSC2):
    etaSC1 = abs(etaSC1)
    etaSC2 = abs(etaSC2)
    etasum = etaSC1 + etaSC2
    ptsum = pt1 + pt2
    if etasum >= 4.8: etasum = 4.79
    if ptsum>= 160.: ptsum = 159. # last bin is valid to infinity
    return self.weightHist.GetBinContent(self.weightHist.GetXaxis().FindBin(etasum), self.weightHist.GetYaxis().FindBin(ptsum))

