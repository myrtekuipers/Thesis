
from EL import EntityLinking
import csv

doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."

#doc = "Met gezond eten krijgt u de meeste vitamines binnen, in de juiste hoeveelheid. Er zijn maar een paar vitamines die u extra kan gebruiken: Heeft u een getinte huid? Dan is extra vitamine D het hele leven aan te raden. Heeft u een lichte huid? Neem op latere leeftijd vitamine D: als vrouw vanaf 50 jaar, als man vanaf 70 jaar. Vitamine B12 heeft u nodig als u alleen plantaardig eet (veganistisch). Als u zwanger bent (of wilt worden): slik foliumzuur en vitamine D, ook als u een lichte huid heeft. Neem geen vitaminepillen waar te veel vitamines in zitten. Te veel is als er een getal boven 100% op het potje staat. Dit kan schadelijk zijn."
#doc = "Taaislijmziekte is een ernstige aangeboren ziekte.  Heeft uw kind volgens de hielprik waarschijnlijk taaislijmziekte? Dan is meer onderzoek nodig.  Uw kind krijgt dan een zweettest.  Uw kind krijgt elektroden op de huid. Die zorgen dat uw kind gaat zweten.   Het zweet wordt opgevangen en onderzocht.   Bij taaislijmziekte zit er meer zout in zweet.  Een verpleegkundige heeft in de eerste week na de geboorte een paar druppels bloed afgenomen bij uw kind (hielprik). Dit bloed is onderzocht op een aantal aangeboren ziektes, zoals taaislijmziekte.  U hoort van de huisarts dat de kans groot is dat uw kind taaislijmziekte heeft. Om dit zeker te weten, is meer onderzoek nodig. De huisarts stuurt u door naar een ziekenhuis speciaal voor mensen met taaislijmziekte. Hier wordt uw kind onderzocht door een kinderlongarts.  Zweettest  Uw kind krijgt een zweettest. Deze test meet hoeveel zout er in het zweet van uw kind zit. Mensen met taaislijmziekte hebben meer zout in hun zweet.  De zweettest gaat zo:  Uw kind krijgt elektroden op de huid. Meestal op de onderarm of het bovenbeen. Elektroden zijn kleine stickers met een draadje eraan.  De elektroden zorgen dat uw kind gaat zweten. Dat doet geen pijn.  Het zweet wordt opgevangen.  In het laboratorium wordt het zweet onderzocht.  Meestal hoort u op de dag van het onderzoek of uw kind taaislijmziekte heeft. De zweettest kan mislukken. Heel jonge baby’s kunnen namelijk nog niet goed zweten. De kinderlongarts bespreekt dan met u wat u wilt: de zweettest later nog een keer laten doen of een bloedonderzoek. Contact met andere mensen die taaislijmziekte hebben en informatie en tips over leven met taaislijmziekte: Nederlandse Cystic Fibrosis Stichting."
#HTML file test
# f = open('html_test.txt','r')
# doc = f.read()
# f.close()

doc = "Deze gel of crème mag je niet gebruiken als je zwanger bent of wilt worden."

el = EntityLinking(doc)
    
print("Finished!")



