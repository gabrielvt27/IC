'''
    Programa modificado por Gabriel Valentin Tiburcio,
    aluno da graduação em Sistemas de Informação na UFU.
    Pesquisa "Exploração de Estratégias para Mineração de Expertise",
    orientada pela professora Maria Camila Nardini Barioni.

    Programa é baseado no script feito por "" da UFJF orientado por
    "" que o disponibilizou para auxilio da pesquisa.

    "Colocar referência da pesquisa aqui".
    -----------------------------------------------------------------

    Programa realiza extração do conteúdo do arquivo "dblp.xml" e carrega
    os objetos no banco NEO4J. Posteriormente o conteúdo do banco será
    utilizado pelos programas "02-WebScrapingACMeIEEE.py", "02-WebScrapingIEEE.py"
    e "02-WebScrapingACM.py".

    O arquivo xml é formatado no esquema a seguir:

        <article mdate="2017-05-28" key="journals/acta/HuT72">
        <author>T. C. Hu</author>
        <author>K. C. Tan</author>
        <title>Least Upper Bound on the Cost of Optimum Binary Search Trees.</title>
        <journal>Acta Inf.</journal>
        <volume>1</volume>
        <year>1972</year>
        <pages>307-310</pages>
        <url>db/journals/acta/acta1.html#HuT72</url>
        <ee>https://doi.org/10.1007/BF00289510</ee>
        </article>

    OBS: Essa formatação é para a tag principal "article", porém temos outras tags
    principais como "www", "incollection", "inproceedings" e "proceedings".
'''

# EXEMPLO XML ACIMA

import xml.sax # biblioteca padrão do python
from xml.sax.saxutils import unescape
from neo4jrestclient.client import GraphDatabase #pip install neo4j e pip install neo4jrestclient

db = GraphDatabase("http://localhost:7474", username="neo4j", password="admin")


class articleHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentDada = " "

        self.article = None
        self.inproceedings = None
        self.www = None
        self.incollection = None
        self.proceedings = None

        self.author = None
        self.title = None
        self.pages = None
        self.year = None
        self.journal = None
        self.number = None
        self.ee = None
        self.url = None
        self.volume = None
        self.key =  None
        self.mdate = None
        self.note = None
        self.booktitle = None
        self.crossref = None
        self.publisher = None
        self.series = None
        self.isbn = None
        self.editor = None


    def startElement(self, tag, attributes):
        '''
        evento startElement do SAX. disparado quando o processador SAX identifica
	    a abertura de uma tag.
        :param tag: 
        :param attributes: 
        :return: 
        '''

        self.CurrentDada = tag

        if tag == "article":
            self.article = tag
            self.key = attributes["key"]
            self.mdate = attributes["mdate"]

        if tag == "www":
            self.www = tag
            self.key = attributes["key"]
            self.mdate = attributes["mdate"]

        if tag == "inproceedings":
            self.inproceedings = tag
            self.key = attributes["key"]
            self.mdate = attributes["mdate"]

        if tag == "proceedings":
            self.proceedings = tag
            self.key = attributes["key"]
            self.mdate = attributes["mdate"]

        if tag == "incollection":
            self.incollection = tag
            self.key = attributes["key"]
            self.mdate = attributes["mdate"]

    def characters(self, content):
            '''
            evento characters do SAX. É onde podemos recuperar as informações texto
	        * contidas no documento XML (textos contidos entre tags).
            :param content: 
            :return: 
            '''
            
            global autor_aux, flag_autor, nomes_ordenados
            if self.CurrentDada == "article" and content == "article":
                self.article = content
            elif self.CurrentDada == "www" and content == "www":
               self.www = content
            elif self.CurrentDada == "inproceedings" and content == "inproceedings":
               self.inproceedings = content
            elif self.CurrentDada == "proceedings" and content == "proceedings":
               self.proceedings = content
            elif self.CurrentDada == "incollection" and content == "incollection":
               self.incollection = content

            elif self.CurrentDada == "author":
                if binary_search(nomes_ordenados, content):
                    self.author = content
                    author = db.labels.create("Autor")
                    au = db.nodes.create(autor=self.author, key = self.key)
                    print("Autor: ",content)
                    author.add(au)
                    
                    #Esse codigo abaixo auxilia nas relações entre Nós
                    global autores
                    autores.append(au)

            elif self.CurrentDada == "editor":
                if binary_search(nomes_ordenados, content):
                    self.editor = content
                    editor = db.labels.create("Editor")
                    e1 = db.nodes.create(editor=self.editor, key=self.key)
                    print("Editor: ",content)
                    editor.add(e1)

                    global editores
                    editores.append(e1)

            elif self.CurrentDada == "title":
                self.title = content
            elif self.CurrentDada == "pages":
                self.pages = content
            elif self.CurrentDada == "year":
                self.year = content
            elif self.CurrentDada == "volume":
                self.volume = content
            elif self.CurrentDada == "journal":
                self.journal = content
            elif self.CurrentDada == "number":
                self.number = content
            elif self.CurrentDada == "ee":
                self.ee = content
            elif self.CurrentDada == "url":
                self.url = content
            elif self.CurrentDada == "note":
                self.note = content
            elif self.CurrentDada == "booktitle":
                self.booktitle = content
            elif self.CurrentDada == "crossref":
                self.crossref = content
            elif self.CurrentDada == "publisher":
                self.publisher = content
            elif self.CurrentDada == "series":
                self.series = content
            elif self.CurrentDada == "isbn":
                self.isbn = content

                
    def endElement(self, tag):
        '''
        O evento endElement é disparado quando o processador SAX identifica o fechamento de uma tag
        Já o evento endDocument é disparado quando o SAX chega ao final do documento XML

        :param tag: 
        :return: 
        '''
        global autores
        global editores
        if self.CurrentDada == "/":
            if (self.author != None):

                if (self.article == "article"):
                    articlee = db.labels.create("Article")  # user ->person
                    a1 = db.nodes.create(title=self.title, pages=self.pages,
                                         year=self.year, volume=self.volume,journal=self.journal,
                                         number=self.number, ee=self.ee, url=self.url,key=self.key, mdate=self.mdate)
                    articlee.add(a1)
                    #Esse código abaixo irá adicionar os relacionamentos de cada autor para com seu Artigo
                    #global autores
                    nome_relacao_autor = "Escrito"
                    for i in range(len(autores)):
                        autor_vector = autores[i]
                        db.relationships.create(a1, nome_relacao_autor, autor_vector)
                        i += 1
                    self.article = None
                    autores = []
                    
                if (self.www == "www"):
                    www = db.labels.create("WWW")
                    a1 = db.nodes.create(author=self.author, title=self.title, note=self.note, url=self.url, key=self.key, mdate=self.mdate)
                    www.add(a1)

                    nome_relacao_autor = "Escrito"
                    for i in range(len(autores)):
                        autor_vector = autores[i]
                        db.relationships.create(a1, nome_relacao_autor, autor_vector)
                        i += 1
                    self.article = None
                    autores = []
                    self.www = None

                if (self.inproceedings == "inproceedings"):
                    inproceedings = db.labels.create("Inproceedings")
                    a1 = db.nodes.create(author=self.author, title=self.title, pages=self.pages,
                                         year=self.year, volume=self.volume, booktitle=self.booktitle,
                                         crossref=self.crossref, publisher=self.publisher, series=self.series, ee=self.ee,
                                         isbn=self.isbn, key=self.key, mdate=self.mdate)
                    inproceedings.add(a1)

                    nome_relacao_autor = "Escrito"
                    for i in range(len(autores)):
                        autor_vector = autores[i]
                        db.relationships.create(a1, nome_relacao_autor, autor_vector)
                        i += 1
                    self.article = None
                    autores = []
                    self.inproceedings = None

                if (self.proceedings == "proceedings"):
                    proceedings = db.labels.create("Proceedings")
                    prcee1 = db.nodes.create(title=self.title,year=self.year, volume=self.volume, booktitle=self.booktitle,
                                         publisher=self.publisher, series=self.series, ee=self.ee, isbn=self.isbn,
                                         url= self.url, key=self.key, mdate=self.mdate)
                    proceedings.add(prcee1)

                    nome_relacao_editor = "Editou"
                    for i in range(len(autores)):
                        autor_vector = autores[i]
                        db.relationships.create(prcee1, nome_relacao_editor, autor_vector)
                        i += 1
                    self.article = None
                    autores = []
                    self.proceedings = None

                if (self.incollection == "incollection"):
                    incollection = db.labels.create("Incollection")
                    a1 = db.nodes.create(title=self.title,year=self.year, booktitle=self.booktitle,
                                         pages=self.pages, ee=self.ee, crossref=self.crossref,
                                         url= self.url, key=self.key, mdate=self.mdate)
                    incollection.add(a1)

                    nome_relacao_autor = "Escrito"
                    for i in range(len(autores)):
                        autor_vector = autores[i]
                        db.relationships.create(a1, nome_relacao_autor, autor_vector)
                        i += 1
                    self.article = None
                    autores = []
                    self.incollection = None

                    
                self.author = None
                self.editor = None
                self.title = None
                self.pages = None
                self.year = None
                self.journal = None
                self.number = None
                self.ee = None
                self.url = None
                self.volume = None
                self.key = None
                self.mdate = None
                self.note = None
                self.booktitle = None
                self.crossref = None
                self.publisher = None
                self.series = None
                self.isbn = None

        self.CurrentDada = "/"

def binary_search(theList,key):
    begin=0    
    end=len(theList)-1

    while(begin<=end):
        average=(begin+end)//2       
        if(theList[average]==key.upper()):
            return True
        else:    
            if(theList[average]>key.upper()):
                end=average-1
            else:
                begin=average+1
    return False


if (__name__ == "__main__"):
    arquivo = open('nomes.txt', 'r')
    lista = arquivo.readlines()
    arquivo.close()
    nomes = []
    for j in lista:
        nomes.append(j.replace("\n",""))

    nomes_ordenados = sorted(set(nomes))
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    Handler = articleHandler()
    parser.setContentHandler(Handler)
    autores = [] #Contem Objetos do tipo AUTOR
    editores = [] #Contem Objetos do tipo EDITOR
    parser.parse("dblp.xml")

    '''
    print("\n\nFim do Carregamento !!!\n\n")
    print("-----------------------------------------------------------------")
    print("\nLista de Autores carregados\n")
    for j in list_autores:
        print(j)
    '''
