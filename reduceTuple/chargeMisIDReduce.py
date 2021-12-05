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
argParser.add_argument('--year',      action='store',      default=None,                 help='Only run for a specific year', choices=['2016Pre', '2016Post', '2017', '2018'])
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


from topSupport.tools.logger import getLogger
log = getLogger(args.logLevel)

import pdb

#
# Retrieve sample list, reducedTuples need to be created for the samples listed in tuples.conf
#
from topSupport.samples.Sample import createSampleList, getSampleFromList
sampleList = createSampleList(os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/tuples_2016.conf'),
                              os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/tuples_2017.conf'),
                              os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/tuples_2018.conf'))

# sampleList = createSampleList(os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/tuples_2016.conf'))



#
# Submit subjobs:
#   - each sample is splitted by the splitJobs parameter defined in tuples.conf, if a sample runs too slow raise the splitJobs parameter
#   - data is additional splitted per run to avoid too heavy chains to be loaded
#   - skips the isr and fsr systematic samples when tuples for scale and resolution systematics are prepared
#


if args.singleJob and args.subJob and not args.isChild:
  from topSupport.tools.jobSubmitter import submitJobs
  jobs = [(args.sample, args.year, args.subJob, args.splitData)]
  submitJobs(__file__, ('sample', 'year', 'subJob', 'splitData'), jobs, argParser, subLog=args.type, jobLabel = "RT")
  exit(0)

if not args.isChild and not args.subJob:
  from topSupport.tools.jobSubmitter import submitJobs
  if args.sample: sampleList = [s for s in sampleList if s.name == args.sample]
  if args.year:   sampleList = [s for s in sampleList if s.year == args.year[:4]]

  jobs = []
  for sample in sampleList:
    if sample.isData:
      if args.splitData:          splitData = [args.splitData]
      elif args.year.count('2016'):
        if args.year.count('Pre'): splitData = ['B', 'C', 'D', 'E', 'F']
        else: splitData = ['F', 'G', 'H']
      elif args.year == '2017': splitData = ['B', 'C', 'D', 'E', 'F']
      elif args.year == '2018': splitData = ['A', 'B', 'C', 'D']
    else:                         splitData = [None]
    jobs += [(sample.name, args.year, str(i), j) for i in xrange(sample.splitJobs) for j in splitData]
  # pdb.set_trace()
  submitJobs(__file__, ('sample', 'year', 'subJob', 'splitData'), jobs, argParser, subLog=args.type, jobLabel = "RT")
  exit(0)


args.year = args.year[:4] 

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
from topSupport.tools.helpers import reducedTupleDir, isValidRootFile
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
unusedBranches += ["_gen", '_ph', '_jet', '_rho']
deleteBranches = ["Scale", "Res", "pass", "met", "POG", "lElectron", "JECGrouped"]
if not sample.isData:
  # unusedBranches += ["gen_nL", "gen_l", "gen_met"]
  # deleteBranches += ["heWeight", "gen_ph"]
  deleteBranches += ["heWeight"]


for i in unusedBranches + deleteBranches: sample.chain.SetBranchStatus("*"+i+"*", 0)
# sample.chain.SetBranchStatus("*", 0)
# sample.chain.SetBranchStatus("*gen*", 1)
sample.chain.SetBranchStatus("*weight*", 1)


outputTree = sample.chain.CloneTree(0)
for i in deleteBranches: sample.chain.SetBranchStatus("*"+i+"*", 1)



#
# Define new branches
#

newBranches  = []

newBranches += ['l1/I', 'l2/I', 'l1_pt/F', 'l2_pt/F', 'nLepSel/I']
newBranches += ['mll/F']
newBranches += ['isEE/O', 'isMuMu/O', 'isEMu/O', 'isOS/O']

if not sample.isData:
  newBranches += ['genWeight/F']


  
from topSupport.tools.makeBranches import makeBranches
newVars = makeBranches(outputTree, newBranches)


c.egvar = 'Corr'
c.muvar = 'Corr'


# from topSupport.reduceTuple.objectSelection import setIDSelection, selectLeptons, selectPhotons, makeInvariantMasses, goodJets, bJets, makeDeltaR, reconstTops, getTopKinFit, storeLheTops
from topSupport.reduceTuple.objectSelection import selectLeptons, makeInvariantMasses




log.info('Starting event loop')
for i in sample.eventLoop(totalJobs=sample.splitJobs, subJob=int(args.subJob), selectionString=None):
  if c.GetEntry(i) < 0: 
    log.warning("problem reading entry, skipping")
    continue

  # NOTE respect the orders here!
  if not selectLeptons(c, newVars, 2):                continue
  

  if not c._passMETFilters:                           continue
  if sample.isData:
    if sample.name.count('DoubleMuon') and not c._passTrigger_mm:                                      continue
    if sample.name.count('DoubleEG')   and not c._passTrigger_ee:                                      continue  #does not exist in 2018
    if sample.name.count('MuonEG')     and not c._passTrigger_em:                                      continue
    if sample.name.count('SingleMuon'):
      if newVars.isMuMu and not (not c._passTrigger_mm and c._passTrigger_m):                          continue
      if newVars.isEMu  and not (not c._passTrigger_em and c._passTrigger_m):                          continue
    if sample.name.count('SingleElectron'):  #does not exist in 2018
      if newVars.isEE   and not (not c._passTrigger_ee and c._passTrigger_e):                          continue
      if newVars.isEMu  and not (not c._passTrigger_em and c._passTrigger_e and not c._passTrigger_m): continue
    if sample.name.count('EGamma'):   # 2018 only
      if newVars.isEE   and not (c._passTrigger_ee or c._passTrigger_e):                               continue
      # if newVars.isEMu  and not (not c._passTrigger_em and c._passTrigger_e and not c._passTrigger_m): continue
      if newVars.isEMu  and not ((c._passTrigger_e or c._passTrigger_ee) and not c._passTrigger_em and not c._passTrigger_m): continue
  else:
    if newVars.isEE   and not (c._passTrigger_ee or c._passTrigger_e):                                 continue
    if newVars.isEMu  and not (c._passTrigger_em or c._passTrigger_e or c._passTrigger_m):             continue
    if newVars.isMuMu and not (c._passTrigger_mm or c._passTrigger_m):                                 continue

  if not sample.isData:
    newVars.genWeight    = c._weight*lumiWeights[0]

  makeInvariantMasses(c, newVars)




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
