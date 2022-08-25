from topSupport.tools.logger  import getLogger
from topSupport.tools.helpers import deltaR
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


#  SIP3D < 15 and Irel < 1.0
# lPOGMedium is part of the muon object definition

def baseMuonSelector(tree, index):
  if leptonPt(tree, index) < 10.:                         return False
  if abs(tree._lEta[index]) > 2.4:                        return False
  if not abs(tree._3dIPSig[index]) < 15:                  return False
  if not tree._relIso[index] < 1.0:                  return False
  if not tree._lPOGMedium[index]:                         return False
  return True


def looseMuonSelector(tree, index):
  if not baseMuonSelector(tree, index):                   return False
  return True


def muonSelector(tree, index):
  if not baseMuonSelector(tree, index):                   return False
  return tree._leptonMvaTOPv2UL[index] > 0.90


def electronSelector(tree, index):
  # if not baseElectronSelector(tree, index):             return False
  if leptonPt(tree, index) < 10. :                        return False
  if abs(tree._lEta[index]) > 2.5:                        return False
  if not abs(tree._3dIPSig[index]) < 15:                  return False
  if not tree._relIso[index] < 1.0:                       return False   # abs not needed, reliso always positive, so it doesn't matter


  for i in xrange(tree._nMu): # cleaning electrons around muons
    if not (tree._lFlavor[i] == 1 and looseMuonSelector(tree, i)): continue
    if deltaR(tree._lEta[i], tree._lEta[index], tree._lPhi[i], tree._lPhi[index]) < 0.05: return False
  if 1.4442 < abs(tree._lEtaSC[index]) < 1.566:         return False

  return (tree._leptonMvaTOPv2UL[index] > 0.90 and tree._lElectronChargeConst[index])


def leptonSelector(tree, index):
  if leptonPt(tree, index) < 10:       return False
  if tree._lFlavor[index] == 0:      
    return electronSelector(tree, index)
  elif tree._lFlavor[index] == 1:      
    return muonSelector(tree, index)
  else:                                return False


#
# Selects leptons passing the id and iso criteria, sorts them, and save their indices
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
  # return (leptonPt(t, n.l1) > 20 and n.isEE)
  n.nLepSel = len(ptAndIndex)

  return leptonPt(t, n.l1) > 20



def selectLeptons(t, n, minLeptons):
  t.leptons = [i for i in xrange(t._nLight) if leptonSelector(t, i)]
  if   minLeptons == 2: return select2l(t, n)
  else: return False #we're sticking to  2 leptons right now
  # elif minLeptons == 1: return select1l(t, n)
  # elif minLeptons == 0: return True


#
# Add invariant masses to the tree
#
def makeInvariantMasses(t, n):
  first  = getLorentzVector(leptonPt(t, n.l1), t._lEta[n.l1], t._lPhi[n.l1], leptonE(t, n.l1))   if len(t.leptons) > 0 else None
  second = getLorentzVector(leptonPt(t, n.l2), t._lEta[n.l2], t._lPhi[n.l2], leptonE(t, n.l2))   if len(t.leptons) > 1 else None
  n.mll  = (first+second).M()        if first and second else -1


def getEta(pt, pz):
  theta = atan(pt/pz)
  if( theta < 0 ): theta += pi
  return -logar(tan(theta/2))
