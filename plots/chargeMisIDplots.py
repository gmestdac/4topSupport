#! /usr/bin/env python

#
# Argument parser and logging
#
import os, argparse, copy, pickle
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel',       action='store',      default='INFO',      nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'], help="Log level for logging")
argParser.add_argument('--year',           action='store',      default=None,        help='year for which to plot, of not specified run for all 3', choices=['2016', '2017', '2018', 'all', 'comb'])
argParser.add_argument('--selection',      action='store',      default=None)
argParser.add_argument('--extraPlots',     action='store',      default='')
argParser.add_argument('--channel',        action='store',      default=None)
argParser.add_argument('--tag',            action='store',      default='phoCBfull')
argParser.add_argument('--sys',            action='store',      default='')
argParser.add_argument('--filterPlot',     action='store',      default=None)
argParser.add_argument('--noZgCorr',       action='store_true', default=False,       help='do not correct Zg shape and yield')
argParser.add_argument('--runSys',         action='store_true', default=False)
argParser.add_argument('--showSys',        action='store_true', default=False)
argParser.add_argument('--debugFrac',      action='store',      default=0, type=int)
argParser.add_argument('--post',           action='store_true', default=False)
argParser.add_argument('--editInfo',       action='store_true', default=False)
argParser.add_argument('--isChild',        action='store_true', default=False)
argParser.add_argument('--runLocal',       action='store_true', default=False)
argParser.add_argument('--dryRun',         action='store_true', default=False,       help='do not launch subjobs')
argParser.add_argument('--fromCache',    action='store_true', default=False,       help='load a plot from cache if it already exists')
argParser.add_argument('--dumpArrays',     action='store_true', default=False)
args = argParser.parse_args()


from topSupport.tools.logger import getLogger
import pdb
log = getLogger(args.logLevel)

if args.noZgCorr: args.tag += '-noZgCorr'

if args.debugFrac:
  args.tag += 'debugOneIn' + str(args.debugFrac)

#
# Check git and edit the info file
#
from topSupport.tools.helpers import editInfo, plotDir, updateGitInfo, deltaPhi, deltaR, lumiScales, lumiScalesRounded
if args.editInfo:
  editInfo(os.path.join(plotDir, args.tag))

#
# Systematics
#
# from topSupport.plots.systematics import getReplacementsForStack, systematics, linearSystematics, applySysToTree, applySysToString, applySysToReduceType, showSysList, getSigmaSystFlat, getSigmaSystHigh, correlations, showSysListRunII, addYearLumiUnc, getBWrew

#
# Submit subjobs
#

import glob
for f in sorted(glob.glob("../samples/data/*.stack")):
  stackName = os.path.basename(f).split('.')[0]
  if not stackName[-5:] in ['_2016', '_2017', '_2018', '_comb']:
    log.warning('stack file without year label found (' + stackName + '), please remove or label properly')
    exit(0)




if not args.isChild:
  updateGitInfo()
  from topSupport.tools.jobSubmitter import submitJobs
  from topSupport.plots.variations   import getVariations
  # if args.runSys and not os.path.exists(os.path.join(plotDir, args.year, args.tag, args.channel, args.selection, 'yield.pkl')):
  #   log.info('Make sure the nominal plots exist before running systematics')
  #   exit(0)
  if args.showSys and args.runSys: sysList = showSysList + ['stat']
  elif args.sys:                   sysList = [args.sys]
  else:                            sysList = [None] + (systematics.keys() if args.runSys else [])

  subJobArgs, subJobList = getVariations(args, sysList)
  submitJobs(__file__, subJobArgs, subJobList, argParser, subLog= args.tag + '/' + args.year, jobLabel = "PL", wallTime= '30' if args.tag.count("base") else "15")
  exit(0)

#
# Initializing
#
import ROOT
from topSupport.plots.plot                   import Plot, xAxisLabels, fillPlots, addPlots, customLabelSize, copySystPlots
from topSupport.plots.plot2D                 import Plot2D, add2DPlots, normalizeAlong, xAxisLabels2D, yAxisLabels2D
from topSupport.plots.cutInterpreter         import cutStringAndFunctions
from topSupport.samples.Sample               import createStack


from math import pi
import numpy

ROOT.gROOT.SetBatch(True)

# reduce string comparisons in loop --> store as booleans
noWeight    = args.tag.count('noWeight')
normalize   = any(args.tag.count(x) for x in ['sigmaIetaIeta', 'randomConeCheck', 'splitOverlay', 'compareWithTT', 'compareTTSys', 'comparetopSupportammaSys', 'normalize', 'IsoRegTTDil', 'IsoFPTTDil'])
onlyMC = args.tag.count('onlyMC')



def chargeCheck(reco, match):
  if match == 0: return 2
  elif reco == match: return 0
  else: return 1


def chargeCheckBoth(reco1, match1, reco2, match2):
  if reco1 == match1 and reco2 == match2: return 0
  if reco1 != match1 and reco2 != match2: return 3  # both wrong, but no distinction, the order matters here
  if match1 == 0 or match2 == 0: return 2
  else: return 1  #1 single charge flip

#
# Create stack
#
stackFile = 'default' 
for f in sorted(glob.glob("../samples/data/*.stack")):
  stackName = os.path.basename(f).split('.')[0][:-5]
  if stackName in args.tag and (len(stackName) > len(stackFile) or stackFile == 'default'):
    stackFile = stackName 

years = ['2016', '2017', '2018'] if args.year == 'all' else [args.year]
if args.year == 'all':
  for year in years:
    if not os.path.isfile('../samples/data/' + stackFile + '_' + year + '.stack'):
      log.warning('stackfile ' + stackFile + '_' + year + '.stack is missing, exiting')
      exit(0)

tupleFiles = {y : os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/tuples_' + y + '.conf') for y in ['2016', '2017', '2018', 'comb']}

# when running over all years, just initialise the plots with the stack for 16
stack = createStack(tuplesFile   = os.path.expandvars(tupleFiles['2016' if args.year == 'all' else args.year]),
                    styleFile    = os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/' + stackFile + '_' + ('2016' if args.year == 'all' else args.year) + '.stack'),
                    channel      = args.channel,
                    # replacements = getReplacementsForStack(args.sys, args.year)
                    )


#
# Define plots
#
# Plot.setDefaults(stack=stack, texY = ('(1/N) dN/dx' if normalize else 'Events'), modTexLeg = [('(genuine)', ''), ('nonprompt-estimate', 'Nonprompt #gamma')] if args.tag.lower().count('nice') else [])

# NOTE legend entry tweaks for paper plots
# modTexLeg = [('(genuine)', ''), ('nonprompt-estimate', 'Nonprompt #gamma'), ('data', 'Data'), ('nonprompt', 'Nonprompt #gamma')] if args.tag.lower().count('earlytest') else []


modTexLeg = [('DY TT chamidEstimate (MC)', 'estimate'), ('chamidEstimate', 'estimate'), ('TT', 't#bar{t}')]

Plot.setDefaults(stack=stack, texY = ('(1/N) dN/dx' if normalize else 'Events / bin'), modTexLeg = modTexLeg )
Plot2D.setDefaults(stack=stack)

from topSupport.plots.plotHelpers  import *

# Plot definitions (allow long lines, and switch off unneeded lambda warning, because lambdas are needed)
def makePlotList():
  # pylint: disable=C0301,W0108
  plotList = []
  # plotList.append(Plot('nll',        'nll',          lambda c : c.nll,              (6, 0, 6)))
  # plotList.append(Plot('nhtau',        'nhtau',          lambda c : c.nhtau,         (6, 0, 6)))
  # plotList.append(Plot('totYield',                   'total yield',                           lambda c : 0.5,                                                (1, 0, 1),   histModifications=xAxisLabels([''])))
  plotList.append(Plot('isOS',   '',          lambda c : c.isOS,         (2, 0, 2), histModifications=xAxisLabels(['SS', 'OS'])))
  plotList.append(Plot('totYield',                   'total yield',                           lambda c : 0.5,                                                (1, 0, 1),   histModifications=xAxisLabels(['yield'])))

  plotList.append(Plot('l1_pt',                      'p_{T}(l_{1}) [GeV]',                    lambda c : c.l1_pt,                                            (20, 20, 220)))
  plotList.append(Plot('l1_eta',                     '|#eta|(l_{1})',                         lambda c : abs(c._lEta[c.l1]),                                 (20, 0, 2.5)))
  plotList.append(Plot('l2_pt',                      'p_{T}(l_{2}) [GeV]',                    lambda c : c.l2_pt,                                            (20, 20, 220)))
  plotList.append(Plot('l2_eta',                     '|#eta|(l_{2})',                         lambda c : abs(c._lEta[c.l2]),                                 (20, 0, 2.5)))

  plotList.append(Plot('l1_pt_small',                      'p_{T}(l_{1}) [GeV]',                    lambda c : c.l1_pt,                                            (100, 20, 120)))
  plotList.append(Plot('l1_eta_small',                     '|#eta|(l_{1})',                         lambda c : abs(c._lEta[c.l1]),                                 (75, 0, 2.5)))
  plotList.append(Plot('l2_pt_small',                      'p_{T}(l_{2}) [GeV]',                    lambda c : c.l2_pt,                                            (100, 20, 120)))
  plotList.append(Plot('l2_eta_small',                     '|#eta|(l_{2})',                         lambda c : abs(c._lEta[c.l2]),                                 (75, 0, 2.5)))

  plotList.append(Plot('l1_pt_medBining',                      'p_{T}(l_{1}) [GeV]',                    lambda c : c.l1_pt,                                            (10, 20, 120)))
  plotList.append(Plot('l2_pt_medBining',                      'p_{T}(l_{2}) [GeV]',                    lambda c : c.l2_pt,                                            (10, 20, 80)))


  plotList.append(Plot('l1_eta_EB',                     '|#eta|(l_{1})',                         lambda c : abs(c._lEta[c.l1]),                     [0., 1.479, 2.5], histModifications=xAxisLabels(['Barrel', 'Endcap']) ))
  plotList.append(Plot('l2_eta_EB',                     '|#eta|(l_{2})',                         lambda c : abs(c._lEta[c.l2]),                     [0., 1.479, 2.5], histModifications=xAxisLabels(['Barrel', 'Endcap']) ))

  plotList.append(Plot('dl_mass',                    'm(ll) [GeV]',                           lambda c : c.mll,                                              (20, 0, 200)))
  plotList.append(Plot('dl_mass_small',              'm(ll) [GeV]',                           lambda c : c.mll,                                              (100, 0, 200)))
  plotList.append(Plot('dl_mass_smaller',             'm(ll) [GeV]',                           lambda c : c.mll,                                             (400, 0, 200)))


  plotList.append(Plot('l1_chargeCheck',   '',        lambda c : (c._lCharge[c.l1] == c._lMatchCharge[c.l1]) ,         (2, 0, 2), histModifications=xAxisLabels(['charge misId', 'correct charge'])))
  plotList.append(Plot('l2_chargeCheck',   '',        lambda c : (c._lCharge[c.l2] == c._lMatchCharge[c.l2]) ,         (2, 0, 2), histModifications=xAxisLabels(['charge misId', 'correct charge'])))

  plotList.append(Plot('l1_chargeCheckB',   '',        lambda c : chargeCheck(c._lCharge[c.l1], c._lMatchCharge[c.l1]) ,         (3, 0, 3), histModifications=xAxisLabels(['correct', 'opposite', 'conversion'])))
  plotList.append(Plot('l2_chargeCheckB',   '',        lambda c : chargeCheck(c._lCharge[c.l2], c._lMatchCharge[c.l2]) ,         (3, 0, 3), histModifications=xAxisLabels(['correct', 'opposite', 'conversion'])))

  plotList.append(Plot('chargeCheckBoth',   '',        lambda c : chargeCheckBoth(c._lCharge[c.l1], c._lMatchCharge[c.l1], c._lCharge[c.l2], c._lMatchCharge[c.l2]) ,         (4, 0, 4), histModifications=xAxisLabels(['both correct', 'one flip', 'one conversion', 'both wrong'])))


  plotList.append(Plot('nlepSel',                      'Number of selected leptons',                        lambda c : c.nLepSel,                                      (8, -.5, 7.5)))


  # plotList.append(Plot('njets',                      'Number of jets',                        lambda c : c.njets,                                            (8, -.5, 7.5)))
  # plotList.append(Plot('nbtag',                      'Number of b-tagged jets',               lambda c : c.ndbjets,                                          (4, -.5, 3.5)))0
  # plotList.append(Plot('j1_pt',                      'p_{T}(j_{1}) [GeV]',                    lambda c : c._jetSmearedPt[c.j1],                              (30, 30, 330)))
  # plotList.append(Plot('j1_eta',                     '|#eta|(j_{1})',                         lambda c : abs(c._jetEta[c.j1]),                               (15, 0, 2.4)))
  # plotList.append(Plot('j2_pt',                      'p_{T}(j_{2}) [GeV]',                    lambda c : c._jetSmearedPt[c.j2],                              (30, 30, 330)))
  # plotList.append(Plot('j2_eta',                     '|#eta|(j_{2})',                         lambda c : abs(c._jetEta[c.j2]),                               (15, 0, 2.4)))


  plotList.append(Plot2D('eta2D',          '|#eta|(l_{A})',           lambda c :  max(abs(c._lEta[c.l1]), abs(c._lEta[c.l2])),               (10, 0, 2.5),          '|#eta|(l_{B})',          lambda c : min(abs(c._lEta[c.l1]), abs(c._lEta[c.l2])),              (10, 0, 2.5)))
  plotList.append(Plot2D('eta2DEB',        '|#eta|(l_{A})',           lambda c :  max(abs(c._lEta[c.l1]), abs(c._lEta[c.l2])),               [0., 1.479, 2.5],     '|#eta|(l_{B})',          lambda c : min(abs(c._lEta[c.l1]), abs(c._lEta[c.l2])),              [0., 1.479, 2.5]))
  plotList.append(Plot2D('pt2D',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               (6, 20, 140),          'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              (6, 20, 140)))

  plotList.append(Plot2D('ptEtaTTbinning_l1',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,           [20.,  30., 45., 60. ,100., 200.],          '|#eta|(l_{1})',          lambda c : abs(c._lEta[c.l1]),         [0. , 0.4, 0.8, 1.1, 1.4, 1.6, 1.9, 2.2, 2.5]))
  plotList.append(Plot2D('ptEtaTTbinning_l2',          'p_{T}(l_{2}) [GeV]',           lambda c : c.l2_pt,           [20.,  30., 45., 60. ,100., 200.],          '|#eta|(l_{2})',          lambda c : abs(c._lEta[c.l2]),         [0. , 0.4, 0.8, 1.1, 1.4, 1.6, 1.9, 2.2, 2.5]))

  plotList.append(Plot2D('ptEtaTTbinning_l1_B',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,           [20., 25.,  30., 45., 60. ,100., 200.],          '|#eta|(l_{1})',          lambda c : abs(c._lEta[c.l1]),         [0. , 0.4, 0.8, 1.1, 1.4, 1.6, 1.9, 2.2, 2.5]))
  plotList.append(Plot2D('ptEtaTTbinning_l2_B',          'p_{T}(l_{2}) [GeV]',           lambda c : c.l2_pt,           [20., 25.,  30., 45., 60. ,100., 200.],          '|#eta|(l_{2})',          lambda c : abs(c._lEta[c.l2]),         [0. , 0.4, 0.8, 1.1, 1.4, 1.6, 1.9, 2.2, 2.5]))


  plotList.append(Plot2D('ptEtaNEWbinning_l1',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,           [20.,  30., 45., 60. ,100., 200.],          '|#eta|(l_{1})',          lambda c : abs(c._lEta[c.l1]),         [0., 0.8, 1.1, 1.4, 1.6, 1.9, 2.5]))
  plotList.append(Plot2D('ptEtaNEWbinning_l2',          'p_{T}(l_{2}) [GeV]',           lambda c : c.l2_pt,           [20.,  30., 45., 60. ,100., 200.],          '|#eta|(l_{2})',          lambda c : abs(c._lEta[c.l2]),         [0., 0.8, 1.1, 1.4, 1.6, 1.9, 2.5]))


  plotList.append(Plot('l1_pt_NEW',                      'p_{T}(l_{1}) [GeV]',                    lambda c : c.l1_pt,                                            [20.,  30., 45., 60. ,100., 200.]))
  plotList.append(Plot('l2_pt_NEW',                      'p_{T}(l_{2}) [GeV]',                    lambda c : c.l2_pt,                                            [20.,  30., 45., 60. ,100., 200.]))
  plotList.append(Plot('l1_eta_NEW',                     '|#eta|(l_{1})',                         lambda c : abs(c._lEta[c.l1]),                                 [0., 0.8, 1.1, 1.4, 1.6, 1.9, 2.5]))
  plotList.append(Plot('l2_eta_NEW',                     '|#eta|(l_{2})',                         lambda c : abs(c._lEta[c.l2]),                                 [0., 0.8, 1.1, 1.4, 1.6, 1.9, 2.5]))


  # plotList.append(Plot2D('pt2D_A',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 60., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 40., 60.]))
  # plotList.append(Plot2D('pt2D_B',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 40., 60., 80. ],                   'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 30., 40., 50.]))
  # plotList.append(Plot2D('pt2D_C',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 30, 40., 50., 60., 70., 80. ],     'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 30., 40., 50.]))
  # plotList.append(Plot2D('pt2D_D',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 30, 40., 50., 60., 70., 80. ],     'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 25., 30., 35., 40., 45., 50., 60.]))
  # plotList.append(Plot2D('pt2D_E',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 40., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 30., 60.]))
  # plotList.append(Plot2D('pt2D_F',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 50., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 35., 60.]))
  # plotList.append(Plot2D('pt2D_G',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 45., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 32., 60.]))

  plotList.append(Plot2D('pt2D_H',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 55., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 37., 60.]))
  plotList.append(Plot2D('pt2D_HA',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 50., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 37., 60.]))
  plotList.append(Plot2D('pt2D_HB',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               [20., 52., 100 ],                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              [20., 37., 60.]))

  # plotList.append(Plot2D('ptetasum2D',      '|#eta|(l_{1})+|#eta|(l_{2})',    lambda c : abs(c._lEta[c.l1])+abs(c._lEta[c.l2]),          [0., 1.4, 2.1,  2.8, 3.8, 4.8],      'p_{T}(l_{1})+ p_{T}(l_{2}) [GeV]',          lambda c :  c.l1_pt + c.l2_pt,     [40., 60., 80., 100., 160.]))
  # plotList.append(Plot('ptsum',    'p_{T}(l_{1})+ p_{T}(l_{2}) [GeV]',      lambda c :  c.l1_pt + c.l2_pt,     [40., 60., 80., 100., 160.]))
  # plotList.append(Plot('etasum',   '|#eta|(l_{1})+|#eta|(l_{2})',           lambda c : abs(c._lEta[c.l1])+abs(c._lEta[c.l2]),          [0., 1.4, 2.1,  2.8, 3.8, 4.8] ))

  # plotList.append(Plot2D('ptetasum2DfitA',      '|#eta|(l_{1})+|#eta|(l_{2})',    lambda c : abs(c._lEta[c.l1])+abs(c._lEta[c.l2]),        (10, 0., 4.8),      'p_{T}(l_{1})+ p_{T}(l_{2}) [GeV]',          lambda c :  c.l1_pt + c.l2_pt,     (10, 40., 200.)))
  # plotList.append(Plot2D('ptetasum2DfitB',      '|#eta|(l_{1})+|#eta|(l_{2})',    lambda c : abs(c._lEta[c.l1])+abs(c._lEta[c.l2]),        (20, 0., 4.8),      'p_{T}(l_{1})+ p_{T}(l_{2}) [GeV]',          lambda c :  c.l1_pt + c.l2_pt,     (20, 40., 200.)))
  # plotList.append(Plot2D('pt2D_fitA',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               (5, 20., 120.),                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              (6, 20., 80.)))
  # plotList.append(Plot2D('pt2D_fitB',          'p_{T}(l_{1}) [GeV]',           lambda c : c.l1_pt,               (10, 20., 120.),                        'p_{T}(l_{2}) [GeV]',          lambda c : c.l2_pt,              (12, 20., 80.)))

  # pylint: enable=C0301

  if args.filterPlot:
    plotList[:] = [p for p in plotList if args.filterPlot in p.name]

  doBlind = False  #unblinding

  if not doBlind:
    for p in plotList: p.blindRange = None
  return plotList

years = ['2016', '2017', '2018'] if args.year == 'all' else [args.year]

              
lumiScales['comb'] = lumiScales['2018']

totalPlots = []


if args.tag.lower().count('pretend'):
  lumiScales['2016'] = lumiScales['RunII']
  lumiScalesRounded['2016'] = lumiScalesRounded['RunII']



lumiScalesRounded['2016pre']  = 19.5
lumiScalesRounded['2016post'] = 16.8


from topSupport.tools.style import drawLumi, drawLumi2D, setDefault, ttgGeneralStyle
# from topSupport.plots.SSOSweight import ssosWeight
from topSupport.plots.chamidWeight import chamidWeight

# NOTE WARNING
# from topSupport.plots.SSOSweight import ssosWeight

# from topSupport.plots.summingSSOSweight import ssosWeight

setDefault()
ttgGeneralStyle()

for year in years:
  plots = makePlotList()
  stack = createStack(tuplesFile   = os.path.expandvars(tupleFiles[year]),
                    styleFile    = os.path.expandvars('$CMSSW_BASE/src/topSupport/samples/data/' + stackFile + '_' + year + '.stack'),
                    channel      = args.channel,
                    # replacements = getReplacementsForStack(args.sys, args.year)
                    )

  # link the newly loaded samples to their respective existing histograms in the plots
  for plot in plots:
    plot.stack = stack
    for sample in plot.histos.keys():
      for newSample in sum(stack, []):
        if sample.name == newSample.name: plot.histos[newSample] = plot.histos.pop(sample)
  
  if args.year == 'all' and args.showSys: continue

  log.info('Using stackFile ' + stackFile)
  loadedPlots = []
  if args.fromCache:
    for plot in plots:
      loaded = plot.loadFromCache(os.path.join(plotDir, year, args.tag, args.channel, args.selection))
      if loaded: loadedPlots.append(plot)    
    plotsToFill = []
    # plotsToFill = [plot for plot in plots if not plot.name in [Lplot.name for Lplot in loadedPlots]]
    loadedPlots = [Lplot for Lplot in loadedPlots if Lplot.name in [plot.name for plot in plots]]
    log.info('Plots loaded from cache:')
    log.info([Lplot.name for Lplot in loadedPlots])
    # log.info('Plots to be filled:')
    # log.info([plot.name for plot in plotsToFill])
  else: 
    plotsToFill = plots

  #
  # Loop over events (except in case of showSys when the histograms are taken from the results.pkl file)
  #
  if not args.showSys and plotsToFill:

    # reduceType = 'chaB'

    # reduceType = 'chaNEW'
    # reduceType = 'chaEta'
    reduceType = 'chaREL'

    # reduceType = 'chaD'
    # if args.year == '2017' or args.year == '2016':
    #   reduceType = 'chaE'
    # reduceType = 'chaBnoTCha'
    
    log.info("using reduceType " + reduceType)


    chamidEst = chamidWeight(year)

    for sample in sum(stack, []):
      # ddEst = ssosWeight(year, sample.isData)

      chamidEstimate        = sample.texName.count('chamidEstimate')
      ddEstimate            = sample.texName.count('ddEstimate')

      if chamidEstimate or ddEstimate:
        selection = args.selection.replace('SS', 'OS')
      else:
        selection = args.selection
      
      if args.tag.count('DCorr'):
        if year == '2016': chamidCorr = 0.966
        elif year == '2017': chamidCorr = 1.509
        elif year == '2018': chamidCorr = 1.515
        else: 
          log.warning('invalid year '+ year + 'for charge misId CF')
      else:
        chamidCorr = 1.

      cutString, passingFunctions = cutStringAndFunctions(selection, args.channel)

      # cutString, passingFunctions = cutStringAndFunctions(args.selection, args.channel)


      c = sample.initTree(reducedType = reduceType)
      c.year = sample.name[:4] if year == "comb" else year
      if c.year == '2016':
        if sample.name.lower().count('post'):
          lumiScale = 16.8
        elif sample.name.lower().count('pre'):
          lumiScale = 19.5
        else:
          log.warning('2016 sample with no pre/post designation, using full luminosity')
          lumiScale = lumiScales[c.year]
      else:
        lumiScale = lumiScales[c.year]
      c.data = sample.isData


      for i in sample.eventLoop(cutString, debugFrac = args.debugFrac):
        if c.GetEntry(i) < 0:
          log.info('corrupt basket in ' + str(c.GetFile()) )

        if not passingFunctions(c): continue

        
        if chamidEstimate:
          chamidEstWeight = chamidEst.getWeight(c.l1_pt, c._lEta[c.l1], c.l2_pt, c._lEta[c.l2]) * chamidCorr
        else:
          chamidEstWeight = 1.

        # if ddEstimate:
        #   ddEstWeight = ddEst.getWeight(c.l1_pt, c._lEtaSC[c.l1], c.l2_pt, c._lEtaSC[c.l2])
        #   # ddEstWeight = 0.1461634*c._lEta[c.l1] + 0.1454445*c._lEta[c.l2] -0.0000495 *c.l1_pt -0.0004385 *c.l2_pt - 0.1755677
        #   # SOMETHING THAT CAN BE DONE WITH THE FACT THAT THEY ARE SO SIMILAR FOR L1 / L2?
        #   # log.info(ddEstWeight)
        # else:
        #   ddEstWeight = 1.


        # if sample.isData: eventWeight = 1. * chamidEstWeight * ddEstWeight
        if sample.isData: eventWeight = 1. * chamidEstWeight
        elif noWeight:      eventWeight = 1.
        # else:             eventWeight = c.genWeight*lumiScale * chamidEstWeight * ddEstWeight
        else:             eventWeight = c.genWeight*lumiScale * chamidEstWeight


        # else:             eventWeight = c.genWeight*c.puWeight*c.lWeight*c.lTrackWeight*c.phWeight*c.bTagWeight*c.triggerWeight*prefireWeight*lumiScale*c.ISRWeight*c.FSRWeight*c.PVWeight*estWeight*zgw


        if year == "comb": 
          eventWeight *= lumiScales['2018'] / lumiScales[c.year]
        # pdb.set_trace()
        fillPlots(plotsToFill, sample, eventWeight)

  plots = plotsToFill + loadedPlots

  if args.year == 'all':
    sortedPlots = sorted(plots, key=lambda x: x.name)
    if totalPlots:
      for i, totalPlot in enumerate(sorted(totalPlots, key=lambda x: x.name)):
        if isinstance(totalPlot, Plot2D):
          totalPlot = add2DPlots(totalPlot, sortedPlots[i])
        else:
          totalPlot = addPlots(totalPlot, sortedPlots[i])
    else:
      totalPlots = copy.deepcopy(plots)
    continue #don't draw individual years



  if args.tag.lower().count('pre'): VFPcase = 'pre'
  elif args.tag.lower().count('post'): VFPcase = 'post'
  else: VFPcase = ''


  #
  # Drawing the plots
  #
  noWarnings = True
  for plot in plots: # 1D plots
    if isinstance(plot, Plot2D): continue
    if not args.showSys:
      plot.saveToCache(os.path.join(plotDir, year, args.tag, args.channel, args.selection), args.sys)



  
  #
  # set some extra arguments for the plots
  #
    if not args.sys or args.showSys:
      extraArgs = {}
      normalizeToMC = [False, True] if (args.channel != 'noData' and not onlyMC and not args.tag.count('norat')) else [False]
      if args.tag.count('onlydata'):
        extraArgs['resultsDir']  = os.path.join(plotDir, year, args.tag, args.channel, args.selection)
        extraArgs['systematics'] = ['sideBandUnc']
      elif args.showSys:
        extraArgs['addMCStat']   = True
        if args.sys:
          extraArgs['addMCStat'] = (args.sys == 'stat')
          showSysList            = [args.sys] if args.sys != 'stat' else []
          linearSystematics      = {i: j for i, j in linearSystematics.iteritems() if i.count(args.sys)}
          if args.sys.count('-'):
            showSysList = args.sys.split('-')
            linearSystematics = {}
        # this is only to add lumi unc to total syst bands when plotting 1 year
        if args.showSys and not args.sys and not args.year == 'all':
          linearSystematics = addYearLumiUnc(linearSystematics, args.year)
        extraArgs['systematics']       = showSysList
        extraArgs['linearSystematics'] = linearSystematics
        extraArgs['postFitInfo']       = (args.year + 'srFit') if args.post else None
        extraArgs['resultsDir']        = os.path.join(plotDir, year, args.tag, args.channel, args.selection)



      if args.channel != 'noData':
        extraArgs['ratio']   = {'yRange' : (0.38, 1.62), 'texY': 'Data / pred.'}

      if args.tag.count('norat'):
        extraArgs['ratio']   = None

      if(normalize):
        extraArgs['scaling'] = 'unity'

      for norm in normalizeToMC:
        if norm: extraArgs['scaling'] = {0:1}
        for logY in [False, True]:
          if not logY and args.tag.count('sigmaIetaIeta') and plot.name.count('photon_chargedIso_bins_NO'): yRange = (0.0001, 0.35)
          else:                                                                                             yRange = None
          extraTag  = '-log'    if logY else ''
          extraTag += '-sys'    if args.showSys else ''
          extraTag += '-normMC' if norm else ''
          extraTag += '-post'   if args.post else ''

          err = plot.draw(
                    plot_directory    = os.path.join(plotDir, year, args.tag, args.channel + extraTag, args.selection, (args.sys if args.sys else '')),
                    logX              = False,
                    logY              = logY,
                    sorting           = False,
                    yRange            = yRange if yRange else (0.003 if logY else 0.0001, "auto"),
                    drawObjects       = drawLumi(None, lumiScalesRounded[year + VFPcase ], isOnlySim=(args.channel=='noData' or onlyMC), onlyLum=True),
                    uncBandRatio = (0.15 if args.tag.count('Closure') else None)  , 
                    **extraArgs
          )
          extraArgs['saveGitInfo'] = False
          if err: noWarnings = False

  if not args.sys:
    for plot in plots: # 2D plots
      if not hasattr(plot, 'varY'): continue
      if not args.showSys:
        plot.applyMods()
        plot.saveToCache(os.path.join(plotDir, year, args.tag, args.channel, args.selection), args.sys)
      for logX in [False, True]:
        for option in ['SCAT', 'COLZ', 'COLZ TEXT']:
          plot.draw(plot_directory = os.path.join(plotDir, year, args.tag, args.channel + ('-log' if logX else ''), args.selection, option),
                    logZ           = False,
                    logX           = logX,
                    drawOption     = option,
                    drawObjects    = drawLumi2D(None, lumiScalesRounded[year + VFPcase ], isOnlySim=(args.channel=='noData' or onlyMC)))
                    
  if args.dumpArrays: 
    dumpArrays["info"] = " ".join(s for s in [args.year, args.selection, args.channel, args.tag, args.sys] if s) 
    with open( os.path.join( os.path.join(plotDir, year, args.tag, args.channel, args.selection), 'dumpedArrays' + (args.sys if args.sys else '') + '.pkl') ,'wb') as f:
      pickle.dump(dumpArrays, f)

  if noWarnings: 
    log.info('Plots made for ' + year)
    if not args.year == 'all': log.info('Finished')
  else:          
    log.info('Could not produce all plots for ' + year)


#
# Drawing the full RunII plots if requested
#

if not args.year == 'all': exit(0)

lumiScale = lumiScalesRounded['RunII']



log.info('Using stackFile ' + stackFile)
if args.year == 'all' and args.showSys:
  totalPlots = []
  for plot in plots:
    loaded = plot.loadFromCache(os.path.join(plotDir, args.year, args.tag, args.channel, args.selection))
    if loaded: totalPlots.append(plot)    
  totalPlots = [Lplot for Lplot in totalPlots if Lplot.name in [plot.name for plot in plots]]
  log.info('Plots loaded from cache:')
  log.info([Lplot.name for Lplot in totalPlots])

noWarnings = True
for plot in totalPlots: # 1D plots
  if isinstance(plot, Plot2D): continue
  if not args.showSys:
    plot.saveToCache(os.path.join(plotDir, 'all', args.tag, args.channel, args.selection), args.sys)
  if plot.name == "yield":
    log.info("Yields: ")
    for s, y in plot.getYields().iteritems(): log.info('   ' + (s + ':').ljust(25) + str(y))
  #
  # set some extra arguments for the plots
  #
  if not args.sys or args.showSys:


    extraArgs = {}
    normalizeToMC = [False, True] if (args.channel != 'noData' and not onlyMC and not args.tag.count('norat')) else [False]
    if args.tag.count('onlydata'):
      extraArgs['resultsDir']  = os.path.join(plotDir, args.year, args.tag, args.channel, args.selection)
      extraArgs['systematics'] = ['sideBandUnc']
    elif args.showSys:
      extraArgs['addMCStat']   = True
      if args.sys:
        extraArgs['addMCStat'] = (args.sys == 'stat')
        showSysList            = [args.sys] if args.sys != 'stat' else []
        linearSystematics      = {i: j for i, j in linearSystematics.iteritems() if i.count(args.sys)}
        if args.sys.count('-'):
          showSysList = args.sys.split('-')
          linearSystematics = {}
      extraArgs['systematics']       = showSysList
      extraArgs['linearSystematics'] = linearSystematics
      extraArgs['resultsDir']        = os.path.join(plotDir, args.year, args.tag, args.channel, args.selection)
      extraArgs['postFitInfo']       = (args.year + 'srFit') if args.post else None


    if args.channel != 'noData':
      extraArgs['ratio']   = {'yRange' : (0.38, 1.62), 'texY': 'Data / pred.'}

    for norm in normalizeToMC:
      if norm: extraArgs['scaling'] = {0:1}
      for logY in [False, True]:
        if not logY and args.tag.count('sigmaIetaIeta') and plot.name.count('photon_chargedIso_bins_NO'): yRange = (0.0001, 0.75)
        else:                                                                                             yRange = None
        extraTag  = '-log'    if logY else ''
        extraTag += '-sys'    if args.showSys else ''
        extraTag += '-normMC' if norm else ''
        extraTag += '-post'   if args.post else ''
        err = plot.draw(
                  plot_directory    = os.path.join(plotDir, 'all', args.tag, args.channel + extraTag, args.selection, (args.sys if args.sys else '')),
                  logX              = False,
                  logY              = logY,
                  sorting           = False,
                  yRange            = yRange if yRange else (0.003 if logY else 0.0001, "auto"),
                  drawObjects       = drawLumi(None, lumiScale, isOnlySim=(args.channel=='noData' or onlyMC)),
                  **extraArgs
        )
        extraArgs['saveGitInfo'] = False
        if err: noWarnings = False

if not args.sys:
  for plot in totalPlots: # 2D plots
    if not hasattr(plot, 'varY'): continue
    if not args.showSys:
      plot.applyMods()
      plot.saveToCache(os.path.join(plotDir, 'all', args.tag, args.channel, args.selection), args.sys)
    for logY in [False, True]:
      for option in ['SCAT', 'COLZ', 'COLZ TEXT']:
        plot.draw(plot_directory = os.path.join(plotDir, 'all', args.tag, args.channel + ('-log' if logY else ''), args.selection, option),
                  logZ           = False,
                  drawOption     = option,
                  drawObjects    = drawLumi2D(None, lumiScale, isOnlySim=(args.channel=='noData' or onlyMC)))
if noWarnings: log.info('Finished')
else:          log.info('Could not produce all plots - finished')
