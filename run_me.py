
from EL import EntityLinking
import csv

# with open('data/situation_content.txt') as f:
#         content = f.read()
#         example_doc = content[:content.find('Situatie:', content.find('Situatie:')+1)]

#get the text from task_data and then column text
with open('data/task_data.csv', 'r') as file:
    content = csv.reader(file)
    next(content)
    for row in content:
        task_id = row[0]
        situation_title = row[1]
        example_doc = row[2]
        break
    

# doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."
# doc = "Taaislijmziekte is een ernstige aangeboren ziekte.  Heeft uw kind volgens de hielprik waarschijnlijk taaislijmziekte? Dan is meer onderzoek nodig.  Uw kind krijgt dan een zweettest.  Uw kind krijgt elektroden op de huid. Die zorgen dat uw kind gaat zweten.   Het zweet wordt opgevangen en onderzocht.   Bij taaislijmziekte zit er meer zout in zweet.  Een verpleegkundige heeft in de eerste week na de geboorte een paar druppels bloed afgenomen bij uw kind (hielprik). Dit bloed is onderzocht op een aantal aangeboren ziektes, zoals taaislijmziekte.  U hoort van de huisarts dat de kans groot is dat uw kind taaislijmziekte heeft. Om dit zeker te weten, is meer onderzoek nodig. De huisarts stuurt u door naar een ziekenhuis speciaal voor mensen met taaislijmziekte. Hier wordt uw kind onderzocht door een kinderlongarts.  Zweettest  Uw kind krijgt een zweettest. Deze test meet hoeveel zout er in het zweet van uw kind zit. Mensen met taaislijmziekte hebben meer zout in hun zweet.  De zweettest gaat zo:  Uw kind krijgt elektroden op de huid. Meestal op de onderarm of het bovenbeen. Elektroden zijn kleine stickers met een draadje eraan.  De elektroden zorgen dat uw kind gaat zweten. Dat doet geen pijn.  Het zweet wordt opgevangen.  In het laboratorium wordt het zweet onderzocht.  Meestal hoort u op de dag van het onderzoek of uw kind taaislijmziekte heeft. De zweettest kan mislukken. Heel jonge baby’s kunnen namelijk nog niet goed zweten. De kinderlongarts bespreekt dan met u wat u wilt: de zweettest later nog een keer laten doen of een bloedonderzoek. Contact met andere mensen die taaislijmziekte hebben en informatie en tips over leven met taaislijmziekte: Nederlandse Cystic Fibrosis Stichting."
# HTML file test
#f = open('html_test.txt','r')
#doc = f.read()
#f.close()

el = EntityLinking(example_doc)

print(el.AllCandidates)

for candidate in el.AllCandidates:
    print(candidate.variations[candidate.match_variation].text)

print("Finished!")



