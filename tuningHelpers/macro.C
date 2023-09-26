{
        TFile *f = new TFile("Luigi_Gaioni_Procedure_Results_09_21_23_14:44:29/BIAS300_TDAC0_LDAC130/ThresholdScan/results.root");
	TList *lk = f->GetListOfKeys();
        TObject *o = lk->Last();
        const char *dn = o->GetName();
        f->cd(dn);
        TCanvas *c1; gDirectory->GetObject("S-Curves;1",c1);
        c1->Draw();
        gPad->SetLogz(1);
        c1->SetWindowSize(1400,800);
        c1->Print("Luigi_Gaioni_Procedure_Results_09_21_23_14:44:29/BIAS300_TDAC0_LDAC130/S_Curve_BIAS300_TDAC0_LDAC130.pdf");
        TCanvas *c2; gDirectory->GetObject("Threshold Distribution (fitting);1",c2);
        c2->Draw();
        c2->SetWindowSize(1400,800);
        c2->Print("Luigi_Gaioni_Procedure_Results_09_21_23_14:44:29/BIAS300_TDAC0_LDAC130/Threshold_Dist_BIAS300_TDAC0_LDAC130.pdf");
        TCanvas *c3; gDirectory->GetObject("Noise Distribution (probit);1",c3);
        c3->Draw();
        c3->SetWindowSize(1400,800);
        c3->Print("Luigi_Gaioni_Procedure_Results_09_21_23_14:44:29/BIAS300_TDAC0_LDAC130/Noise_Dist_BIAS300_TDAC0_LDAC130.pdf");
}
