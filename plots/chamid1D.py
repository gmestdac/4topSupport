#
# nonprompt photon background estimation weights
#

import os
from topSupport.tools.helpers import getObjFromFile, multiply
from topSupport.tools.uncFloat import UncFloat
from topSupport.tools.logger import getLogger
import pickle
import time
import ROOT
import pdb
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadRightMargin(0.12)

ROOT.TH1.SetDefaultSumw2()
ROOT.TH2.SetDefaultSumw2()

log = getLogger()

def sumHists(dict, sumkeys = [], antiSumKeys = []):
  sumHist = None
  for name, hist in dict.iteritems():
    if (any((name.count(key) for key in sumkeys)) or not sumkeys) and (not any((name.count(key) for key in antiSumKeys)) or not antiSumKeys):
      if not sumHist: sumHist = hist.Clone()
      else: sumHist.Add(hist)
  return sumHist


labels = {
          'LEP_eta_NEW' :         '#eta'  ,
          'LEP_pt_NEW' :          'p_{T}' ,
          }

l1RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat-FINAL/ee/SEL-l1NCF/'
l1WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat-FINAL/ee/SEL-l1CF/'
l2RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat-FINAL/ee/SEL-l2NCF/'
l2WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat-FINAL/ee/SEL-l2CF/'


# l1 en l2 moeten zelfde binning hebben

for year in ['2016', '2017' , '2018']:
  for plot in ['LEP_pt_NEW', 'LEP_eta_NEW']:
    for sel in ['nLep2-lepsPrompt']:
    # for sel in ['onZ-nLep2-lepsPrompt']:
      log.info('plotting for ' + year + ' ' + plot)
      canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
      
      # canv.SetRightMargin(0.19)
      canv.SetLeftMargin(0.15)
      # canv.SetTopMargin(0.07)
      canv.SetBottomMargin(0.15)

      DYl1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year).replace('PROC', 'DYpile').replace('SEL', sel) + plot.replace('LEP', 'l1') + '.pkl', 'r'))[plot.replace('LEP', 'l1')], [] , ['data'])
      DYl1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year).replace('PROC', 'DYpile').replace('SEL', sel) + plot.replace('LEP', 'l1') + '.pkl', 'r'))[plot.replace('LEP', 'l1')], [] , ['data'])
      DYl2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year).replace('PROC', 'DYpile').replace('SEL', sel) + plot.replace('LEP', 'l2') + '.pkl', 'r'))[plot.replace('LEP', 'l2')], [] , ['data'])
      DYl2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year).replace('PROC', 'DYpile').replace('SEL', sel) + plot.replace('LEP', 'l2') + '.pkl', 'r'))[plot.replace('LEP', 'l2')], [] , ['data'])

      TTl1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year).replace('PROC', 'TTpile').replace('SEL', sel) + plot.replace('LEP', 'l1') + '.pkl', 'r'))[plot.replace('LEP', 'l1')], [] , ['data'])
      TTl1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year).replace('PROC', 'TTpile').replace('SEL', sel) + plot.replace('LEP', 'l1') + '.pkl', 'r'))[plot.replace('LEP', 'l1')], [] , ['data'])
      TTl2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year).replace('PROC', 'TTpile').replace('SEL', sel) + plot.replace('LEP', 'l2') + '.pkl', 'r'))[plot.replace('LEP', 'l2')], [] , ['data'])
      TTl2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year).replace('PROC', 'TTpile').replace('SEL', sel) + plot.replace('LEP', 'l2') + '.pkl', 'r'))[plot.replace('LEP', 'l2')], [] , ['data'])



      DYl1W.Add(DYl2W)
      DYl1R.Add(DYl2R)
      TTl1W.Add(TTl2W)
      TTl1R.Add(TTl2R)

      nx = DYl1W.GetXaxis().GetNbins()

      DYl1W.SetBinContent(nx, DYl1W.GetBinContent(nx) + DYl1W.GetBinContent(nx+1))
      DYl1W.SetBinError(nx, (DYl1W.GetBinError(nx)**2. + DYl1W.GetBinError(nx+1)**2.)**0.5)
      DYl1W.SetBinContent(nx+1, 0.)
      DYl1W.SetBinError(nx+1, 0.)

      DYl1R.SetBinContent(nx, DYl1R.GetBinContent(nx) + DYl1R.GetBinContent(nx+1))
      DYl1R.SetBinError(nx, (DYl1R.GetBinError(nx)**2. + DYl1R.GetBinError(nx+1)**2.)**0.5)
      DYl1R.SetBinContent(nx+1, 0.)
      DYl1R.SetBinError(nx+1, 0.)

      TTl1W.SetBinContent(nx, TTl1W.GetBinContent(nx) + TTl1W.GetBinContent(nx+1))
      TTl1W.SetBinError(nx, (TTl1W.GetBinError(nx)**2. + TTl1W.GetBinError(nx+1)**2.)**0.5)
      TTl1W.SetBinContent(nx+1, 0.)
      TTl1W.SetBinError(nx+1, 0.)

      TTl1R.SetBinContent(nx, TTl1R.GetBinContent(nx) + TTl1R.GetBinContent(nx+1))
      TTl1R.SetBinError(nx, (TTl1R.GetBinError(nx)**2. + TTl1R.GetBinError(nx+1)**2.)**0.5)
      TTl1R.SetBinContent(nx+1, 0.)
      TTl1R.SetBinError(nx+1, 0.)


      DYa = DYl1W.Integral()
      DYb = DYl1R.Integral()
      TTa = TTl1W.Integral()
      TTb = TTl1R.Integral()

      log.info(DYa/DYb)
      log.info(TTa/TTb)

      DYratio = DYl1W.Clone()
      DYratio.Divide(DYl1R)
      TTratio = TTl1W.Clone()
      TTratio.Divide(TTl1R)

      DYratio.GetYaxis().SetRangeUser(0.00001, 0.006)
      TTratio.SetLineColor(ROOT.kRed)
      DYratio.SetTitle('')

      # pdb.set_trace()

      DYratio.Draw('E1')
      TTratio.Draw('E1 same')
      canv.SetLogy(True)

      DYratio.GetXaxis().SetTitle(labels[plot])
      DYratio.GetYaxis().SetTitle('charge misID rate')
      DYratio.GetXaxis().SetTitleOffset(1.2)
      DYratio.GetYaxis().SetTitleOffset(1.4)

      legend = ROOT.TLegend(0.25,0.91,0.87,0.98)
      legend.AddEntry(DYratio,"DY","L")
      legend.AddEntry(TTratio,"TT","L")
      legend.SetBorderSize(0)
      legend.SetNColumns(2)
      legend.Draw()

      canv.SaveAs('chamid1Dplots/' + year + plot + sel + '.pdf')
      canv.SaveAs('chamid1Dplots/' + year + plot + sel + '.png')
