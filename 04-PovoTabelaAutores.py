import re
import mysql.connector

# Conecta com o banco MySQL local.
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="ic1"
)

arquivo = open('urls_Outros-Inproceeding.txt', 'r') # É possível alterar p/ "registroIEEE.txt" ou "registroACM.txt".

# Lê linhas do arquivo.
conteudo = arquivo.readlines()
arquivo.close()
conteudo_separado_por_linha = []

# Retira "\n" e "}" das linhas. 
for linha in conteudo:
    linha = linha.replace('}\n', '')
    conteudo_separado_por_linha.append(linha)

mycursor = mydb.cursor()
aux = []
i = 0

for x in conteudo_separado_por_linha:

    if re.search('Titulo{', x, re.IGNORECASE):
        titulo = x.replace('Titulo{','')
        sql = "SELECT * FROM artigo WHERE titulo = %s"
        val = (titulo,)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        if len(myresult) == 1:
            aux.append(x)
            i = 1
            
    if i != 0:
        if re.search('URL{', x, re.IGNORECASE):
            i = 0
        if re.search('Autor{', x, re.IGNORECASE):
            aux.append(x)
            
# Loop p/ cada linha do arquivo.
for x in aux:

    if re.search('Titulo{', x, re.IGNORECASE):
        titulo = x.replace('Titulo{','')
        sql = "SELECT artigo_id FROM artigo WHERE titulo = %s"
        val = (titulo,)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        id_titulo = myresult[0][0]
            
    if re.search('Autor{', x, re.IGNORECASE):
        autor = x.replace('Autor{','')
        sql = "SELECT docente_id FROM docente WHERE nome_docente = %s"
        val = (autor.upper(),)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        id_autor = myresult[0][0]
        sql = "SELECT * FROM autores WHERE autor_id = %s AND artigo_id = %s"
        val = (id_autor,id_titulo)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            sql = "INSERT INTO autores VALUES(%s,%s)"
            val = (id_autor,id_titulo)
            mycursor.execute(sql,val)
        

# Faz commit no banco e fecha arquivo.
mydb.commit()
