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

sourceHists ={'2016MC':  '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2016pt2D_HA_REG_MC.pkl',
              '2017MC' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2017pt2D_HA_REG_MC.pkl',
              '2018MC' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2018pt2D_HA_REG_MC.pkl',
              '2016Da':  '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2016pt2D_HA_REG_data.pkl',
              '2017Da' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2017pt2D_HA_REG_data.pkl',
              '2018Da' : '/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/topSupport/plots/python/chamidWeights/SSoOS_2018pt2D_HA_REG_data.pkl'}

class ssosWeight:
  def __init__(self, year, isData):
    try:
      self.weightHistEE = pickle.load(open(sourceHists[year + ('Da' if isData else 'MC')].replace('REG', 'EE'), 'r'))
      self.weightHistBE = pickle.load(open(sourceHists[year + ('Da' if isData else 'MC')].replace('REG', 'BE'), 'r'))
      self.weightHistEB = pickle.load(open(sourceHists[year + ('Da' if isData else 'MC')].replace('REG', 'EB'), 'r'))
      self.weightHistBB = pickle.load(open(sourceHists[year + ('Da' if isData else 'MC')].replace('REG', 'BB'), 'r'))
      assert self.weightHistEE
      assert self.weightHistBE
      assert self.weightHistEB
      assert self.weightHistBB
    except:
      log.warning('No charge misID ratios avaialable, no problem if not used later')


# NOTE OVERFLOW ADDING DONE IN CREATING THESE WEIGHTS?

  def getWeight(self, pt1, etaSC1, pt2, etaSC2):
    etaSC1 = abs(etaSC1)
    etaSC2 = abs(etaSC2)
    if pt1>= 100.: pt1 = 99. # last bin is valid to infinity
    if pt2>= 60.: pt2 = 59. # last bin is valid to infinity
    if etaSC1 < 1.497:
      if etaSC2 < 1.497:
        return self.weightHistBB.GetBinContent(self.weightHistBB.GetXaxis().FindBin(pt1), self.weightHistBB.GetYaxis().FindBin(pt2))
      else:
        return self.weightHistBE.GetBinContent(self.weightHistBE.GetXaxis().FindBin(pt1), self.weightHistBE.GetYaxis().FindBin(pt2))
    else:
      if etaSC2 < 1.497:
        return self.weightHistEB.GetBinContent(self.weightHistEB.GetXaxis().FindBin(pt1), self.weightHistEB.GetYaxis().FindBin(pt2))
      else:
        return self.weightHistEE.GetBinContent(self.weightHistEE.GetXaxis().FindBin(pt1), self.weightHistEE.GetYaxis().FindBin(pt2))

