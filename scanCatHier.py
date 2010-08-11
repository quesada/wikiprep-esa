#!/usr/bin/python

'''
Copyright (C) 2010  Cagatay Calli <ccalli@gmail.com>

Scans XML output (gum.xml) from Wikiprep and outputs cat_hier file.
Output format: <cat id> <list of immediate descendants cat ids>

USAGE: scanCatHier.py <hgw.xml file from Wikiprep> <cat_hier output file path>

IMPORTANT: If you use XML output from a recent version of Wikiprep
(e.g. Zemanta fork), then set FORMAT to 'Zemanta-legacy' or 'Zemanta-modern'.

'''

import sys
import re

FORMAT = 'Gabrilovich'


# read list of stop categories from 'wiki_stop_categories.txt'
STOP_CATS = []
try:   
        f = open('wiki_stop_categories.txt','r')
        for line in f.readlines():
                [strId,strCat] = line.split('\t')
                STOP_CATS.append(int(strId))
        f.close()
except:
        print 'Stop categories cannot be read! Please put "wiki_stop_categories.txt" file containing stop categories in this folder.'
        sys.exit(1)


rePage = re.compile('<page id="(?P<id>\d+)".+?>(?P<page>.+?)</page>',re.MULTILINE | re.DOTALL)

reContent = re.compile('<title>(?P<title>.+?)</title>\n<categories>(?P<categories>.*?)</categories>',re.MULTILINE | re.DOTALL)

reCategory = re.compile("^Category:.+",re.DOTALL)

RSIZE = 10000000	# read chunk size = 10 MB

outFile = None

catDict = {}

# pageContent - <page>..content..</page>
# pageDict - stores page attribute dict
def recordArticle(pageDict):
   global outFile, catDict

   mContent = reContent.search(pageDict['page'])
   if not mContent:
	return

   contentDict = mContent.groupdict()

   title = contentDict['title']
   if not reCategory.match(title):
	return

   id = pageDict['id']
   curId = int(id)

   cats = contentDict['categories']

   # leaf category
   if not cats:
	return

   catIds = []
   for cat in cats.split():
	catIds.append(int(cat))

   catDict[curId] = catIds

   outFile.write(id + '\t' + cats + '\n')

   return


args = sys.argv[1:]
# scanCatHier.py <hgw_file> <RSIZE>

if len(args) < 2:
    sys.exit()

if len(args) == 3:
    RSIZE = int(args[2])

f = open(args[0],'r')
outFile = open(args[1],'w')
prevText = ''

firstRead = f.read(10000)

if FORMAT == 'Gabrilovich':
	documentStart = firstRead.find('</siteinfo>') + len('</siteinfo>')
else:
	documentStart = firstRead.find('<gum>') + len('<gum>')

prevText = firstRead[documentStart:10000]

while True:

    newText = f.read(RSIZE)
    if not newText:
        break
    
    text = prevText + newText

    endIndex = -1
    
    for page in rePage.finditer(text):
        recordArticle(page.groupdict())
	endIndex = page.end()

    prevText = text[endIndex:]

outFile.close()
f.close()

print 'cat_hier output complete'
print 'traversing category tree..'

cats = set(STOP_CATS)
outcats = set(STOP_CATS)

while cats:
	parent = cats.pop()
	childs = catDict[parent]
	outcats.update(childs)
	
	# avoid cycles/repeats
	for c in childs:
		if not c in outcats:
			cats.add(c)

# write extended stop category list
f = open('extended_stop_categories.txt','w')
for c in outcats:
	f.write(str(c) + '\n')
f.close()
