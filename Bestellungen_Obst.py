import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from copy import deepcopy
from math import pi


def auflistung_der_Sortimente(bestandsdaten): # Zu Beginn des Programms werden alle Firmen mit den entsprechenden Angeboten angezeigt.
    for firma in bestandsdaten["Firma"]: # Als nächstes kommt der Firmenname
        print("Firma: ", firma["Name"])
        for posten in firma["Lager"]:
            typ = posten["Typ"]
            sorte = posten["Sorte"]
            bestand = posten["Lagerbestand"]
            preis = posten["PreisProKG"]
            print(f"Typ: {typ}")
            print(f"\t{sorte} \t\t| Bestand: {bestand} kg | {preis}€/kg")
            print("")

def user_abfrage(frage, options_liste):
    if len(options_liste) == 0: return None
    while True:
        for i in range(len(options_liste)):
            print(f"{i}: {options_liste[i]}")
        print(frage)
        chosen_option = input()
        if not chosen_option.isdigit():
            print(f"Bitte wählen Sie eine Zahl zwischen 0 und {len(options_liste)-1}")
        elif int(chosen_option) >= len(options_liste):
            print("Diese Option ist nicht verfügbar")
        else:
            return(options_liste[int(chosen_option)])

def bestellung(bestandsdaten,warenkorb):
    auflistungProdukte = []
    auflistungSorten = []
    sortenListe = []
    firmenListe = []
    for firma in bestandsdaten["Firma"]:
        for produkt in firma["Lager"]:
            if produkt["Typ"] not in auflistungProdukte:
                auflistungProdukte.append(produkt["Typ"])
    
    produkteingabe_kunde = user_abfrage("Welches Produkt möchten Sie haben", auflistungProdukte)

    print(produkteingabe_kunde)
    produktListe = produktlisteBefüllen(bestandsdaten,produkteingabe_kunde,)
    sortenListe = sortenListeBefüllen(produktListe,sortenListe)

    sorteneingabe_kunde = user_abfrage("Welche Sorte möchten Sie",sortenListe)

    gesamtmenge = gesamtmengeBerechnen(produktListe, sorteneingabe_kunde)
    gewuenschteMenge = int(input(f"Wir haben {gesamtmenge} kg im Angebot. Wie viel Kilogramm möchten Sie kaufen? "))
    while gewuenschteMenge <= 0 or gewuenschteMenge > gesamtmenge:
        gewuenschteMenge = int(input(f"Die gewünschte Menge überschreitet unseren Lagerbestand oder ist kleiner als 1. Bitte geben Sie eine neue Menge ein: ")) # Fehlerhafte MengeneingabeEe
    if gewuenschteMenge <= gesamtmenge and gewuenschteMenge > 0:
        #Sicherheit, das die Menge nicht zu groß ist oder unter 1
        bestandsdaten,warenkorb = produktAuswaehlenUndWarenkorbHinzufuegen(bestandsdaten,sorteneingabe_kunde, gewuenschteMenge, produktListe,warenkorb)
        return bestandsdaten,warenkorb

def produktlisteBefüllen(bestandsdaten,produkteingabe_kunde):
    produktliste = [] # Vorerst leere Liste, in der später Produktinformationen hinzugefügt werden
    einProdukt = { # Dieses Dictionary beinhalt alle Informationen über ein Produkt (Durch Nutzereingabe)
        "Typ": "",
        "Sorte": "",
        "Bestand": "", # Kategorien der json Datei
        "PreisKG": "",
        "Firmenname": ""
    }
    for firma in bestandsdaten["Firma"]: # Läuft durch jedes Element bzw. Angebot der Firmen (.json Datei)
        for posten in firma["Lager"]:
            if produkteingabe_kunde == posten["Typ"]: # Wenn Die Eingabe, die der User tätigt, mit einem Typen in der Liste übereinstimmt, dann Nimm die anderen Informationen und füge Sie dem Dictionary hinzu
                einProdukt["Typ"] = produkteingabe_kunde
                einProdukt["Sorte"] = posten["Sorte"]
                einProdukt["Bestand"] = posten["Lagerbestand"]
                einProdukt["PreisKG"] = posten["PreisProKG"]
                einProdukt["Firmenname"] = firma["Name"]
                produktliste.append(einProdukt.copy()) # Zu der Produktliste werden dann alle Informationen von "einProdukt" hinzugefügt, aber als Kopie, weil sonst "einProdukt", bei möglichen doppelten Typen bzw. Sorten, überschrieben wird und nicht bloß hinzugefügt

    return(produktliste) # Der return Command verlässt die Funktion an dieser Stelle

def sortenListeBefüllen(produktListe,sortenListe): # Hier wird anhand des gewünschte Produktes des Nutzers nach den Sorten geschaut, die dann im Terminal ausgegeben werden, damit der Nutzer sieht, welche Sorten er kaufen kann
    for einProdukt in produktListe:
        if einProdukt["Sorte"] not in sortenListe:
            sortenListe.append(einProdukt["Sorte"])
    return sortenListe
    
def gesamtmengeBerechnen(postenListe, sorte): # Hier wird nach der verfügbaren GESAMTMENGE der *eingegebenen* Sorte geschaut. Dabei werden vorerst nicht auf verschiedene Preise geachtet.
    gesamtmenge = 0
    for posten in postenListe:
        if posten["Sorte"] == sorte: # Wenn die eingegebene Sorte mit der Sorte der json Datei übereinstimmt, nimm den Lagerbestand und addiere diese
            gesamtmenge = gesamtmenge + posten["Bestand"]
    return gesamtmenge

def indexBesterPreis(produktListe, sorte): # Hier wird der Index zurückgegeben, an dem der günstigste Preis gefunden wurde (damit dem Nutzer zum Schluss automatisch der günstigste Preis aufgetischt wird)
    minimum = -1 # -1 ist der Hinweis für das Programm, dass noch kein Wert zum vergleichen hinzugefügt wurde
    index = -1 # - " -
    count = 0
    for produkt in produktListe:
        # print("Produktliste: ", produktListe)
        # print(f"PRODUKT : {produkt}")
        if sorte == produkt["Sorte"]: # Wenn die Sorte wieder übereinstimmt
            if minimum < 0: # Wenn minimum unter 0 liegt (was es hier tut, weil es oben als -1 deklariert ist)
                minimum = produkt["PreisKG"] # Dann nimmt minimum der PreisProKG von genau dieser Sorte an
                index = count # Der Index wird gezählt, damit dieser Artikel dann später angesprochen werden kann
            elif produkt["PreisKG"] < minimum: # Prüfung, ob bereits ein Wert eingefügt wurde und minimum Funktion -> Wenn der Preis vom nächsten, gleichen Produkt kleiner ist, nimmt minimum den kleineren Preis an
                minimum = produkt["PreisKG"] # 
                index = count
                # print("#############################################", index)
        # print("count: ", count)
        count = count + 1
    return index
    # print(f"Kleinster Preis: {minimum} beim Index: {index}")

def produktAuswaehlenUndWarenkorbHinzufuegen(bestandsdaten,sorte, gewünschteMenge, produktListe, warenkorb):
    while gewünschteMenge > 0: # Solange die gewünschte Menge nicht abgedeckt ist, suche weiter nach den Produkten. Wenn die Menge eines Preis ausgeht, dann nimm die nächste Menge mit dem nächstbesten Preis 
        indexLP = indexBesterPreis(produktListe, sorte) # Der index wird wiederverwendet
        #print("AFFE::::::::::::::::______________________", produktListe[indexLP])
        if gewünschteMenge <= produktListe[indexLP]["Bestand"]: # Genau ein Posten wird angesprochen (Bestand) und solange die gewünschte Menge kleiner ist als der Bestand in der Produktliste (gesamtbestand), dann ziehe es einfach von dem gesamtbestand ab
            bestandsdaten,warenkorb = abInDenWarenkorb(bestandsdaten,gewünschteMenge, produktListe[indexLP].copy(),warenkorb) # Setze diese Funktion ein (Bestand überschreiben)
            gewünschteMenge = 0
            # print("Gewünschte Menge Reduziert")
        elif gewünschteMenge > produktListe[indexLP]["Bestand"]:
            # print("Das war zu viel für eine Firma")
            bestandsdaten,warenkorb = abInDenWarenkorb(bestandsdaten,produktListe[indexLP]["Bestand"], produktListe[indexLP].copy(),warenkorb)
            #print("################### PRUDUKTLISTE: ", produktListe)
            gewünschteMenge = gewünschteMenge - produktListe[indexLP]["Bestand"]
            produktListe.pop(indexLP) # Wenn der Bestand komplett aufgebraucht wird, dann lösche das Produkt
    return(bestandsdaten,warenkorb)

def abInDenWarenkorb(bestandsdaten,bestellmenge, einProdukt,warenkorb):
    # print("Warenkorb Prüfung Bestand: ", einProdukt["Bestand"], "für Firma: ", einProdukt["Firmenname"])
  #  if einProdukt["Bestand"] == 0:
    einProdukt.pop("Bestand")
  #  if einProdukt["Bestand"] > 0 and einProdukt["Bestand"] > bestellmenge:
  #      einProdukt["Bestand"] = einProdukt["Bestand"] - bestellmenge
    einProdukt["Bestellmenge"] = bestellmenge # Die Bestellmenge wird zu dem Dictionary hinzugefügt und entspricht der gewünschten Menge
    # print("Produkt vor Warenkorb: ", einProdukt)
    warenkorb.append(einProdukt) # Das Dictionary, also alle Produktinformationen, wird dem Warenkorb hinzugefügt
    bestandsdaten = bestandReduzierer(bestandsdaten,einProdukt.copy()) # Funktion bestandReduzierer
    # print(f"Warenkorb: {warenkorb}")
    return(bestandsdaten,warenkorb)

