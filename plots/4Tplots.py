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
  # from topSupport.plots.variations   import getVariations
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
normalize   = any(args.tag.count(x) for x in ['sigmaIetaIeta', 'randomConeCheck', 'splitOverlay', 'compareWithTT', 'compareTTSys', 'compareTTGammaSys', 'normalize', 'IsoRegTTDil', 'IsoFPTTDil'])
onlyMC = args.tag.count('onlyMC')



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


modTexLeg = []

Plot.setDefaults(stack=stack, texY = ('(1/N) dN/dx' if normalize else 'Events / bin'), modTexLeg = modTexLeg )
Plot2D.setDefaults(stack=stack)

from topSupport.plots.plotHelpers  import *



def getSortKey(item): return item[0]

def sortedLeps(c, num):
  ptAndIndex= [(c._gen_lPt[i], i) for i in [c.llep1, c.llep2, c.llep3, c.llep4]]
  ptAndIndex.sort(reverse=True, key=getSortKey)
  return ptAndIndex[num][1]

# Plot definitions (allow long lines, and switch off unneeded lambda warning, because lambdas are needed)
def makePlotList():
  # pylint: disable=C0301,W0108
  plotList = []
  plotList.append(Plot('genl',          'genl',         lambda c : c._gen_nL,               (20, 0, 20)))
  plotList.append(Plot('nl',          'nl',           lambda c : c.nl,               (6, 0, 6)))
  plotList.append(Plot('nll',        'nll',          lambda c : c.nll,              (6, 0, 6)))
  plotList.append(Plot('nhtau',        'nhtau',          lambda c : c.nhtau,         (6, 0, 6)))
  plotList.append(Plot('totYield',                   'total yield',                           lambda c : 0.5,                                                (1, 0, 1),   histModifications=xAxisLabels([''])))
  plotList.append(Plot('decayCateg',   '',          lambda c : c.decayCateg,         (6, 0, 6), histModifications=xAxisLabels(['0l', '1l', '2l SS', '2l OS', '3l', '4l'])))

#   plotList.append(Plot2D('nl_nll',          'nl',           lambda c : c.nl,               (6, 0, 6),          'nll',          lambda c : c.nll,              (6, 0, 6)))
#   plotList.append(Plot2D('nl_nhtau',          'nl',           lambda c : c.nl,               (6, 0, 6),        'nhtau',          lambda c : c.nhtau,         (6, 0, 6)))
#   plotList.append(Plot2D('nll_nhtau',        'nll',          lambda c : c.nll,              (6, 0, 6),         'nhtau',          lambda c : c.nhtau,         (6, 0, 6)))
#   plotList.append(Plot2D('decayCateg_nhtau',        '',          lambda c : c.decayCateg,              (6, 0, 6),         'nhtau',          lambda c : c.nhtau,         (6, 0, 6), histModifications=xAxisLabels2D(['0l', '1l', '2l SS', '2l OS', '3l', '4l'])))

