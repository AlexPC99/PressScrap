import time
import codecs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

class Articulo:
    Titulo = None
    Subtitulo = None
    Autor = None
    AID = None
    Texto = None

def CargarPagina(driver): #Funcion se encanrga de esperar hasta que la pagina tenga texto cargado
    cargada = False
    while cargada == False:
        time.sleep(0.1)
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        BuscarCarga = soup.find_all(class_="art")
        for Tag in BuscarCarga:
            if Tag.has_attr('aid'):
                if Tag['aid'] != "":
                    cargada = True
    time.sleep(5)
    print("Loaded")
    return driver.page_source

def LimpiarTexto(Tag): #Esta funcion limpia el texto de caracteres de basura
    if(Tag != None):
        Txt = Tag.text.replace("&shy", '').replace(";\xad","").replace("\xad","")
        return Txt
    else:
        return None

def Elem2Xpath(element): #Codigo obtenido de https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def ImprimirArt(Art):
    print("\n\n")
    print(Art.AID)
    print(Art.Titulo)
    print(Art.Subtitulo)
    print(Art.Autor)
    print(Art.Texto)
    print("\n\n")

def GuardarComoPDF(Art):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('arial', 'B', 14)
    pdf.cell(0, 8, 'Notas',0,2,align='C')
    pdf.set_font('arial', 'B', 8)
    pdf.cell(0,10,str(Art.Titulo),0,2,align='C')
    pdf.cell(0,10,str(Art.Subtitulo),0,2,align='C')
    pdf.cell(0,10,str(Art.Autor),0,2,align='C')
    pdf.output("test.pdf", 'F')

def EncontrarArticulo(soup, aid): #Recupera el elemento html entero del articulo en base a su ID
    listaarts = soup.find_all("article")
    for Tag in listaarts:
        if Tag.has_attr('aid'):
            if Tag['aid'] == aid:
                return Tag

def EncontrarDatos(Tag): #Recupera los datos del elemento HTML del articulo ingresado como parametro
    Datos = []
    Titulo = None
    Subtitulo = None
    Autor = None
    Texto = None
    Titulo = LimpiarTexto(Tag.find("h1"))
    Subtitulo = LimpiarTexto(Tag.find("h2"))
    Autor = LimpiarTexto(Tag.find(class_="art-author"))
    TagTexto = Tag.find_all("p")
    TextCont = ""
    PrevT = ""
    for Tags in TagTexto:
        Txt = LimpiarTexto(Tags)
        if PrevT == Txt:
            TagTexto.remove(Tags)
        else:
            TextCont = TextCont + Txt + "\n"
        PrevT = Txt
    Texto = TextCont
    Datos.append(Titulo)
    Datos.append(Subtitulo)
    Datos.append(Autor)
    Datos.append(Texto)
    return Datos

def BuscaAID(soup, Articulos, debug, run):
    ClosestPix = 90000
    ClosestID = ""
    BuscarTexto = None
    BuscarTexto = soup.find_all("article")
    ToClick = None
    ClickID = ""
    for Tag in BuscarTexto:
        Rep = False
        if Tag.has_attr('aid'):
            if len(Articulos) > 0:
                for arts in Articulos:
                    if arts.AID == Tag["aid"]:
                        Rep = True
            if Rep == False:
                info = Tag.find("header")
                if info is not None and info.has_attr("style"):
                    StyleString = info["style"]
                    temp = StyleString.split("left: ")[1]
                    PixSize = int(temp.split("px")[0])
                    if PixSize < ClosestPix:
                        ClosestPix = PixSize
                        ClickID = Tag["aid"]
                        ToClick = info
                    if debug == True:
                        print(info)
                        print("\n\nc")
    for Tag in BuscarTexto:
        if Tag.has_attr("aid"):
            if Tag["aid"] == ClickID:
                Premium = None
                Premium = Tag.find("a", class_="readmore dis")
                if Premium != None:
                    print("Locked")
                    ToClick = None
    returnarr = []
    returnarr.append(ClickID)
    returnarr.append(ToClick)
    return returnarr

