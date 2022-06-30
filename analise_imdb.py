# %%

import sqlite3 as sql
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

from IPython.display import display # para imprimir as tabelas no terminal no estilo do jupyter notebook
from time import time
from sklearn.feature_extraction.text import CountVectorizer
from sympy import expand

sns.set_theme(style = "whitegrid")

# %%
#abrindo a conexão com o bando de dados imdb.db
con = sql.connect('imdb.db')

# %%
# as querys são feitas pelo pandas usando instruções sql
# Primeiro, vamos listar as tabelas no banco de dados

com1 = 'SELECT name as table_name from sqlite_master WHERE type = "table"'
tabelas = pd.read_sql_query(com1, con)
display(tabelas)

# %%
# Agora vamos checar os tipos de dados em cada tabela

table_names = tabelas.values.tolist()

for x in table_names:

    com2 = "PRAGMA TABLE_INFO({})".format(x[0])
    answer = pd.read_sql_query(com2, con)
    print("Esquema da tabela: {}".format(x[0]))
    display(answer)
    print(80*'-' + '\n')

# %%
# Vamos conferir uma amostra de cada uma das tabelas no banco de dados

for x in table_names:
    com = "SELECT * FROM {} LIMIT 5".format(x[0])
    tabela = pd.read_sql_query(com, con)
    print("Amostra da tabela: {}".format(x[0]))
    display(tabela)
    print(80*'-' + '\n')


# %%
# 1 - Quais as categorias de filmes mais comuns no IMDB?

query1 = "SELECT type, count(*) as count from titles group by type"
movie_types = pd.read_sql_query(query1, con)

# adicionando a coluna com dados percentuais
movie_types['percentual'] = (100*movie_types['count']/(movie_types['count'].sum())).round(2)

print(80*'-' + '\n')
print("Quais as categorias de filmes mais comuns no IMDB")
display(movie_types)

# %%
# Gráfico de pizza com os dados
fig = plt.figure(figsize = (5,5))
plt.pie(movie_types['percentual'].values.tolist())
fig.show()

# %%
# Temos muitas categorias de filmes com porcentagens inexpressivas. Portanto, podemos agrupá-las numa única categoria, 'others'. Para que a categoria não seja agrupada em 'others', deve ter um percentual acima de 5%

# Selecionado os tipos que não serão agrupados
majority = movie_types[movie_types['percentual'] >= 5]

# agrupando as outras categorias
others = movie_types[movie_types['percentual'] < 5].sum()
others['type'] = 'others'

# combinando as novas categorias
per_movies = majority.append(others, ignore_index = True).sort_values(by = 'percentual', ascending = False, ignore_index = True)

# %%
types = per_movies['type'].values
for i in range(len(types)):
    types[i] = types[i] + ' [' + str(per_movies['percentual'][i]) + '%]'

# %%
# Gráfico de pizza com os dados
fig = plt.figure(figsize = (5,5))
plt.pie(per_movies['percentual'].values, wedgeprops = {'width': 0.8}, radius = 2.7)
plt.legend(labels = types, loc = 'center', prop = {'size': 14})
plt.title('Distribuição por Categoria', loc = 'Center', fontdict = {'fontsize':20, 'fontweight':20})
fig.show()
fig.savefig('movies_categories.pdf')

# %%
# 2 - Qual o número de títulos por gênero?

# Os 

com = '''SELECT genres, count(*) as counts FROM titles
         group by genres'''
table_types = pd.read_sql_query(com, con)
display(table_types.head())

# %%
# Retirando um valor nulo da tabela, provavelmente filmes cadastrados incorretamente
table_types = table_types.loc[table_types['genres'] != r'\N']

# Lista de gêneros misturados
genres_list = table_types['genres'].values

temp_dict = {}

for x in genres_list:
    l = x.lower().split(',')
    
    for y in l:
        if y.lower() in temp_dict.keys():
            temp_dict[y.lower()] += table_types.loc[table_types['genres'] == x, 'counts']
        else:
            temp_dict[y.lower()] = table_types.loc[table_types['genres'] == x, 'counts']

# %%


u = table_types['genres'].str.lower().str.split(pat = ',', expand = True)

ddd = pd.get_dummies(u, prefix= {0:'', 1:'', 2:''}, prefix_sep='')

ddd = ddd.drop(columns=[r'\n'])

ddd.loc[ddd.index[-1] + 1, :] = ddd.columns

uuu = ddd.groupby(by= ddd.columns, axis = 'columns', as_index = True).sum()

# %%
