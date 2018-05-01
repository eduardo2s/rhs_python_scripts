# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 13:17:11 2018

@author: eduardo
"""
import pymysql
import pandas as pd
import re
import datetime as dt
from html.parser import HTMLParser
from collections import Counter

conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           passwd='',
                           db='rhs')
cur = conn.cursor()
cur.execute("select post_content as post, date(post_date) as Data, year(post_date) as Ano from rhs_wpress.rhs_posts where post_type = 'post' and post_content <> ''")

# Drupal base
#cur.execute("SELECT FROM_UNIXTIME(A.created, '%Y') AS Data, C.type AS Tipo, B.comment_body_value AS Comentario FROM comment A INNER JOIN field_data_comment_body B ON A.cid = B.entity_id JOIN node C ON A.nid = C.nid WHERE C.type LIKE 'blog'")

# armazena o nome de cada uma das colunas do banco
row_headers=[x[0] for x in cur.description]

# cria uma lista com os dados do banco
rhs_data = []
for row in cur:
    rhs_data.append(dict(zip(row_headers,row)))

# Transform the first item in the list into a dictionary
# transforma a primeira entrada da lista em um dicionário
rhs_dict = rhs_data[0]

df = pd.DataFrame(rhs_data)

# usa o próprio pandas para juntar os dados
df_new = pd.DataFrame(df.groupby('Data')['post'].apply(' '.join))
# Copia as datas do groupby do index para uma coluna
df_new['Data'] = df_new.index
# Reseta o index para ficar númerado de acordo com a ordem dos items
df_new = df_new.reset_index(drop=True)
# Transforma as Datas em Strings (facilita para trabalhar)
df_new['Data'] = df_new['Data'].apply(lambda x: dt.datetime.strftime(x, '%d/%m/%Y'))

df_new.info()

dflist = df_new['post'].tolist()

# Limpa erros de códificação das postagens (uma vez que tem erros de ASCII não reconhece caracteres como "ç")
df_html =[]
for item in dflist:
       parser = HTMLParser()
       df_html.append(parser.unescape(item))

df_new['post'] = df_html

# tratar o texto
def standardize_text(df, text_field):
    df[text_field] = df[text_field].str.replace(r"http\S+", "")
    df[text_field] = df[text_field].str.replace(r"http", "")
    df[text_field] = df[text_field].str.replace(r"@\S+", "")
    df[text_field] = df[text_field].str.replace(r"[\,\$\&\*\%\(\)\~\-\"\^\+\#\/|0-9]", " ")
    df[text_field] = df[text_field].str.replace(r"[\.\=\'\:\;\?\!\_\...]", " ")
    df[text_field] = df[text_field].str.replace(r"@", "at")
    df[text_field] = df[text_field].str.replace(r"<.*?>", " ")
    df[text_field] = df[text_field].str.lower()
    return df

df_new = standardize_text(df_new, 'post')

# Remover múltiplos espaços em branco tornando o texto em algo único
df_aux = []
for word in df_new.get('post'):
       df_aux.append(word.split())

# Juntar novamente as palavras de cada um dos post para o texto ficar uniforme
final_correction = [ ' '.join(l) for l in df_aux]

df_new['post'] = final_correction


# Remover caracteres repetidos
from nltk.corpus import wordnet

def remove_repeated_characters(tokens):
    repeat_pattern = re.compile(r'(\w*)(\w)\2(\w*)')
    match_substitution = r'\1\2\3'
    def replace(old_word):
        if wordnet.synsets(old_word):
            return old_word
        new_word = repeat_pattern.sub(match_substitution, old_word)
        if new_word != old_word:
            return replace(new_word)
        else:
            return new_word
    correct_tokens = [replace(word) for word in tokens]
    return correct_tokens

remove_repeated_chars = []
for text in df_new.get('post'):
    txt = text.split()
    remove_repeated_chars.append(remove_repeated_characters(txt))

remove_repeated_chars = [ ' '.join(l) for l in remove_repeated_chars]

df_new['post'] = remove_repeated_chars


# remove stopwords
# Por serem textos mais completos usar um arquivo próprio para stopwords
pathStopwords = "C:/Users/eduar/Documents/RHS compara/nuvem de palavra/stop_words.txt"
# Read in and split the stopwords file.
with open(pathStopwords, 'r') as f:
    stop_words = f.read().split("\n")

#LIST WITH NO STOPWORDS
dflist = df_new['post'].tolist()

my_new_list = [[word for word in text.split() if word not in stop_words] for text in dflist]
my_new_list = [ ' '.join(l) for l in my_new_list]
df_new['post'] = my_new_list


# remove caracteres soltos que possam existir no texto
aux_single_letter =[[word for word in text.split() if len(word)>1] for text in df_new.get('post')]
aux_single_letter = [ ' '.join(l) for l in aux_single_letter]
df_new['post'] = aux_single_letter

# Pickle files
df_new.to_pickle("C:/Users/eduar/Documents/RHS compara/nuvem de palavra/rhs_word_cloud.pkl")

df_new = pd.read_pickle("C:/Users/eduar/Documents/RHS compara/nuvem de palavra/rhs_word_cloud.pkl")

# Contar palavras por dia
wordstring = df_new['post'].tolist()

wordlist = []
for wordlists in df_new.get('post'):
    wordlist.append(wordlists.split())

wordfreq = []
c = 0
for c in range(len(wordlist)):
    if c <= 3228:
        wordfreq.append(Counter(wordlist[c]))

wordfreqmost = []
for counter in wordfreq:
    wordfreqmost.append(Counter(counter).most_common(20))

df_teste = pd.DataFrame(wordfreqmost)
df_teste.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']

d = list(zip(df_teste.A,df_teste.B,df_teste.C,df_teste.D,df_teste.E,df_teste.F,
             df_teste.G,df_teste.H,df_teste.I,df_teste.J,df_teste.K,
             df_teste.L,df_teste.M,df_teste.N,df_teste.O,df_teste.P,
             df_teste.Q,df_teste.R,df_teste.S,df_teste.T))

df_final = pd.DataFrame()
df_final['Data'] = df_new['Data']
df_final['Concatenado'] = pd.Series(d)

df_final.to_csv("C:/Users/eduar/Documents/RHS compara/nuvem de palavra/rhs_word_cloud.csv", encoding='UTF-8', index=False)
