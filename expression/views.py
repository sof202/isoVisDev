from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from expression import models
from .models import Film, Genesummary, Genecounts, Transcriptcounts, TranscriptFeature
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import subprocess
import os


def home(request):
    return render(request, 'home.html')


def main(request):
    #title = 'Main Page'
    #Gene_list = Genesummary.objects.all()
    #context = {'title': title,
    #           'genes_list': Gene_list}
    #return render(request,
    #              'films/main.html',
    #              context)
    if request.method == 'GET':
        context = {'title': 'User Form Page'}
        template = 'expression/user_form.html'

        return render(request,
                  template,
                  context)
        
    elif request.method == 'POST':
        username = request.POST.get('username')
        request.session['username'] = username

        # transcript counts
        gene = Genesummary.objects.get(geneName=username)

        # gene expression
        queryset = Genecounts.objects.filter(geneName=username)
        data = list(queryset.values())
        df = pd.DataFrame(data)
        fig = gene_boxplot(df)

        context = {
            'title': 'Gene Details Page',
            'gene': gene,
            'plot': fig
        }

        #context = {'gene': gene}
        template = 'expression/genelevel.html'

        return render(request,
              template,
              context)


def user_info(request):
    if request.method == 'GET':    
        print('\n\nrequest.GET ==>>',
              request.GET,
              '\n\n')
    
        if request.session.get('username', False):
            userinfo = {
                'username': request.session['username'],
                'country': request.session['country'],
            }
        else:
            userinfo = False
            
        context = {'userinfo': userinfo,
                   'title': 'User Info Page'}
        template = 'expression/user_info.html'
        return render(request,
                      template,
                      context)

def gene_boxplot(df):
    #custom_params = {"axes.spines.right": False, "axes.spines.top": False}
    #sns.set_theme(style="ticks", rc=custom_params)
    #fig = sns.boxplot(data = df, x = "group", y = "counts", hue = "sex") 
    #fig.set_ylabel('Normalised counts')
    #fig.set_xlabel('')
    fig = px.box(
      data_frame = df,
      x = 'group',
      y = 'counts',
      color = 'sex',
      template='simple_white',
      labels={'x': '', 'y':'Normalised counts'})
      
    fig =  fig.to_html()
    return fig
  

def user_form(request):
    if request.method == 'GET':
        context = {'title': 'User Form Page'}
        template = 'expression/user_form.html'

        return render(request,
                      template,
                      context)
        
    elif request.method == 'POST':
        username = request.POST.get('username')
        request.session['username'] = username

        try:
            # try to fet gene if in database
            # gene summary
            gene = Genesummary.objects.get(geneName=username)

            # gene expression
            queryset = Genecounts.objects.filter(geneName=username)
            data = list(queryset.values())
            df = pd.DataFrame(data)
            fig = gene_boxplot(df)

            context = {
                'title': 'Gene Details Page',
                'gene': gene,
                'plot': fig
            }

            #context = {'gene': gene}
            template = 'expression/genelevel.html'

        except Genesummary.DoesNotExist:
            # Handle case where gene is not found
            context = {
                'title': 'Gene Not Found',
                'error_message': f'{username} not found in our dataset',
            }
            template = 'expression/not_found.html'

        return render(request,
              template,
              context)

def run_r_ggtranscript():
    scriptR = os.path.join('C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/management/commands/plot_transcript_structure.R')
    try:
        result = subprocess.run(
            ['Rscript', scriptR], 
            capture_output=True, text=True, check=True
        )
        print("R Script Output:", result.stdout)
        print("R Script Error Output:", result.stderr)
        return result.stdout  # Return plot or relevant output
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")  # Print R script errors
        return None  # Return None if there's an error 

def to_intron(gexons, group_var):
    introns = []
    for isoform, group in gexons.groupby(group_var):
        for i in range(len(group) - 1):
            intron_start = group.iloc[i]['end']
            intron_end = group.iloc[i + 1]['start']
            introns.append({
                'isoform': isoform,
                'start': intron_start,
                'end': intron_end,
                'type': 'intron'
            })
    return pd.DataFrame(introns)

