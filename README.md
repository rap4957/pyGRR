# pyGRR
<h1> PyGRR: Gage R&R in Python! </h1>
The following code demonstrates usage of this package


```python
import pyGRR
```


```python
myData = pyGRR.read_grr_data('C:/users/ryanp/downloads/grr_wksht.xlsx')
myGRR = pyGRR.GRR(myData)
myGRR.ANOVA_Table()
```

    Alpha for interaction term 1.0, removing term from model....
    




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Source</th>
      <th>DF</th>
      <th>SS</th>
      <th>MS</th>
      <th>F</th>
      <th>p</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Part</td>
      <td>9</td>
      <td>1.170455</td>
      <td>0.130051</td>
      <td>1.931903</td>
      <td>0.940659</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Operator</td>
      <td>2</td>
      <td>0.548582</td>
      <td>0.274291</td>
      <td>4.074602</td>
      <td>0.979256</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Repeatability</td>
      <td>78</td>
      <td>5.250749</td>
      <td>0.067317</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>3</th>
      <td>Total</td>
      <td>89</td>
      <td>6.969786</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>
</div>




```python
myGRR.varComp()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Source</th>
      <th>VarComp</th>
      <th>% Contribution (of VarComp)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Total Gage R&amp;R</td>
      <td>0.074216</td>
      <td>0.914144</td>
    </tr>
    <tr>
      <th>1</th>
      <td>\tRepeatability</td>
      <td>0.067317</td>
      <td>0.829166</td>
    </tr>
    <tr>
      <th>2</th>
      <td>\tReproducibility</td>
      <td>0.006899</td>
      <td>0.084978</td>
    </tr>
    <tr>
      <th>3</th>
      <td>\t\tOperator</td>
      <td>0.006899</td>
      <td>0.084978</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Part-to-Part</td>
      <td>0.006970</td>
      <td>0.085856</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Total Variation</td>
      <td>0.081187</td>
      <td>1.000000</td>
    </tr>
  </tbody>
</table>
</div>




```python
myGRR.GRR(tolerance=1.467405)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Source</th>
      <th>StdDev</th>
      <th>Study Var 5.15 * stdDev</th>
      <th>% Study Var</th>
      <th>% Tolerance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Total Gage R&amp;R</td>
      <td>0.272427</td>
      <td>1.402999</td>
      <td>0.956109</td>
      <td>0.956109</td>
    </tr>
    <tr>
      <th>1</th>
      <td>\tRepeatability</td>
      <td>0.259456</td>
      <td>1.336197</td>
      <td>0.910585</td>
      <td>0.910585</td>
    </tr>
    <tr>
      <th>2</th>
      <td>\tReproducibility</td>
      <td>0.083061</td>
      <td>0.427764</td>
      <td>0.291511</td>
      <td>0.291511</td>
    </tr>
    <tr>
      <th>3</th>
      <td>\t\tOperator</td>
      <td>0.083061</td>
      <td>0.427764</td>
      <td>0.291511</td>
      <td>0.291511</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Part-to-Part</td>
      <td>0.083489</td>
      <td>0.429967</td>
      <td>0.293012</td>
      <td>0.293012</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Total Variation</td>
      <td>0.284933</td>
      <td>1.467405</td>
      <td>1.000000</td>
      <td>1.000000</td>
    </tr>
  </tbody>
</table>
</div>





