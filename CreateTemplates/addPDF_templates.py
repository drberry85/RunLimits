#! /usr/bin/env python
# add "envelope" of q2 variations for ttbar and w+jets
# input: root file with rebinned Mttbar templates 
# output: root file with rebinned Mttbar templates + q2ttbar and q2w+jets variations with name "input name"+_addedQ2.root
# created on 02.11.2017

import sys
sys.argv.append('-b')

import ROOT
ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetOptStat(000000000)
ROOT.gStyle.SetOptTitle(0)

from ROOT import TCanvas, TFile, TH1, THStack, TLegend

class hinfo:
  def __init__(self, name):
    fields = name.split('__')
    self.channel = fields[0]
    self.process = fields[1]
    self.systematic = None
    self.shift = None
    if len(fields) > 2:
      self.systematic = fields[2]
      self.shift = fields[3]


def name(channel, process, systematic = None, shift = None):
  if not systematic:
    return '__'.join([channel, process])
  return '__'.join([channel, process, systematic, shift])



def addPDFFile(rerror, filename, xtitle, backgrounds):
  file = TFile(filename)
  keys = file.GetListOfKeys()
  h_bkg = {}

#  system_q2ttbar_list={"q2ttbarMuRdnMuFdn","q2ttbarMuRupMuFup","q2ttbarMuRdnMuFct","q2ttbarMuRupMuFct","q2ttbarMuRctMuFdn","q2ttbarMuRctMuFup"}
  h_tmp_PDF = {}
  h_PDF = {} # final "PDF__plus","PDF__minus" hists
  
  # system_q2wjets_list={"q2wjetsMuRdnMuFdn","q2wjetsMuRupMuFup","q2wjetsMuRdnMuFct","q2wjetsMuRupMuFct","q2wjetsMuRctMuFdn","q2wjetsMuRctMuFup"}
  # h_tmp_q2syst_q2wjets = {}
  # h_q2syst_q2wjets = {} # final "q2wjets__plus","q2wjets__minus" hists
  
  # load all the background histograms and create tmp hists to store q2 variations
  for key in keys:
    key = key.GetName()
    info = hinfo(key)
    if not info.systematic:
      h_bkg[info.channel+info.process] = file.Get(key).Clone()
      for i in range(1,h_bkg[info.channel+info.process].GetNbinsX()+1):
        h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)] = ROOT.TH1F(info.channel+info.process+"_"+str(i)+"_PDF",info.channel+info.process+"_"+str(i)+"_PDF", 150000, 1., 15000.)
        
  #read 244 variations for PDF and store them in a histogram. One histtogram per Mttbar bin        
  for key in keys:
    key = key.GetName()
    info = hinfo(key)
    if info.systematic:
      #print info.systematic
      if  'wgtMCPDF' in info.systematic:
        #print info.process
        h_bkg[info.channel+'_'+info.process+'_'+info.systematic] = file.Get(key).Clone()
        for i in range(1,h_bkg[info.channel+'_'+info.process+'_'+info.systematic].GetNbinsX()+1):
          value = h_bkg[info.channel+'_'+info.process+'_'+info.systematic].GetBinContent(i)
          h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].Fill(value)
#          print info.channel+'_'+info.process+'_'+str(i)
      # if info.process in backgrounds:
      #   for key_q2syst_q2ttbar in system_q2ttbar_list:
      #     if key_q2syst_q2ttbar == info.systematic:
      #       h_bkg[info.channel+info.process+key_q2syst_q2ttbar] = file.Get(key).Clone()
      #       for i in range(1,h_bkg[info.channel+info.process+key_q2syst_q2ttbar].GetNbinsX()+1):
      #         value = h_bkg[info.channel+info.process+key_q2syst_q2ttbar].GetBinContent(i)
      #         h_tmp_q2syst_q2ttbar[info.channel+'_'+info.process+'_'+str(i)].Fill(value)

  #store hists in a root file
  output = TFile(filename.split('.')[0]+'_addedPDF.root', 'RECREATE')

  #In each Mttbar bin store Mean-Sigma (minus) and Mean+Sigma(plus) of histogram with all (244) PDF variation.
  #This gives "envelope" of PDF variations for ttbar
  #Draw tmp hist for a sanity check and store it in the output root file
  for key in keys:
    key = key.GetName()
    info = hinfo(key)
    if info.systematic:
      if info.process in backgrounds:
        if info.systematic == "wgtMCPDF_1":
          if info.shift == "plus":
            h_PDF["PDF__plus"+info.channel+'_'+info.process] = h_bkg[info.channel+'_'+info.process+'_'+info.systematic].Clone()
            h_PDF["PDF__plus"+info.channel+'_'+info.process].SetName(info.channel+"__"+info.process+"__PDF__plus")
            h_PDF["PDF__plus"+info.channel+'_'+info.process].SetTitle(info.channel+"__"+info.process+"__PDF__plus")
            h_PDF["PDF__minus"+info.channel+'_'+info.process] = h_bkg[info.channel+'_'+info.process+'_'+info.systematic].Clone()
            h_PDF["PDF__minus"+info.channel+'_'+info.process].SetName(info.channel+"__"+info.process+"__PDF__minus")
            h_PDF["PDF__minus"+info.channel+'_'+info.process].SetTitle(info.channel+"__"+info.process+"__PDF__minus")

            canvas = TCanvas()
            for i in range(1,h_bkg[info.channel+'_'+info.process+'_'+info.systematic].GetNbinsX()+1):
              # if 'wjets_l' in info.process:
              #   canvas_tmp = TCanvas()
              #   h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].Print()
              #   h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].Draw('e')
              #   canvas_tmp.SaveAs(info.channel+'_'+info.process+'_'+str(i)+'.pdf')
