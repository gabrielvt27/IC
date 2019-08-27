'''
    Programa feito por Gabriel Valentin Tiburcio,
    aluno da graduação em Sistemas de Informação na UFU.
    Pesquisa "Exploração de Estratégias para Mineração de Expertise",
    orientada pela professora Maria Camila Nardini Barioni

    -----------------------------------------------------------------

    Programa realiza extração do Abstract(resumo) das pesquisas contidas
    nas páginas Web da ACM, e extração das Keywords das pesquisas
    encontradas no BIBTEX dessa mesma página. Depois o conteúdo encontrado
    é armazenado em um arquivo denominado "registroACM.txt", onde será lido
    posteriormente pelo programa "03-CarregaBancoMySQL.py".

    O site segue o padrão desses exemplo a seguir:
        https://dl.acm.org/citation.cfm?doid=3019612.3019674
'''

import re
import time

# Importar a classe para abrir o navegador e usar suas funções
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# Importar a classe que contém as funções e aplicar um alias
from selenium.webdriver.support import expected_conditions as EC
# Importar classe para ajudar a localizar os elementos
from selenium.webdriver.common.by import By
# Importar a classe ActionChains responsável pelas manipulações
from selenium.webdriver.common.action_chains import ActionChains


# Função p/ extrair as keywords dos inproceedings
def pegakeywords(conteudo,titulo,autor,abstract,url):
    aux1 = conteudo.split(',')
    
    conteudo_separado_por_virgula = []
    string_de_keywords = []
    
    for n in aux1:
        n = n.replace('\n', '')
        conteudo_separado_por_virgula.append(n.replace('}',''))

    for i in conteudo_separado_por_virgula:
        if re.search('keywords = {', i, re.IGNORECASE):
            string_de_keywords.append(i.replace('keywords = {',''))
            aux2 = string_de_keywords[0]
            lista_keywords = aux2.split(';')
    
    texto = []
    texto.append('Titulo{')
    texto.append(titulo)
    texto.append('}\n')
    texto.append('Autor{')
    texto.append(autor)
    texto.append('}\n')
    texto.append('Keywords{')
    for j in lista_keywords:
        k=j.rjust(0).strip()
        texto.append(k)
        texto.append(';')
    texto.append('}\n')
    texto.append('Abstract{')
    texto.append(abstract)
    texto.append('}\n')
    texto.append('URL{')
    texto.append(url)
    texto.append('}\n')

    arq = open('registro_ACM-Inproceeding.txt', 'a')
    arq.writelines(texto)
    arq.close()


# ---------------------------------- Início do Programa -------------------------------- #

# Início do Programa
inicio = time.time()

arquivo = open('urls_Outros-Inproceeding.txt', 'r')

# Lê linhas do arquivo.
conteudo = arquivo.readlines()
arquivo.close()

conteudo_separado_por_linha = []
titulo = []
autor = []
url = []

# Retira "\n" e "}" das linhas. 
for linha in conteudo:
    linha = linha.replace('}\n', '')
    conteudo_separado_por_linha.append(linha)

for x in conteudo_separado_por_linha:
    if re.search('Titulo{', x, re.IGNORECASE):
        titulo.append(x.replace('Titulo{',''))
    elif re.search('Autor{', x, re.IGNORECASE):
        autor.append(x.replace('Autor{',''))
    elif re.search('URL{', x, re.IGNORECASE):
        url.append(x.replace('URL{',''))

esperar_carregar_abstract = '/html/body/div/div/div/div/div/div/div/div/div/p'

cont_inproceedings = 0 # contador de inproceedings
cont_not_found = 0 # contador de páginas não encontradas
cont_erro_pag = 0 # contador de páginas que não foi possível pegar o conteúdo
i = 0 # contador de inproceedings
cont = 0

pag_erro = []
pag_not_found = []

padrao_url = "https://dl.acm.org/"
padrao_not_found_url_acm = 'https://dl.acm.org/not-found'

for u in url:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    
    driver = webdriver.Chrome(chrome_options=options)
    wait = WebDriverWait(driver,30)
    actions = ActionChains(driver)
    
    driver.get(u)
    
    if padrao_url in driver.current_url:
        
        if padrao_not_found_url_acm in driver.current_url:
            pag_not_found.append(u)
            cont_not_found+=1
            cont+=1
            driver.quit()
        else:
            try:
                elemento = wait.until(EC.presence_of_element_located((By.ID, 'header')))
                elemento = wait.until(EC.presence_of_element_located((By.XPATH,esperar_carregar_abstract)))

                bib = driver.find_element_by_link_text('BibTeX')

                actions.click_and_hold(bib)

                actions.release(bib)

                actions.perform()

                elemento = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))

                pre = driver.find_element(By.TAG_NAME, 'pre')
            
                abstract = driver.find_element(By.XPATH,esperar_carregar_abstract)

                pegakeywords(pre.text,titulo[cont],autor[cont],abstract.text,u)

                driver.quit()
            
                cont_inproceedings+=1
                cont+=1
            except:
                pag_erro.append(u)
                cont_erro_pag+=1
                cont+=1
                driver.quit()
    else:
        driver.quit()


if(len(pag_erro)>0):
    arq = open('PaginasComErroACM.txt', 'w')
    texto = []
    texto.append('Páginas que não foi possível pegar o conteúdo\n')
    for j in pag_erro:
        texto.append(j)
        texto.append('\n')
    texto.append('Páginas com ERRO 404 Not Found\n')
    for k in pag_not_found:
        texto.append(k)
        texto.append('\n')
    arq.writelines(texto)
    arq.close()
    
print('\n---------------------------- INFORMACOES ADICIONAIS ---------------------------')
print("\nNUMERO DE INPROCEEDINGS MINERADOS: ",cont_inproceedings)
print("\nNUMERO DE PAGINAS NAO ENCONTRADAS: ",cont_not_found)
print("\nNUMERO DE PAGINAS COM ERRO DE EXTRAÇÃO DE CONTEUDO: ",cont_erro_pag)
fim = time.time()
print("\nTEMPO DE EXECUCAO: ",fim - inicio,"s")
