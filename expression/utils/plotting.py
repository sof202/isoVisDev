import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import plotly.express as px
import os
import subprocess
import logging
from django.shortcuts import render

logger = logging.getLogger('isoVisDev')

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
    print(f"Current Directory: {dir_path}")
    
    scriptR = os.path.join(dir_path, 'plot_transcript_structure.R')
    print(f"R Script Path: {scriptR}")
    
    try:
        result = subprocess.run(
            ['Rscript', scriptR, gtfPath, expression_path],
            capture_output=True, text=True, check=True
        )
        
        # Log the standard output from the R script
        logger.info("R Script Output:\n%s", result.stdout)
        print("R Script Output:", result.stdout)

        # Log the standard error from the R script
        if result.stderr:  # Check if there's any error output
            logger.error("R Script Error Output:\n%s", result.stderr)
            print("R Script Error Output:", result.stderr)
            
        return result.stdout  # Return plot or relevant output
    except subprocess.CalledProcessError as e:
        logger.error(f'Error running R script: {e.stderr}')  # Log the error
        print(f"Error: {e.stderr}")
        return None  # Return None if there's an error
  