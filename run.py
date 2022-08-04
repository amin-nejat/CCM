# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 22:31:20 2022

@author: Amin
"""

from causality import causality_indices as ci
from causality import interventional as intcnn
from causality import helpers as inth

from causality import granger
from delay_embedding import ccm

import visualizations as viz
import data_loader

import numpy as np

import argparse
import yaml

import os
# %%
def get_args():
    '''Parsing the arguments when this file is called from console
    '''
    parser = argparse.ArgumentParser(description='Runner for CCM',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config', '-c', metavar='Configuration',help='Configuration file address',default='/')
    parser.add_argument('--output', '-o', metavar='Output',help='Folder to save the output and results',default='/')
    
    return parser.parse_args()

# %%
if __name__ == '__main__':
    '''Read the arguments and run given the configuration in args
    '''
    args = get_args()
    if not os.path.exists(args.output): os.makedirs(args.output)
    with open(args.config, 'r') as stream: pm = yaml.safe_load(stream)
    

    # %%
    dl = eval('data_loader.'+pm['dataset'])(pm)
    if 'visualize_adjacency' in pm['visualizations']: viz.visualize_adjacency(dl.network.pm['J'],fontsize=pm['fontsize'],save=True,file=args.output+'cnn')

    # %%
    r,t,out = dl.load_rest(pm)
    
    if 'visualize_rates' in pm['visualizations']: viz.visualize_signals(t,[r.T],['Rest Rates'],t_range=(min(t),max(t)),fontsize=pm['fontsize'],save=True,file=args.output+'rest_rates')
    if 'visualize_voltages' in pm['visualizations']: viz.visualize_signals(out['t'],[out['x'].T],['Rest Voltages'],t_range=(min(t),max(t)),fontsize=pm['fontsize'],save=True,file=args.output+'rest_voltages')
    if 'visualize_spikes' in pm['visualizations']: viz.visualize_spikes([out['spikes_flat']],['Rest Spikes'],t_range=(min(t),max(t)),fontsize=pm['fontsize'],distinct_colors=True,distinction_point=pm['distinction_point'],save=True,file=args.output+'rest_spikes')
    
    mask = np.ones((r.shape[1],r.shape[1])).astype(bool)
    mask[:,dl.stimulated_recorded] = False
    np.fill_diagonal(mask, True)
    
    indices,indices_pval = {},{}
    if 'gc' in pm['indices']:
        indices['gc'],indices_pval['gc'] = granger.univariate_gc(r.T,maxlag=pm['max_lag'],mask=mask)
        viz.visualize_ccm(indices['gc'],pval=indices_pval['gc']<pm['pval_thresh'],titlestr='GC',fontsize=pm['fontsize'],save=True,file=args.output+'rest_gc')
    
    if 'te' in pm['indices']:
        indices['te'],indices_pval['te'] = ci.transfer_entropy_ksg(r.T,mask=mask)
        viz.visualize_ccm(indices['te'],pval=indices_pval['te']<pm['pval_thresh'],titlestr='TE',fontsize=pm['fontsize'],save=True,file=args.output+'rest_te')
        
    if 'egc' in pm['indices']:
        indices['egc'],indices_pval['egc'] = ci.extended_granger_causality(r.T,mask=mask)
        viz.visualize_ccm(indices['egc'],pval=indices_pval['egc']<pm['pval_thresh'],titlestr='EGC',fontsize=pm['fontsize'],save=True,file=args.output+'rest_egc')
        
    if 'ngc' in pm['indices']:
        indices['ngc'],indices_pval['ngc'] = ci.nonlinear_granger_causality(r.T,mask=mask,mx=pm['mx'],my=pm['my'])
        viz.visualize_ccm(indices['ngc'],pval=indices_pval['ngc']<pm['pval_thresh'],titlestr='NGC',fontsize=pm['fontsize'],save=True,file=args.output+'rest_ngc')

    if 'mgc' in pm['indices']:
        indices['mgc'],indices_pval['mgc'] = granger.multivariate_gc(r.T,maxlag=pm['max_lag'],mask=mask)
        viz.visualize_ccm(indices['mgc'],pval=indices_pval['mgc']<pm['pval_thresh'],titlestr='MGC',fontsize=pm['fontsize'],save=True,file=args.output+'rest_mgc')
        
    if 'fcf' in pm['indices']:
        indices['fcf'],indices_pval['fcf'],_ = ccm.connectivity(r,mask=mask,test_ratio=pm['test_ratio'],delay=pm['tau'],dim=pm['D'],n_neighbors=pm['n_neighbors'],return_pval=True,n_surrogates=pm['n_surrogates'])
        viz.visualize_ccm(indices['fcf'],pval=indices_pval['fcf']<pm['pval_thresh'],titlestr='FCF',fontsize=pm['fontsize'],save=True,file=args.output+'rest_fcf')
    
    # %%
    
    if 'ic' in pm['indices']:
        r,t,out = dl.load_stim(pm)
        
        if 'I' in out.keys():
            if 'visualize_rates' in pm['visualizations']: viz.visualize_signals(t,[r.T],['Stim Rates'],t_range=(min(t),max(t)),stim=out['I'][:,dl.recorded],stim_t=out['t_stim'],fontsize=pm['fontsize'],save=True,file=args.output+'stim_rates')
            if 'visualize_voltages' in pm['visualizations']: viz.visualize_signals(out['t'],[out['x'].T],['Stim Voltages'],t_range=(min(t),max(t)),stim=out['I'][:,dl.recorded],stim_t=out['t_stim'],fontsize=pm['fontsize'],save=True,file=args.output+'stim_voltages')
            if 'visualize_spikes' in pm['visualizations']: viz.visualize_spikes([out['spikes_flat']],['Stim Spikes'],t_range=(min(t),max(t)),stim=out['I'],stim_t=out['t_stim'],distinct_colors=True,distinction_point=pm['distinction_point'],fontsize=pm['fontsize'],save=True,file=args.output+'stim_spikes')
            if 'visualize_stim_protocol' in pm['visualizations']: viz.visualize_stim_protocol(out['I'],min(t),max(t),pm['N'],fontsize=pm['fontsize'],save=True,file=args.output+'stim_protocol')


            stim_s = np.where(np.diff(out['I'][:,dl.recorded].T,axis=1) > 0)
            stim_e = np.where(np.diff(out['I'][:,dl.recorded].T,axis=1) < 0)
            
            # stim_e = stim_s
            
            # Stimulation duration
            stim_d = [out['t_stim'][stim_e[1][i]] - out['t_stim'][stim_e[1][i]] for i in range(len(stim_e[1]))] 
            
            # Stimulation array [(chn,start,end),...]
            stim_info = [(stim_s[0][i], out['t_stim'][stim_s[1][i]], out['t_stim'][stim_e[1][i]]) for i in range(len(stim_e[1]))] 
        
        if 'stim_info' in out.keys():
            stim_info = out['stim_info']
        
        output = intcnn.interventional_connectivity(
                    r.T,
                    stim_info,
                    t=t,
                    mask=mask,
                    bin_size=pm['bin_size'],
                    skip_pre=pm['skip_pre'],
                    skip_pst=pm['skip_pst'],
                    pval_threshold=1,
                    methods=pm['methods']
                )
        
        intcnn = output[pm['methods'][0]].T
        intcnn_pval = output['aggr_ks_pval'].T
        viz.visualize_ccm(intcnn,intcnn_pval<=pm['pval_thresh'],titlestr='IC',cmap='copper',fontsize=pm['fontsize'],save=True,file=args.output+'stim_ic')
        
        viz.visualize_scatters(
            [index[~mask] for index in indices.values()],
            [intcnn[~mask] for index in indices.values()],
            [intcnn_pval[~mask]<pm['pval_thresh'] for index in indices.values()],
            xlabel=list(indices.keys()),
            ylabel=[pm['methods'][0] for i in range(len(indices.keys()))],
            titlestr='Functional vs. Interventional Correlation',
            fontsize=pm['fontsize'],
            save=True,file=args.output+'stim_rest_corr'
        )