#              print h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].GetMean(), h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].GetRMS()

              h_PDF["PDF__plus"+info.channel+'_'+info.process].SetBinContent(i,h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].GetMean()+h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].GetRMS())
              h_PDF["PDF__minus"+info.channel+'_'+info.process].SetBinContent(i,h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].GetMean()-h_tmp_PDF[info.channel+'_'+info.process+'_'+str(i)].GetRMS())
               
            #plots hists for canity check  
            h_PDF["PDF__plus"+info.channel+'_'+info.process].SetLineColor(2)
            h_PDF["PDF__minus"+info.channel+'_'+info.process].SetLineColor(3)                  
            h_PDF["PDF__plus"+info.channel+'_'+info.process].Draw('hist')
            h_PDF["PDF__minus"+info.channel+'_'+info.process].Draw('samehist')
            canvas.SaveAs(info.channel+'__'+info.process+'__PDF.pdf')
            output.cd()
            h_PDF["PDF__minus"+info.channel+'_'+info.process].Write()
            h_PDF["PDF__plus"+info.channel+'_'+info.process].Write()

 
  #Add the rest of systematic to the new root file
  h_all_system = {}
  for key in keys:
    key = key.GetName()
    #print key
    info = hinfo(key)
    if not info.systematic:
      h_all_system[info.channel+"__"+info.process] = file.Get(key).Clone()
      output.cd()
      h_all_system[info.channel+"__"+info.process].Write()
    else:   
      if 'wgtMCPDF' not in info.systematic:
        isStore = True
      # for key_q2_q2wjets in system_q2_list:
      #   if info.systematic == key_q2_q2wjets:
      #     isStore = False
        if isStore:
          h_all_system[info.channel+"__"+info.process+"__"+info.systematic+"__"+info.shift] = file.Get(key).Clone()
          output.cd()
          h_all_system[info.channel+"__"+info.process+"__"+info.systematic+"__"+info.shift].Write()

addPDFFile(0.30,  'ele_theta_bdt0p5_chi30_addedQ2.root','M_{t#bar{t}} [GeV/c^{2}]',['ttbar','wjets_l','wjets_c','wjets_b'])
addPDFFile(0.30,  'mu_theta_bdt0p5_chi30_addedQ2.root','M_{t#bar{t}} [GeV/c^{2}]',['ttbar','wjets_l','wjets_c','wjets_b'])
addPDFFile(0.30,  'ele_theta_wFlatShapeSyst_rebinned_addedQ2.root','M_{t#bar{t}} [GeV/c^{2}]',['ttbar','wjets_l'])
addPDFFile(0.30,  'mu_theta_wFlatShapeSyst_rebinned_addedQ2.root','M_{t#bar{t}} [GeV/c^{2}]',['ttbar','wjets_l'])
addPDFFile(0.30,  'ele_theta_bdt0p5_chi30_1MttbarBin_addedQ2.root','M_{t#bar{t}} [GeV/c^{2}]',['ttbar','wjets_l','wjets_c','wjets_b'])
addPDFFile(0.30,  'mu_theta_bdt0p5_chi30_1MttbarBin_addedQ2.root','M_{t#bar{t}} [GeV/c^{2}]',['ttbar','wjets_l','wjets_c','wjets_b'])