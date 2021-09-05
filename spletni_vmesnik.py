import bottle
import model
import datetime

#--------------------------------------------------------------------------------------------

PISKOTEK_UPORABNISKO_IME = "uporabnisko_ime"
SKRIVNOST = "skrivnost"

#--------------------------------------------------------------------------------------------
def shrani_stanje(uporabnik):
    uporabnik.v_datoteko()

def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie(PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST)
    if uporabnisko_ime:
        return model.Uporabnik.iz_datoteke(uporabnisko_ime)
    else:
        bottle.redirect("/prijava/")

@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napaka=None)

@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!")
    try:
        model.Uporabnik.prijava(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template(
            "prijava.html", napaka=e.args[0]
        )

@bottle.post("/odjava/")
def odjava():
    bottle.response.delete_cookie(PISKOTEK_UPORABNISKO_IME, path="/")
    bottle.redirect("/")

@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html", napaka=None)

@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!")
    try:
        model.Uporabnik.registracija(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST
        )
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template(
            "registracija.html", napaka=e.args[0]
        )
#-------------------------------------------------------------------------------------------
#prikaz osnovnega zaslona
@bottle.get('/')
def osnovni_zaslon():
  uporabnik = trenutni_uporabnik()
  podatki = [sport for sport in uporabnik.sport.keys()]
  return bottle.template("osnovna_stran.html", seznam = podatki)

#---------------------------------------------------------------------------------------------
#opravljenje in preusmerjanje osnovnega zaslona

@bottle.get('/dodaj/')
def dodaj_vnesen_sport():
  uporabnik = trenutni_uporabnik()
  nov_sport = bottle.request.query.getunicode('dodaj')
  if nov_sport not in uporabnik.sport:
    nov_sport_slika = bottle.request.query.getunicode('url_slika')
    if nov_sport_slika == None or nov_sport_slika == "":
      nov_sport_slika = "https://img.freepik.com/free-vector/soccer-volleyball-baseball-rugby-equipment_1441-4026.jpg?size=626&ext=jpg"
    uporabnik.dodaj_disciplino(nov_sport, nov_sport_slika)
    uporabnik.v_datoteko()
    return bottle.redirect('/')
  else:
    return bottle.redirect('/napaka/1/')

#-----

@bottle.get('/izbrisi/')
def izbrisi_vnesen_sport():
  uporabnik = trenutni_uporabnik()
  sport_za_izbris = bottle.request.query.getunicode('izbrisi')
  if sport_za_izbris in uporabnik.sport:
    uporabnik.pobrisi_disciplino(sport_za_izbris)
    uporabnik.v_datoteko()
    return bottle.redirect('/')
  else:
    return bottle.redirect('/napaka/2/')

#----------

@bottle.get('/napaka/<indeks>/')
def napaka(indeks):
  if int(indeks) == 1:
    besedilo = 'šport je že na seznamu športov'
  else:
    besedilo = 'športa se ne da izbrisati saj ga ni seznamu športov'
  return bottle.template('stran_za_napake.html', napaka = besedilo)
  
#----------------------------------------------------------------------------------------------
#drugi zaslon (zaslon za posamezen sport) 
@bottle.get('/<disciplina>/')
def stran_za_disciplino(disciplina):
  return bottle.template('vse_discipline.html', sport = disciplina, url_slika = sporti_slike[f'{disciplina}'])

#-----------
@bottle.get('/vnos/<disciplina>/<vrsta>/')
def vnos(disciplina, vrsta):

  danasnji_datum = f"{datetime.datetime.now():%Y-%m-%d}"

  poudarek = bottle.request.query.getunicode('poudarek')
  stevilo_serij = bottle.request.query.getunicode('stevilo_serij')

  vrsta_sporta = Disciplina(disciplina, vrsta, poudarek, stevilo_serij)

  return bottle.template('vnos_podatkov.html', vadba = vrsta_sporta, datum = danasnji_datum, url_slika = sporti_slike[f'{vrsta_sporta.panoga}'])

@bottle.get('/vnos_podatkov/')
def podrobni_podatki():

  #ze vnaprej vneseni podatki
  disciplina = bottle.request.query.getunicode('disciplina')
  vrsta = bottle.request.query.getunicode('oblika') 
  poudarek = bottle.request.query.getunicode('poudarek')
  stevilo_serij = bottle.request.query.getunicode('stevilo')

  #----------
  def pretvorba_zapis(ure, minute,sekunde):
    if minute != 0 or sekunde != 0 or ure != 0:
      return str(datetime.timedelta(hours= ure, minutes=minute, seconds=sekunde))
    else:
      return None

  #----------
  #vnos za ogrevanje

  razdalja_ogrevanje = bottle.request.query.getunicode('razdalja_ogrevanja')
  opis_ogrevanje = bottle.request.query.getunicode('opis_ogrevanje')
  trajanje_ogrevanje = str(bottle.request.query.getunicode('trajanje_ogrevanje'))

  ogrevanje = [razdalja_ogrevanje, opis_ogrevanje, trajanje_ogrevanje]

  #-----
  #vnos podatkov za serijo
  serije = []

  for indeks in range(int(stevilo_serij)):
    razdalja = bottle.request.query.getunicode(f'razdalja{indeks+1}')
    ponovitev = bottle.request.query.getunicode(f'ponovitev{indeks+1}')

    trajanje= str(bottle.request.query.getunicode(f'trajanje_ponovitve{indeks+1}'))

    opis = bottle.request.query.getunicode(f'opis_serije{indeks+1}')
    serija = [razdalja, ponovitev, trajanje, opis]
    serije.append(serija)

  #-----
  #vnos lokacije in datuma treninga

  lokacija = bottle.request.query.getunicode('lokacija')
  datum = bottle.request.query.getunicode('datum')

  #-----
  #izracun dolzine za vadbo
  def dolzina_vadbe(serije):
    dolzina = 0
    for serija in serije:
      if serija[0] != "":
        vrednost = int(serija[0]) * int(serija[1])
        dolzina+=vrednost
    if ogrevanje[0] != "":
      dolzina += int(ogrevanje[0]) 
    return dolzina

  #-----
  #izracun casa vadbe
  def izracun_casa(serije):
    cas_ure = 0
    cas_minute = 0
    cas_sekunde = 0
    for serija in serije:
      if serija[2] != None and serija[2] != "":
        ure, minute, sekunde = map(int, serija[2].split(':'))
        ure_skupaj, minute_skupaj, sekunde_skupaj = int(serija[1])* ure, int(serija[1])* minute, int(serija[1])* sekunde
        cas_ure += ure_skupaj
        cas_minute += minute_skupaj
        cas_sekunde += sekunde_skupaj

    if ogrevanje[2] != None and ogrevanje[2] != "":
      ure_ogrevanje, minute_ogrevanje, sekunde_ogrevanje = map(int, ogrevanje[2].split(':'))
      cas_ure += ure_ogrevanje
      cas_minute += minute_ogrevanje
      cas_sekunde += sekunde_ogrevanje
    return cas_ure, cas_minute, cas_sekunde

  ure_za_obliko, minute_za_obliko, sekunde_za_obliko = izracun_casa(serije)
  cas_oblika = pretvorba_zapis(ure_za_obliko, minute_za_obliko, sekunde_za_obliko)

  #-----
  nov_sport = Disciplina(disciplina, vrsta, poudarek, stevilo_serij)

  if nov_sport.opravljeno:
    zadnji_treningi.append(nov_sport)
    vadbe_treningi.update({f'{nov_sport}':Vadba(disciplina, poudarek, nov_sport.opravljeno, datum, lokacija, serije, ogrevanje, dolzina_vadbe(serije), cas_oblika)})

  else:
    ideje.append(nov_sport)
    vadbe_ideje.update({f'{nov_sport}':Vadba(disciplina, poudarek, nov_sport.opravljeno, datum, lokacija, serije, ogrevanje, dolzina_vadbe(serije), cas_oblika)})

  vadba = Vadba(disciplina, poudarek, nov_sport.opravljeno, datum, lokacija, serije, ogrevanje, dolzina_vadbe(serije), cas_oblika)

  nazaj = 3
  #vnasanje podatkov 

  return bottle.template('izpis_podatkov.html', izpis = vadba, vrednost = nazaj)

@bottle.get('/zadnje_aktivnosti/')
def izpis_zadnjih_aktivnosti():
  return bottle.template('zadnje_aktivnosti.html', izpis = zadnji_treningi)

@bottle.post('/zadnje_aktivnosti/izbrisi/')
def izbris_aktivnosti():
  objekt_indeks = int(bottle.request.forms.getunicode('objekt_indeks'))
  del vadbe_treningi[f'{zadnji_treningi[objekt_indeks]}']
  zadnji_treningi.remove(zadnji_treningi[objekt_indeks])

  return bottle.redirect('/zadnje_aktivnosti/')

@bottle.get('/zadnje_aktivnosti/podrobno/')
def podrobno():
  objekt_indeks = bottle.request.query.getunicode('objekt_indeks')
  objekt = zadnji_treningi[int(objekt_indeks)]
  objekt_podrobno = vadbe_treningi[f'{objekt}']

  nazaj = 0
  #zadnje aktivnosti 

  return bottle.template('izpis_podatkov.html', izpis = objekt_podrobno,vrednost = nazaj)
#----

@bottle.get('/isci/')
def isci():
  disciplina = bottle.request.query.getunicode('iskana_disciplina')
  iskalni_niz = bottle.request.query.getunicode('niz')
  skupaj = ideje + zadnji_treningi
  ustrezni = isci_po_poudarku(disciplina, iskalni_niz, skupaj)
  return bottle.template('iskanje.html', izpisi = ustrezni, kljuc = iskalni_niz, sport = disciplina, url_slika = sporti_slike[f'{disciplina}'])

def isci_po_poudarku(sport, beseda,vadbe):
    ustrezni = []
    if len(vadbe) != 0:
      for vadba in vadbe:
          if beseda in vadba.poudarek.split() and vadba.panoga == sport:
            ustrezni.append(vadba)
          else:
            pass
    else:
      pass
    return ustrezni

@bottle.get('/isci/podrobno/')
def podrobno_iskanje():
  objekt_indeks = int(bottle.request.query.getunicode('objekt_indeks'))
  disciplina = bottle.request.query.getunicode('disciplina')
  iskalni_niz = bottle.request.query.getunicode('iskalni_niz')

  skupaj = ideje + zadnji_treningi

  ustrezni = isci_po_poudarku(disciplina, iskalni_niz, skupaj)
  objekt = ustrezni[objekt_indeks]

  if objekt.opravljeno:
    objekt_podrobno = vadbe_treningi[f'{objekt}']
  else:
    objekt_podrobno = vadbe_ideje[f'{objekt}']

  nazaj = 2
  #isci

  return bottle.template('izpis_podatkov.html', izpis = objekt_podrobno, vrednost = nazaj, kljuc = iskalni_niz)

@bottle.get('/ideje/pregled/')
def prikazi_ideje():
  ustrezni = []
  for ideja in ideje:
    dodaj = vadbe_ideje[f'{ideja}']
    ustrezni.append(dodaj)
  datum = f'{datetime.datetime.now():%Y-%m-%d}'
  return bottle.template('izpis_idej.html', izpis = ustrezni, danasnji_datum = datum)

@bottle.post('/opravi/ideja/')
def opravi_idejo():
  indeks_ideje = int(bottle.request.forms.getunicode('indeks_ideje'))
  datum_opravljeno = bottle.request.forms.getunicode('datum_ideja')

  ideja_kratko = ideje[indeks_ideje]
  ideja_podrobno = vadbe_ideje[f'{ideje[indeks_ideje]}']

  del vadbe_ideje[f'{ideje[indeks_ideje]}']
  ideje.remove(ideje[indeks_ideje])

  ideja_podrobno.datum = datum_opravljeno
  ideja_podrobno.opravljenost = True
  ideja_podrobno.oblika = "trening"

  ideja_kratko.opravljeno = True
  ideja_kratko.oblika = "trening"

  vadbe_treningi.update({f'{ideja_kratko}': ideja_podrobno})
  zadnji_treningi.append(ideja_kratko)

  nazaj = 1
  #pregled idej

  return bottle.template("izpis_podatkov.html", izpis = ideja_podrobno, vrednost = nazaj )
#----------------------------------------------------------------------------------------------
bottle.run(debug=True, reloader=True)