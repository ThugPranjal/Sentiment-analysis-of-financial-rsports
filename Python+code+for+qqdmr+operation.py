
# coding: utf-8

# In[9]:

import pandas as pd
import re
import urllib2
from textblob import TextBlob
pd.options.display.max_colwidth = 100
import urllib
from bs4 import BeautifulSoup


# In[10]:

cik_list=pd.read_excel("cik_list.xlsx")
uncertainty_list=list(pd.read_excel("uncertainty_dictionary.xlsx")["Word"])
uncertainty_list=(str(" ".join(uncertainty_list).lower())).split()
constraining_list=list(pd.read_excel("constraining_dictionary.xlsx")["Word"])
constraining_list=(str(" ".join(constraining_list).lower())).split()


# In[16]:

cik_list.loc[105]


# In[12]:

def complete_text(link):                  # Function to extract the complete text from the url
    url = link
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


# In[76]:

def remove_stop_words(text):                                                        #Function to remove stop words
    mytxt=TextBlob(text)
    l=mytxt.tags
    word_list=[]
    for word, tag in l:
        if  str(tag)=="RB" or str(tag)=="JJ" or str(tag)=="NN" or str(tag)=="VBG":
            word_list.append(word)
            
    text=" ".join(word_list)
    text= re.sub('\W+',' ', text )
    return str(text)


# In[14]:

def CheckLines(line1, line2):          
    line1=line1.lower()
    line2=line2.lower()
    wordlist=line1.split()
    wordlist=wordlist+line2.split()
    count=wordlist.count("qualitative")+wordlist.count("quantitative")+wordlist.count("disclosures")+wordlist.count("market")+wordlist.count("risk")
        
    ispresent=wordlist.count("7a.")==0 and wordlist.count("qualitative")!=0 and wordlist.count("quantitative")!=0 and wordlist.count("disclosures")!=0
   
    return count>=4 and ispresent 
        


# In[78]:

def findend(text):
    text=text.lower()
    index=text.find("\n\nitem")
    if index==-1:
        index=text.find("\n\npart")
        
    return index
    
    


# In[18]:

def find_qqdmr_text(link):                        # Function to extract he required qqdmr text from the complete text
    text=complete_text(link)
    linelist=text.split("\n")
    i=0
    start=0
    while i <len(linelist)-2:
        if CheckLines(linelist[i], linelist[i+1]):
            start=i
        i+=1
        
   
   
    if start==0:
        return ""
    
    for line in linelist[start+1:]:
        if line.lower().startswith("item ") or line.lower().startswith("part "):
                end=linelist[start+1:].index(line)+start+1
                
                break
    
    text=''.join(linelist[start:end])
    text=text.encode('ascii','ignore')
    
    
    return text


# In[19]:

text=find_qqdmr_text("https://www.sec.gov/Archives/edgar/data/4962/0001193125-14-167067.txt")


# In[81]:

def positive_score(text):                #Function to calculate number of positive words in the article
    poscount=0
    mytxt=TextBlob(text)
    l=mytxt.words
    for word in l:
        mywrd=TextBlob(word)
        if mywrd.polarity>0.2:
            poscount+=1
        
    return poscount


# In[82]:

def negative_score(text):                    #Function to find out number of negative words
    negcount=0
    mytxt=TextBlob(text)
    l=mytxt.words
    for word in l:
        mywrd=TextBlob(word)
        if mywrd.polarity<-0.2:
            negcount+=1
        
    return negcount


# In[83]:

def average_sentence_length(link):              #Function to find out average sentence length
    text=find_qqdmr_text(link)
    mytext=TextBlob(text)
    sentence_count=len(mytext.sentences)
    word_count=len(mytext.words)
    if sentence_count==0:
        return 0
    return (word_count*1.0)/sentence_count


# In[84]:

def syllables(word):                               #Function to find the number of syllables in a word
    count = 0
    vowels = 'aeiouy'
    word = word.lower().strip(".:;?!")
    if word[0] in vowels:
        count +=1
    for index in range(1,len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            count +=1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count+=1
    if count == 0:
        count +=1
    return count


# In[85]:

def count_complex_words(link):                  #Function to count the number of complex words in the paragraph
    text=find_qqdmr_text(link)
    mytext=TextBlob(text)
    word_list=list(mytext.words)
    count_complex=0
    percentage_complex=0
    for word in word_list:
        if syllables(word)>=2:
            count_complex+=1
    if len(word_list)!=0:
        percentage_complex=((count_complex*1.0)/len(word_list))*100

    dic={"percentage complex words":percentage_complex,
         "count complex words":count_complex,
         "qqdmr word list":len(word_list)
        }
    return dic


# In[86]:

def count_uncertainty(link):                      #Function to calculate the uncertainty index of the article
    text=find_qqdmr_text(link)
    text=(remove_stop_words(text)).lower()
    text=TextBlob(text)
    count=0
    word_list=list(text.words)
    for word in word_list:
        if uncertainty_list.count(word)!=0:
            count+=1
    
    return count


# In[87]:

def count_constraining(link):                    #Function to calculate the number of constraining words in the article
    text=find_qqdmr_text(link)
    text=(remove_stop_words(text)).lower()
    text=TextBlob(text)
    count=0
    word_list=list(text.words)
    for word in word_list:
        if constraining_list.count(word)!=0:
            count+=1
    
    return count


# In[88]:

positive_list=[]
negative_list=[]
average_sentence_length_list=[]
complex_count_list=[]
complex_perecentage_list=[]
qqdmr_word_list=[]
qqdmr_constraining_list=[]
qqdmr_uncertainty_list=[]
polarity_list=[]
subjectivity_list=[]


# In[92]:

def run(index):
    while index<cik_list["SECFNAME"].count():
        
        link=cik_list.loc[index]["SECFNAME"]
        qqdmr_text=find_qqdmr_text(link)
        qqdmr_text=remove_stop_words(qqdmr_text)
        
        p_score=positive_score(qqdmr_text)
        n_score=negative_score(qqdmr_text)
        txt=TextBlob(qqdmr_text)
        polarity, subjectivity=txt.sentiment
        positive_list.append(p_score)
        negative_list.append(n_score)
        polarity_list.append(polarity)
        subjectivity_list.append(subjectivity)
        
        sentence_length=average_sentence_length(link)
        average_sentence_length_list.append(sentence_length)
        
        d=count_complex_words(link)
        complex_count_list.append(d["count complex words"])
        complex_perecentage_list.append(d["percentage complex words"])
        qqdmr_word_list.append(d["qqdmr word list"])
        
        qqdmr_constraining_count=count_constraining(link)
        qqdmr_uncertainty_count=count_uncertainty(link)
        qqdmr_constraining_list.append(qqdmr_constraining_count)
        qqdmr_uncertainty_list.append(qqdmr_uncertainty_count)
        
        print p_score
        print n_score
        print polarity
        print subjectivity
        print "Average sentence length:",sentence_length
        print "Total words in this link's qqdmr text",d["qqdmr word list"]
        print d["count complex words"],"-Count of complex words"
        print d["percentage complex words"],"-% of complex words"
        print qqdmr_uncertainty_count,"-Count of uncertainty words"
        print qqdmr_constraining_count,"-Count of constraining words"


       
        print "",index,"done \n"
        index+=1


# In[119]:

run(0)


# In[157]:

superlist=[]                                              #Code to handle connection interrupt
superlist.append(positive_list)                         
superlist.append(negative_list)
superlist.append(average_sentence_length_list)
superlist.append(complex_count_list)
superlist.append(complex_perecentage_list)
superlist.append(rf_word_list)
superlist.append(rf_constraining_list)
superlist.append(polarity_list)
superlist.append(subjectivity_list)
superlist.append(rf_uncertainty_list)

def remove_extra(superlist, x):
    i=0
    while i < len(superlist):
        print len(superlist[i])
        if len(superlist[i])>x+1:
            print "lengh before change",len(superlist[i]),"/n"
            superlist[i]=superlist[i][:(x+1)]
            print "lengh after change",len(superlist[i]),"/n"

        i+=1
        
remove_extra(superlist,62)
        
for l in superlist:
    print "Changed length",len(l)
    
positive_list=superlist[0]
negative_list=superlist[1]
average_sentence_length_list=superlist[2]
complex_count_list=superlist[3]
complex_perecentage_list=superlist[4]
rf_word_list=superlist[5]
rf_constraining_list=superlist[6]
polarity_list=superlist[7]
subjectivity_list=superlist[8]
rf_uncertainty_list=superlist[9]


# In[164]:

cik_list["qqdmr_constraining_word_proportion"]=qqdmr_constraining_list
cik_list["qqdmr_uncertainty_word_proportion"]=qqdmr_uncertainty_list
cik_list["qqdmr_word_count"]=qqdmr_word_list
cik_list["qqdmr_constraining_word_proportion"]=cik_list["qqdmr_constraining_word_proportion"]/cik_list["qqdmr_word_count"]
cik_list["qqdmr_uncertainty_word_proportion"]=cik_list["qqdmr_uncertainty_word_proportion"]/cik_list["qqdmr_word_count"]
cik_list["qqdmr_percentage_of_complex_words"]=complex_perecentage_list
cik_list["qqdmr_count_of_complex_words"]=complex_count_list

cik_list["qqdmr_average_sentence_length"]=average_sentence_length_list
cik_list["qqdmr_positive_score"]=positive_list
cik_list["qqdmr_negative_score"]=negative_list
cik_list["qqdmr_polarity_score"]=polarity_list
cik_list["qqdmr_fog_index"]=cik_list["qqdmr_average_sentence_length"]+cik_list["qqdmr_percentage_of_complex_words"]
cik_list["qqdmr_fog_index"].apply(lambda x: x*0.4)
cik_list["qqdmr_fog_index"]=cik_list["qqdmr_fog_index"].apply(lambda x: x*0.4)


# In[165]:

cik_list


# In[167]:

cik_list.to_excel("cik_list_qqdmr.xlsx")


# In[17]:

find_qqdmr_text("https://www.sec.gov/Archives/edgar/data/6201/0000006201-01-500047.txt")


# In[ ]:



