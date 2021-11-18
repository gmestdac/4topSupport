#! /usr/bin/env python

#
# Script to create additional variables in the trees and reduce it to manageable size
#


#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
argParser.add_argument('--sample',    action='store',      default=None,                 help='Sample for which to produce reducedTuple, as listed in samples/data/tuples*.conf')
argParser.add_argument('--year',      action='store',      default=None,                 help='Only run for a specific year', choices=['2016', '2017', '2018'])
argParser.add_argument('--type',      action='store',      default='phoCB',              help='Specify type of reducedTuple')
argParser.add_argument('--subJob',    action='store',      default=None,                 help='The xth subjob for a sample, number of subjobs is defined by split parameter in tuples.conf')
argParser.add_argument('--splitData', action='store',      default=None,                 help='Splits the data in its separate runs')
argParser.add_argument('--runLocal',  action='store_true', default=False,                help='use local resources instead of Cream02')
argParser.add_argument('--debug',     action='store_true', default=False,                help='only run over first three files for debugging')
argParser.add_argument('--dryRun',    action='store_true', default=False,                help='do not launch subjobs, only show them')
argParser.add_argument('--isChild',   action='store_true', default=False,                help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--overwrite', action='store_true', default=False,                help='overwrite if valid output file already exists')
argParser.add_argument('--recTops',   action='store_true', default=False,                help='reconstruct tops, save top and neutrino kinematics')
argParser.add_argument('--singleJob', action='store_true', default=False,                help='submit one single subjob, be careful with this')
argParser.add_argument('--onlyMC',    action='store_true', default=False,                   help='submit only MC samples for skimming')
args = argParser.parse_args()


from ttg.tools.logger import getLogger
log = getLogger(args.logLevel)

import pdb

#
# Retrieve sample list, reducedTuples need to be created for the samples listed in tuples.conf
#
from ttg.samples.Sample import createSampleList, getSampleFromList
# sampleList = createSampleList(os.path.expandvars('$CMSSW_BASE/src/ttg/samples/data/tuples_2016.conf'),
#                               os.path.expandvars('$CMSSW_BASE/src/ttg/samples/data/tuples_2017.conf'),
#                               os.path.expandvars('$CMSSW_BASE/src/ttg/samples/data/tuples_2018.conf'))

sampleList = createSampleList(os.path.expandvars('$CMSSW_BASE/src/ttg/samples/data/tuples_2016.conf'))


#
# Submit subjobs:
#   - each sample is splitted by the splitJobs parameter defined in tuples.conf, if a sample runs too slow raise the splitJobs parameter
#   - data is additional splitted per run to avoid too heavy chains to be loaded
#   - skips the isr and fsr systematic samples when tuples for scale and resolution systematics are prepared
#

forSys = args.type.count('Scale') or args.type.count('Res')  # Tuple is created for specific sys
noSys = ['ttgjets', 'mtup', 'mtdown','uedown', 'ueup', '_erd', '_CR1', '_CR2']

if args.singleJob and args.subJob and not args.isChild:
  from ttg.tools.jobSubmitter import submitJobs
  jobs = [(args.sample, args.year, args.subJob, args.splitData)]
  submitJobs(__file__, ('sample', 'year', 'subJob', 'splitData'), jobs, argParser, subLog=args.type, jobLabel = "RT")
  exit(0)

if not args.isChild and not args.subJob:
  from ttg.tools.jobSubmitter import submitJobs
  if args.sample: sampleList = [s for s in sampleList if s.name == args.sample]
  if args.year:   sampleList = [s for s in sampleList if s.year == args.year]

  jobs = []
  for sample in sampleList:
    if sample.isData:
      if forSys or args.onlyMC: continue #no need to have data for systematics
      if args.splitData:          splitData = [args.splitData]
      elif sample.year == '2016': splitData = ['B', 'C', 'D', 'E', 'F', 'G', 'H']
      elif sample.year == '2017': splitData = ['B', 'C', 'D', 'E', 'F']
      elif sample.year == '2018': splitData = ['A', 'B', 'C', 'D']
    else:                         splitData = [None]
    jobs += [(sample.name, sample.year, str(i), j) for i in xrange(sample.splitJobs) for j in splitData]
  # pdb.set_trace()
  submitJobs(__file__, ('sample', 'year', 'subJob', 'splitData'), jobs, argParser, subLog=args.type, jobLabel = "RT")
  exit(0)


#
# From here on we are in the subjob, first init the chain and the lumiWeight
#
import ROOT
ROOT.gROOT.SetBatch(True)

sample = getSampleFromList(sampleList, args.sample, args.year)
c      = sample.initTree(shortDebug=args.debug, splitData=args.splitData)
c.year = sample.year #access to year wherever chain is passed to function, prevents having to pass year every time


if not sample.isData:
  lumiWeights  = [(float(sample.xsec)*1000/totalWeight) for totalWeight in sample.getTotalWeights()]

#
# Create new reduced tree (except if it already exists and overwrite option is not used)
#
from ttg.tools.helpers import reducedTupleDir, isValidRootFile
outputId   = (args.splitData if args.splitData else '') + str(args.subJob)
outputName = os.path.join(reducedTupleDir, sample.productionLabel, args.type, sample.name, sample.name + '_' + outputId + '.root')

try:    os.makedirs(os.path.dirname(outputName))
except: pass

if not args.overwrite and isValidRootFile(outputName):
  log.info('Finished: valid outputfile already exists')
  exit(0)

outputFile = ROOT.TFile(outputName ,"RECREATE")
outputFile.cd()


#
# Switch off unused branches, avoid copying of branches we want to delete
#
# FIXME NOTE temporarily saving extra vars for MVA input check
# unusedBranches = ["HLT", "Flag", "HN", "tau", "Ewk", "lMuon", "miniIso", "closest", "_pt", "decay"]
# unusedBranches = ["HLT", "Flag", "HN", "tau", "Ewk", "lMuon", "decay"]
# deleteBranches = ["Scale", "Res", "pass", "met", "POG", "lElectron"]
# deleteBranches = ["Scale", "Res", "pass", "met", "lElectron"]
# deleteBranches = ["Scale", "Res", "pass", "met"]

unusedBranches = ["HLT", "Flag", "flag", "HN", "tau", "Ewk", "lMuon", "WOIso", "closest", "decay", "JECSources", 'jetPt_', 'corrMET' ]
deleteBranches = ["Scale", "Res", "pass", "met", "POG", "lElectron", "JECGrouped"]
if not sample.isData:
  # unusedBranches += ["gen_nL", "gen_l", "gen_met"]
  # deleteBranches += ["heWeight", "gen_ph"]
  deleteBranches += ["heWeight"]


# for i in unusedBranches + deleteBranches: sample.chain.SetBranchStatus("*"+i+"*", 0)
sample.chain.SetBranchStatus("*", 0)
sample.chain.SetBranchStatus("*gen*", 1)
sample.chain.SetBranchStatus("*weight*", 1)


outputTree = sample.chain.CloneTree(0)
# for i in deleteBranches: sample.chain.SetBranchStatus("*"+i+"*", 1)


isTTG = sample.name.count('TTGamma')

#
# Define new branches
#

newBranches  = []
# newBranches  = ['ph/I', 'ph_pt/F', 'phJetDeltaR/F', 'phBJetDeltaR/F', 'matchedGenPh/I', 'matchedGenEle/I', 'nphotons/I']
# newBranches += ['njets/I', 'j1/I', 'j2/I', 'ndbjets/I', 'dbj1/I', 'dbj2/I']
# newBranches += ['l1/I', 'l2/I', 'looseLeptonVeto/O', 'l1_pt/F', 'l2_pt/F']
# newBranches += ['mll/F', 'mllg/F', 'ml1g/F', 'ml2g/F', 'phL1DeltaR/F', 'phL2DeltaR/F', 'l1JetDeltaR/F', 'l2JetDeltaR/F', 'jjDeltaR/F', 'j1_pt/F']
# newBranches += ['isEE/O', 'isMuMu/O', 'isEMu/O']
# if args.recTops:
  # newBranches += ['top1Pt/F', 'top1Eta/F', 'top2Pt/F', 'top2Eta/F', 'nu1Pt/F', 'nu1Eta/F', 'nu2Pt/F', 'nu2Eta/F', 'topsReconst/O', 'liHo/F']

# if isTTG:
  # newBranches += ['mlhetop/F', 'mlheatop/F']


if not sample.isData:
  newBranches += ['genWeight/F']
  newBranches += ['decayCateg/I', 'nll/I', 'nl/I', 'nhtau/I']
  # newBranches += ['gdecayCateg/I', 'gnll/I', 'gnl/I', 'gnhtau/I']
  newBranches += ['llep1/I', 'llep2/I', 'llep3/I', 'llep4/I']

  # newBranches += ['genWeight/F', 'lTrackWeight/F', 'lWeight/F', 'puWeight/F', 'triggerWeight/F', 'phWeight/F', 'bTagWeight/F', 'PVWeight/F']
  # newBranches += ['genPhDeltaR/F', 'genPhPassParentage/O', 'genPhMinDeltaR/F', 'genPhRelPt/F', 'genPhPt/F', 'genPhEta/F', 'lhePhPt/F', 'genPhMomPdg/I']
  # if not forSys:

  #   for sys in ['JECUp', 'JECDown', 'JERUp', 'JERDown']:
  #     newBranches += ['njets_' + sys + '/I', 'ndbjets_' + sys +'/I', 'j1_' + sys + '/I', 'j2_' + sys + '/I', 'dbj1_' + sys + '/I', 'dbj2_' + sys + '/I']
  #     newBranches += ['phJetDeltaR_' + sys + '/F', 'phBJetDeltaR_' + sys + '/F', 'l1JetDeltaR_' + sys + '/F', 'l2JetDeltaR_' + sys + '/F', 'j1_pt_' + sys + '/F']
  #   for sys in ['Absolute','BBEC1','EC2','FlavorQCD','HF','RelativeBal','Total','HFUC','AbsoluteUC','BBEC1UC','EC2UC','RelativeSampleUC']:
  #     for direc in ['Up','Down']:
  #       newBranches += ['njets_' + sys + direc +  '/I', 'ndbjets_' + sys + direc + '/I', 'j1_' + sys + direc +  '/I', 'j2_' + sys + direc +  '/I', 'dbj1_' + sys + direc +  '/I', 'dbj2_' + sys + direc +  '/I']
  #       newBranches += ['phJetDeltaR_' + sys + direc +  '/F', 'phBJetDeltaR_' + sys + direc +  '/F', 'l1JetDeltaR_' + sys + direc +  '/F', 'l2JetDeltaR_' + sys + direc +  '/F', 'j1_pt_' + sys + direc + '/F']

  #   for var in ['Ru', 'Fu', 'RFu', 'Rd', 'Fd', 'RFd']:   newBranches += ['weight_q2_' + var + '/F']
  #   for i in range(0, 100):                              newBranches += ['weight_pdf_' + str(i) + '/F']
  #   for sys in ['Up', 'Down']:                           newBranches += ['lWeightPSSys' + sys + '/F', 'lWeightElSyst' + sys + '/F','lWeightMuSyst' + sys + '/F','lWeightElStat' + sys + '/F','lWeightMuStat' + sys + '/F', 'puWeight' + sys + '/F', 'triggerWeightStatMM' + sys + '/F', 'triggerWeightStatEM' + sys + '/F', 'triggerWeightStatEE' + sys + '/F', 'triggerWeightSyst' + sys + '/F', 'phWeight' + sys + '/F', 'ISRWeight' + sys + '/F', 'FSRWeight' + sys + '/F',  'PVWeight' + sys + '/F', 'lTrackWeight' + sys + '/F']
  #   for sys in ['lUp', 'lDown', 'bCOUp', 'bCODown', 'bUCUp', 'bUCDown']:         newBranches += ['bTagWeight' + sys + '/F']

from ttg.tools.makeBranches import makeBranches
newVars = makeBranches(outputTree, newBranches)



# nllT = [0,0,0,0,0,0,0]
# catT = [0,0,0,0,0,0,0]

log.info('Starting event loop')
for i in sample.eventLoop(totalJobs=sample.splitJobs, subJob=int(args.subJob), selectionString=None):
  if c.GetEntry(i) < 0: 
    log.warning("problem reading entry, skipping")
    continue

  if not sample.isData:
    newVars.genWeight    = c._weight*lumiWeights[0]


    # _gen_l based gen info #############################################

    newVars.nll = 0 # number of final state leptons
    newVars.nl = 0  # number of leptons, either final state or tau. if its mother is a tau we don't count it, just the tau
    newVars.nhtau = 0 # number of hadronically decaying tau's

    lleps = []
    for i in range(c._gen_nL):
      if not c._gen_lIsPrompt[i]: continue
      # if c._gen_lIsPrompt[i]: 
      if c._gen_lFlavor[i] in [0, 1]: 
        # no tau's in here at all
        newVars.nl+=1
        newVars.nll+=1
        lleps.append(i)
      elif c._gen_lDecayedHadr[i] and c._gen_lFlavor[i] == 2 :
        # we count tau's towards nl, but only if they didn't decay into leptons, don't want to count twice
        newVars.nl+=1
        newVars.nhtau += 1
    
    # Need to filter out muons decaying into electrons from being counted twice | actually no, of they have status 1 (which is the case for prompts) they can't decay anymore
    # not possible with _l variables?

    newVars.llep1 = 999
    newVars.llep2 = 999
    newVars.llep3 = 999
    newVars.llep4 = 999

    for i in range(len(lleps)):
      setattr(newVars, 'llep' + str(i+1), lleps[i])


    # WARNING more than 4 leps is going into 0 right now
    newVars.decayCateg = 0
    if newVars.nll == 1: newVars.decayCateg = 1
    if newVars.nll == 2: 
      if c._gen_lCharge[lleps[0]] == c._gen_lCharge[lleps[1]]:
        # log.info(c._gen_lCharge[lleps[0]])
        # log.info(c._gen_lCharge[lleps[1]])
        # log.info('----------')
        newVars.decayCateg = 2
      else:
        newVars.decayCateg = 3
    if newVars.nll == 3: 
      newVars.decayCateg = 4
    if newVars.nll == 4: 
      newVars.decayCateg = 5




#     # full gen collection based gen info ###############################################

#     newVars.gnll = 0 # number of final state leptons
#     newVars.gnl = 0  # number of leptons, either final state or tau. if its mother is a tau we don't count it, just the tau
#     newVars.gnhtau = 0 # number of hadronically decaying tau's

# # NOTE  DON'T FORGET isLastCopy
#     for i in range(c._gen_n):
#       if not abs(c._gen_pdgId[i]) in [11, 13, 15]: continue
#       if abs(c._gen_pdgId[i]) in [11, 13] and not c._gen_status[i] == 1: continue
#       if abs(c._gen_pdgId[i]) == 15 and not (c._gen_status[i] == 2 and c._gen_isLastCopy[i]): continue
#       # remaining are leptons, either final state mu or 

#       if c._gen_isPromptFinalState[i] or (c._gen_isPromptDecayed[i] and abs(c._gen_pdgId[i]) == 15): newVars.gnl +=1
#       if c._gen_isPromptFinalState[i]: 
#         newVars.gnll +=1
#         print 'A'
#       if c._gen_isPromptFinalState[i] and abs(c._gen_pdgId[i]) in [11, 13]: 
#         print 'B'
#       print '------------------------'

#       # if c._gen_isPromptDecayed[i] and abs(c._gen_pdgId[i]) == 15

#       # if c._gen_lFlavor[i] in [0, 1]: 
#       #   # no tau's in here at all
#       #   newVars.nl+=1
#       #   newVars.nll+=1
#       #   lleps.append(i)
#       # elif c._gen_lDecayedHadr[i] and c._gen_lFlavor[i] == 2 :
#       #   # we count tau's towards nl, but only if they didn't decay into leptons, don't want to count twice
#       #   newVars.nl+=1
#       #   newVars.nhtau += 1


#     # nllT[newVars.nll] += 1
#     # catT[newVars.decayCateg] += 1

#     # log.info(nllT)
#     # log.info(catT)
#     # log.info('----------')
#     # pdb.set_trace()

  outputTree.Fill()
outputTree.AutoSave()
outputFile.Close()

f = ROOT.TFile.Open(outputName)
try:
  for event in f.blackJackAndHookersTree:
    continue
except:
  print 'produced a corrupt file, exiting'
  exit(1)


log.info('Finished')
