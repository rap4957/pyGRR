import GRR
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import matplotlib.ticker as mtick
from abc import ABC, abstractmethod
sns.set()


class plotter(object):
    def __init__(GRR):
        self.GRR = GRR
    @abstractmethod
    def plot(ax):
        pass #define that every instance of a plotter object needs an axis object to plot
            
        
class components_of_variation(plotter):
    def __init__(self, GRR):
        self.GRR = GRR.GRR_Table
        self.varComp = GRR.vc_table

    def plot(self, ax, barWidth = 0.25):
        components = ['Total Gage R&R', 'Repeatability', 'Reproducibility', 'Part-to-Part']
        GRR_Table = self.GRR
        GRR_Table = GRR_Table[GRR_Table['Source'].isin(components)]

        varcomp = self.varComp
        varcomp = varcomp[varcomp['Source'].isin(components)]

        h1 = varcomp['% Contribution (of VarComp)'].values * 100
        h2 = GRR_Table['% Study Var'].values * 100

        # Set position of bar on X axis
        br1 = np.arange(len(h1))
        br2 = [x + barWidth for x in br1]

        ax.bar(br1, h1, color ='r', width = barWidth,
        edgecolor ='grey', label ='%Contribution')

        ax.bar(br2, h2, color ='g', width = barWidth,
        edgecolor ='grey', label ='%Study Var')

        if('% Tolerance' in GRR_Table.columns):
            h3 = GRR_Table['% Tolerance'].values * 100
            br3 = [x + barWidth for x in br2]
            ax.bar(br3, h3, color ='b', width = barWidth,
            edgecolor ='grey', label ='%Tolerance')
            
        fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
        yticks = mtick.FormatStrFormatter(fmt)
        ax.yaxis.set_major_formatter(yticks)

        ax.legend()
        ax.set_title('Components of Variation')
        ax.set_ylabel('Percent')
        ax.set_xticks([r + barWidth for r in range(len(h1))], components)

class measurement_by_part(plotter):
    def __init__(self, GRR):
        self.data = GRR.data

    def plot(self, ax, normed=True):
        parts = self.data['Part'].unique()
        means = self.data.groupby(by='Part').mean(numeric_only=True)['Measurement'].values
        ax.plot(parts, means, linestyle='-', linewidth=1, marker='o', markersize=10, color='blue') 
        for part in parts:
            df = self.data
            y = df[df['Part']==part]['Measurement'].values
            ax.scatter([part]*len(y), y, marker='o', s=10, color='grey')
        ax.set_title('Measurement by Part')
        ax.set_xlabel('Part')
        ax.set_xticks([r+1 for r in range(len(parts))], parts)
        
class r_chart_by_operator(plotter):
    def __init__(self, GRR):
        self.data = GRR.data
        self.n_ops = GRR.n_operators
        
    def plot(self, ax):
        y_vals = self.data.groupby(by=[ 'Operator','Part']).apply(lambda x: x.max()- x.min())['Measurement'].values
        parts = parts = self.data['Part'].unique()

        #unbiasing constants for estimating range. Used later in UCL/LCL calculation
        d2 = lambda n: 1.0676*np.log(n) + 0.5636
        d3 = lambda n: -0.0078*n + 0.8857
        subgroup_size = 2
        x_labels = (np.array([parts]*self.n_ops)).flatten()
        x_vals = np.array([x for x in range(len(x_labels))])
        ax.plot(x_vals, y_vals, marker='o', markersize=10, color='blue')
        ax.set_xticks([x for x in range(len(x_labels))], x_labels)
        
        UCL = d2(subgroup_size) * y_vals.std() + (3*y_vals.std() * d3(subgroup_size)) 
        LCL = d2(subgroup_size) * y_vals.std() - (3*y_vals.std() * d3(subgroup_size)) 
        LCL = LCL if LCL> 0 else 0 #set LCL to 0 if negative
        grand_mean = y_vals.mean()
        ax.hlines(y=[LCL,UCL], xmin=0, xmax=len(x_labels), color='red')
        ax.hlines(y=grand_mean, xmin=0, xmax=len(x_labels), color='green')
        stages = x_vals[np.where(x_vals%max(parts)==0)]
        ax.vlines(x=stages, ymin=0, ymax=max(UCL,max(y_vals)), linestyle='--', color='grey', alpha=.4)
        
        ax.set_title('R Chart by Operator')
        ax.set_ylabel('Sample Range')
        ax.set_xlabel('Part')
        

