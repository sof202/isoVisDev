#!/usr/bin/env python

# modules
import csv
import pandas as pd

# input gtf, out csv
file = "C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/files/final.gtf"
outputfile= "C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/files/finalgtf.csv"

# read gtf
df = pd.read_table(file, names = ["seqname", "source", "feature", "start", "end", "score", "strand", "frame", "attributes"])

# split attributes to gene_id and transcript_id
df['gene_id'] = df['attributes'].str.split(';',expand=True)[0].str.replace('"', '').str.replace('gene_id', '')
df['transcript_id'] = df['attributes'].str.split(';',expand=True)[1].str.replace('"', '').str.replace('transcript_id', '')

# retain the relevant columns
df = df.drop(["attributes","source", "score", "frame"], axis = 1)

# output 
df.to_csv(outputfile, index = False)
