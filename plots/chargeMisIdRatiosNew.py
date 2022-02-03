import os
from topSupport.tools.logger import getLogger
from topSupport.tools.style import drawTex
log = getLogger()
import pickle
import ROOT
from array import array
ROOT.TH2.SetDefaultSumw2()
ROOT.TH1.SetDefaultSumw2()

import pdb


ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetPaintTextFormat("3.2f")


# Not the same as in other code, doesn't start at pure white
# red = array('d', [0.93,0.302])
# green = array('d', [0.974,0.745])
# blue = array('d', [0.99,0.933])
# stops = array('d', [0.0,1.0])
# ROOT.TColor.CreateGradientColorTable(2,stops,red,green,blue,25)


# l1RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/new-onlyPROC-norat/ee/SEL-l1Right/'
# l1WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/new-onlyPROC-norat/ee/SEL-l1Wrong/'
# l2RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/new-onlyPROC-norat/ee/SEL-l2Right/'
# l2WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/new-onlyPROC-norat/ee/SEL-l2Wrong/'

l1RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat/ee/SEL-l1NCF/'
l1WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat/ee/SEL-l1CF/'
l2RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat/ee/SEL-l2NCF/'
l2WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/hpe-onlyPROC-norat/ee/SEL-l2CF/'



labels = {
          'eta2D' :         ('#eta A',   '#eta B'  ),
          'pt2D' :          ('p_{T} A',  'p_{T} B' ),
          'ptEtaTTbinning': ('p_{T}',    '#eta'    ),
          'ptEtaNEWbinning': ('p_{T}',    '#eta'    )
          }

scaling = 5

def sumHists(dict, sumkeys = [], antiSumKeys = []):
  sumHist = None
  for name, hist in dict.iteritems():
    if (any((name.count(key) for key in sumkeys)) or not sumkeys) and (not any((name.count(key) for key in antiSumKeys)) or not antiSumKeys):
      if not sumHist: sumHist = hist.Clone()
      else: sumHist.Add(hist)
  return sumHist


############# truth based charge misID ratios





