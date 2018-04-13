
# coding: utf-8

# In[3]:

import pandas as pd
import re
import urllib2
from textblob import TextBlob
pd.options.display.max_colwidth = 100
import urllib
from bs4 import BeautifulSoup


# In[4]:

cik_list=pd.read_excel("cik_list.xlsx")
uncertainty_list=list(pd.read_excel("uncertainty_dictionary.xlsx")["Word"])
uncertainty_list=(str(" ".join(uncertainty_list).lower())).split()
constraining_list=list(pd.read_excel("constraining_dictionary.xlsx")["Word"])
constraining_list=(str(" ".join(constraining_list).lower())).split()


# In[5]:

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


# In[21]:

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


# In[8]:

def CheckLines(line1, line2):    # Function to heck for the heading of required article of "Management and discussion analysis"
    line1=line1.lower()
    line2=line2.lower()
    wordlist=line1.split()
    wordlist=wordlist+line2.split()
    count=wordlist.count("management's")+wordlist.count("discussion")+wordlist.count("analysis")+wordlist.count("and")
        
    ispresent= wordlist.count("management's")!=0 and wordlist.count("discussion")!=0 and wordlist.count("analysis")!=0
   
    return count>=4 and ispresent 


# In[13]:

def find_mda_text(link):                        # Function to extract the required mda section from the complete text
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


# In[26]:

def positive_score(text):                #Function to calculate number of positive words in the article
    poscount=0
    mytxt=TextBlob(text)
    l=mytxt.words
    for word in l:
        mywrd=TextBlob(word)
        if mywrd.polarity>0.2:
            poscount+=1
        
    return poscount


# In[27]:

def negative_score(text):                    #Function to find out number of negative words
    negcount=0
    mytxt=TextBlob(text)
    l=mytxt.words
    for word in l:
        mywrd=TextBlob(word)
        if mywrd.polarity<-0.2:
            negcount+=1
        
    return negcount


# In[28]:

def average_sentence_length(link):              #Function to find out average sentence length
    text=find_mda_text(link)
    mytext=TextBlob(text)
    sentence_count=len(mytext.sentences)
    word_count=len(mytext.words)
    if sentence_count==0:
        return 0
    return (word_count*1.0)/sentence_count


# In[29]:

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


# In[30]:

def count_complex_words(link):                  #Function to count the number of complex words in the paragraph
    text=find_mda_text(link)
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
         "mda word list":len(word_list)
        }
    return dic


# In[31]:

def count_uncertainty(link):                      #Function to calculate the uncertainty index of the article
    text=find_mda_text(link)
    text=(remove_stop_words(text)).lower()
    text=TextBlob(text)
    count=0
    word_list=list(text.words)
    for word in word_list:
        if uncertainty_list.count(word)!=0:
            count+=1
    
    return count


# In[32]:

def count_constraining(link):                    #Function to calculate the number of constraining words in the article
    text=find_mda_text(link)
    text=(remove_stop_words(text)).lower()
    text=TextBlob(text)
    count=0
    word_list=list(text.words)
    for word in word_list:
        if constraining_list.count(word)!=0:
            count+=1
    
    return count


# In[57]:

positive_list=[]
negative_list=[]
average_sentence_length_list=[]
complex_count_list=[]
complex_perecentage_list=[]
mda_word_list=[]
mda_constraining_list=[]
mda_uncertainty_list=[]
polarity_list=[]
subjectivity_list=[]


# In[115]:

def run(index):
    while index<cik_list["SECFNAME"].count():
        
        link=cik_list.loc[index]["SECFNAME"]
        mda_text=find_mda_text(link)
        mda_text=remove_stop_words(mda_text)
        
        p_score=positive_score(mda_text)
        n_score=negative_score(mda_text)
        txt=TextBlob(mda_text)
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
        mda_word_list.append(d["mda word list"])
        
        mda_constraining_count=count_constraining(link)
        mda_uncertainty_count=count_uncertainty(link)
        mda_constraining_list.append(mda_constraining_count)
        mda_uncertainty_list.append(mda_uncertainty_count)
        
        print p_score
        print n_score
        print polarity
        print subjectivity
        print "Average sentence length:",sentence_length
        print "Total words in this link's mda text",d["mda word list"]
        print d["count complex words"],"-Count of complex words"
        print d["percentage complex words"],"-% of complex words"
        print mda_uncertainty_count,"-Count of uncertainty words"
        print mda_constraining_count,"-Count of constraining words"


       
        print "",index,"done"
        index+=1


# In[140]:

run(149)


# In[11]:

superlist=[]                                          #Code to handle connection problem
superlist.append(positive_list)
superlist.append(negative_list)
superlist.append(average_sentence_length_list)
superlist.append(complex_count_list)
superlist.append(complex_perecentage_list)
superlist.append(mda_word_list)
superlist.append(mda_constraining_list)
superlist.append(polarity_list)
superlist.append(subjectivity_list)

def remove_extra(superlist, x):
    i=0
    while i < len(superlist):
        print len(superlist[i])
        if len(superlist[i])>x+1:
            print "lengh before change",len(superlist[i]),"/n"
            superlist[i]=superlist[i][:(x+1)]
            print "lengh after change",len(superlist[i]),"/n"

        i+=1
        
remove_extra(superlist,151)
        
for l in superlist:
    print "Changed length",len(l)
    
positive_list=superlist[0]
negative_list=superlist[1]
average_sentence_length_list=superlist[2]
complex_count_list=superlist[3]
complex_perecentage_list=superlist[4]
mda_word_list=superlist[5]
mda_constraining_list=superlist[6]

polarity_list=superlist[7]
subjectivity_list=superlist[8]


# In[146]:

len(positive_list)


# In[166]:

cik_list["mda_constraining_word_proportion"]=mda_constraining_list
cik_list["mda_uncertainty_word_proportion"]=mda_uncertainty_list
cik_list["mda_word_count"]=mda_word_list
cik_list["mda_constraining_word_proportion"]=cik_list["mda_constraining_word_proportion"]/cik_list["mda_word_count"]
cik_list["mda_uncertainty_word_proportion"]=cik_list["mda_uncertainty_word_proportion"]/cik_list["mda_word_count"]
cik_list["mda_percentage_of_complex_words"]=complex_perecentage_list
cik_list["mda_count_of_complex_words"]=complex_count_list

cik_list["mda_average_sentence_length"]=average_sentence_length_list
cik_list["mda_positive_score"]=positive_list
cik_list["mda_negative_score"]=negative_list
cik_list["mda_polarity_score"]=polarity_list
cik_list["mda_fog_index"]=cik_list["mda_average_sentence_length"]+cik_list["mda_percentage_of_complex_words"]
cik_list["mda_fog_index"].apply(lambda x: x*0.4)
cik_list["mda_fog_index"]=cik_list["mda_fog_index"].apply(lambda x: x*0.4)


# In[6]:

cik_list.loc[0]


# In[14]:

text=find_mda_text(" https://www.sec.gov/Archives/edgar/data/3662/0000950170-98-000413.txt")


# In[15]:

text


# In[167]:

cik_list


# In[169]:

cik_list.to_excel("cik_list_mda.xlsx")


# In[ ]:



