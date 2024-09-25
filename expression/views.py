from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from expression import models
from .models import Film, Genesummary, Genecounts, Transcriptcounts, TranscriptFeature
from .forms import GeneForm, TheForm # Import the form
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import subprocess
import os
import time


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

def run_r_ggtranscript(gtfPath):
    scriptR = os.path.join('C:/Users/skl215/Dropbox/Scripts/isoVisDev/expression/management/commands/plot_transcript_structure.R')
    try:
        result = subprocess.run(
            ['Rscript', scriptR, gtfPath], 
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
    if request.method == 'GET':
        # Display the gene input form
        form = GeneForm()
        return render(request, 'expression/gene_form.html', {'form': form})

    elif request.method == 'POST':
        # Check if the user submitted the gene form
        if 'gene_name' in request.POST:
            gene_form = GeneForm(request.POST)
            if gene_form.is_valid():
                gene_name = gene_form.cleaned_data['gene_name']
                transcripts = TranscriptFeature.objects.filter(geneName=gene_name)
                unique_transcripts = {transcript.isoform: transcript for transcript in transcripts}.values()

                if transcripts.exists():
                    # Create choices for the dropdown based on the fetched transcripts
                    transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
                    print("Available transcript choices:", transcript_choices)

                    # Initialize the multiple selection form with transcript choices
                    transcript_form = TheForm()  # No POST data here
                    transcript_form.fields['Transcripts'].choices = transcript_choices
                    
                    # Store gene_name in session for later use
                    request.session['gene_name'] = gene_name
                    
                    # Render the form with transcript options
                    return render(request, 'expression/select_transcript.html', {
                        'form': transcript_form,
                        'gene_name': gene_name
                    })

                else:
                    # If no transcripts found for the gene
                    return render(request, 'expression/gene_form.html', {
                        'form': gene_form,
                        'error_message': f"No transcripts found for gene {gene_name}"
                    })

        # Check if the user submitted the transcript selection form
        else:
            transcript_form = TheForm(request.POST)
            gene_name = request.session.get('gene_name')

            # Re-fetch transcripts based on the stored gene_name
            transcripts = TranscriptFeature.objects.filter(geneName=gene_name)
            unique_transcripts = {transcript.isoform: transcript for transcript in transcripts}.values()
            transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
            transcript_form.fields['Transcripts'].choices = transcript_choices

            if transcript_form.is_valid():
                selected_transcripts = transcript_form.cleaned_data['Transcripts']
                print(selected_transcripts[0])
                selected_transcript_df = TranscriptFeature.objects.filter(isoform=selected_transcripts[0])
                df = pd.DataFrame(selected_transcript_df.values())
                gtfPath = 'C:/Users/skl215/Dropbox/Scripts/isoVisDev/expression/df.csv'
                df.to_csv(gtfPath)
                plot = run_r_ggtranscript(gtfPath)  # Modify this function to accept isoform ID

                print("Selected transcripts:", selected_transcripts)
                # Render the success message with selected transcripts
                return render(request, 'expression/transcript_selected_success.html', {
                    'selected_transcripts': selected_transcripts,
                    'plot' : plot,
                    'gene_name': gene_name
                })
            else:
                print("Form is not valid:", transcript_form.errors)
                return render(request, 'expression/select_transcript.html', {
                    'form': transcript_form,
                    'gene_name': gene_name,
                    'error_message': 'Please select at least one transcript.'
                })


def transcript_identify_old(request):
    plot = ""
    if request.method == 'GET':
        context = {'title': 'User Form Page'}
        template = 'expression/user_form.html'

        return render(request,
                      template,
                      context)
        
    elif request.method == 'POST':
        username = request.POST.get('username')
        transcript_id = request.POST.get('transcript_id')  # Fetch the selected transcript id
        print("POST data:", request.POST)  # Debugging: Print all POST data
        request.session['username'] = username

        transcripts = TranscriptFeature.objects.filter(geneName=username)
        unique_transcripts = {transcript.isoform: transcript for transcript in transcripts}.values()
        
         # If specific transcript is selected, filter the data for that isoform
        if transcript_id:
            print("Transcript ID received:", transcript_id)
            selected_transcript = TranscriptFeature.objects.get(isoform=transcript_id)
            print("Query complete:", time.time() - start_time, "seconds")
            selected_transcript_df = TranscriptFeature.objects.filter(isoform=transcript_id)
            print("Query 2 complete:", time.time() - start_time, "seconds")
            df = pd.DataFrame(selected_transcript_df.values())
            print(df)
            gtfPath = 'C:/Users/sl693/Dropbox/Scripts/isoVisDev/expression/df.csv'
            df.to_csv(gtfPath)
            # Process the specific transcript data for the plot
            plot = run_r_ggtranscript()  # Modify this function to accept isoform ID
            # Respond with JSON data to dynamically update the plot
            return JsonResponse({'plot': plot})

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