def shorten_gaps(gexons, gintrons, group_var):
    return pd.concat([gexons, gintrons], ignore_index=True)

def plot_simply(gtf):
    gexons = gtf
    gintrons = to_intron(gexons, group_var="isoform")
    grescaled = shorten_gaps(gexons, gintrons, group_var="isoform")

    fig, ax = plt.subplots(figsize=(10, 6))

    for _, row in grescaled[grescaled['type'] == 'exon'].iterrows():
        ax.add_patch(patches.Rectangle((row['start'], row['isoform']),
                                        row['end'] - row['start'],
                                        0.4,
                                        color=row['Type'],
                                        label=row['Type'] if row['Type'] not in ax.get_legend_handles_labels()[1] else ""))

    for _, row in grescaled[grescaled['type'] == 'intron'].iterrows():
        ax.add_patch(patches.FancyArrowPatch((row['start'], row['isoform']),
                                              (row['end'], row['isoform']),
                                              mutation_scale=20,
                                              color='black',
                                              linewidth=1,
                                              arrowstyle='-|>',
                                              connectionstyle="arc3,rad=0.5"))

    ax.set_yticks(grescaled['isoform'].unique())
    ax.set_ylabel('Transcripts')
    ax.set_title('Transcript Structure')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('grey')
    ax.spines['bottom'].set_color('grey')
    plt.xticks(size=12)
    plt.yticks(size=12)
    plt.legend(title='Type', loc='upper right', frameon=False)

    html_fig = mpld3.fig_to_html(fig)
    plt.close(fig)  # Close the figure to avoid display

    return html_fig

def transcript_identify(request):
    plot = ""
    if request.method == 'GET':
        context = {'title': 'User Form Page'}
        template = 'expression/user_form.html'

        return render(request,
                      template,
                      context)
        
    elif request.method == 'POST':
        username = request.POST.get('username')
        request.session['username'] = username

        transcripts = TranscriptFeature.objects.filter(geneName=username)
        print(transcripts)
        unique_transcripts = {transcript.isoform: transcript for transcript in transcripts}.values()
        
        data = list(transcripts.values())
        df = pd.DataFrame(data)
        print(df)
        gtfPath = 'C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/df.csv'
        df.to_csv(gtfPath)
        plot = run_r_ggtranscript()

        if transcripts.exists():
            context = {
                'gene': username, 
                'title': 'Gene Details Page',
                'transcripts': unique_transcripts,  # Pass all transcripts to the context
                'plot': plot  # Include the plot in the context
            }
            template = 'expression/transcriptlevel.html'
        else:
            context = {
                'title': 'Gene Not Found',
                'error_message': f'Gene "{username}" not found in our dataset',
            }
            template = 'expression/not_found.html'

        return render(request,
              template,
              context)

def film_all(request):
    film = Film.all()[:50]
    context ={
        'film': film
    }
    return render(request,'expression/details.html',context)


def details(request, id):
    film = Film.objects.get(id=id)
    # other query option:
    # film = Film.objects.filter(id=id)[0]
    context = {'film': film}
    return render(request, 'expression/details.html', context)


def get_data():
    df = px.data.gapminder()
    return df

def create_plot(df, year):
    fig = px.scatter(
      data_frame = df.query(f'year=={year}'),
      x = 'gdpPercap',
      y = 'lifeExp',
      color = 'continent',
      size = 'pop',
      height = 500,
      log_x=True,
      size_max=60,
      hover_name="country")
      
    fig =  fig.to_html()
    return fig

def gapminder(request, year):
    df = get_data()
    fig = create_plot(df, year)
    context = {"plot": fig, "year": year}
    template = 'gapminder.html'
    return render(request, template, context)


def gene_expression(request, gene):
    queryset = Genecounts.objects.filter(geneName=gene)
    data = list(queryset.values())
    # Convert list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    fig = gene_boxplot(df)
    context = {"plot": fig}
    template = 'genecounts.html'
    return render(request, template, context)
