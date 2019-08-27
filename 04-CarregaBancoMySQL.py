'''
    Programa feito por Gabriel Valentin Tiburcio,
    aluno da graduação em Sistemas de Informação na UFU.
    Pesquisa "Exploração de Estratégias para Mineração de Expertise",
    orientada pela professora Maria Camila Nardini Barioni

    -----------------------------------------------------------------

    Programa realiza leitura do arquivo "registro.txt" com o conteúdo
    das inproceedings mineradas e armazena essas informações em um
    banco MySQL local.

    O arquivo é formato como no exemplo a seguir:
        Titulo{Pattern Recognition and Image Description by
            Suitable Textural Information.}
        Autor{Ricardo Augusto Rabelo Oliveira}
        Keywords{image texture,pattern recognition,textural
            information,image description,feature spaces,unsupervised
            segmentation,unsupervised classification,}
        Abstract{One of the difficulties of pattern recognition is
            developing a good evaluation of the classes presented in a
            scene. To suitably describe those classes it is necessary to
            find feature spaces which allow them to be distinguished from
            each other. We propose an unsupervised segmentation/classification
            technique associated with textural description and report the
            results obtained, which are quite encouraging.}

'''

import re
import mysql.connector

# Conecta com o banco MySQL local.
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="ic1"
)

arquivo = open('registro_ELSEVIER-Article.txt', 'r') # É possível alterar p/ "registroIEEE.txt" ou "registroACM.txt".

# Lê linhas do arquivo.
conteudo = arquivo.readlines()
arquivo.close()
conteudo_separado_por_linha = []

# Retira "\n" e "}" das linhas. 
for linha in conteudo:
    linha = linha.replace('}\n', '')
    conteudo_separado_por_linha.append(linha)

mycursor = mydb.cursor()

# Loop p/ cada linha do arquivo.
for x in conteudo_separado_por_linha:

    # Se for linha do Título entra aqui, trata a string e inseri no banco.
    if re.search('Titulo{', x, re.IGNORECASE):
        titulo = x.replace('Titulo{','')
        sql = "SELECT titulo FROM artigo WHERE titulo = %s"
        val = (titulo,)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            sql = "INSERT INTO artigo(titulo,classificacao) VALUES (%s,'inproceeding')"
            mycursor.execute(sql,val)
            
    # Se for linha das Keywords entra aqui, trata a string e inseri no banco.
    if re.search('Keywords{', x, re.IGNORECASE):
        sql = "SELECT keyword.artigo_id FROM keyword,artigo WHERE artigo.artigo_id = keyword.artigo_id AND %s = artigo.titulo"
        val = (titulo,)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            aux = x.replace('Keywords{','')
            aux = aux[:len(aux)-1]
            keywords = aux.split(';')
            keywords = sorted(set(keywords))
            for n in keywords:
                sql = "SELECT artigo_id FROM artigo WHERE titulo = %s"
                val = (titulo,)
                mycursor.execute(sql,val)
                myresult = mycursor.fetchone()
                sql = "INSERT INTO keyword(nome_kw,artigo_id) VALUES (%s,%s)"
                val = (n,myresult[0])
                mycursor.execute(sql,val)

    # Se for linha do Abstract entra aqui, trata a string e inseri no banco.
    if re.search('Abstract{', x, re.IGNORECASE):
        abstract = x.replace('Abstract{','')
        sql = "SELECT abstract FROM artigo WHERE titulo = %s"
        val = (titulo,)
        mycursor.execute(sql,val)
        myresult = mycursor.fetchone()
        if myresult[0] == None:
            sql = "UPDATE artigo SET abstract = %s WHERE titulo = %s"
            val = (abstract,titulo)
            mycursor.execute(sql,val)

# Faz commit no banco e fecha arquivo.
mydb.commit()
