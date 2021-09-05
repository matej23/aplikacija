import bottle
import model
import datetime


PISKOTEK_UPORABNISKO_IME = "uporabnisko_ime"
SKRIVNOST = "skrivnost"


def shrani_stanje(uporabnik):
    uporabnik.v_datoteko()


def trenutni_uporabnik():
    uporabnisko_ime = bottle.request.get_cookie(
        PISKOTEK_UPORABNISKO_IME, secret=SKRIVNOST)
    if uporabnisko_ime:
        return model.Uporabnik.iz_datoteke(uporabnisko_ime)
    else:
        bottle.redirect("/prijava/")


@bottle.get("/prijava/")
def prijava_get():
    return bottle.template("prijava.html", napaka=None, x=1)


@bottle.post("/prijava/")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!", x=1)
    try:
        model.Uporabnik.prijava(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template("prijava.html", napaka=e.args[0], x=1)


@bottle.get("/registracija/")
def registracija_get():
    return bottle.template("registracija.html", napaka=None, x=1)


@bottle.post("/registracija/")
def registracija_post():
    uporabnisko_ime = bottle.request.forms.getunicode("uporabnisko_ime")
    geslo_v_cistopisu = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!", x=1)
    try:
        model.Uporabnik.registracija(uporabnisko_ime, geslo_v_cistopisu)
        bottle.response.set_cookie(
            PISKOTEK_UPORABNISKO_IME, uporabnisko_ime, path="/", secret=SKRIVNOST)
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template("registracija.html", napaka=e.args[0], x=1)


@bottle.get("/odjavi/se/")
def odjava():
    bottle.response.delete_cookie(PISKOTEK_UPORABNISKO_IME, path="/")
    bottle.redirect("/prijava/")


@bottle.get('/')
def osnovni_zaslon():
    uporabnik = trenutni_uporabnik()
    podatki = [sport for sport in uporabnik.sport.keys()]
    return bottle.template("osnovna_stran.html", seznam=podatki, x=2)


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


@bottle.get('/napaka/<indeks>/')
def napaka(indeks):
    if int(indeks) == 1:
        besedilo = 'šport je že na seznamu športov'
    else:
        besedilo = 'športa se ne da izbrisati saj ga ni seznamu športov'
    return bottle.template('stran_za_napake.html', napaka=besedilo, x=2)


@bottle.get('/<disciplina>/')
def stran_za_disciplino(disciplina):
    uporabnik = trenutni_uporabnik()
    podatki = uporabnik.sport
    podatki_za_disciplino = podatki[disciplina]
    povezava = podatki_za_disciplino.slika
    return bottle.template('vse_discipline.html', sport=disciplina, url_slika=povezava, x=2)


@bottle.get('/vnos/<disciplina>/<vrsta>/')
def vnos(disciplina, vrsta):
    uporabnik = trenutni_uporabnik()

    danasnji_datum = f"{datetime.datetime.now():%Y-%m-%d}"

    poudarek = bottle.request.query.getunicode('poudarek')
    stevilo_serij = bottle.request.query.getunicode('stevilo_serij')

    sport_vrsta = disciplina
    podatki_sporti = uporabnik.sport
    podatki_class = podatki_sporti[sport_vrsta]
    povezava = podatki_class.slika

    oblika = vrsta
    if oblika == "ideja":
        opravljenost = False
    else:
        opravljenost = True

    novi_podatki = {"poudarek": poudarek, "stevilo_serij": stevilo_serij,
                    "opravljenost": opravljenost, "disciplina": sport_vrsta, "oblika": oblika}

    vadba_osnovni = {"disciplina": "", "poudarek": "",
                     "opravljenost": "", "oblika": "", "stevilo_serij": ""}
    vadba_osnovni.update(novi_podatki)

    return bottle.template('vnos_podatkov.html', vneseni_podatki=vadba_osnovni, datum=danasnji_datum, url_slika=povezava, x=2)


@bottle.get('/vnos_podatkov/')
def podrobni_podatki():

    uporabnik = trenutni_uporabnik()

    disciplina = bottle.request.query.getunicode('disciplina')
    vrsta = bottle.request.query.getunicode('oblika')
    poudarek = bottle.request.query.getunicode('poudarek')
    stevilo_serij = bottle.request.query.getunicode('stevilo')

    oblika = vrsta
    if oblika == "ideja":
        opravljenost = False
    else:
        opravljenost = True

    podatki = {"poudarek": poudarek, "stevilo_serij": stevilo_serij,
               "opravljenost": opravljenost, "disciplina": disciplina, "oblika": oblika}
    vadba = {"disciplina": "", "poudarek": "", "opravljenost": "", "oblika": "", "stevilo_serij": "",
             "datum": "", "kraj": "", "serije": "", "ogrevanje": "", "dolzina": "", "trajanje": ""}
    vadba.update(podatki)

    razdalja_ogrevanje = bottle.request.query.getunicode('razdalja_ogrevanja')
    opis_ogrevanje = bottle.request.query.getunicode('opis_ogrevanje')
    trajanje_ogrevanje = str(
        bottle.request.query.getunicode('trajanje_ogrevanje'))

    ogrevanje = [razdalja_ogrevanje, opis_ogrevanje, trajanje_ogrevanje]

    serije = []

    for indeks in range(int(stevilo_serij)):
        razdalja = bottle.request.query.getunicode(f'razdalja{indeks+1}')
        ponovitev = bottle.request.query.getunicode(f'ponovitev{indeks+1}')

        trajanje = str(bottle.request.query.getunicode(
            f'trajanje_ponovitve{indeks+1}'))

        opis = bottle.request.query.getunicode(f'opis_serije{indeks+1}')
        serija = [razdalja, ponovitev, trajanje, opis]
        serije.append(serija)

    lokacija = bottle.request.query.getunicode('lokacija')
    datum = bottle.request.query.getunicode('datum')

    def dolzina_vadbe(serije, ogrevanje):
        dolzina = 0
        for serija in serije:
            if serija[0] != "":
                vrednost = int(serija[0]) * int(serija[1])
                dolzina += vrednost
        if ogrevanje[0] != "":
            dolzina += int(ogrevanje[0])
        return dolzina

    skupna_dolzina = dolzina_vadbe(serije, ogrevanje)

    def pretvorba_zapis(ure, minute, sekunde):
        if minute != 0 or sekunde != 0 or ure != 0:
            return str(datetime.timedelta(hours=ure, minutes=minute, seconds=sekunde))
        else:
            return None

    def izracun_casa(serije):
        cas_ure = 0
        cas_minute = 0
        cas_sekunde = 0
        for serija in serije:
            if serija[2] != None and serija[2] != "":
                ure, minute, sekunde = map(int, serija[2].split(':'))
                ure_skupaj, minute_skupaj, sekunde_skupaj = int(
                    serija[1]) * ure, int(serija[1]) * minute, int(serija[1]) * sekunde
                cas_ure += ure_skupaj
                cas_minute += minute_skupaj
                cas_sekunde += sekunde_skupaj

        if ogrevanje[2] != None and ogrevanje[2] != "":
            ure_ogrevanje, minute_ogrevanje, sekunde_ogrevanje = map(
                int, ogrevanje[2].split(':'))
            cas_ure += ure_ogrevanje
            cas_minute += minute_ogrevanje
            cas_sekunde += sekunde_ogrevanje
        return cas_ure, cas_minute, cas_sekunde

    ure_za_obliko, minute_za_obliko, sekunde_za_obliko = izracun_casa(serije)
    cas_oblika = pretvorba_zapis(
        ure_za_obliko, minute_za_obliko, sekunde_za_obliko)

    novi_podatki = {"datum": datum, "kraj": lokacija, "serije": serije,
                    "ogrevanje": ogrevanje, "dolzina": skupna_dolzina, "trajanje": cas_oblika}
    vadba.update(novi_podatki)

    seznam_class = uporabnik.seznam
    sport_class = uporabnik.sport[disciplina]

    if vadba["opravljenost"]:
        seznam_class.dodaj_trening(vadba)
        sport_class.dodaj_trening(vadba)
    else:
        seznam_class.dodaj_idejo(vadba)
        sport_class.dodaj_idejo(vadba)

    uporabnik.v_datoteko()
    nazaj = 3

    return bottle.template('izpis_podatkov.html', izpis=vadba, vrednost=nazaj, x=2)


@bottle.get('/zadnje_aktivnosti/')
def izpis_zadnjih_aktivnosti():
    uporabnik = trenutni_uporabnik()
    seznam = uporabnik.seznam
    zadnji_treningi = seznam.treningi
    return bottle.template('zadnje_aktivnosti.html', izpis=zadnji_treningi, x=2)


@bottle.post('/zadnje_aktivnosti/izbrisi/')
def izbris_aktivnosti():
    uporabnik = trenutni_uporabnik()
    objekt_indeks = int(bottle.request.forms.getunicode('objekt_indeks'))

    zadnji_treningi = uporabnik.seznam.treningi
    za_izbris = zadnji_treningi[objekt_indeks]
    uporabnik.seznam.odstrani_trening(za_izbris)

    uporabnik.sport[za_izbris["disciplina"]].odstrani_trening(za_izbris)
    uporabnik.v_datoteko()

    return bottle.redirect('/zadnje_aktivnosti/')


@bottle.get('/zadnje_aktivnosti/podrobno/')
def podrobno():
    uporabnik = trenutni_uporabnik()
    seznam_treningov = uporabnik.seznam.treningi

    objekt_indeks = bottle.request.query.getunicode('objekt_indeks')
    objekt = seznam_treningov[int(objekt_indeks)]

    nazaj = 0

    return bottle.template('izpis_podatkov.html', izpis=objekt, vrednost=nazaj, x=2)


@bottle.get('/isci/')
def isci():
    uporabnik = trenutni_uporabnik()
    disciplina = bottle.request.query.getunicode('iskana_disciplina')
    iskalni_niz = bottle.request.query.getunicode('niz')

    sport_class = uporabnik.sport[disciplina]
    povezava = sport_class.slika

    seznam_idej = sport_class.seznam_i
    seznam_treningov = sport_class.seznam_t
    skupaj = seznam_treningov + seznam_idej

    ustrezni = isci_po_poudarku(iskalni_niz, skupaj)

    return bottle.template('iskanje.html', izpisi=ustrezni, kljuc=iskalni_niz, sport=disciplina, url_slika=povezava, x=2)


def isci_po_poudarku(beseda, seznam_slovarjev):
    ustrezni = []
    if len(seznam_slovarjev) != 0:
        for slovar in seznam_slovarjev:
            if beseda in slovar["poudarek"].split():
                ustrezni.append(slovar)
            else:
                pass
    else:
        pass
    return ustrezni


@bottle.get('/isci/podrobno/')
def podrobno_iskanje():
    uporabnik = trenutni_uporabnik()
    objekt_indeks = int(bottle.request.query.getunicode('objekt_indeks'))
    disciplina = bottle.request.query.getunicode('disciplina')
    iskalni_niz = bottle.request.query.getunicode('iskalni_niz')

    sport_class = uporabnik.sport[disciplina]

    seznam_idej = sport_class.seznam_i
    seznam_treningov = sport_class.seznam_t
    skupaj = seznam_treningov + seznam_idej

    ustrezni = isci_po_poudarku(iskalni_niz, skupaj)
    objekt = ustrezni[objekt_indeks]

    nazaj = 2

    return bottle.template('izpis_podatkov.html', izpis=objekt, vrednost=nazaj, kljuc=iskalni_niz, x=2)


@bottle.get('/ideje/pregled/')
def prikazi_ideje():
    uporabnik = trenutni_uporabnik()
    ustrezni = uporabnik.seznam.ideje

    datum = f'{datetime.datetime.now():%Y-%m-%d}'
    return bottle.template('izpis_idej.html', izpis=ustrezni, danasnji_datum=datum, x=2)


@bottle.post('/opravi/ideja/')
def opravi_idejo():
    uporabnik = trenutni_uporabnik()
    indeks_ideje = int(bottle.request.forms.getunicode('indeks_ideje'))
    datum_opravljeno = bottle.request.forms.getunicode('datum_ideja')

    vse_ideje = uporabnik.seznam.ideje
    objekt = vse_ideje[indeks_ideje]
    vse_vadbe = uporabnik.seznam
    vse_vadbe.odstrani_idejo(objekt)

    disciplina = objekt["disciplina"]
    seznam_class_sport = uporabnik.sport[disciplina]
    seznam_class_sport.odstrani_idejo(objekt)

    objekt.update({"datum": datum_opravljeno})
    vse_vadbe.dodaj_trening(objekt)
    seznam_class_sport.dodaj_trening(objekt)

    uporabnik.v_datoteko()
    nazaj = 1

    return bottle.template("izpis_podatkov.html", izpis=objekt, vrednost=nazaj, x=2)


bottle.run(debug=True, reloader=True)
