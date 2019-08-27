import mysql.connector
import math

# Conecta com o banco MySQL local.
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="ic1"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT count(*) FROM artigo")

myresult = mycursor.fetchall()

N = myresult[0][0] # Número total de artigos na base

mycursor.execute("SELECT LOWER(nome_kw),count(artigo_id) as nVezes FROM `keyword` GROUP by nome_kw")

myresult = mycursor.fetchall()

dict_kw_freq = dict(myresult)

dict_idf_kw= dict()

for x, y in dict_kw_freq.items():
    aux = N/y
    dict_idf_kw[x] = math.log(aux,10) # Dicionário de IDF de cada Keyword

mycursor.execute("SELECT autor_id,count(autor_id),LOWER(nome_kw) from teste GROUP BY nome_kw,autor_id")

myresult = mycursor.fetchall()

tf_idf = []

for i in myresult:
    tf = 1 + math.log(i[1],10)
    aux = tf * dict_idf_kw[i[2]]
    tf_idf.append((i[0],i[2],aux))

for z in tf_idf:
    sql = "INSERT INTO grau_comp_especifica VALUE (%s,%s,%s)"
    val = (z[0],z[1],z[2])
    mycursor.execute(sql,val)
    

    
'''
# fazer o TF com relação ao número de vezes que uma KW aparece nos documentos de um autor.
CREATE VIEW teste as select autores.autor_id,keyword.nome_kw
from autores INNER join keyword on autores.artigo_id = keyword.artigo_id
SELECT autor_id,count(autor_id),nome_kw from teste GROUP BY nome_kw,autor_id`
'''
