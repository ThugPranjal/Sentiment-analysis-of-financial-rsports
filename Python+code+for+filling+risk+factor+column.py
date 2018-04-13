
# coding: utf-8

# In[319]:

import pandas as pd
import re
import urllib2
from textblob import TextBlob
pd.options.display.max_colwidth = 100
import urllib
from bs4 import BeautifulSoup


# In[320]:

cik_list=pd.read_excel("cik_list.xlsx")
uncertainty_list=list(pd.read_excel("uncertainty_dictionary.xlsx")["Word"])
uncertainty_list=(str(" ".join(uncertainty_list).lower())).split()
constraining_list=list(pd.read_excel("constraining_dictionary.xlsx")["Word"])
constraining_list=(str(" ".join(constraining_list).lower())).split()


# In[321]:

cik_list.loc[25]


# In[322]:

def remove_stop_words(text):                                                        #Function to remove stop words
    mytxt=TextBlob(text)
    l=mytxt.tags
    word_list=[]
    for word, tag in l:
        if  str(tag)=="RB" or str(tag)=="JJ" or str(tag)=="NN" or str(tag)=="VBG":
            word_list.append(word)
            
    text=" ".join(unique_list(word_list))
    text= re.sub('\W+',' ', text )
    return str(text)


# In[323]:

def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist



# In[324]:

def CheckLines(line):
    line=line.lower()
    wordlist=line.split()
  
    count=wordlist.count("risk")+wordlist.count("factors")
        
    ispresent=  wordlist.count("risk")!=0 and  wordlist.count("factors")!=0   
    return count>=2 and ispresent 
        


# In[325]:

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
    


# In[326]:

link="https://www.sec.gov/Archives/edgar/data/6201/0000006201-09-000038.txt"


# In[70]:

text=complete_text(link)


# In[71]:

text
#text


# In[126]:

text=complete_text(link)
linelist=text.split("\n")
start=0
for line in linelist:
        if line.lower().encode('ascii','ignore')=="item 1a.risk factors" or line.lower().encode('ascii','ignore')=="item 1a. risk factors":
            start=linelist.index(line)
            print line,"\n"


# In[327]:

def findRFtext(link):                     # Function to extract he required text
    text=complete_text(link)
    linelist=text.split("\n")
    start=0
    end=0
    for line in linelist:
        if line.lower().encode('ascii','ignore')=="item 1a.risk factors" or line.lower().encode('ascii','ignore')=="item 1a. risk factors" or line.lower().encode('ascii','ignore')=="item 1a.  risk factors":
            start=linelist.index(line)
    
        
                
    if start==0:
        return ""
    
    for line in linelist[start+1:]:
        if line.lower().startswith("item ") or line.lower().startswith("part "):
                end=linelist[start+1:].index(line)+start+1
                
                break
    
    text=''.join(linelist[start:end])
    text=text.encode('ascii','ignore')
    
    
    return text


# In[295]:

text=findRFtext("https://www.sec.gov/Archives/edgar/data/3982/0000950129-06-009522.txt")


# In[296]:

mytext=TextBlob(text)
word_list=list(mytext.words)
len(list(word_list))


# In[164]:

t=text.split()
for word in t:
    if word.lower()=="item" or word.lower()=="part":
        print ' '.join(t[t.index(word):10])


# In[328]:

def positive_score(text):                #Function to calculate number of positive words in the article
    poscount=0
    mytxt=TextBlob(text)
    l=mytxt.words
    for word in l:
        mywrd=TextBlob(word)
        if mywrd.polarity>0.2:
            poscount+=1
        
    return poscount


# In[329]:

def negative_score(text):                    #Function to find out number of negative words
    negcount=0
    mytxt=TextBlob(text)
    l=mytxt.words
    for word in l:
        mywrd=TextBlob(word)
        if mywrd.polarity<-0.2:
            negcount+=1
        
    return negcount


# In[330]:

def average_sentence_length(link):              #Function to find out average sentence length
    text=findRFtext(link)
    mytext=TextBlob(text)
    sentence_count=len(mytext.sentences)
    word_count=len(mytext.words)
    if sentence_count==0:
        return 0
    return (word_count*1.0)/sentence_count


# In[331]:

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


# In[332]:

def count_complex_words(link):                  #Function to count the number of complex words in the paragraph
    text=findRFtext(link)
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
         "rf word list":len(word_list)
        }
  
    return dic


# In[333]:

def count_uncertainty(link):                      #Function to calculate the uncertainty index of the article
    text=findRFtext(link)
    text=(remove_stop_words(text)).lower()
    text=TextBlob(text)
    count=0
    word_list=list(text.words)
    for word in word_list:
        if uncertainty_list.count(word)!=0:
            count+=1
    
    return count


# In[334]:

def count_constraining(link):                    #Function to calculate the number of constraining words in the article
    text=findRFtext(link)
    text=(remove_stop_words(text)).lower()
    text=TextBlob(text)
    count=0
    word_list=list(text.words)
    for word in word_list:
        if constraining_list.count(word)!=0:
            count+=1
    
    return count


# In[285]:

positive_list=[]
negative_list=[]
average_sentence_length_list=[]
complex_count_list=[]
complex_perecentage_list=[]
rf_word_list=[]
rf_constraining_list=[]
rf_uncertainty_list=[]
polarity_list=[]
subjectivity_list=[]


# In[335]:

def run(index):
    while index<cik_list["SECFNAME"].count():
        
        link=cik_list.loc[index]["SECFNAME"]
        rf_text=findRFtext(link)
        rf_text=remove_stop_words(rf_text)
        
        p_score=positive_score(rf_text)
        n_score=negative_score(rf_text)
        txt=TextBlob(rf_text)
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
        rf_word_list.append(d["rf word list"])
        
        rf_constraining_count=count_constraining(link)
        rf_uncertainty_count=count_uncertainty(link)
        rf_constraining_list.append(rf_constraining_count)
        rf_uncertainty_list.append(rf_uncertainty_count)
        
        print p_score,"-positive score"
        print n_score,"-negative score"
        print polarity,"-polarity"
        print subjectivity,"-subjectivity"
        print "Average sentence length:",sentence_length
        print "Total words in this link's rf text",d["rf word list"]
        print d["count complex words"],"-Count of complex words"
        print d["percentage complex words"],"-% of complex words"
        print rf_uncertainty_count,"-Count of uncertainty words"
        print rf_constraining_count,"-Count of constraining words"


       
        print "",index,"done \n"
        index+=1


# In[343]:

run(63)


# In[347]:

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


# In[344]:

cik_list["rf_constraining_word_proportion"]=rf_constraining_list
cik_list["rf_uncertainty_word_proportion"]=rf_uncertainty_list
cik_list["rf_word_count"]=rf_word_list
cik_list["rf_constraining_word_proportion"]=cik_list["rf_constraining_word_proportion"]/cik_list["rf_word_count"]
cik_list["rf_uncertainty_word_proportion"]=cik_list["rf_uncertainty_word_proportion"]/cik_list["rf_word_count"]
cik_list["rf_percentage_of_complex_words"]=complex_perecentage_list
cik_list["rf_count_of_complex_words"]=complex_count_list

cik_list["rf_average_sentence_length"]=average_sentence_length_list
cik_list["rf_positive_score"]=positive_list
cik_list["rf_negative_score"]=negative_list
cik_list["rf_polarity_score"]=polarity_list
cik_list["rf_fog_index"]=cik_list["rf_average_sentence_length"]+cik_list["rf_percentage_of_complex_words"]
cik_list["rf_fog_index"].apply(lambda x: x*0.4)
cik_list["rf_fog_index"]=cik_list["rf_fog_index"].apply(lambda x: x*0.4)


# In[345]:

cik_list


# In[346]:

cik_list.to_excel("cik_list_rf.xlsx")


# In[ ]:



