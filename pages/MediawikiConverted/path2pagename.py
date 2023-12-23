import csv
from os import listdir
def hyphenToSpace(TEXT):
    TEXT=list(TEXT)
    for i in range(0,len(TEXT)-1):
        if i==0 or TEXT[i-1]==" ":
            TEXT[i]=TEXT[i].upper()
        if TEXT[i]=="-":
            TEXT[i]=" "
    TEXT=''.join(TEXT)
    return TEXT
def upperCase(TEXT):
    TEXT=list(TEXT)
    for i in range(0,len(TEXT)-1):
        if i==0 or TEXT[i-1]=="-":
            TEXT[i]=TEXT[i].upper()
    TEXT=''.join(TEXT)
    return TEXT

def convertAndSave(PATHNAME):
    original_file=open(PATHNAME,"r",encoding="utf-8")
    text=original_file.read()
    original_file.close()
    for item in pagedex:
        text=text.replace("[\\"+item[0]+"|","[\\"+item[1]+"|")
        text=text.replace("[["+item[0]+"|","[["+item[1]+"|")
        text=text.replace("[\\"+hyphenToSpace(item[0])+"|","[\\"+item[1]+"|")
        text=text.replace("[["+hyphenToSpace(item[0])+"|","[["+item[1]+"|")
        text=text.replace("[\\"+upperCase(item[0])+"|","[\\"+item[1]+"|")
        text=text.replace("[["+upperCase(item[0])+"|","[["+item[1]+"|")
        text=text.replace("[\\"+item[0]+" ","[\\"+item[1]+" ")
        text=text.replace("[["+item[0]+" ","[["+item[1]+" ")
        text=text.replace("[\\"+hyphenToSpace(item[0])+" ","[\\"+item[1]+" ")
        text=text.replace("[["+hyphenToSpace(item[0])+" ","[["+item[1]+" ")
        text=text.replace("[\\"+upperCase(item[0])+" ","[\\"+item[1]+" ")
        text=text.replace("[["+upperCase(item[0])+" ","[["+item[1]+" ")
        text=text.replace("|]]","]]")
        text=text.replace("[/","[[")
    new_file=open("output\\"+PATHNAME,"w",encoding="utf-8")
    new_file.write(text)
    new_file.close
    

pagedex_file=open("000-path,pagename.csv","r",encoding="utf-8")
pagedex=list(csv.reader(pagedex_file,delimiter=","))
pagedex_file.close()

for path in listdir(".\\"):
    if ".txt" in path:
        convertAndSave(path)
        print(path+"is converted")