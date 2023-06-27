import numpy as np
import pandas as pd
from scipy import stats

def read_grr_data(path):
    df = pd.read_excel(path)
    df = df.sort_values(by=['Operator','Part'])
    return df

def sumSquares(GRR, interaction=True):
    df = GRR.data
    grand_mean = df['Measurement'].mean()
    SS_Total = np.sum((df['Measurement'].values - grand_mean)**2)

    SS_Part = GRR.n_operators * GRR.n_repeats * np.sum((df.groupby(by='Part').mean()['Measurement'].values - grand_mean)**2)
    SS_Operator = GRR.n_parts * GRR.n_repeats * np.sum((df.groupby(by='Operator').mean()['Measurement'].values - grand_mean)**2)

    if(interaction):
        SS_Repeatability = 0

        for part in df['Part'].unique():
            for operator in df['Operator'].unique():
                pbo = df[(df['Part']==part) & (df['Operator']==operator)]['Measurement'].values
                pbo_mean = pbo.mean()
                SS_Repeatability += np.sum((pbo - pbo_mean)**2)
        SS_Part_by_Operator = SS_Total - SS_Part - SS_Operator
        return {'SS_Total': SS_Total, 'SS_Part': SS_Part, 'SS_Operator': SS_Operator, 'SS_Part_by_Operator': SS_Part_by_Operator, 'SS_Repeatability': SS_Repeatability}
    else:
        SS_Repeatability = SS_Total - SS_Part - SS_Operator
        return {'SS_Total': SS_Total, 'SS_Part': SS_Part, 'SS_Operator': SS_Operator, 'SS_Repeatability': SS_Repeatability}

    
def dofs(GRR, interaction=True):
    df = GRR.data
    DOF_Part = GRR.n_parts - 1
    DOF_Operator = GRR.n_operators - 1
    DOF_Total = GRR.n_parts * GRR.n_operators * GRR.n_repeats - 1
    if(interaction):
        DOF_Part_by_Operator = DOF_Part * DOF_Operator
        DOF_Repeatability = GRR.n_parts * GRR.n_operators * (GRR.n_repeats - 1)
        return {'DOF_Part': DOF_Part, 'DOF_Operator': DOF_Operator, 'DOF_Part_by_Operator': DOF_Part_by_Operator, 'DOF_Repeatability': DOF_Repeatability, 'DOF_Total': DOF_Total}
    else:
        DOF_Repeatability = DOF_Total - DOF_Part - DOF_Operator
        return {'DOF_Part': DOF_Part, 'DOF_Operator': DOF_Operator, 'DOF_Repeatability': DOF_Repeatability, 'DOF_Total': DOF_Total}


    
def mean_squares(GRR, interaction=True):
    ssqs = sumSquares(GRR, interaction=interaction)
    dof = dofs(GRR, interaction=interaction)

    MS = lambda x: ssqs['SS_'+x]/dof['DOF_'+x]

    MS_Part = MS('Part')
    MS_Operator = MS('Operator')
    MS_Repeatability = MS('Repeatability')
    if(interaction):
        MS_Part_by_Operator = MS('Part_by_Operator')
        return {'MS_Part': MS_Part, 'MS_Operator': MS_Operator, 'MS_Part_by_Operator': MS_Part_by_Operator, 'MS_Repeatability': MS_Repeatability}
    else:
        return {'MS_Part': MS_Part, 'MS_Operator': MS_Operator, 'MS_Repeatability': MS_Repeatability}
        
def Fs(GRR, interaction=True):
    MS = mean_squares(GRR, interaction=interaction)

    if(interaction):
        F_Part = MS['MS_Part']/MS['MS_Part_by_Operator']
        F_Operator = MS['MS_Operator']/MS['MS_Part_by_Operator']
        F_Part_by_Operator = MS['MS_Part_by_Operator']/MS['MS_Repeatability']
        return {'F_Part': F_Part, 'F_Operator': F_Operator, 'F_Part_by_Operator': F_Part_by_Operator}
    else:
        F_Part = MS['MS_Part']/MS['MS_Repeatability']
        F_Operator = MS['MS_Operator']/MS['MS_Repeatability']
        return {'F_Part': F_Part, 'F_Operator': F_Operator}
        
