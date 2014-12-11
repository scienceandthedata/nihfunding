def extractXmlText(data,tags,texts):
  nrTags = len(set(tags))
  if nrTags <= 1:
    if tags[0] in data:
      data[tags[0]].append(texts)
    else:
      data[tags[0]] = []
      data[tags[0]].append(texts)
  else:
    for tag, text in zip(tags,texts):
      if tag in data:
        data[tag].append(text)
      else:
        data[tag] = []
        data[tag].append(text)
  return data

data = {}
for node in root.findall('row'):
  tags = []
  texts = []
  
  cnodes = node.getchildren()
  if cnodes:
    for cnode in cnodes:
      tags = []
      texts = []
      
      ccnodes = cnode.getchildren()
      if ccnodes:
        for ccnode in ccnodes:
          tags = []
          texts = []
          
          cccnodes = ccnode.getchildren()
          if cccnodes:
            for cccnode in cccnodes:
              tags = []
              texts = []

              ccccnodes = cccnode.getchildren()
              if ccccnodes:
                print "Aahhh! Code only parses xml up to four levels deep. This file has more levels. GET OUT OF HERE ...\n\n"
                #sys.exit(1)
          
              else:
                tags.append(cccnode.tag)
                texts.append(cccnode.text)
                data = extractXmlText(data,tags,texts)
          else:
            tags.append(ccnode.tag)
            texts.append(ccnode.text)
            data = extractXmlText(data,tags,texts)
      else:
        tags.append(cnode.tag)
        texts.append(cnode.text)
        data = extractXmlText(data,tags,texts)
  else:
    tags.append(node.tag)
    texts.append(node.text)
    data = extractXmlText(data,tags,texts)








