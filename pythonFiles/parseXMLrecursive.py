            

def extractData(nodes,data):
  for node in nodes:
    nchildren = node.getchildren()
    if nchildren:
      extractData(nchildren,data)
    else:
      data.append((node.tag, node.text))
  return data

def extractHeader(nodes,header):
  for node in nodes:
    nchildren = node.getchildren()
    if nchildren:
      extractHeader(nchildren,header)
    else:
      if node.tag not in header:
        header.append(node.tag)
  return header

data = []
data = extractData(root.findall('row'),data)

header = [] 
header = extractHeader(root.findall('row'),header)

prevTag = None
rowStart = header[0]
allData = []

def addElement(header,row,c, i, j):
  row.append('NULL')
  c +=1
  if header[c] == i:
    return row.append(j)
  else:
    addElement(header,row,c, i, j)

for i,j in data:
  
  if i == rowStart:
    row = []
    row.append(j)
    c = 1
  else:
    prevTag = header[c-1]
    if i == prevTag:
      row[-1] = row[-1] + ';' + j
    elif i == header[c]:
      row.append(j)
      c+=1
    else:
      addElement(header,row,c, i, j)
  allData.append(row)



  if i not in allData:
    allData[i] = []
    allData[i].append(j)
  elif i == prevTag:
    allData[i][-1] = allData[i][-1]+';'+j
  else:
    allData[i].append(j)
  prevTag = i