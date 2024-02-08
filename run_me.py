
from EL import EntityLinking

with open('data/situation_content.txt') as f:
        content = f.read()
        example_doc = content[:content.find('Situatie:', content.find('Situatie:')+1)]

#doc = "Bij wie wordt het risico op hart en vaatziekten geschat. Voor veel patiënten is een risicocategorie aan te wijzen zonder dat hun risico kwantitatief geschat hoeft te worden met een risicoscore. Denk aan patiënten met bestaande hart en vaatziekten, diabetes mellitus en daarmee gepaard gaande orgaanschade, ernstige chronische nierschade en extreem verhoogde risicofactoren. Deze categorieën staan toegelicht in tabel 1."

# HTML file test
#f = open('html_test.txt','r')
#doc = f.read()
#f.close()

el = EntityLinking(example_doc)
print("Finished!")

