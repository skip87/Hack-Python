 # -*-coding:Latin-1 -*- 
import urllib
import re
import HTMLParser
import json

max_numero_bus = 2
liste_bus = []
liste_des_arrets= []



def listedesbus(liste_bus,max_numero_bus):
    i = 0
    url = "http://www.rtcquebec.ca/Horairesettrajets/Parcoursparsecteur/tabid/56/Default.aspx"	
    htmlfile = urllib.urlopen(url)
    htmltext = htmlfile.read()
    while i< max_numero_bus:
		
		regex = '<option value="'+ str(i) +'">(.+?)</option>'
		pattern = re.compile(regex)
		numero = re.findall(pattern,htmltext)
		i+=1
		if numero:
			liste_bus.append(numero[0]) 	
    return liste_bus


list = listedesbus(liste_bus,max_numero_bus)

def jsonlist(liste_bus,titre_trajet,url_destination,numero_arret,nom_arret,horaire_liste,numero_voyage):
    #"liste":[{"bus": "1","direction": [{"id":"","name": "","arret": [{ "id":"","name": "", "horaire": [{"heure":"","voyage":""}]}]}]}]
    #"direction": [{"id":"","name": "","arret": [{ "id":"","name": "", "horaire": [{"heure":"","voyage":""}]
    #"arret": [{ "id":"","name": "", "horaire": [{"heure":"","voyage":""}]}]
    #"horaire": [{"heure":"","voyage":""}]
    liste =[]
    
    
    
    h=0
    while h < len(liste_bus):
        i=0
        direction =[]
        while i< len(titre_trajet):
            j=0
            arret =[]
            while j < len(numero_arret)and j < len(nom_arret):
                k = 0
                horaire =[]
                while k < len(numero_voyage) and k < len(horaire_liste):
                    l=0
                    while l <len(numero_voyage[k]) and l < len(horaire_liste[k]):

                        d = {}
                        d['heure']= horaire_liste[k][l]
                        d['voyage']= numero_voyage[k][l]
                        horaire.append(d)
                        l+=1
                    k+=1
                c = {}
                c['id_arret']= numero_arret[j]
                c['name_arret']= nom_arret[j]
                c['horaire']= horaire
                arret.append(c)
                j+=1
            b ={}
            b['id_trajet']=i+1
            b['name_trajet']= titre_trajet[i]
            b['arret']= arret
            direction.append(b)
            i+=1
        a={}
        a['bus']=liste_bus[h]
        a['direction']= direction
        liste.append(a)
        h+=1
    return liste


def liste_des_arrets(liste_bus):
    i = 0
    bus_noArret_nomArret = []
    #stoke la valuer de destion pour url des horaire 
    url_destination = []
    horaire_liste = []
    numero_voyage_liste=[]
    while i< len(liste_bus):
        url = "http://www.rtcquebec.ca/HoraireArret/Default.aspx?page=arret_parcours_recherche&parcours="+ str(liste_bus[i])+"&date=2013-10-28"
        htmlfile = urllib.urlopen(url)
        htmltext = htmlfile.read()
        regex3 = '<caption>(\s*.+\s*)</caption><thead>'
        pattern3 = re.compile(regex3)   
        titre_trajet = re.findall(pattern3,htmltext) 
        j = 0
        while j< len(titre_trajet):
            titre_trajet[j] = titre_trajet[j].strip()
            j+= 1
        print titre_trajet    
        html_text_split = htmltext.split('</caption>')
        k = 0
        l = 0
        while k < len(html_text_split):    
            regex = '<td class="fond" align="center">(.+?)</td>'
            pattern = re.compile(regex)
            numero_arret = re.findall(pattern,html_text_split[k])
            regex2 = '<td align="center">(.+?)</td>'
            pattern2 = re.compile(regex2)
            nom_arret = re.findall(pattern2,html_text_split[k]) 
            #go search the hour  for the arrete 
            m=0
            while m <len(numero_arret) and m <len(nom_arret):
                url_arret = 'http://www.rtcquebec.ca/HoraireArret/Default.aspx?page=arret_resultat&arret='+ str(numero_arret[m])
                htmlfile2 = urllib.urlopen(url_arret)
                htmltext2 =  htmlfile2.read()
                regex_lien_arret_heure = '&destination=(.*)"><b>'+str(liste_bus[i])+ '</b> -'
                pattern_lien_arret_heure = re.compile(regex_lien_arret_heure)
                parametre_destination_url = re.findall(pattern_lien_arret_heure,htmltext2)
                if parametre_destination_url:
                    url_destination.append(parametre_destination_url[0])
                m+= len(numero_arret)
            n=0
            while n < len(numero_arret):
                h = HTMLParser.HTMLParser()
                url_destination_html = h.unescape(url_destination[l])
                url_destination_html = url_destination_html.encode('latin-1')
                url_horaire_arret = 'http://www.rtcquebec.ca/HoraireArret/Default.aspx?page=arret_parcours_resultat&parcours='+ str(liste_bus[i])+'&arret='+str(numero_arret[n])+'&destination='+ str(url_destination_html)
                htmlfile3 = urllib.urlopen(url_horaire_arret)
                htmltext3 = htmlfile3.read()
                regex_horaire ='<td align="right">\s*(\d\d:\d\d)\s*[</td><td>|<acronym title="Descente]'
                pattern_horaire = re.compile(regex_horaire)
                horaire = re.findall(pattern_horaire,htmltext3)
                regex_voyage = "detail&parcours=[\d*]&voyage=(\d*)'><img\ssrc="
                pattern_voyage = re.compile(regex_voyage)
                numero_voyage = re.findall(pattern_voyage,htmltext3)
                print numero_voyage
                print numero_arret[n]
                print horaire
                if horaire:
                    horaire_liste.append(horaire)
                    numero_voyage_liste.append(numero_voyage)
                n+=1  

            if numero_arret and nom_arret:
                #"direction": [{"id":"","name": "","arret": [{ "id":"","name": "", "horaire": [{"heure":"","voyage":""}]
                direction = []
                #"arret": [{ "id":"","name": "", "horaire": [{"heure":"","voyage":""}]}]
                arret =[]
                #"horaire": [{"heure":"","voyage":""}]
                horaire = []
                bus=[]
                bus= jsonlist(liste_bus,titre_trajet,url_destination,numero_arret,nom_arret,horaire_liste,numero_voyage_liste)
                #bus = [liste_bus[i],titre_trajet[l],url_destination[l],numero_arret,nom_arret,horaire_liste,numero_voyage]
                #bus_noArret_nomArret.append(bus)
                l+= 1
            k+= 1   
        i+= 1
    return bus,i

print liste_des_arrets(list)
