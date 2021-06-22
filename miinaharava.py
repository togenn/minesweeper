import random
import csv
import time
import datetime
import math
import haravasto as ha
import ikkunasto as ik

tila = {
    "kentta": [],
    "suljetut_ruudut": [],
    "miinoja": 0,
    "päättynyt": False,
    "aloitus_aika": None,
    "vuorot": 0
}

kayttoliittyman_komponentit = {
    "leveys": "tekstikenttä",
    "korkeus": "tekstikenttä",
    "miinoja": "tekstikenttä",
    "asetukset": "ali_ikkuna",
    "tilastot": "ali-ikkuna",
    "tekstilaatikko": ""
}


def luo_kentta(leveys, korkeus):
    tila["kentta"] = []
    tila["suljetut_ruudut"] = []

    rivi = []
    for i in range(int(leveys)):
        rivi.append(" ")
    for i in range(int(korkeus)):
        tila["kentta"].append(rivi.copy())
        tila["suljetut_ruudut"].append(rivi.copy())


def miinoita(kentta, miinat):
    tila["miinoja"] = miinat
    vapaat_ruudut = []
    for y, rivi in enumerate(kentta):
        for x in range(len(rivi)):
            vapaat_ruudut.append((x, y))

    for i in range(miinat):
        vapaa_ruutu = random.choice(vapaat_ruudut)
        x, y = vapaa_ruutu
        vapaat_ruudut.remove(vapaa_ruutu)
        kentta[y][x] = "x"


def testaa_miinojen_maara(kentta, miinat):
    maksimi = len(kentta) * len(kentta[0]) - 1
    if miinat < 1:
        ik.avaa_viesti_ikkuna(
            "Virhe", "Kentällä pitää olla vähintään yksi miina!", True)
        return False
    if miinat > maksimi:
        ik.avaa_viesti_ikkuna(
            "Virhe", "Kentälle pitää jäädä vähintään yksi vapaa ruutu!", True)
        return False
    
    return True


def testaa_syote(syote):
    try:
        syote = int(syote)
    except ValueError:
        return False, None
    else:
        return True, syote


def piirra_kentta():
    ha.tyhjaa_ikkuna()
    ha.piirra_tausta()
    ha.aloita_ruutujen_piirto()
    for y, rivi in enumerate(tila["suljetut_ruudut"]):
        for x, ruutu in enumerate(rivi):
            ha.lisaa_piirrettava_ruutu(ruutu, x * 40, y * 40)
    ha.piirra_ruudut()


def laske_miinat(kentta, x, y):
    if kentta[y][x] == "x":
        return

    miinoja = 0
    for rivin_numero in range(y - 1, y + 2):
        for sarakkeen_numero in range(x - 1, x + 2):
            if rivin_numero < len(kentta) and rivin_numero >= 0:
                if sarakkeen_numero < len(kentta[0]) and sarakkeen_numero >= 0:
                    if kentta[rivin_numero][sarakkeen_numero] == "x":
                        miinoja += 1

    kentta[y][x] = str(miinoja)


def aseta_numerot_kenttaan(kentta):
    for y, rivi in enumerate(kentta):
        for x in range(len(rivi)):
            laske_miinat(kentta, x, y)


def tulvataytto(kentta, suljetut_ruudut, x, y):
    if y >= len(kentta) or x >= len(kentta[0]):
        return

    tutkittavat = [(x, y)]
    tutkitut = []

    while tutkittavat:
        tutkittava = tutkittavat[-1]
        tutkittava_x, tutkittava_y = tutkittava
        tutkitut.append((tutkittava_x, tutkittava_y))
        tutkittavat.pop(-1)

        for rivin_numero in range(tutkittava_y - 1, tutkittava_y + 2):
            for sarakkeen_numero in range(tutkittava_x - 1, tutkittava_x + 2):
                if rivin_numero < len(kentta) and rivin_numero >= 0:
                    if sarakkeen_numero < len(kentta[0]) and sarakkeen_numero >= 0:
                        suljetut_ruudut[rivin_numero][sarakkeen_numero] = kentta[rivin_numero][sarakkeen_numero]
                        if kentta[rivin_numero][sarakkeen_numero] == "0" and (sarakkeen_numero, rivin_numero) not in tutkitut:
                            tutkittavat.append((sarakkeen_numero, rivin_numero))


def kasittele_hiiri(x, y, nappi, muokkausnapit):
    ruutu_x = int(x / 40)
    ruutu_y = int(y / 40)
    try:
        if tila["päättynyt"]:
            ha.lopeta()
            paavalikko()
            return

        if nappi == ha.HIIRI_VASEN:
            tila["vuorot"] += 1
            if tila["kentta"][ruutu_y][ruutu_x] == "x":
                tila["suljetut_ruudut"][ruutu_y][ruutu_x] = "x"
                peli_paattyi("häviö")
                return
            if tila["kentta"][ruutu_y][ruutu_x] == "0":
                tulvataytto(tila["kentta"],
                            tila["suljetut_ruudut"], ruutu_x, ruutu_y)
            else:
                tila["suljetut_ruudut"][ruutu_y][ruutu_x] = tila["kentta"][ruutu_y][ruutu_x]

            if testaa_voitto(tila["suljetut_ruudut"]):
                peli_paattyi("voitto")

        if nappi == ha.HIIRI_OIKEA:
            if tila["suljetut_ruudut"][ruutu_y][ruutu_x] == "f":
                tila["suljetut_ruudut"][ruutu_y][ruutu_x] = " "
            else:
                tila["suljetut_ruudut"][ruutu_y][ruutu_x] = "f"
    except IndexError:
        pass


def testaa_voitto(suljetut_ruudut):
    suljetut = 0
    for rivi in suljetut_ruudut:
        suljetut += rivi.count(" ")

    if suljetut == tila["miinoja"]:
        return True

    return False


def muotoile_aika(sekunnit):
    minuutit = 0
    if sekunnit > 60:
        minuutit = math.floor(sekunnit / 60)
        sekunnit = sekunnit - 60 * minuutit

    return "{:02}:{:02}".format(minuutit, round(sekunnit))


def peli_paattyi(tulos):
    tila["päättynyt"] = True
    tila["suljetut_ruudut"] = tila["kentta"].copy()
    if tulos == "häviö":
        print("Hävisit pelin!")
    else:
        print("Voitit pelin!")
    kesto = muotoile_aika(time.time() - tila["aloitus_aika"])
    print("Aika:", kesto)
    print("Vuorot:", tila["vuorot"])
    tallenna_tulokset(tulos, kesto)


def tallenna_tulokset(tulos, kesto):
    paivamaara = datetime.datetime.now()
    with open("tilastot.csv", "a", newline="") as tiedosto:
        kirjoittaja = csv.writer(tiedosto)
        kirjoittaja.writerow([paivamaara.hour, str(paivamaara.minute).zfill(2), paivamaara.day, paivamaara.month,
                            paivamaara.year, tulos, kesto, "{}x{}".format(len(tila["kentta"][0]),
                            len(tila["kentta"])), tila["miinoja"], tila["vuorot"]])


def nayta_tilastot():
    try:
        with open("tilastot.csv", newline="") as tiedosto:
            lukija = csv.reader(tiedosto)
            for rivi in lukija:
                ik.kirjoita_tekstilaatikkoon(kayttoliittyman_komponentit["tekstilaatikko"],
                    "klo ja pvm: {}:{} {}.{}.{}\ntulos: {}\nkesto: {}\nkentän koko: {}\nmiinojen määrä:{}\nvuorot: {}"
                    .format(*rivi))
                ik.kirjoita_tekstilaatikkoon(
                    kayttoliittyman_komponentit["tekstilaatikko"], "------------------------------------------")
    except FileNotFoundError:
        ik.avaa_viesti_ikkuna("Virhe", "Yhtään peliä ei ole pelattu!", True)

    ik.nayta_ali_ikkuna(kayttoliittyman_komponentit["tilastot"])


