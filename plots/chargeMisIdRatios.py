import os
from ttg.tools.logger import getLogger
from ttg.tools.style import drawTex
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
red = array('d', [0.93,0.302])
green = array('d', [0.974,0.745])
blue = array('d', [0.99,0.933])
stops = array('d', [0.0,1.0])
ROOT.TColor.CreateGradientColorTable(2,stops,red,green,blue,25)


# ssPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2016/chamidPostTestB-noTightCharge/noData/onZ-SS/'
# osPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2016/chamidPostTestB-noTightCharge/noData/onZ-OS/'

ssPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2016/chamidPostTestB/noData/onZ-SS/'
osPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2016/chamidPostTestB/noData/onZ-OS/'

labels = {
          'eta2D' :            ('#eta A',       '#eta B'            ),
          'pt2D' :            ('p_{T} A',       'p_{T} B'            ),
          }

scaling = 3


for year in ['2016']:
  for plot in ['eta2D', 'pt2D']:
    log.info('plotting for ' + year + ' ' + plot)
    canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
    # statCovCanv.SetLogz(True)
    canv.SetRightMargin(0.17)
    canv.SetLeftMargin(0.12)
    canv.SetTopMargin(0.07)
    canv.SetBottomMargin(0.11)


    # TODO ############### WARNING #############
    # TODO if there's multiple processes we need some summing code here
    ss = pickle.load(open(ssPath + plot + '.pkl', 'r'))[plot].values()[0]
    os = pickle.load(open(osPath + plot + '.pkl', 'r'))[plot].values()[0]

    # pdb.set_trace()

    ratio = ss.Clone()
    ratio.Divide(os)

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
    ratio.GetXaxis().SetTickLength(0)
    ratio.GetYaxis().SetTickLength(0)
    # ratio.LabelsOption('v','x')
    
    # pdb.set_trace()
    
    ratio.Draw('COLZ text error')

    drawTex((1-ROOT.gStyle.GetPadRightMargin()-0.02,  1-ROOT.gStyle.GetPadTopMargin()+0.034, '#times10^{#minus' + str(scaling) + '}'), 11,  size=0.05)

    canv.SaveAs('chargeMisIdRatios/ratio' + year + plot + '.pdf')
    canv.SaveAs('chargeMisIdRatios/ratio' + year + plot + '.png')

    # sftp://gmestdac@m6.iihe.ac.be/storage_mnt/storage/user/gmestdac/TTTT/CMSSW_10_2_10/src/ttg/plots/chargeMisIdRatios