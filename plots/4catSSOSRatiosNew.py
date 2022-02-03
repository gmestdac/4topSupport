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
'TT-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/hpe-onlyTTpile-norat/ee/nLep2-lepsPrompt-SIGN-REG/',
'TT-onZ-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/hpe-onlyTTpile-norat/ee/onZ-nLep2-lepsPrompt-SIGN-REG/',
'DY-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/hpe-onlyDYpile-norat/ee/nLep2-lepsPrompt-SIGN-REG/',
'DY-onZ-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/hpe-onlyDYpile-norat/ee/onZ-nLep2-lepsPrompt-SIGN-REG/',
  }

# nLep2-lepsPrompt-SS-EE
# onZ-nLep2-lepsPrompt-OS-BE


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

ratioDict = {}

for year in ['2016', '2017', '2018']:
  for var in ['TT-Prompt', 'TT-onZ-Prompt', 'DY-Prompt', 'DY-onZ-Prompt']:
    for plot in ['pt2D_HA']:
      for region in ['BB', 'EE', 'BE', 'EB']:
        try:
          print 'running for ' + year + ' ' + plot
          canv = ROOT.TCanvas(year + plot, '', 1200, 1100)
          # statCovCanv.SetLogz(True)
          canv.SetRightMargin(0.19)
          canv.SetLeftMargin(0.12)
          canv.SetTopMargin(0.07)
          canv.SetBottomMargin(0.11)


          # NOTE WARNING summing all non-data for MC, so if you want e.g. DY only plot only that or adjust here
          ssPath= paths[var].replace('2017', year).replace('SIGN', 'SS').replace('REG', region)
          osPath= paths[var].replace('2017', year).replace('SIGN', 'OS').replace('REG', region)
          ss = sumHists(pickle.load(open(ssPath + plot + '.pkl', 'r'))[plot], ['data'] if var.lower().count('data') else [] , ['data'] if not var.lower().count('data') else [])
          os = sumHists(pickle.load(open(osPath + plot + '.pkl', 'r'))[plot], ['data'] if var.lower().count('data') else [] , ['data'] if not var.lower().count('data') else [])

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

          ratio = ss.Clone()
          ratio.Divide(os)

          ratioDict[plot+year+var+region] = ratio.Clone()

          print plot+year+var+region
          print ss.Integral()/os.Integral()
          del canv
        except: print 'incomplete input for ' + plot+year+var+region 
        

def printvals(h1, h2, h3, h4):
  valstring = ''
  errstring = ''
  for h in [h1, h2, h3, h4]:
    valstring += (str( round(1000. * h.GetBinContent(1,1), 3))+'000')[:5] + ' & ' 
    errstring += (str( round(1000. * h.GetBinError(1,1), 3))+'000')[:5] + ' & '
    valstring += (str( round(1000. * h.GetBinContent(2,2), 3))+'000')[:5] + ' & ' 
    errstring += (str( round(1000. * h.GetBinError(2,2), 3))+'000')[:5] + ' & '
    valstring += (str( round(1000. * h.GetBinContent(1,2), 3))+'000')[:5] + ' & ' 
    errstring += (str( round(1000. * h.GetBinError(1,2), 3))+'000')[:5] + ' & '
    valstring += (str( round(1000. * h.GetBinContent(2,1), 3))+'000')[:5] + ' & '
    errstring += (str( round(1000. * h.GetBinError(2,1), 3))+'000')[:5] + ' & '
  return (valstring[:-3], errstring[:-3])

def printvalsErrs(h1, h2, h3, h4):
  valstring = ''
  for h in [h1, h2, h3, h4]:
    valstring += (str( round(1000. * h.GetBinContent(1,1), 2))+'000')[:4] + '+-' 
    valstring += (str( round(1000. * h.GetBinError(1,1), 2))+'000')[:4] + ' & '
    valstring += (str( round(1000. * h.GetBinContent(2,2), 2))+'000')[:4] + '+-' 
    valstring += (str( round(1000. * h.GetBinError(2,2), 2))+'000')[:4] + ' & '
    valstring += (str( round(1000. * h.GetBinContent(1,2), 2))+'000')[:4] + '+-' 
    valstring += (str( round(1000. * h.GetBinError(1,2), 2))+'000')[:4] + ' & '
    valstring += (str( round(1000. * h.GetBinContent(2,1), 2))+'000')[:4] + '+-'
    valstring += (str( round(1000. * h.GetBinError(2,1), 2))+'000')[:4] + ' & '
  return valstring[:-3]

def printvalsErrsPercentage(h1, h2, h3, h4):
  valstring = ''
  for h in [h1, h2, h3, h4]:
    valstring += (str( round(100. * h.GetBinContent(1,1), 0))+'000')[:2] + '+-' 
    valstring += (str( round(100. * h.GetBinError(1,1), 0))+'000')[:2] + ' & '
    valstring += (str( round(100. * h.GetBinContent(2,2), 0))+'000')[:2] + '+-' 
    valstring += (str( round(100. * h.GetBinError(2,2), 0))+'000')[:2] + ' & '
    valstring += (str( round(100. * h.GetBinContent(1,2), 0))+'000')[:2] + '+-' 
    valstring += (str( round(100. * h.GetBinError(1,2), 0))+'000')[:2] + ' & '
    valstring += (str( round(100. * h.GetBinContent(2,1), 0))+'000')[:2] + '+-'
    valstring += (str( round(100. * h.GetBinError(2,1), 0))+'000')[:2] + ' & '
  return valstring[:-3]

# for year in ['2016', '2017', '2018']:
for year in [ '2017', '2018']:
  print year
  print 'BB LL' + ' & ' + 'BB HH' + ' & ' + 'BB LH' + ' & ' + 'BB HL' + ' & ' + 'EE LL' + ' & ' + 'EE LH' + ' & ' + 'EE HL' + ' & ' + 'EE HH' + ' & ' + 'BE LL' + ' & ' + 'BE LH' + ' & ' + 'BE HL' + ' & ' + 'BE HH' + ' & ' + 'EB LL' + ' & ' + 'EB LH' + ' & ' + 'EB HL' + ' & ' + 'EB HH'
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EB'])
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'EB'])
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EB'])
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'EB'])

# NOTE all multiplied by 10^3