def bestandReduzierer(bestandsdaten, einProdukt):
    # print("Frimenname BeRe: ", einProdukt)
    for firma in bestandsdaten["Firma"]: # Es wird durch die Firmen iteriert (in dem Fall nur Namen oder die Erweiterung "Lager")
        if einProdukt["Firmenname"] == firma["Name"]: 
            # Wenn der Name mit dem Firmennamen übereinstimmt liegt der Index bei 0
            indexHD = 0
            for posten in firma["Lager"]: # Hier wird dann durch das Lager iteriert
                if posten["Typ"] == einProdukt["Typ"] and posten["Sorte"] == einProdukt["Sorte"]: # Wenn der Typ UND die Sorte übereinstimmen dann ist der Lagerbestand von der Firma subtrahiert mit der Bestellmenge
                    posten["Lagerbestand"] = posten["Lagerbestand"] - einProdukt["Bestellmenge"]
                    # print("PPPOOSSSTEEEEENNN LLAGERBESTAAAAND: ", posten["Lagerbestand"])
                    if posten["Lagerbestand"] == 0: 
                        # Wenn der Lagerbestand leer ist, soll das Produkt gelöscht werden, weil es logischerweise nicht mehr verkauft werden
                        # print("ACHTUNG! Jetzt wird gelöscht. POP!")
                        firma["Lager"].pop(indexHD)
                    break
                indexHD = indexHD + 1 # Hier wird der Index wieder erhöht, damit sich der Index für das leere Produkt gemerkt werden kann
    return(bestandsdaten)

def warenkorbSortieren(warenkorb):
    warenkorbSortiert = {}
    for dict in warenkorb:
        firmenname = dict["Firmenname"]
        if firmenname not in warenkorbSortiert:
            warenkorbSortiert[firmenname] = []
        dict.pop("Firmenname")
        warenkorbSortiert[firmenname].append(dict)
    return(warenkorbSortiert)

def rechnung_in_xml(warenkorb,firmenListe):
    warenkorbSortiert = warenkorbSortieren(warenkorb)

    gesamtpreis_rechnung = 0

    root = ET.Element("Daten")
    ebene1 = ET.SubElement(root, "Firmen")
    for firma, produkte in warenkorbSortiert.items():
        daten0_01 = ET.SubElement(ebene1, "Name")
        daten0_01.text = firma

        daten0_02 = ET.SubElement(ebene1, "Bestellung")

        gesamtpreis_firma = 0
        for posten in produkte:   
            print(posten)
            daten1_00 = ET.SubElement(daten0_02, "Posten")

            daten1_01 = ET.SubElement(daten1_00, "Produkttyp")
            daten1_01.text = posten["Typ"]
                
            daten1_02 = ET.SubElement(daten1_00, "Sorte")
            daten1_02.text = posten["Sorte"]
                
            daten1_03 = ET.SubElement(daten1_00, "Menge")
            daten1_03.text = str(round(posten["Bestellmenge"],2))
                
            daten2 = ET.SubElement(daten1_00, "Preis")
            daten2.text = str(round(posten["Bestellmenge"]*posten["PreisKG"],2))

            gesamtpreis_firma += posten["Bestellmenge"]*posten["PreisKG"]

        daten1_04 = ET.SubElement(ebene1, "GesamtpreisEineFirma")
        daten1_04.text = str(round(gesamtpreis_firma,2))

        gesamtpreis_rechnung += gesamtpreis_firma

    gesamtPreis = ET.SubElement(root, "Gesamtpreis")
    gesamtPreis.text = str(round(gesamtpreis_rechnung,2))

    tree = ET.ElementTree(root)
    tree.write("Rechnung_Einkaufssoftware.xml")



def main():
    # Initialisierung Warenkorb und Bestandsdaten
    warenkorb = []
    with open('erstellungVonBeispieldaten.json', "r") as datei:
        bestandsdaten = json.load(datei)

    #Bestellen bis Abbruchkriterien erfüllt sind
    while True:
        #Auflistung Sortiment
        auflistung_der_Sortimente(bestandsdaten)

        #Bestellung durchführen, Daten updaten
        bestandsdaten, warenkorb = bestellung(bestandsdaten,warenkorb)

        #Abbruchkriterium 1: Lager leer
        lager_leer = 0
        for firma in bestandsdaten["Firma"]:
            lager_leer += len(firma["Lager"])
        if lager_leer == 0:
            print("Alles alle")
            break
        
        #Abfrage ob noch mehr bestellt werden soll
        x = user_abfrage("Möchten Sie noch mehr bestellen?",["Ja","Nein"])
        if x == "Nein":
            break
    print("Vielen Dank für Ihren Einkauf die Bestellung ist abgeschlossen")

    firmenListe = []
    for firmen in warenkorb:
        if firmen["Firmenname"] not in firmenListe:
            firmenListe.append(firmen["Firmenname"])

    rechnung_in_xml(warenkorb,firmenListe)


#Starte mit main() als Eisntiegspunkt
if __name__ == "__main__":
    main()