class measurement_by_operator(plotter):
    def __init__(self, GRR):
        self.data = GRR.data
        self.n_ops = GRR.n_operators
        
    def plot(self, ax, normed=True):
        df = self.data 
        norm = lambda x: (x - self.data['Measurement'].mean())/self.data['Measurement'].std()
        if(normed):
            my_dict = dict([[key, norm(df[df['Operator']==key]['Measurement'].values)] for key in df['Operator'].unique()])
            means = norm(df.groupby(by='Operator').mean()['Measurement'])
        else: 
            my_dict = dict([[key, df[df['Operator']==key]['Measurement'].values] for key in df['Operator'].unique()])
            means = df.groupby(by='Operator').mean()['Measurement']
            
        bplot = ax.boxplot(my_dict.values(), vert=True, patch_artist=True)
        for patch in bplot['boxes']:
            patch.set_facecolor('lightblue')
            
        ax.plot([x+1 for x in range(len(df['Operator'].unique()))], means, linewidth=.5, color='black', marker='o', markersize=10, markerfacecolor='none')
        ax.plot([x+1 for x in range(len(df['Operator'].unique()))], means, marker='+', color='black', linestyle='None', markersize=10)
        ax.set_xticklabels(my_dict.keys())
        ax.set_xlabel('Operator')
        ax.set_title('Measurement by Operator')

class x_bar_chart_by_operator(plotter):
    def __init__(self, GRR):
        self.data = GRR.data
        self.n_ops = GRR.n_operators
        
    def plot(self, ax):
        y_vals = self.data.groupby(by=[ 'Operator','Part']).mean()['Measurement'].values
        parts = parts = self.data['Part'].unique()

        #unbiasing constants for estimating range. Used later in UCL/LCL calculation
        subgroup_size = 2
        x_labels = (np.array([parts]*self.n_ops)).flatten()
        x_vals = np.array([x for x in range(len(x_labels))])
        
        ax.plot(x_vals, y_vals, marker='o', markersize=10, color='blue')
        ax.set_xticks([x for x in range(len(x_labels))], x_labels)
        
        UCL = y_vals.mean() + 3*y_vals.std()/np.sqrt(self.n_ops)
        LCL = y_vals.mean() - 3*y_vals.std()/np.sqrt(self.n_ops) 
        grand_mean = y_vals.mean()
        ax.hlines(y=[LCL,UCL], xmin=0, xmax=len(x_labels), color='red')
        ax.hlines(y=grand_mean, xmin=0, xmax=len(x_labels), color='green')
        stages = x_vals[np.where(x_vals%max(parts)==0)]
        ax.vlines(x=stages, ymin=min(min(y_vals), LCL), ymax=max(UCL,max(y_vals)), linestyle='--', color='grey', alpha=.4)
        
        ax.set_title('X-Bar Chart Chart by Operator')
        ax.set_ylabel('Sample Mean')
        ax.set_xlabel('Part')

class part_by_operator_interaction(plotter):
    def __init__(self, GRR):
        self.data = GRR.data
        self.n_ops = GRR.n_operators
        
    def plot(self, ax):
        operators = self.data['Operator'].unique()
        if(len(operators) > 10):
            raise ValueError('Too many operators to plot. Max:10')
        else:
            markers = ['o', 's', '^', 'D', 'p', '+', 'x', 'P', '*', '2']

            for operator, marker in zip(operators, markers):
                df = self.data[self.data['Operator']==operator]
                ax.plot(df['Part'].unique(), df.groupby(by='Part').mean(numeric_only=True)['Measurement'].values, marker=marker, markersize=10, label=operator)

            ax.set_title('Part * Operator Interaction')
            ax.set_ylabel('Part Mean')
            ax.set_xlabel('Part')
            ax.legend(title='Operator')

        
def GRRSixPack(GRR, figsize=(20,10)):
    fig, axs = plt.subplots(3,2, figsize=figsize)
    
    plt_objs = [components_of_variation, measurement_by_part, r_chart_by_operator, 
                measurement_by_operator, x_bar_chart_by_operator, part_by_operator_interaction]
    
    for obj, ax in zip(plt_objs, axs.ravel()):
        obj(GRR).plot(ax)
    plt.tight_layout()
    






    
    
    
    
    
    