def EsperaCargaTexto(driver, soup, aid):
    time.sleep(1)
    loaded = False
    i = 0
    while loaded == False:
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        tags = soup.find_all("article")
        for tag in tags:
            if tag.has_attr('aid'):
                if tag["aid"] == aid:
                    hrefs = tag.find_all("div", class_="art-tools-tiny")
                    if len(hrefs) > 0:
                        loaded = True
                    else:
                        time.sleep(1)
        i = i+1
        if (i > 5):
            loaded = True

def LimpiezaArticulos(ListaArts):
    i = 0
    j = 0
    NewList = []
    for Art in ListaArts:
        if Art.Texto is not None:
            NewList.append(Art)
    return NewList

def Scroll(SleepTime, driver):
    elm = driver.find_element_by_xpath("//body")
    elm.send_keys(Keys.ARROW_DOWN)
    time.sleep(SleepTime)
    html = driver.page_source
    soup = BeautifulSoup(html, features="html.parser")
    #f = codecs.open("test.html", "w", "utf−8")
    #f.write(html)
    return soup

def PressReader(fecha, periodico):
    try:
        #aaaa-dd-mm
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        #Mac Settings
        #ser = Service("/Users/mch/Documents/GitHub/Prueba/chromedriver")
        #driver = webdriver.Chrome(service = ser, options=options)
        driver = webdriver.Chrome("/Users/mch/Documents/GitHub/Prueba/chromedriver")

        #Windows Settings
        #driver = webdriver.Chrome(options = options)

        FechaFull = fecha.split('-')
        FechaStr = str(FechaFull[0])+str(FechaFull[1])+str(FechaFull[2])
        LinkStr = "https://www.pressreader.com/mexico/"+str(periodico)+"/"+FechaStr+"/page/1/textview"
        driver.get(LinkStr)
        link = CargarPagina(driver)
        soup = BeautifulSoup(link, features="html.parser")
        ScrollFinal = False
        i = 0
        j = 0
        ClickID = ""
        Articulos = []
        phtml = None
        while ScrollFinal == False:
            ArticulosUnicos = BuscaAID(soup, Articulos, False, i)
            ClickID = ArticulosUnicos[0]
            ToClick = ArticulosUnicos[1]
            Art = Articulo()
            if ToClick != None:
                RPath = Elem2Xpath(ToClick)
                element = driver.find_element_by_xpath(RPath)
                action = ActionChains(driver)
                action.double_click(element).perform()
                action.release()
                EsperaCargaTexto(driver, soup, ClickID)
                #time.sleep(1)
                #EsperaCargaTexto(driver, soup, ClickID)
                html = driver.page_source
                soup = BeautifulSoup(html, features="html.parser")
                soup2 = BeautifulSoup(html, features="html.parser")
                ArtCompleto = EncontrarArticulo(soup2, ClickID)
                if ArtCompleto is not None:
                    Dat = EncontrarDatos(ArtCompleto)
                    Art.AID = ArtCompleto['aid']
                    Art.Titulo = Dat[0]
                    Art.Subtitulo = Dat[1]
                    Art.Autor = Dat[2]
                    Art.Texto = Dat[3]
                    ImprimirArt(Art)
                    Articulos.append(Art)
                    soup = Scroll(1, driver)
                else:
                    ScrollFinal = True
                i = i + 1
                html = driver.page_source
                print("\n\n")
            else:
                print("Didn't click anything")
                ArtCompleto = EncontrarArticulo(soup2, ClickID)
                if ArtCompleto is not None:
                    Dat = EncontrarDatos(ArtCompleto)
                    Art.AID = ArtCompleto['aid']
                    ImprimirArt(Art)
                    Articulos.append(Art)
                    soup = Scroll(1, driver)
                else:
                    ScrollFinal = True
                html = driver.page_source
                print("\n\n")
            if phtml == html:
                ScrollFinal = True
            else:
                phtml = html
        print("Finished scraping")
        ScrapList = LimpiezaArticulos(Articulos)
        for Art in ScrapList:
            ImprimirArt(Art)
        driver.quit()
        return ScrapList
    except Exception as e:
        print(e)
        return None

#PressReader("2014-08-10", "el-universal")