def paavalikko():
    ikkuna = ik.luo_ikkuna("Miinaharava")
    kehys = ik.luo_kehys(ikkuna)
    ik.luo_nappi(kehys, "Aloita peli", nayta_pelin_asetukset)
    ik.luo_nappi(kehys, "Tilastot", nayta_tilastot)
    ik.luo_nappi(kehys, "Lopeta", lopeta)

    # luodaan ali_ikkunat
    asetukset_ikkuna = ik.luo_ali_ikkuna("Miinaharava")
    kayttoliittyman_komponentit["asetukset"] = asetukset_ikkuna
    ylakehys = ik.luo_kehys(asetukset_ikkuna, ik.YLA)
    alakehys = ik.luo_kehys(asetukset_ikkuna, ik.YLA)
    ik.luo_tekstirivi(ylakehys, "Syötä kentän koko ja miinojen määrä")
    ohjekehys = ik.luo_kehys(alakehys, ik.VASEN)
    syotekehys = ik.luo_kehys(alakehys, ik.VASEN)
    ik.luo_tekstirivi(ohjekehys, "leveys")
    kayttoliittyman_komponentit["leveys"] = ik.luo_tekstikentta(syotekehys)
    ik.luo_tekstirivi(ohjekehys, "korkeus")
    kayttoliittyman_komponentit["korkeus"] = ik.luo_tekstikentta(syotekehys)
    ik.luo_tekstirivi(ohjekehys, "miinoja")
    kayttoliittyman_komponentit["miinoja"] = ik.luo_tekstikentta(syotekehys)
    ik.luo_nappi(alakehys, "aloita peli", aseta_pelin_asetukset)
    ik.luo_nappi(alakehys, "Sulje", piilota_asetukset)
    ik.piilota_ali_ikkuna(asetukset_ikkuna)

    tilastot_ikkuna = ik.luo_ali_ikkuna("Tilastot")
    kayttoliittyman_komponentit["tilastot"] = tilastot_ikkuna
    tilastot_kehys = ik.luo_kehys(tilastot_ikkuna)
    kayttoliittyman_komponentit["tekstilaatikko"] = ik.luo_tekstilaatikko(
        tilastot_kehys)
    ik.piilota_ali_ikkuna(tilastot_ikkuna)

    ik.kaynnista()


def nayta_pelin_asetukset():
    ik.nayta_ali_ikkuna(kayttoliittyman_komponentit["asetukset"])


def piilota_asetukset():
    ik.piilota_ali_ikkuna(kayttoliittyman_komponentit["asetukset"])


def aseta_pelin_asetukset():
    leveys = testaa_syote(ik.lue_kentan_sisalto(
        kayttoliittyman_komponentit["leveys"]))
    korkeus = testaa_syote(ik.lue_kentan_sisalto(
        kayttoliittyman_komponentit["korkeus"]))
    miinoja = testaa_syote(ik.lue_kentan_sisalto(
        kayttoliittyman_komponentit["miinoja"]))
    if leveys[0] and korkeus[0] and miinoja[0]:
        luo_kentta(leveys[1], korkeus[1])
        if testaa_miinojen_maara(tila["kentta"], miinoja[1]):
            miinoita(tila["kentta"], miinoja[1])
            kaynnista_peli()
    else:
        ik.avaa_viesti_ikkuna("Virhe", "Syötä kokonaislukuja", True)


def lopeta():
    ik.lopeta()


def kaynnista_peli():
    try:
        tila["päättynyt"] = False
        tila["vuorot"] = 0
        aseta_numerot_kenttaan(tila["kentta"])
        ha.lataa_kuvat("spritet")
        ha.luo_ikkuna(len(tila["kentta"][0]) * 40, len(tila["kentta"]) * 40)
        ha.aseta_piirto_kasittelija(piirra_kentta)
        ha.aseta_hiiri_kasittelija(kasittele_hiiri)
        tila["aloitus_aika"] = time.time()
        ik.lopeta()
        ha.aloita()
    except RuntimeError:
        pass


if __name__ == "__main__":
    paavalikko()
