from ttg.tools.logger  import getLogger
from ttg.tools.helpers import deltaR
from math import sqrt, atan, pi, tan
from math import log as logar
import ROOT
import os

log = getLogger()

#
# All functions to select objects, as well as some functions which add new variables based on the selected objects to the tree
#

#
# Helper functions
#
def getLorentzVector(pt, eta, phi, e):
  vector = ROOT.TLorentzVector()
  vector.SetPtEtaPhiE(pt, eta, phi, e)
  return vector

#
# Individual lepton selector
#
def leptonPt(tree, index):
  if tree._lFlavor[index]: return getattr(tree, '_lPt'+tree.muvar)[index]
  else:                    return getattr(tree, '_lPt'+tree.egvar)[index]

def leptonE(tree, index):
  if tree._lFlavor[index]: return getattr(tree, '_lE'+tree.muvar)[index]
  else:                    return getattr(tree, '_lE'+tree.egvar)[index]


def baseElectronSelector(tree, index):
  if not abs(tree._dxy[index]) < 0.05:                  return False
  if not abs(tree._dz[index]) < 0.1:                    return False
  if not abs(tree._3dIPSig[index]) < 8:                 return False
  if not tree._lElectronMissingHits[index] < 2:         return False
  if not tree._miniIso[index] < 0.4:                    return False
  if not tree._lElectronPassConvVeto[index]:            return False
  return True

def baseMuonSelector(tree, index):
  if not tree._lPOGMedium[index]:                       return False
  if not abs(tree._dxy[index]) < 0.05:                  return False
  if not abs(tree._dz[index]) < 0.1:                    return False
  if not abs(tree._3dIPSig[index]) < 8:                 return False
  if not tree._miniIso[index] < 0.4:                    return False
  # log.info('B')
  return True


def looseMuonSelector(tree, index):
  if not baseMuonSelector(tree, index):                 return False
  return tree._leptonMvaTOP[index] > 0.05

# muons:

# Base selection:
# POG Medium ID
# dxy < 0.05cm
# dz < 0.1cm
# SIP3D < 8
# miniIso(fall17) < 0.4

# LeptonMvaVLoose: leptonMvaTop>-0.45
# LeptonMvaLoose: leptonMvaTop>0.05
# LeptonMvaMedium: leptonMvaTop>0.65
# LeptonMvaTight: leptonMvaTop>0.90



def muonSelector(tree, index):
  if not baseMuonSelector(tree, index):                 return False
  return tree._leptonMvaTOP[index] > 0.65

def electronSelector(tree, index):
  if not baseElectronSelector(tree, index):             return False
  for i in xrange(tree._nMu): # cleaning electrons around muons
    # need to do this with MVA Loose muons
    if not (tree._lFlavor[i] == 1 and looseMuonSelector(tree, i)): continue
    if deltaR(tree._lEta[i], tree._lEta[index], tree._lPhi[i], tree._lPhi[index]) < 0.05: return False
  if 1.4442 < abs(tree._lEtaSC[index]) < 1.566:         return False
  return (tree._leptonMvaTOP[index] > 0.4 and tree._lElectronChargeConst[index] )


# electrons:

# Baseline selection:
# dxy < 0.05cm
# dz < 0.1cm
# SIP3D < 8
# missing hits < 2
# miniIso (fall17) < 0.4
# conversion rejection

# If I understand well, it seems the medium and tight workingpoints are only used in combination with the charge consistency requirement, so let's limit to 4 workingpoints for this next round:

# LeptonMvaTight (base selection + leptonMvaTOP > 0.9)
# LeptonMvaTightAnd3Charge

# LeptonMvaMedium (base selection + leptonMvaTOP > 0.4)
# LeptonMvaMediumAnd3Charge

# LeptonMvaLoose (base selection + leptonMvaTOP > 0)

# LeptonMvaVLoose (base selection + leptonMvaTOP > -.55)







def leptonSelector(tree, index):
  if leptonPt(tree, index) < 20:       return False
  if abs(tree._lEta[index]) > 2.4:     return False
  if   tree._lFlavor[index] == 0:      
    return electronSelector(tree, index)
  elif tree._lFlavor[index] == 1:      
    return muonSelector(tree, index)
  else:                                return False


#
# Selects leptons passing the id and iso criteria, sorts them, and save their indices
# First lepton needs to pass pt > 25 GeV
#
def getSortKey(item): return item[0]

