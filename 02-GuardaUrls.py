# Importar a classe para utilizar o Banco de Dados
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time

def criaArquivos(arq,result):
    for r in result:
        try:
            url = r[0]["ee"]
            titulo = r[0]["title"]
            autor = r[1]["autor"]
            texto = []
            
            texto.append('Titulo{')
            texto.append(titulo)
            texto.append('}\n')
            texto.append('Autor{')
            texto.append(autor)
            texto.append('}\n')
            texto.append('URL{')
            texto.append(url)
            texto.append('}\n')
            
            arq.writelines(texto)
        except:
            continue;


inicio = time.time()

# conecta ao banco
db = GraphDatabase("http://localhost:7474", username="neo4j", password="admin")

# consulta no banco
q1='MATCH (n:Inproceedings)-[]->(s:Autor) WHERE left(n.ee,35) = "http://doi.ieeecomputersociety.org/" RETURN n,s'
q2='MATCH (n:Inproceedings)-[]->(s:Autor) WHERE left(n.ee,16) = "https://doi.org/" RETURN n,s'
q3='MATCH (n:Article)-[]->(s:Autor) WHERE left(n.ee,35) = "http://doi.ieeecomputersociety.org/" RETURN n,s'
q4='MATCH (n:Article)-[]->(s:Autor) WHERE left(n.ee,16) = "https://doi.org/" RETURN n,s'

result1 = db.query(q1,returns=(client.Node,client.Node))
result2 = db.query(q2,returns=(client.Node,client.Node))
result3 = db.query(q3,returns=(client.Node,client.Node))
result4 = db.query(q4,returns=(client.Node,client.Node))

arq1 = open('urls_IEEE-Inproceeding.txt', 'w')
arq2 = open('urls_Outros-Inproceeding.txt', 'w')
arq3 = open('urls_IEEE-Article.txt', 'w')
arq4 = open('urls_Outros-Article.txt', 'w')

criaArquivos(arq1,result1)
arq1.close()
criaArquivos(arq2,result2)
arq2.close()
criaArquivos(arq3,result3)
arq3.close()
criaArquivos(arq4,result4)
arq4.close()

print('urls_IEEE-Inproceeding.txt Criado\n')
print('urls_Outros-Inproceeding.txt Criado\n')
print('urls_IEEE-Article.txt Criado\n')
print('urls_Outros-Article.txt Criado\n')

fim = time.time()
print("\nTEMPO DE EXECUCAO: ",fim - inicio,"s")
