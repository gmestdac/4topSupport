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
red = array('d', [0.93,0.302])
green = array('d', [0.974,0.745])
blue = array('d', [0.99,0.933])
stops = array('d', [0.0,1.0])
ROOT.TColor.CreateGradientColorTable(2,stops,red,green,blue,25)


# ssPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2016/chamidPostTestB-noTightCharge/noData/onZ-SS/'
# osPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2016/chamidPostTestB-noTightCharge/noData/onZ-OS/'



ssPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/A-chamid/ee/onZ-nLep2-SS/'
osPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/A-chamid/ee/onZ-nLep2-OS/'

l1RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/Dcha-onlyDY-norat/ee/onZ-nLep2-lepsPrompt-l1Right/'
l1WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/Dcha-onlyDY-norat/ee/onZ-nLep2-lepsPrompt-l1Wrong/'
l2RPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/Dcha-onlyDY-norat/ee/onZ-nLep2-lepsPrompt-l2Right/'
l2WPath = '/storage_mnt/storage/user/gmestdac/public_html/TTTT/YEAR/Dcha-onlyDY-norat/ee/onZ-nLep2-lepsPrompt-l2Wrong/'

labels = {
          'eta2D' :         ('#eta A',   '#eta B'  ),
          'pt2D' :          ('p_{T} A',  'p_{T} B' ),
          'ptEtaTTbinning': ('p_{T}',    '#eta'    )
          }

scaling = 5

def sumHists(dict, sumkeys = [], antiSumKeys = []):
  sumHist = None
  for name, hist in dict.iteritems():
    if (any((name.count(key) for key in sumkeys)) or not sumkeys) and (not any((name.count(key) for key in antiSumKeys)) or not antiSumKeys):
      if not sumHist: sumHist = hist.Clone()
      else: sumHist.Add(hist)
  return sumHist



# # THIS PART JUST TAKES THE SS/OS RATIO
# for year in ['2017' , '2018']:
#   for plot in ['eta2D', 'pt2D']:
#     for data in [False, True]:
#       log.info('plotting for ' + year + ' ' + plot)
#       canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
#       # statCovCanv.SetLogz(True)
#       canv.SetRightMargin(0.19)
#       canv.SetLeftMargin(0.12)
#       canv.SetTopMargin(0.07)
#       canv.SetBottomMargin(0.11)


#       if data:
#         ss = sumHists(pickle.load(open(ssPath.replace('YEAR', year) + plot + '.pkl', 'r'))[plot], ['data'] , [])
#         os = sumHists(pickle.load(open(osPath.replace('YEAR', year) + plot + '.pkl', 'r'))[plot], ['data'] , [])
#       else:
#         ss = sumHists(pickle.load(open(ssPath.replace('YEAR', year) + plot + '.pkl', 'r'))[plot], [] , ['data'])
#         os = sumHists(pickle.load(open(osPath.replace('YEAR', year) + plot + '.pkl', 'r'))[plot], [] , ['data'])

#       # pdb.set_trace()

#       ratio = ss.Clone()
#       ratio.Divide(os)

#       ratio.Scale(10.**scaling)

#       ratio.SetTitle('')
#       ratio.GetXaxis().SetTitle(labels[plot][0])
#       ratio.GetYaxis().SetTitle(labels[plot][1])
#       ratio.GetZaxis().SetTitle("Ratio")
#       ratio.GetYaxis().SetTitleOffset(1.3)
#       ratio.GetXaxis().SetTitleOffset(1.1)
#       ratio.GetZaxis().SetTitleOffset(1.1)
#       ratio.GetXaxis().SetTitleSize(0.045)
#       ratio.GetYaxis().SetTitleSize(0.045)
#       ratio.GetZaxis().SetTitleSize(0.045)
#       ratio.GetXaxis().SetLabelSize(0.04)
#       ratio.GetYaxis().SetLabelSize(0.04)
#       ratio.GetZaxis().SetLabelSize(0.04)
#       ratio.GetXaxis().SetTickLength(0)
#       ratio.GetYaxis().SetTickLength(0)
#       # ratio.LabelsOption('v','x')
      
#       # pdb.set_trace()
      
#       ratio.Draw('COLZ text error')

#       drawTex((1-ROOT.gStyle.GetPadRightMargin()-0.02,  1-ROOT.gStyle.GetPadTopMargin()+0.034, '#times10^{#minus' + str(scaling) + '}'), 11,  size=0.05)

#       canv.SaveAs('chargeMisIdRatios/ratio' + year + plot + ('data' if data else 'MC') +'.pdf')
#       canv.SaveAs('chargeMisIdRatios/ratio' + year + plot + ('data' if data else 'MC') +'.png')






############# truth based charge misID ratios

# for year in ['2016', '2016Pre', '2016Post', '2017' , '2018']:
for year in ['2016', '2017' , '2018']:
# for year in ['2016']:
  for plot in ['ptEtaTTbinning']:
    log.info('plotting for ' + year + ' ' + plot)
    canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
    canv.SetLogx(True)

    
    # statCovCanv.SetLogz(True)
    canv.SetRightMargin(0.19)
    canv.SetLeftMargin(0.12)
    canv.SetTopMargin(0.07)
    canv.SetBottomMargin(0.11)

    if year.count('2016'):
      if year.count('Pre'):
        l1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
        l1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
        l2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
        l2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
      elif year.count('Post'):
        l1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
        l1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
        l2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
        l2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
      else:
        l1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
        l1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
        l2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
        l2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPre') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
        l1R.Add(sumHists(pickle.load(open(l1RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data']))
        l1W.Add(sumHists(pickle.load(open(l1WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data']))
        l2R.Add(sumHists(pickle.load(open(l2RPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data']))
        l2W.Add(sumHists(pickle.load(open(l2WPath.replace('YEAR', year[:4]).replace('chamid', 'chamidPost') + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data']))
    else:
      l1R = sumHists(pickle.load(open(l1RPath.replace('YEAR', year) + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
      l1W = sumHists(pickle.load(open(l1WPath.replace('YEAR', year) + plot + '_l1.pkl', 'r'))[plot + '_l1'], [] , ['data'])
      l2R = sumHists(pickle.load(open(l2RPath.replace('YEAR', year) + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])
      l2W = sumHists(pickle.load(open(l2WPath.replace('YEAR', year) + plot + '_l2.pkl', 'r'))[plot + '_l2'], [] , ['data'])



    l1W.Add(l2W)
    l1R.Add(l2R)

    ratio = l1W.Clone()
    ratio.Divide(l1R)

    pickle.dump(ratio, file('chargeMisIdRatios/chamid' + year + plot + '.pkl', 'w'))
    
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
    # ratio.GetXaxis().SetTickLength(0)
    # ratio.GetYaxis().SetTickLength(0)
    # ratio.LabelsOption('v','x')
    
    # pdb.set_trace()
    
    ratio.Draw('COLZ text error')

    drawTex((1-ROOT.gStyle.GetPadRightMargin()-0.02,  1-ROOT.gStyle.GetPadTopMargin()+0.034, '#times10^{#minus' + str(scaling) + '}'), 11,  size=0.05)

    canv.SaveAs('chargeMisIdRatios/chamid' + year + plot + '.pdf')
    canv.SaveAs('chargeMisIdRatios/chamid' + year + plot + '.png')