def select2l(t, n):
  ptAndIndex        = [(leptonPt(t, i), i) for i in t.leptons]
  if len(ptAndIndex) < 2: return False

  ptAndIndex.sort(reverse=True, key=getSortKey)
  n.l1              = ptAndIndex[0][1]
  n.l2              = ptAndIndex[1][1]
  n.l1_pt           = ptAndIndex[0][0]
  n.l2_pt           = ptAndIndex[1][0]
  n.isEE            = (t._lFlavor[n.l1]==0 and t._lFlavor[n.l2]==0)
  n.isEMu           = (t._lFlavor[n.l1]==0 and t._lFlavor[n.l2]==1) or (t._lFlavor[n.l1]==1 and t._lFlavor[n.l2]==0)
  n.isMuMu          = (t._lFlavor[n.l1]==1 and t._lFlavor[n.l2]==1)
  n.isOS            = t._lCharge[n.l1] != t._lCharge[n.l2]
  return (leptonPt(t, n.l1) > 20 and n.isEE)


# def select1l(t, n):
#   ptAndIndex        = [(leptonPt(t, i), i) for i in t.leptons]
#   if len(ptAndIndex) < 1: return False

#   ptAndIndex.sort(reverse=True, key=getSortKey)
#   n.l1              = ptAndIndex[0][1]
#   n.l1_pt           = ptAndIndex[0][0]
#   n.isE             = (t._lFlavor[n.l1] == 0)
#   n.isMu            = (t._lFlavor[n.l1] == 1)
#   return True

def selectLeptons(t, n, minLeptons):
  t.leptons = [i for i in xrange(t._nLight) if leptonSelector(t, i)]
  if   minLeptons == 2: return select2l(t, n)
  else: return False #we're sticking to exactly 2 leptons right now
  # elif minLeptons == 1: return select1l(t, n)
  # elif minLeptons == 0: return True


#
# Add invariant masses to the tree
#
def makeInvariantMasses(t, n):
  first  = getLorentzVector(leptonPt(t, n.l1), t._lEta[n.l1], t._lPhi[n.l1], leptonE(t, n.l1))   if len(t.leptons) > 0 else None
  second = getLorentzVector(leptonPt(t, n.l2), t._lEta[n.l2], t._lPhi[n.l2], leptonE(t, n.l2))   if len(t.leptons) > 1 else None
  n.mll  = (first+second).M()        if first and second else -1


# #
# # Jets (filter those within 0.4 from lepton or 0.1 from photon)
# #
# def isGoodJet(tree, n, index):
#   if not tree._jetIsTight[index]:        return False
#   if not abs(tree._jetEta[index]) < 2.4: return False
#   if len(tree.photons) > 0 and tree.photonCutBased: #selected photon is necessarily CB (but not always CBfull)
#     if deltaR(tree._jetEta[index], tree._phEta[n.ph], tree._jetPhi[index], tree._phPhi[n.ph]) < 0.1: return False
  
#   for lep in tree.leptons:
#     if deltaR(tree._jetEta[index], tree._lEta[lep], tree._jetPhi[index], tree._lPhi[lep]) < 0.4: return False
#   return True



# # Note that all cleared jet variables are smearedJet based, not sure if the should be renamed
# def goodJets(t, n, forSys=True):
#   allGoodJets = [i for i in xrange(t._nJets) if isGoodJet(t, n, i)]
#   for var in ['']:
#     setattr(t, 'jets'+var,  [i for i in allGoodJets if getattr(t, '_jetSmearedPt'+var)[i] > t.jetPtCut])
#     setattr(n, 'njets'+var, len(getattr(t, 'jets'+var)))
#     setattr(n, 'j1'+var, getattr(t, 'jets'+var)[0] if getattr(n, 'njets'+var) > 0 else -1)
#     setattr(n, 'j2'+var, getattr(t, 'jets'+var)[1] if getattr(n, 'njets'+var) > 1 else -1)
#     setattr(n, 'j1_pt'+var, getattr(t, '_jetSmearedPt'+var)[getattr(n, 'j1'+var)] if getattr(n, 'njets'+var) > 0 else -1)



