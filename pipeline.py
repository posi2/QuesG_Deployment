from collections.abc import Mapping
from textblob import TextBlob
import nltk
from textblob import Word
import warnings
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
warnings.filterwarnings('ignore')
import re
from nltk import sent_tokenize
from nltk.corpus import stopwords
from rake_nltk import Rake
import numpy as np
from gensim.models import Word2Vec
from scipy import spatial
import networkx as nx
from random import shuffle


class Pipeline():

    def text_preprocessing(self,text):
        """
            The numbers, alphanumeric, punctuation and stopwords  will be removed from the text.
        """
        #words = set(nltk.corpus.words.words())
        #text = " ".join(w for w in nltk.wordpunct_tokenize(text) if w.lower() in words or not w.isalpha())
        sentences = sent_tokenize(text) #array of sentences
        sentences_clean = [ re.sub(r'[0-9]+[a-z]*','',sentence.lower()) for sentence in sentences] # remove number and alphanumeric
        sentences_clean = [ re.sub(r'[^\w\s]','',sentence) for sentence in sentences_clean] #remove punctuattion except whitespacce, tabs and newline
        
        stop_words = stopwords.words('english')
        sentence_tokens = [[ word for word in sentence.split(" ") if word not in stop_words and word] for sentence in sentences_clean]
        #print(sentence_tokens)
        return sentence_tokens,sentences

    def Stemming(self,tokens):
        """
            Multiple stemmer Porter Stemmer (5 level suufix mapping rules) and Snowfall Stemmer
        """
        pass
    
    def pos(self, text):
        """
              This Function will do the part of the speech tagging.
        """
        doc = nlp(text)
        for token in doc:
          print(token, "->", token.pos_)
    
    def similar_words(self,word):
      """
          Find similar words of answer keywors
      """
      similar_w = self.w2v_model.most_similar(positive = word,topn=3)
      return [i[0] for i in similar_w]

    def top_sentences(self, text, sentences, num_ques=1):
        """
            Using text rank algorithm finding top sentences from the text
        """
        self.w2v=Word2Vec(text,size=1,min_count=1,iter=1000,window=2)
        sentence_embeddings=[[self.w2v[word][0] for word in words] for words in text]
        max_len=max([len(tokens) for tokens in text])
        sentence_embeddings=[np.pad(embedding,(0,max_len-len(embedding)),'constant') for embedding in sentence_embeddings]
        similarity_matrix = np.zeros([len(text), len(text)])
        for i,row_embedding in enumerate(sentence_embeddings):
          for j,column_embedding in enumerate(sentence_embeddings):
            similarity_matrix[i][j]=1-spatial.distance.cosine(row_embedding,column_embedding)
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)
        top_sentence={sentence:scores[index] for index,sentence in enumerate(sentences)}
        top=dict(sorted(top_sentence.items(), key=lambda x: x[1], reverse=True)[:num_ques])

        return top


    def keywords_extraction(self, sent_list):
        """
            Extract keywords from list of sentences using rake nltk
        """
        r = Rake()

        # Extraction given the list of strings where each string is a sentence.
        r.extract_keywords_from_text(sent_list)
        return r.get_ranked_phrases()
    
    def genQuestion(self, line):
        """
        outputs question from the given text
        """
        if type(line) is str:     
            line = TextBlob(line) 
        bucket = {}               

        for i,j in enumerate(line.tags):
            if j[1] not in bucket:
                bucket[j[1]] = i  
        
        question = ''     

        l = [['NNP', 'VBG', 'VBZ', 'IN'],['NNP', 'VBG', 'VBZ'],['PRP', 'VBG', 'VBZ', 'IN'],['PRP', 'VBG', 'VBZ'],['PRP', 'VBG', 'VBD'],['NNP', 'VBG', 'VBD'],['NN', 'VBG', 'VBZ'],['NNP', 'VBZ', 'JJ'],['NNP', 'VBZ', 'NN'],['NNP', 'VBZ'],['PRP', 'VBZ'],['NNP', 'NN', 'IN'],['NN', 'VBZ']]  
        
        if all(key in  bucket for key in l[0]): #'NNP', 'VBG', 'VBZ', 'IN' in sentence.
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ line.words[bucket['NNP']]+ ' '+ line.words[bucket['VBG']] + '?'

        
        elif all(key in  bucket for key in l[1]): #'NNP', 'VBG', 'VBZ' in sentence.
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ line.words[bucket['NNP']] +' '+ line.words[bucket['VBG']] + '?'

        elif all(key in  bucket for key in l[2]): #'PRP', 'VBG', 'VBZ', 'IN' in sentence.
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ line.words[bucket['PRP']]+ ' '+ line.words[bucket['VBG']] + '?'

        elif all(key in  bucket for key in l[3]): #'PRP', 'VBG', 'VBZ' in sentence.
            question = 'What ' + line.words[bucket['PRP']] +' '+  ' does ' + line.words[bucket['VBG']]+ ' '+  line.words[bucket['VBG']] + '?'

        elif all(key in  bucket for key in l[6]): #'NN', 'VBG', 'VBZ' in sentence.
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ line.words[bucket['NN']] +' '+ line.words[bucket['VBG']] + '?'

        elif all(key in bucket for key in l[7]): #'NNP', 'VBZ', 'JJ' in sentence.
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + line.words[bucket['NNP']] + '?'

        elif all(key in bucket for key in l[8]): #'NNP', 'VBZ', 'NN' in sentence
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + line.words[bucket['NNP']] + '?'

        elif all(key in bucket for key in l[10]): #'PRP', 'VBZ' in sentence.
            if line.words[bucket['PRP']] in ['she','he']:
                question = 'What' + ' does ' + line.words[bucket['PRP']].lower() + ' ' + line.words[bucket['VBZ']].singularize() + '?'

        elif all(key in bucket for key in l[9]): #'NNP', 'VBZ' in sentence.
            question = 'What' + ' does ' + line.words[bucket['NNP']] + ' ' + line.words[bucket['VBZ']].singularize() + '?'

        elif all(key in bucket for key in l[12]): #'NN', 'VBZ' in sentence.
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + line.words[bucket['NN']] + '?'

        if 'VBZ' in bucket and line.words[bucket['VBZ']] == "’":
            question = question.replace(" ’ ","'s ")
            
        if question != '':
            return 'Question: ' + question
        
    def prediction(self,article):
        """
        An article/ a sentence passed as an input and fill up as an ouput 
        """
        text,sentences=self.text_preprocessing(article)

        top_sentences=self.top_sentences(text,sentences)
        wh_question = self.genQuestion(list(top_sentences)[0])
        itr=1
        result = ''
        for key, value in top_sentences.items():
            main_keywords=self.keywords_extraction(key)
            #print(main_keywords)
            #genQuestion(key)
            result += " %s : %s  "%(str(itr),key.lower().replace(main_keywords[0],"______"))
            similar_options = self.w2v.most_similar(positive=main_keywords[0].split()[:2], topn = 3)
            #print(similar_options)
            similar_options=list(list(zip(*similar_options))[0])
            #print(similar_options)
            #similar_options = self.similar_words(main_keywords[0])
            similar_options.insert(3, main_keywords[0])
            shuffle(similar_options)
            #print(similar_options)
            #print(shuffle(options))
            itr+=1
            result+="\n"
        return result, wh_question


      