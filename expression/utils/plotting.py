import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import plotly.express as px
import os
import subprocess
import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render



def gene_boxplot(df):
    fig = px.box(
      data_frame = df,
      x = 'group',
      y = 'counts',
      color = 'sex',
      template='simple_white',
      labels={'x': '', 'y':'Normalised counts'})
      
    fig =  fig.to_html()
    return fig


def run_r_ggtranscript(gtfPath):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    expression_path = os.path.join(dir_path, '..')
    print(dir_path)
    scriptR = os.path.join(dir_path, 'plot_transcript_structure.R')
    try:
        result = subprocess.run(
            ['Rscript', scriptR, gtfPath, expression_path], 
            capture_output=True, text=True, check=True
        )
        print("R Script Output:", result.stdout)
        print("R Script Error Output:", result.stderr)
        return result.stdout  # Return plot or relevant output
    except subprocess.CalledProcessError as e:
        logger.error(f'Error running R script: {e.stderr}')
        print(f"Error: {e.stderr}")  # Print R script errors
        return None  # Return None if there's an error 
  