# def bJets(t, n, forSys=True):
#   workingPoints = {'2016':0.6321, '2017':0.4941, '2018':0.4184}
#   for var in ['', '_JECUp', '_JECDown', '_JERUp', '_JERDown'] if not forSys else ['']:
#     setattr(t, 'dbjets'+var,  [i for i in getattr(t, 'jets'+var) if t._jetDeepCsv_b[i] + t._jetDeepCsv_bb[i] > workingPoints[t.year]])
#     setattr(n, 'ndbjets'+var, len(getattr(t, 'dbjets'+var)))
#     setattr(n, 'dbj1'+var, getattr(t, 'dbjets'+var)[0] if getattr(n, 'ndbjets'+var) > 0 else -1)
#     setattr(n, 'dbj2'+var, getattr(t, 'dbjets'+var)[1] if getattr(n, 'ndbjets'+var) > 1 else -1)
#   if not forSys:
#     groupVars = ['_Absolute', '_BBEC1', '_EC2', '_FlavorQCD', '_HF', '_RelativeBal', '_Total']
#     groupYearVars = ['_HFUC', '_AbsoluteUC', '_BBEC1UC', '_EC2UC', '_RelativeSampleUC']
#     for var in groupVars:
#       for direc in ['Up','Down']:
#         setattr(t, 'dbjets'+var + direc,  [i for i in getattr(t, 'jets'+var+direc) if t._jetDeepCsv_b[i] + t._jetDeepCsv_bb[i] > workingPoints[t.year]])
#         setattr(n, 'ndbjets'+var + direc, len(getattr(t, 'dbjets'+var+direc)))
#         setattr(n, 'dbj1'+var + direc, getattr(t, 'dbjets'+var+direc)[0] if getattr(n, 'ndbjets'+var+direc) > 0 else -1)
#         setattr(n, 'dbj2'+var + direc, getattr(t, 'dbjets'+var+direc)[1] if getattr(n, 'ndbjets'+var+direc) > 1 else -1)
#     for var in groupYearVars:
#       for direc in ['Up','Down']:
#         setattr(t, 'dbjets'+var + direc,  [i for i in getattr(t, 'jets'+var+direc) if t._jetDeepCsv_b[i] + t._jetDeepCsv_bb[i] > workingPoints[t.year]])
#         setattr(n, 'ndbjets'+var + direc, len(getattr(t, 'dbjets'+var+direc)))
#         setattr(n, 'dbj1'+var + direc, getattr(t, 'dbjets'+var+direc)[0] if getattr(n, 'ndbjets'+var+direc) > 0 else -1)
#         setattr(n, 'dbj2'+var + direc, getattr(t, 'dbjets'+var+direc)[1] if getattr(n, 'ndbjets'+var+direc) > 1 else -1)

