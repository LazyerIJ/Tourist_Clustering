import re
import os
import gensim

from stopwords import stopwords
from pandas import read_csv

import warnings
warnings.filterwarnings('ignore')

def clean_str(string):
    string = re.sub(r"\'s", "", string)
    string = re.sub(r"\'ve", "", string)
    string = re.sub(r"n\'t", "", string)
    string = re.sub(r"\'re", "", string)
    string = re.sub(r"\'d", "", string)
    string = re.sub(r"\'ll", "", string)
    string = re.sub(r",", "", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", "", string)
    string = re.sub(r"\)", "", string)
    string = re.sub(r"\?", "", string)
    string = re.sub(r"'", "", string)
    string = re.sub(r"[^A-Za-z0-9()]", " ", string)
    string = re.sub(r"[0-9]\w+|[0-9]", "", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def removeStopwords(wordlist, stopwords):
    return [w for w in wordlist if w not in stopwords]


def wordListToFreqDict(wordlist):
    wordfreq = [wordlist.count(p) for p in wordlist]
    return dict(zip(wordlist, wordfreq))


def sortFreqDict(freqdict):
    aux = [(freqdict[key], key) for key in freqdict]
    aux.sort()
    aux.reverse()
    return aux


def getScore(score):
    return score*score


def getTotalScore(dist, num):
    return dist/num


def getDataWordList(data, column='Comment'):
    data = [clean_str(comment) for comment in data[column].values]
    data = [x.split() for x in data]
    data = [clean_str(word) for comment in data for word in comment]
    data = removeStopwords(data, stopwords)
    data = wordListToFreqDict(data)
    data = sortFreqDict(data)
    return data


def getWord2vecModel(path):
    return gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)


def print_count_similarity(keyword,count_word,model,threshold=0.3):
        for word in count_word:
            try:
                score = model.similarity(keyword,word[1])
                score = getScore(score)
                if(score>threshold):
                    print('{}({}) : {}'.format(word[1],word[0],score))
            except:
                pass


def calculate_dist_num(keyword, count_word, model, threshold=0.3):
    dist = 0.0
    num = 0
    for word in count_word:
        try:
            score = model.similarity(keyword, word[1])
            score = getScore(score)
            if(score > threshold):
                dist += score * word[0]
                num += word[0]
        except:
            pass
    return dist, num


if __name__ == '__main__':

    model_path = '../utils/GoogleNews-vectors-negative300.bin'
    data_dir = '../data/'

    # data list
    data_list = os.listdir(data_dir)
    # test_word
    # keywords=["food","photo","view","fear","sunset","history","love"]

    # get model
    print('[*]Get word2vec model..')
    model = getWord2vecModel(model_path)

    # print result num
    result_num = 5

    # add score over than threshold similarity
    threshold = 0.1

    print('[*]Tourlist')
    for tour in data_list:
        print(tour[:-4])
    print()

    while True:
        keyword = input('[*]Input Keyword("exit" to finish)>>')
        if keyword == 'exit':
            break

        dist_dict = {}

        for data_name in data_list:

            data_csv = read_csv(data_dir+data_name)

            count_word = getDataWordList(data_csv)
            '''
            print()
            print('[*]data_name : {}'.format(data_name[:-4]))
            print_count_similarity(keyword=keyword,
                                   count_word=count_word,
                                   model=model,
                                   threshold=threshold)
            print()
            '''
            dist, num = calculate_dist_num(keyword=keyword,
                                           count_word=count_word,
                                           model=model,
                                           threshold=threshold)
            # dist_dict.update({data_name:dist/len(data_csv)})
            total_score = getTotalScore(dist, len(data_csv))
            dist_dict.update({data_name: total_score})

        print('[*]Keyword >> {}'.format(keyword))
        dist_dict = sortFreqDict(dist_dict)
        for idx, city in enumerate(dist_dict[:result_num]):
            # print('{}. {}({})'.format(idx+1,city[1][:-4],city[0]))
            print('{}. {}'.format(idx+1, city[1][:-4]))
        print()