def p_values(GRR, interaction=True):
    F_values = Fs(GRR, interaction=interaction)
    dof = dofs(GRR, interaction=interaction)
    p = lambda F, df1, df2: stats.f.cdf(F, df1, df2)
    
    if(interaction):
        p_Part = p(F_values['F_Part'], dof['DOF_Part'], dof['DOF_Part_by_Operator'])
        p_Operator = p(F_values['F_Operator'], dof['DOF_Operator'], dof['DOF_Part_by_Operator'])
        p_Part_by_Operator = p(F_values['F_Part_by_Operator'], dof['DOF_Part_by_Operator'], dof['DOF_Repeatability'])
        return {'p_Part': p_Part, 'p_Operator': p_Operator, 'p_Part_by_Operator': p_Part_by_Operator} 
    
    else:
        p_Part = p(F_values['F_Part'], dof['DOF_Part'], dof['DOF_Repeatability'])
        p_Operator = p(F_values['F_Operator'], dof['DOF_Operator'], dof['DOF_Repeatability'])
        return {'p_Part': p_Part, 'p_Operator': p_Operator} 

class GRR(object):
    
    def __init__(self, data):
        self.data = data #expects data in pandas dataframe with balanced operators, parts, replicates, etc.
        self.n_operators = len(self.data['Operator'].unique())
        self.n_parts = len(self.data['Part'].unique())
        self.n_repeats = len(self.data['Repeat'].unique())
        
    def ANOVA_Table(self, alpha=.25):
        ps = p_values(self)
        df = pd.DataFrame(columns=['Source', 'DF', 'SS', 'MS', 'F', 'p'])
        df_add = lambda source, dof, ss, ms, F, p: pd.DataFrame({'Source': source, 'DF': dof, 'SS':ss, 'MS': ms, 'F': F, 'p':p})
        
        if ps['p_Part_by_Operator'] > alpha:
            print(f"Alpha for interaction term {np.round(ps['p_Part_by_Operator'],3)}, removing term from model....")
            ssqs = sumSquares(self, interaction=False)
            dof = dofs(self, interaction=False)
            msqs = mean_squares(self, interaction=False)
            F_s = Fs(self, interaction=False)
            ps = p_values(self, interaction=False)
            df = df_add(['Part', 'Operator', 'Repeatability', 'Total'], 
                        [dof['DOF_Part'], dof['DOF_Operator'], dof['DOF_Repeatability'], dof['DOF_Total']], 
                        [ssqs['SS_Part'], ssqs['SS_Operator'], ssqs['SS_Repeatability'], ssqs['SS_Total']], 
                        [msqs['MS_Part'], msqs['MS_Operator'], msqs['MS_Repeatability'], ''], 
                        [F_s['F_Part'], F_s['F_Operator'], '', ''], 
                        [ps['p_Part'], ps['p_Operator'], '', '']) 
        else:
            ssqs = sumSquares(self, interaction=True)
            dof = dofs(self, interaction=True)
            msqs = mean_squares(self, interaction=True)
            F_s = Fs(self, interaction=True)
            ps = p_values(self, interaction=True)
            df = df_add(['Part', 'Operator', 'Part * Operator', 'Repeatability', 'Total'], 
                        [dof['DOF_Part'], dof['DOF_Operator'], dof['DOF_Part_by_Operator'], dof['DOF_Repeatability'], dof['DOF_Total']], 
                        [ssqs['SS_Part'], ssqs['SS_Operator'], ssqs['SS_Part_by_Operator'], ssqs['SS_Repeatability'], ssqs['SS_Total']], 
                        [msqs['MS_Part'], msqs['MS_Operator'], msqs['MS_Part_by_Operator'], msqs['MS_Repeatability'], None], 
                        [F_s['F_Part'], F_s['F_Operator'], F['F_Part_by_Operator'], None, None], 
                        [ps['p_Part'], ps['p_Operator'], ps['p_Part_by_Operator'], None, None]) 
            
        return df
    
    def varComp(self, alpha = 0.25):
        ps = p_values(self)
        df = pd.DataFrame(columns=['Source', 'VarComp', '% Contribution (of VarComp)'])
        df_add = lambda source, varComp, pct_contribution: pd.DataFrame({'Source': source, 'VarComp': varComp, '% Contribution (of VarComp)':pct_contribution})
        
        if ps['p_Part_by_Operator'] > alpha:
            msqs = mean_squares(self, interaction=False)
            vc_repeatability = msqs['MS_Repeatability']
            vc_operator = (msqs['MS_Operator'] - msqs['MS_Repeatability'])/(self.n_parts * self.n_repeats)
            vc_parts = (msqs['MS_Part'] - msqs['MS_Repeatability'])/(self.n_operators * self.n_repeats)
            vc_reproducibility = vc_operator
            vc_total_grr = vc_repeatability + vc_reproducibility
            total_var = vc_total_grr + vc_parts
            df = df_add(['Total Gage R&R', '\tRepeatability', '\tReproducibility', '\t\tOperator', 'Part-to-Part', 'Total Variation'],
                        [x if x>0 else 0 for x in [vc_total_grr, vc_repeatability, vc_reproducibility, vc_operator, vc_parts, total_var]],
                        [x if x>0 else 0 for x in np.array([vc_total_grr, vc_repeatability, vc_reproducibility, vc_operator, vc_parts, total_var])/total_var])
            return df
            
        else:
            msqs = mean_squares(self, interaction=True)
            vc_repeatability = msqs['MS_Repeatability']
            vc_operator = (msqs['MS_Operator'] - msqs['MS_Part_by_Operator'])/(self.n_parts * self.n_repeats)
            vc_part_by_operator = (msqs['MS_Part_by_Operator'] - msqs['MS_Repeatability'])/(self.n_repeats)
            vc_parts = (msqs['MS_Part'] - msqs['MS_Part_by_Operator'])/(self.n_operators * self.n_repeats)
            vc_reproducibility = vc_operator - vc_part_by_operator
            vc_total_grr = vc_repeatability + vc_reproducibility
            total_var = vc_total_grr + vc_parts
            df = df_add(['Total Gage R&R', '\tRepeatability', '\tReproducibility', '\t\t Part * Operator', '\t\tOperator', 'Part-to-Part', 'Total Variation'],
            [x if x>0 else 0 for x in [vc_total_grr, vc_repeatability, vc_reproducibility, vc_operator, vc_part_by_operator, vc_parts, total_var]],
            [x if x>0 else 0 for x in np.array([vc_total_grr, vc_repeatability, vc_reproducibility, vc_operator, vc_part_by_operator, vc_parts, total_var])/ total_var])
            return df
    
    def GRR(self, study_var_coeff=5.15, **kwargs):
        variance_df = self.varComp()
        components = variance_df['Source'].unique()
        stds = np.sqrt(variance_df['VarComp'].values)
        studyVars = study_var_coeff * stds
        
        if('tolerance' in kwargs):
            pct_tols = studyVars/kwargs.get('tolerance')
            return pd.DataFrame({'Source': components, 'StdDev': stds, f'Study Var {study_var_coeff} * stdDev':studyVars, '% Study Var': studyVars/studyVars[-1], '% Tolerance': pct_tols})
        else:
            return pd.DataFrame({'Source': components, 'StdDev': stds, f'Study Var {study_var_coeff} * stdDev':studyVars, '% Study Var': studyVars/studyVars[-1]})

        