import hashlib
import json
import random
from re import S

plavanje_slika = "https://i1.wp.com/myswimpro.com/blog/wp-content/uploads/2021/01/michael-phelps-butterfly-scaled.jpeg?fit=2560%2C1440&ssl=1"
tek_slika = "https://static01.nyt.com/images/2019/10/20/world/18running-print/12marathon-sub-videoSixteenByNineJumbo1600.jpg"
kolesarjenje_slika = "https://www.teamjumbovisma.com/uploads/_1134x618_crop_center-center_85_none/CORVOS_00032367-040.jpg"
sporti_slike = {'kolesarjenje':kolesarjenje_slika, 'plavanje':plavanje_slika, 'tek':tek_slika}
#------------------------------------------------------
class Šport:
    def __init__(self, disciplina, slika, seznam_idej = [], seznam_treningov = []):
        self.disciplina = disciplina
        self.slika = slika
        self.seznam_i = seznam_idej
        self.seznam_t = seznam_treningov

    def dodaj_idejo(self,ideja):
        self.seznam_i.append(ideja)

    def dodaj_trening(self,trening):
        self.seznam_t.append(trening)

    def odstrani_idejo(self,ideja):
        self.seznam_i.remove(ideja)
        
    def odstrani_trening(self,trening):
        self.seznam_t.remove(trening)
    
    def v_slovar(self):
        return {"discipline":self.disciplina, "slike": self.slika, "vadbe":self.seznam_i, "treningi":self.seznam_t}

    @classmethod
    def iz_slovarja(self, slovar_s_stanjem):
        discipline = slovar_s_stanjem["discipline"]
        slike = slovar_s_stanjem["slike"]
        vadbe = slovar_s_stanjem["vadbe"]
        treningi = slovar_s_stanjem["treningi"]
        sport = Šport(discipline,slike, vadbe, treningi)
        return sport

class Seznam:

    def __init__(self, vadbe_treningi = [], vadbe_ideje = []):

        self.ideje = vadbe_ideje
        self.treningi = vadbe_treningi
    
    def dodaj_trening(self, trening):
        self.treningi.append(trening)

    def dodaj_idejo(self, ideja):
        self.ideje.append(ideja)
    
    def opravi_idejo(self,ideja):
        self.dodaj_trening(ideja)
        self.odstrani_idejo(ideja)
    
    def odstrani_idejo(self,ideja):
        self.ideje.remove(ideja)
    
    def odstrani_trening(self, trening):
        self.treningi.remove(trening)

    def v_slovar(self):
        return {"treningi":[trening for trening in self.treningi], "ideje":[ideja for ideja in self.ideje]}
    
    @classmethod
    def iz_slovarja(self, slovar_s_stanjem):
        treningi = slovar_s_stanjem["treningi"]
        ideje = slovar_s_stanjem["ideje"]
        seznam = Seznam(treningi, ideje) 
        return seznam 

    
class Uporabnik:
    def __init__(self, uporabnisko_ime, zasifrirano_geslo, seznam = Seznam(), sporti = {"tek": Šport("tek", sporti_slike["tek"]), "plavanje": Šport("plavanje", sporti_slike["plavanje"]),"kolesarjenje": Šport("kolesarjenje", sporti_slike["kolesarjenje"])}):
        self.uporabnisko_ime = uporabnisko_ime
        self.zasifrirano_geslo = zasifrirano_geslo
        self.sport = sporti
        self.seznam = seznam

    def dodaj_disciplino(self, disciplina, slika):
        self.sport.update({disciplina:Šport(disciplina, slika)})

    def pobrisi_disciplino(self, disciplina):
        del self.sport[disciplina]
#----------------------    
    @staticmethod
    def prijava(uporabnisko_ime, geslo_v_cistopisu):
        uporabnik = Uporabnik.iz_datoteke(uporabnisko_ime)
        if uporabnik is None:
            raise ValueError("Uporabniško ime ne obstaja")
        elif uporabnik.preveri_geslo(geslo_v_cistopisu):
            return uporabnik        
        else:
            raise ValueError("Geslo je napačno")

    @staticmethod
    def registracija(uporabnisko_ime, geslo_v_cistopisu):
        if Uporabnik.iz_datoteke(uporabnisko_ime) is not None:
            raise ValueError("Uporabniško ime že obstaja")
        else:
            zasifrirano_geslo = Uporabnik._zasifriraj_geslo(geslo_v_cistopisu)
            uporabnik = Uporabnik(uporabnisko_ime, zasifrirano_geslo)
            uporabnik.v_datoteko()
            return uporabnik

    def _zasifriraj_geslo(geslo_v_cistopisu, sol=None):
        if sol is None:
            sol = str(random.getrandbits(32))
        posoljeno_geslo = sol + geslo_v_cistopisu
        h = hashlib.blake2b()
        h.update(posoljeno_geslo.encode(encoding="utf-8"))
        return f"{sol}${h.hexdigest()}"

    def preveri_geslo(self, geslo_v_cistopisu):
        sol, _ = self.zasifrirano_geslo.split("$")
        return self.zasifrirano_geslo == Uporabnik._zasifriraj_geslo(geslo_v_cistopisu, sol)

    @staticmethod
    def ime_uporabnikove_datoteke(uporabnisko_ime):
        return f"{uporabnisko_ime}.json"
#-------------------------
    @staticmethod
    def iz_datoteke(uporabnisko_ime):
        try:
            with open(Uporabnik.ime_uporabnikove_datoteke(uporabnisko_ime)) as datoteka:
                slovar = json.load(datoteka)
                return Uporabnik.iz_slovarja(slovar)
        except FileNotFoundError:
            return None

    def v_datoteko(self):
        with open(
            Uporabnik.ime_uporabnikove_datoteke(self.uporabnisko_ime), "w"
        ) as datoteka:
            json.dump(self.v_slovar(), datoteka, ensure_ascii=False, indent=4)
#--------------------
    @staticmethod
    def iz_slovarja(slovar):
        uporabnisko_ime = slovar["uporabnisko_ime"]
        zasifrirano_geslo = slovar["zasifrirano_geslo"]
        uporabnik = Uporabnik(uporabnisko_ime, zasifrirano_geslo)
        uporabnik.sport = {kljuc : Šport.iz_slovarja(slovar["sport"][kljuc]) for kljuc in slovar["sport"]}
        uporabnik.seznam = Seznam.iz_slovarja(slovar["seznam"])
        return uporabnik

    def v_slovar(self):
        return {
            "uporabnisko_ime": self.uporabnisko_ime,
            "zasifrirano_geslo": self.zasifrirano_geslo,
            "sport": {kljuc:Šport.v_slovar(self.sport[kljuc]) for kljuc in self.sport},
            "seznam" : Seznam.v_slovar(self.seznam)
        }