# #
# # delta R
# #
# def makeDeltaR(t, n, forSys=True):
#   n.phL1DeltaR   = deltaR(t._lEta[n.l1], t._phEta[n.ph], t._lPhi[n.l1], t._phPhi[n.ph]) if len(t.photons) > 0 and len(t.leptons) > 0 else -1
#   n.phL2DeltaR   = deltaR(t._lEta[n.l2], t._phEta[n.ph], t._lPhi[n.l2], t._phPhi[n.ph]) if len(t.photons) > 0 and len(t.leptons) > 1 else -1
#   for var in ['', '_JECUp', '_JECDown', '_JERUp', '_JERDown'] if not forSys else ['']:
#     setattr(n, 'phJetDeltaR'+var,  min([deltaR(t._jetEta[j], t._phEta[n.ph], t._jetPhi[j], t._phPhi[n.ph]) for j in getattr(t, 'jets'+var)] + [999])   if len(t.photons) > 0 else -1)
#     setattr(n, 'phBJetDeltaR'+var, min([deltaR(t._jetEta[j], t._phEta[n.ph], t._jetPhi[j], t._phPhi[n.ph]) for j in getattr(t, 'dbjets'+var)] + [999]) if len(t.photons) > 0 else -1)
#     setattr(n, 'l1JetDeltaR'+var,  min([deltaR(t._jetEta[j], t._lEta[n.l1], t._jetPhi[j], t._lPhi[n.l1]) for j in getattr(t, 'jets'+var)] + [999])     if len(t.leptons) > 0 else -1)
#     setattr(n, 'l2JetDeltaR'+var,  min([deltaR(t._jetEta[j], t._lEta[n.l2], t._jetPhi[j], t._lPhi[n.l2]) for j in getattr(t, 'jets'+var)] + [999])     if len(t.leptons) > 1 else -1)
#     setattr(n, 'jjDeltaR'+var,     min([deltaR(t._jetEta[getattr(n, 'j1'+var)], t._jetEta[getattr(n, 'j2'+var)], t._jetPhi[getattr(n, 'j1'+var)], t._jetPhi[getattr(n, 'j2'+var)])]) if getattr(n, 'njets'+var) > 1 else -1) # pylint: disable=C0301
#   if not forSys:
#     groupVars = ['_Absolute', '_BBEC1', '_EC2', '_FlavorQCD', '_HF', '_RelativeBal', '_Total']
#     groupYearVars = ['_HFUC', '_AbsoluteUC', '_BBEC1UC', '_EC2UC', '_RelativeSampleUC']
#     for var in groupVars:
#       for direc in ['Up','Down']:
#         setattr(n, 'phJetDeltaR'+var + direc,  min([deltaR(t._jetEta[j], t._phEta[n.ph], t._jetPhi[j], t._phPhi[n.ph]) for j in getattr(t, 'jets'+var+direc)] + [999])   if len(t.photons) > 0 else -1)
#         setattr(n, 'phBJetDeltaR'+var + direc, min([deltaR(t._jetEta[j], t._phEta[n.ph], t._jetPhi[j], t._phPhi[n.ph]) for j in getattr(t, 'dbjets'+var+direc)] + [999]) if len(t.photons) > 0 else -1)
#         setattr(n, 'l1JetDeltaR'+var + direc,  min([deltaR(t._jetEta[j], t._lEta[n.l1], t._jetPhi[j], t._lPhi[n.l1]) for j in getattr(t, 'jets'+var+direc)] + [999])     if len(t.leptons) > 0 else -1)
#         setattr(n, 'l2JetDeltaR'+var + direc,  min([deltaR(t._jetEta[j], t._lEta[n.l2], t._jetPhi[j], t._lPhi[n.l2]) for j in getattr(t, 'jets'+var+direc)] + [999])     if len(t.leptons) > 1 else -1)
#         setattr(n, 'jjDeltaR'+var + direc,     min([deltaR(t._jetEta[getattr(n, 'j1'+var+direc)], t._jetEta[getattr(n, 'j2'+var+direc)], t._jetPhi[getattr(n, 'j1'+var+direc)], t._jetPhi[getattr(n, 'j2'+var+direc)])]) if getattr(n, 'njets'+var+direc) > 1 else -1) # pylint: disable=C0301
#     for var in groupYearVars:
#       for direc in ['Up','Down']:
#         setattr(n, 'phJetDeltaR'+var + direc,  min([deltaR(t._jetEta[j], t._phEta[n.ph], t._jetPhi[j], t._phPhi[n.ph]) for j in getattr(t, 'jets'+var+direc)] + [999])   if len(t.photons) > 0 else -1)
#         setattr(n, 'phBJetDeltaR'+var + direc, min([deltaR(t._jetEta[j], t._phEta[n.ph], t._jetPhi[j], t._phPhi[n.ph]) for j in getattr(t, 'dbjets'+var+direc)] + [999]) if len(t.photons) > 0 else -1)
#         setattr(n, 'l1JetDeltaR'+var + direc,  min([deltaR(t._jetEta[j], t._lEta[n.l1], t._jetPhi[j], t._lPhi[n.l1]) for j in getattr(t, 'jets'+var+direc)] + [999])     if len(t.leptons) > 0 else -1)
#         setattr(n, 'l2JetDeltaR'+var + direc,  min([deltaR(t._jetEta[j], t._lEta[n.l2], t._jetPhi[j], t._lPhi[n.l2]) for j in getattr(t, 'jets'+var+direc)] + [999])     if len(t.leptons) > 1 else -1)
#         setattr(n, 'jjDeltaR'+var + direc,     min([deltaR(t._jetEta[getattr(n, 'j1'+var+direc)], t._jetEta[getattr(n, 'j2'+var+direc)], t._jetPhi[getattr(n, 'j1'+var+direc)], t._jetPhi[getattr(n, 'j2'+var+direc)])]) if getattr(n, 'njets'+var+direc) > 1 else -1) # pylint: disable=C0301

def getEta(pt, pz):
  theta = atan(pt/pz)
  if( theta < 0 ): theta += pi
  return -logar(tan(theta/2))
