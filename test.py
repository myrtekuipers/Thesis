import re
import spacy
from spacy.tokenizer import Tokenizer

special_cases = {} #{":)": [{"ORTH": ":)"}]}
prefix_re = re.compile(r'''^[\[\("']''')
#prefix_re = re.compile(r'''<[0-9A-Za-z =\"\']+>''')
suffix_re = re.compile(r'''<[\w\W\s]+>''') #re.compile(r'''[\]\)"']$''')
infix_re = re.compile(r'''<[\w\W\s]+>''') #re.compile(r'''[-~]''')
simple_url_re = re.compile(r'''^https?://''')

def custom_tokenizer(nlp):
    return Tokenizer(nlp.vocab, rules=special_cases,
                                #prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                url_match=simple_url_re.match)

nlp = spacy.load("nl_core_news_sm")
nlp.tokenizer = custom_tokenizer(nlp)
doc = nlp("Deze gel of crème mag je niet gebruiken als je zwanger bent of wilt worden.")
print([t.text for t in doc]) # ['hello', '-', 'world.', ':)']