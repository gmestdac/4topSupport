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
'TT-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyTT-norat/ee/nLep2-lepsPrompt-SIGN-REG/',
'TT' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyTT-norat/ee/nLep2-SIGN-REG/',
'TT-onZ-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyTT-norat/ee/onZ-nLep2-lepsPrompt-SIGN-REG/',
'TT-onZ' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyTT-norat/ee/onZ-nLep2-SIGN-REG/',
'DY-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyDY-norat/ee/nLep2-lepsPrompt-SIGN-REG/',
'DY' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyDY-norat/ee/nLep2-SIGN-REG/',
'DY-onZ-Prompt' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyDY-norat/ee/onZ-nLep2-lepsPrompt-SIGN-REG/',
'DY-onZ' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyDY-norat/ee/onZ-nLep2-SIGN-REG/',
'Data' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyData-norat/ee/nLep2-SIGN-REG/',
'Data-onZ' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/C-onlyData-norat/ee/onZ-nLep2-SIGN-REG/',
'DYPNP' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/onlyDYPNP-norat/ee/nLep2-REG-SIGN/',
'DY-onZPNP' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/onlyDYPNP-norat/ee/nLep2-onZ-REG-SIGN/',
'TTPNP' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/onlyTTPNP-norat/ee/nLep2-REG-SIGN/',
'TT-onZPNP' : '/storage_mnt/storage/user/gmestdac/public_html/TTTT/2017/onlyTTPNP-norat/ee/nLep2-onZ-REG-SIGN/',
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

ratioDict = {}

# for year in ['2017']:
for year in ['2016', '2017', '2018']:
  # for var in ['TT-Prompt', 'TT', 'TT-onZ-Prompt', 'TT-onZ', 'DY-Prompt', 'DY', 'DY-onZ-Prompt', 'DY-onZ', 'Data', 'Data-onZ']:
  for var in ['TT-Prompt', 'DY-Prompt', 'DY-onZ', 'Data-onZ']:
    for plot in ['pt2D_HA']:
      for region in ['BB', 'EE', 'BE', 'EB']:
        log.info('plotting for ' + year + ' ' + plot)
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
# TODO add overflows   ALSO FOR OS3

        # pdb.set_trace()

        ratio = ss.Clone()
        ratio.Divide(os)

        ratioDict[plot+year+var+region] = ratio.Clone()

        print plot+year+var+region
        print ss.Integral()/os.Integral()
        

        # pickle.dump(ratio, file('4catSSOS/SSoOS_' + plot+ '_' + year + '_' + var + '_' + region + '.pkl', 'w'))

        # ratio.Scale(10.**scaling)

        # ratio.SetTitle('')
        # ratio.GetXaxis().SetTitle(labels[plot][0])
        # ratio.GetYaxis().SetTitle(labels[plot][1])
        # ratio.GetZaxis().SetTitle("Ratio")
        # ratio.GetYaxis().SetTitleOffset(1.3)
        # ratio.GetXaxis().SetTitleOffset(1.1)
        # ratio.GetZaxis().SetTitleOffset(1.1)
        # ratio.GetXaxis().SetTitleSize(0.045)
        # ratio.GetYaxis().SetTitleSize(0.045)
        # ratio.GetZaxis().SetTitleSize(0.045)
        # ratio.GetXaxis().SetLabelSize(0.04)
        # ratio.GetYaxis().SetLabelSize(0.04)
        # ratio.GetZaxis().SetLabelSize(0.04)
        # ratio.GetXaxis().SetTickLength(0)
        # ratio.GetYaxis().SetTickLength(0)
        # ratio.SetMarkerSize(2)
        # # ratio.LabelsOption('v','x')
        
        # # pdb.set_trace()
        
        # ratio.Draw('COLZ text error')

        # drawTex((1-ROOT.gStyle.GetPadRightMargin()-0.02,  1-ROOT.gStyle.GetPadTopMargin()+0.034, '#times10^{#minus' + str(scaling) + '}'), 11,  size=0.05)

        # canv.SaveAs('4catSSOS/SSoOS_' + plot+ '_' + year + '_' + var + '_' + region +'.pdf')
        # canv.SaveAs('4catSSOS/SSoOS_' + plot+ '_' + year + '_' + var + '_' + region +'.png')

NPfrac = {}