for year in ['2016', '2017' , '2018']:
  # for plot in ['ptEtaTTbinning']:
  for plot in ['ptEtaTTbinning', 'ptEtaNEWbinning']:
  # for plot in ['ptEtaNEWbinning']:
    # for proc in ['DY', 'TT']:
    # for proc in ['DY', 'TT', 'DYWZ']:
    # for proc in ['onlyDYmix', 'onlyDYMLM', 'onlyDYOLD', 'onlyDYpile']:
    # for proc in ['DYmix', 'DYMLM', 'DYpile', 'DYOLD', 'TTpile'] + ([i + p for i in ['DYmix', 'DYMLM', 'DYpile'] for p in ['Pre', 'Post']] if year == '2016' else []):
    for proc in ['DYpile', 'DYOLD', 'TTpile'] + ([i + p for i in ['DYpile'] for p in ['Pre', 'Post']] if year == '2016' else []):
    # for proc in ['DYmix', 'DYMLM', 'TT']:
    # for proc in ['DYMLM', 'TT']:
    # for proc in ['TT', 'D']:
      # for sel in ['onZ-nLep2-lepsPrompt', 'onZ-nLep2', 'nLep2-lepsPrompt', 'nLep2']:
      for sel in ['nLep2-lepsPrompt', 'onZ-nLep2-lepsPrompt']:
        try:
          log.info('plotting for ' + year + ' ' + plot)
          canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
          canv.SetLogx(True)

          
          # statCovCanv.SetLogz(True)
          canv.SetRightMargin(0.19)
          canv.SetLeftMargin(0.12)
          canv.SetTopMargin(0.07)
          canv.SetBottomMargin(0.11)

          l1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year).replace('PROC', proc).replace('SEL', sel) + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
          l1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year).replace('PROC', proc).replace('SEL', sel) + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
          l2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year).replace('PROC', proc).replace('SEL', sel) + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
          l2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year).replace('PROC', proc).replace('SEL', sel) + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])

          # pdb.set_trace()

          l1W.Add(l2W)
          l1R.Add(l2R)

          nx = l1W.GetXaxis().GetNbins()
          ny = l1W.GetYaxis().GetNbins()

          for hist in [l1W, l1R]:
            for i in range(1, nx+1):
              hist.SetBinContent(i, ny, hist.GetBinContent(i, ny) + hist.GetBinContent(i, ny+1))
              hist.SetBinError(i, ny, (hist.GetBinError(i, ny)**2. + hist.GetBinError(i, ny+1)**2.)**0.5)
              hist.SetBinContent(i, ny+1, 0.)
              hist.SetBinError(i, ny+1, 0.)
            for i in range(1, ny+1):
              hist.SetBinContent(nx, i, hist.GetBinContent(nx, i) + hist.GetBinContent(nx+1, i))
              hist.SetBinError(nx, i, (hist.GetBinError(nx, i)**2. + hist.GetBinError(nx+1, i)**2.)**0.5)
              hist.SetBinContent(nx+1, i, 0.)
              hist.SetBinError(nx+1, i, 0.)
            
            hist.SetBinContent(nx, ny, hist.GetBinContent(nx, ny) + hist.GetBinContent(nx+1, ny+1))
            hist.SetBinError(nx, ny, (hist.GetBinError(nx, ny)**2. + hist.GetBinError(nx+1, ny+1)**2.)**0.5)
            hist.SetBinContent(nx+1, ny+1, 0.)
            hist.SetBinError(nx+1, ny+1, 0.)



          ratio = l1W.Clone('chamidRate' + year)

          log.info('integral ratio for ' + year + '_' + proc + '_' + sel + '_' + plot + ':')
          log.info(l1W.Integral()/l1R.Integral())

          # continue

          ratio.Divide(l1R)

          ratio.SaveAs('chamidRat/chamid_' + year + '_' + proc + '_' + sel + '_' + plot + '.root')
          

          pickle.dump(ratio, file('chamidRat/chamid_' + year + '_' + proc + '_' + sel + '_' + plot + '.pkl', 'w'))
          
          ratio.Scale(10.**scaling)


          ratio.SetTitle('')
          ratio.SetMarkerSize(1.2)
          ratio.GetXaxis().SetTitle(labels[plot][0])
          ratio.GetYaxis().SetTitle(labels[plot][1])
          ratio.GetZaxis().SetTitle("Ratio")
          ratio.GetYaxis().SetTitleOffset(1.3)
          ratio.GetXaxis().SetTitleOffset(1.1)
          ratio.GetZaxis().SetTitleOffset(1.1)
          ratio.GetXaxis().SetTitleSize(0.045)
          ratio.GetYaxis().SetTitleSize(0.045)
          ratio.GetZaxis().SetTitleSize(0.045)
          ratio.GetXaxis().SetLabelSize(0.04)
          ratio.GetYaxis().SetLabelSize(0.04)    
          ratio.GetZaxis().SetLabelSize(0.04)
          ratio.GetZaxis().SetRangeUser(-0.0002*10.**scaling, 0.0105*10.**scaling)
          # ratio.GetXaxis().SetTickLength(0)
          # ratio.GetYaxis().SetTickLength(0)
          # ratio.LabelsOption('v','x')
          
          # pdb.set_trace()
          
          ratio.Draw('COLZ text error')

          drawTex((1-ROOT.gStyle.GetPadRightMargin()-0.02,  1-ROOT.gStyle.GetPadTopMargin()+0.034, '#times10^{#minus' + str(scaling) + '}'), 11,  size=0.05)

          canv.SaveAs('chamidRat/chamid_' + year + '_' + proc + '_' + sel + '_' + plot + '.pdf')
          canv.SaveAs('chamidRat/chamid_' + year + '_' + proc + '_' + sel + '_' + plot + '.png')
        except Exception as e:
          log.info('NOT MADE')
          log.info(e)