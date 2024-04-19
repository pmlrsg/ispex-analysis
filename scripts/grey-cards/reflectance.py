#!/usr/bin/env python
"""
Grey cards positioned at the rear port of a 150mm integrating sphere of a PerkinElmer Lambda1050.
Light absorbance scans over 175 - 2500 nm to compare spectral response, converted to Reflectance.

"""
import os
import numpy as np
import glob
import argparse
import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def import_pe_asc_file(filepath):
    """
    read data block and key metadata from a perkinelmer uvwinlab generated ascii formatted file. 
    Return a dictionary with metadata and numpy.array for the data and wavelength grid.
    : filepath - path to the file to read from
    """
    with open(filepath, 'r') as fp:
        raw = fp.readlines()
    raw = [r.strip() for r in raw]
    data ={}
    data['filename'] = raw[2]
    data['datetime'] = datetime.datetime.strptime(raw[3]+raw[4][0:8], '%y/%m/%d%H:%M:%S')
    data['operator'] = raw[7]
    data['description'] = raw[8]
    for i, d in enumerate(raw):
        if d == '#DATA':
            break
    wavelength, absorbance = zip(*[(float(r.strip().split('\t')[0]), float(r.strip().split('\t')[1])) for r in raw[i+1::]])
    data['reflectance'] = 1.0 - np.array(absorbance)
    data['wavelength'] = np.array(wavelength)

    return data


def plot_series(df, wl_range=[380,950]):
    """
    Plot curves from a list of data dicts
    """
    labels = df['description']
    fig = go.Figure()
    for i in range(len(df)):
        fig.add_scatter(x=df.loc[i]['wavelength'], y=df.loc[i]['reflectance'], name=df.loc[i]['description'])
        i400 = np.argwhere(df.loc[i]['wavelength']<=400)[0][0]
        i700 = np.argwhere(df.loc[i]['wavelength']<=700)[0][0]
        y_avg = np.mean(df.loc[i]['reflectance'][i700:i400])
        annx = 400+(25*i)
        anny = df.loc[i]['reflectance'][np.argwhere(df.loc[i]['wavelength']<=annx)[0][0]]
        fig.add_annotation(x=annx, y=anny, text=f"Avg_VIS={100*y_avg:.1f}%", showarrow=True, arrowhead=1)

    fig.update_xaxes(range=wl_range)
    fig.update_yaxes(range=[0,0.5])



    fig.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Read and display measurements from PE1050")
    parser.add_argument('-f', '--file', help="File or (quoted) pattern to read")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_args()

    files = glob.iglob(args.file)

    df = pd.DataFrame([import_pe_asc_file(f) for f in files])

    plot_series(df, wl_range=[380, 950])