#   plotList.append(Plot2D('nl_nll_ynorm',          'nl',           lambda c : c.nl,               (6, 0, 6),          'nll',          lambda c : c.nll,              (6, 0, 6), histModifications=normalizeAlong('y')))
#   plotList.append(Plot2D('nl_nhtau_ynorm',          'nl',           lambda c : c.nl,               (6, 0, 6),        'nhtau',          lambda c : c.nhtau,         (6, 0, 6), histModifications=normalizeAlong('y')))
#   plotList.append(Plot2D('nll_nhtau_ynorm',        'nll',          lambda c : c.nll,              (6, 0, 6),         'nhtau',          lambda c : c.nhtau,         (6, 0, 6), histModifications=normalizeAlong('y')))
#   plotList.append(Plot2D('decayCateg_nhtau_ynorm',        '',          lambda c : c.decayCateg,              (6, 0, 6),         'nhtau',          lambda c : c.nhtau,         (6, 0, 6), histModifications=[normalizeAlong('y'), xAxisLabels2D(['0l', '1l', '2l SS', '2l OS', '3l', '4l'])]))

  plotList.append(Plot('pt_lep1',          'pt_lep1',           lambda c : c._gen_lPt[sortedLeps(c, 0)],               (30, 0, 100)))
  plotList.append(Plot('pt_lep2',          'pt_lep2',           lambda c : c._gen_lPt[sortedLeps(c, 1)],               (30, 0, 100)))
  plotList.append(Plot('pt_lep3',          'pt_lep3',           lambda c : c._gen_lPt[sortedLeps(c, 2)],               (30, 0, 100)))
  plotList.append(Plot('pt_lep4',          'pt_lep4',           lambda c : c._gen_lPt[sortedLeps(c, 3)],               (30, 0, 100)))




  # plotList.append(Plot('photon_chargedIso',          'chargedIso(#gamma) [GeV]',         lambda c : (c._phChargedIsolation[c.ph] if not c.data else c._phRandomConeChargedIsolation[c.ph]),               (20, 0, 20)))
  # plotList.append(Plot('photon_chargedIso_small',    'chargedIso(#gamma) [GeV]',         lambda c : (c._phChargedIsolation[c.ph] if not c.data else c._phRandomConeChargedIsolation[c.ph]),               (80, 0, 20)))
  # plotList.append(Plot('photon_relChargedIso',       'chargedIso(#gamma)/p_{T}(#gamma)', lambda c : (c._phChargedIsolation[c.ph] if not c.data else c._phRandomConeChargedIsolation[c.ph])/c.ph_pt, (20, 0, 2)))

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


from topSupport.tools.style import drawLumi, drawLumi2D, setDefault, ttgGeneralStyle

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

    reduceType = '4tE'
    log.info("using reduceType " + reduceType)

    # from topSupport.plots.photonCategories import checkMatch, checkSigmaIetaIeta, checkChgIso

    for sample in sum(stack, []):

      cutString, passingFunctions = cutStringAndFunctions(args.selection, args.channel)


      c = sample.initTree(reducedType = reduceType)
      c.year = sample.name[:4] if year == "comb" else year
      lumiScale = lumiScales[c.year]
      c.data = sample.isData


      for i in sample.eventLoop(cutString):
        if c.GetEntry(i) < 0:
          log.info('corrupt basket in ' + str(c.GetFile()) )

        if not c.nll == 4: continue

        # if not c.nhtau == 0: continue
        # log.info(c._gen_lPt[c.llep1])
        # log.info(c._gen_lPt[c.llep2])
        # log.info(c._gen_lPt[c.llep3])
        # log.info(c._gen_lPt[c.llep4])
        # log.info('--------------------------------')
        # if not abs(c._gen_lEta[c.llep1]) <2.4: continue
        # if not abs(c._gen_lEta[c.llep2]) <2.4: continue
        # if not abs(c._gen_lEta[c.llep3]) <2.4: continue
        # if not abs(c._gen_lEta[c.llep4]) <2.4: continue

        # if not c._gen_lPassParentage[c.llep1]: continue
        # if not c._gen_lPassParentage[c.llep2]: continue
        # if not c._gen_lPassParentage[c.llep3]: continue
        # if not c._gen_lPassParentage[c.llep4]: continue



        if not passingFunctions(c): continue

        
        if noWeight:    eventWeight = 1.
        else:             eventWeight = c.genWeight*lumiScale

        # else:             eventWeight = 1.


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
      normalizeToMC = [False, True] if (args.channel != 'noData' and not onlyMC) else [False]
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
                    drawObjects       = drawLumi(None, lumiScalesRounded[year], isOnlySim=(args.channel=='noData' or onlyMC)),
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
      for logY in [False, True]:
        for option in ['SCAT', 'COLZ', 'COLZ TEXT']:
          plot.draw(plot_directory = os.path.join(plotDir, year, args.tag, args.channel + ('-log' if logY else ''), args.selection, option),
                    logZ           = False,
                    drawOption     = option,
                    drawObjects    = drawLumi2D(None, lumiScalesRounded[year], isOnlySim=(args.channel=='noData' or onlyMC)))
                    
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
    normalizeToMC = [False, True] if (args.channel != 'noData' and not onlyMC) else [False]
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
