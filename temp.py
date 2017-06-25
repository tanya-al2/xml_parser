#from xml.etree.ElementTree import parse, tostring
from PyQt5.QtCore import QXmlStreamReader, QFile

#doc = parse('/home/tanya/Documents/myutility/in/1200000412015121700005018.xml')
file = QFile('/home/tanya/Documents/myutility/1000320142016040100000073.xml')
fileOpens = file.open(file.ReadOnly | file.Text)
doc = QXmlStreamReader(file)
temp = doc.readElementText()
while not doc.atEnd():
doc.readNext()
name = doc.name()
attrib=doc.attributes()
if name=='To':
txt = doc.readElementText()
pass
#tokenName = doc.tokenType()
pass
#.readElementText('executorPhone')
#elem = doc.findall('executorPhone')
pass