for year in ['2017']:
  for var in ['DY', 'DY-onZ', 'TT', 'TT-onZ']:
    for plot in ['pt2D_HA']:
      for region in ['BB', 'EE', 'BE', 'EB']:
        ssPath= paths[var+'PNP'].replace('2017', year).replace('SIGN', 'SS').replace('REG', region)
        osPath= paths[var+'PNP'].replace('2017', year).replace('SIGN', 'OS').replace('REG', region)
        ssPandNP = sumHists(pickle.load(open(ssPath + plot + '.pkl', 'r'))[plot], [] , ['data'])
        osPandNP = sumHists(pickle.load(open(osPath + plot + '.pkl', 'r'))[plot], [] , ['data'])
        ssnp = sumHists(pickle.load(open(ssPath + plot + '.pkl', 'r'))[plot], ['notBothPrompt'] , ['data'])
        osnp = sumHists(pickle.load(open(osPath + plot + '.pkl', 'r'))[plot], ['notBothPrompt'] , ['data'])
        ssnp.Divide(ssPandNP)
        osnp.Divide(osPandNP)

        NPfrac[plot+year+var+region + 'ss'] = ssnp
        NPfrac[plot+year+var+region + 'os'] = osnp

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
#   print year
#   print 'BB LL' + ' & ' + 'BB HH' + ' & ' + 'BB LH' + ' & ' + 'BB HL' + ' & ' + 'EE LL' + ' & ' + 'EE LH' + ' & ' + 'EE HL' + ' & ' + 'EE HH' + ' & ' + 'BE LL' + ' & ' + 'BE LH' + ' & ' + 'BE HL' + ' & ' + 'BE HH' + ' & ' + 'EB LL' + ' & ' + 'EB LH' + ' & ' + 'EB HL' + ' & ' + 'EB HH'
#   print printvals(ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EB'])[0]
#   # print printvals(ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-onZ-Prompt' + 'EB'])[0]
#   # print printvals(ratioDict['pt2D_HA'+ year + 'TT-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-onZ' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EB'])[0]
#   # print printvals(ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-onZ-Prompt' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EB'])[0]


# for year in ['2016', '2017', '2018']:
#   print year
#   print 'BB LL' + ' & ' + 'BB HH' + ' & ' + 'BB LH' + ' & ' + 'BB HL' + ' & ' + 'EE LL' + ' & ' + 'EE LH' + ' & ' + 'EE HL' + ' & ' + 'EE HH' + ' & ' + 'BE LL' + ' & ' + 'BE LH' + ' & ' + 'BE HL' + ' & ' + 'BE HH' + ' & ' + 'EB LL' + ' & ' + 'EB LH' + ' & ' + 'EB HL' + ' & ' + 'EB HH'
#   print printvals(ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EB'])[1]
#   print '--------------------------------------------------------------------------------------'
#   print printvals(ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EB'])[1]
#   print '--------------------------------------------------------------------------------------'
#   print printvals(ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EB'])[1]
#   print '--------------------------------------------------------------------------------------'
#   print printvals(ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EB'])[0]
#   print printvals(ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EB'])[1]
#   print '--------------------------------------------------------------------------------------'

for year in ['2016', '2017', '2018']:
  print year
  print 'BB LL' + ' & ' + 'BB HH' + ' & ' + 'BB LH' + ' & ' + 'BB HL' + ' & ' + 'EE LL' + ' & ' + 'EE LH' + ' & ' + 'EE HL' + ' & ' + 'EE HH' + ' & ' + 'BE LL' + ' & ' + 'BE LH' + ' & ' + 'BE HL' + ' & ' + 'BE HH' + ' & ' + 'EB LL' + ' & ' + 'EB LH' + ' & ' + 'EB HL' + ' & ' + 'EB HH'
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'TT-Prompt' + 'EB'])
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-Prompt' + 'EB'])
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'DY-onZ' + 'EB'])
  print printvalsErrs(ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BB'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'BE'], ratioDict['pt2D_HA'+ year + 'Data-onZ' + 'EB'])

print('nonprompt fractions:')
print 'BB LL' + ' & ' + 'BB HH' + ' & ' + 'BB LH' + ' & ' + 'BB HL' + ' & ' + 'EE LL' + ' & ' + 'EE LH' + ' & ' + 'EE HL' + ' & ' + 'EE HH' + ' & ' + 'BE LL' + ' & ' + 'BE LH' + ' & ' + 'BE HL' + ' & ' + 'BE HH' + ' & ' + 'EB LL' + ' & ' + 'EB LH' + ' & ' + 'EB HL' + ' & ' + 'EB HH'
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'BB'+'os'], NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'EE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'BE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'EB'+'os'])
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'BB'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'EE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'BE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'DY-onZ' + 'EB'+'ss'])
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'BB'+'os'], NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'EE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'BE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'EB'+'os'])
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'BB'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'EE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'BE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'TT-onZ' + 'EB'+'ss'])
print('----------------------------------------------------')
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'DY' + 'BB'+'os'], NPfrac['pt2D_HA'+ '2017' + 'DY' + 'EE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'DY' + 'BE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'DY' + 'EB'+'os'])
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'DY' + 'BB'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'DY' + 'EE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'DY' + 'BE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'DY' + 'EB'+'ss'])
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'TT' + 'BB'+'os'], NPfrac['pt2D_HA'+ '2017' + 'TT' + 'EE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'TT' + 'BE'+'os'], NPfrac['pt2D_HA'+ '2017' + 'TT' + 'EB'+'os'])
print printvalsErrsPercentage(NPfrac['pt2D_HA'+ '2017' + 'TT' + 'BB'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'TT' + 'EE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'TT' + 'BE'+'ss'], NPfrac['pt2D_HA'+ '2017' + 'TT' + 'EB'+'ss'])


# pdb.set_trace()

# NOTE all multiplied by 10^3