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
ROOT.gStyle.SetPaintTextFormat("3.3f")


# Not the same as in other code, doesn't start at pure white
red = array('d', [0.93,0.302])
green = array('d', [0.974,0.745])
blue = array('d', [0.99,0.933])
stops = array('d', [0.0,1.0])
ROOT.TColor.CreateGradientColorTable(2,stops,red,green,blue,25)


paths = {
  'MC-OS-BB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-OS-BB/',
  'MC-OS-BE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-OS-BE/',
  'MC-OS-EB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-OS-EB/',
  'MC-OS-EE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-OS-EE/',
  'MC-SS-BB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-SS-BB/',
  'MC-SS-BE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-SS-BE/',
  'MC-SS-EB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-SS-EB/',
  'MC-SS-EE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyDY-norat/ee/onZ-nLep2-SS-EE/',
  'Da-OS-BB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-OS-BB/',
  'Da-OS-BE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-OS-BE/',
  'Da-OS-EB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-OS-EB/',
  'Da-OS-EE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-OS-EE/',
  'Da-SS-BB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-SS-BB/',
  'Da-SS-BE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-SS-BE/',
  'Da-SS-EB' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-SS-EB/',
  'Da-SS-EE' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/onlyData-norat/ee/onZ-nLep2-SS-EE/',
  }

labels = {
          'pt2D_HA' :          ('p_{T}(l_{1})',  'p_{T}(l_{2})'),
          }

scaling = 2

def sumHists(dict, sumkeys = [], antiSumKeys = []):
  sumHist = None
  for name, hist in dict.iteritems():
    if (any((name.count(key) for key in sumkeys)) or not sumkeys) and (not any((name.count(key) for key in antiSumKeys)) or not antiSumKeys):
      if not sumHist: sumHist = hist.Clone()
      else: sumHist.Add(hist)
  return sumHist



# THIS PART JUST TAKES THE SS/OS RATIO
# for year in ['2016', '2017' , '2018']:
for year in ['2017']:
  for plot in ['pt2D_HA']:
    for region in ['EE', 'BE', 'EB', 'BB']:
      for data in [False, True]:
        log.info('plotting for ' + year + ' ' + plot)
        canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
        # statCovCanv.SetLogz(True)
        canv.SetRightMargin(0.19)
        canv.SetLeftMargin(0.12)
        canv.SetTopMargin(0.07)
        canv.SetBottomMargin(0.11)


        # NOTE WARNING summing all non-data for MC, so if you want e.g. DY only plot only that or adjust here
        ss = sumHists(pickle.load(open(paths[('Da' if data else 'MC') + '-SS-' + region].replace('YEAR', year) + plot + '.pkl', 'r'))[plot], ['data'] if data else [] , ['data'] if not data else [])
        os = sumHists(pickle.load(open(paths[('Da' if data else 'MC') + '-OS-' + region].replace('YEAR', year) + plot + '.pkl', 'r'))[plot], ['data'] if data else [] , ['data'] if not data else [])

        nx = ss.GetXaxis().GetNbins()
        ny = ss.GetYaxis().GetNbins()

        for i in range(1, nx+1):
          ss.SetBinContent(i, ny, ss.GetBinContent(i, ny) + ss.GetBinContent(i, ny+1))
          ss.SetBinError(i, ny, (ss.GetBinError(i, ny)**2. + ss.GetBinError(i, ny+1)**2.)**0.5)
          ss.SetBinContent(i, ny+1, 0.)
          ss.SetBinError(i, ny+1, 0.)
        for i in range(1, ny+1):
          ss.SetBinContent(nx, i, ss.GetBinContent(nx, i) + ss.GetBinContent(nx+1, i))
          ss.SetBinError(nx, i, (ss.GetBinError(nx, i)**2. + ss.GetBinError(nx+1, i)**2.)**0.5)
          ss.SetBinContent(nx+1, i, 0.)
          ss.SetBinError(nx+1, i, 0.)
        
        ss.SetBinContent(nx, ny, ss.GetBinContent(nx, ny) + ss.GetBinContent(nx+1, ny+1))
        ss.SetBinError(nx, ny, (ss.GetBinError(nx, ny)**2. + ss.GetBinError(nx+1, ny+1)**2.)**0.5)
        ss.SetBinContent(nx+1, ny+1, 0.)
        ss.SetBinError(nx+1, ny+1, 0.)

        for i in range(1, nx+1):
          os.SetBinContent(i, ny, os.GetBinContent(i, ny) + os.GetBinContent(i, ny+1))
          os.SetBinError(i, ny, (os.GetBinError(i, ny)**2. + os.GetBinError(i, ny+1)**2.)**0.5)
          os.SetBinContent(i, ny+1, 0.)
          os.SetBinError(i, ny+1, 0.)
        for i in range(1, ny+1):
          os.SetBinContent(nx, i, os.GetBinContent(nx, i) + os.GetBinContent(nx+1, i))
          os.SetBinError(nx, i, (os.GetBinError(nx, i)**2. + os.GetBinError(nx+1, i)**2.)**0.5)
          os.SetBinContent(nx+1, i, 0.)
          os.SetBinError(nx+1, i, 0.)
        
        os.SetBinContent(nx, ny, os.GetBinContent(nx, ny) + os.GetBinContent(nx+1, ny+1))
        os.SetBinError(nx, ny, (os.GetBinError(nx, ny)**2. + os.GetBinError(nx+1, ny+1)**2.)**0.5)
        os.SetBinContent(nx+1, ny+1, 0.)
        os.SetBinError(nx+1, ny+1, 0.)
# TODO add overflows   ALSO FOR OS3

        # pdb.set_trace()

        ratio = ss.Clone()
        ratio.Divide(os)


        pickle.dump(ratio, file('chargeMisIdRatios/SSoOS_' + year + plot + '_' + region + '_' + ('data' if data else 'MC') + '.pkl', 'w'))

        ratio.Scale(10.**scaling)

        ratio.SetTitle('')
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
        ratio.GetXaxis().SetTickLength(0)
        ratio.GetYaxis().SetTickLength(0)
        # ratio.LabelsOption('v','x')
        
        # pdb.set_trace()
        
        ratio.Draw('COLZ text error')

        drawTex((1-ROOT.gStyle.GetPadRightMargin()-0.02,  1-ROOT.gStyle.GetPadTopMargin()+0.034, '#times10^{#minus' + str(scaling) + '}'), 11,  size=0.05)

        canv.SaveAs('chargeMisIdRatios/SSoOS_' + year + plot + '_' + region + '_' + ('data' if data else 'MC') +'.pdf')
        canv.SaveAs('chargeMisIdRatios/SSoOS_' + year + plot + '_' + region + '_' + ('data' if data else 'MC') +'.png')




