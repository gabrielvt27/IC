'''
    Programa feito por Gabriel Valentin Tiburcio,
    aluno da graduação em Sistemas de Informação na UFU.
    Pesquisa "Exploração de Estratégias para Mineração de Expertise",
    orientada pela professora Maria Camila Nardini Barioni

    -----------------------------------------------------------------

    Programa realiza extração do Abstract(resumo) das pesquisas contidas
    nas páginas Web do IEEE, e extração das Keywords das pesquisas
    encontradas no BIBTEX dessa mesma página. Depois o conteúdo encontrado
    é armazenado em um arquivo denominado "registroIEEE.txt", onde será lido
    posteriormente pelo programa "03-CarregaBancoMySQL.py".

    O site segue o padrão desse exemplo a seguir:
        https://www.computer.org/csdl/proceedings-article/2011/iv/12OmNxzMnU0/12OmNxymo4x
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
    
    texto = []
    texto.append('Titulo{')
    texto.append(titulo)
    texto.append('}\n')
    texto.append('Autor{')
    texto.append(autor)
    texto.append('}\n')
    texto.append('Keywords{')
    for j in conteudo:
        texto.append(j.text)
        texto.append(';')
    texto.append('}\n')
    texto.append('Abstract{')
    texto.append(abstract)
    texto.append('}\n')
    texto.append('URL{')
    texto.append(url)
    texto.append('}\n')
    
    arq = open('registro_ELSEVIER-Article.txt', 'a')
    arq.writelines(texto)
    arq.close()
    
# Início do Programa
inicio = time.time()

arquivo = open('urls_Outros-Article.txt', 'r')

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


# Caminhos p/ encontrar os Abstracts e Keywords dos Inproceedings no site do IEEE
caminho_abstract = '/html/body/div/div/div/section/div/div/article/div/div/div/p'

padrao_not_found_url_elsevier = 'https://www.sciencedirect.com/science/article/not-found'

padrao_url = 'https://www.sciencedirect.com/'

cont_inproceedings = 0 # contador de inproceedings
cont_not_found = 0 # contador de páginas não encontradas
cont_erro_pag = 0 # contador de páginas que não foi possível pegar o conteúdo
cont = 0

pag_erro = []
pag_not_found = []

for u in url:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
        
    driver = webdriver.Chrome(chrome_options=options)
    wait = WebDriverWait(driver,30)
        
    driver.get(u)

    if padrao_url in driver.current_url:

        # TRATAR PAGE NOT FOUND
        if padrao_not_found_url_elsevier in driver.current_url:
            pag_not_found.append(u)
            cont_not_found+=1
            cont+=1
            driver.quit()
        else:
            try:
                elemento = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'page')))

                nav_pega_abstract = driver.find_element_by_xpath(caminho_abstract)

                nav_para_keyword = driver.find_elements_by_class_name('keyword')

                abstract = nav_pega_abstract.text
                    
                pegakeywords(nav_para_keyword,titulo[cont],autor[cont],abstract,u)

                driver.quit()
                cont_inproceedings+=1
                cont+=1
            except:
                pag_erro.append(u)
                cont_erro_pag+=1
                cont+=1
                driver.quit()
    else:
        cont+=1
        driver.quit()

if(len(pag_erro)>0):
    arq = open('PaginasComErroELSEVIER.txt', 'w')
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
