from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from expression import models
from .models import Film, Genesummary, Genecounts, Transcriptcounts
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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
