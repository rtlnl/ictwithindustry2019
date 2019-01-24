import os
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity



CSV_FILES = ['COCO', 'Objects',
             'Scene attributes', 'Scene categories',
             'Actions']

JSON_ARG = ['coco', 'imagenet', 'places_attributes', 'places', 'kinetics']


def similarity(a, b):
    return cosine_similarity(a, b)


def get_eng2dutch(root):
    translation = {}
    for csv, arg in zip(CSV_FILES, JSON_ARG):
        translation[arg] = {}
        tmp = 'Embeddings - ' + csv + '.csv'
        df = pd.read_csv(os.path.join(tmp))
        for i in range(len(df)):
            if csv == 'Scene categories':
                tmp = df['Original'][i].split('/')
                if len(tmp) == 2:
                    src = tmp[-1]
                else:
                    src = '_'.join(tmp[-2:])
            else:
                src = df['Original'][i]
            target = df['Embedding'][i]
            translation[arg][src] = target
    return translation


class Embedding(object):
    def __init__(self, word_emb_path, translation):
        self.model = KeyedVectors.load_word2vec_format(
            word_emb_path,
            binary=False)
        self.translation = translation

    def word_vec(self, mode, key):
        dutch = self.translation[mode][key]

        keys = dutch.lower().split()
        if len(keys) == 1:
            return self.model.word_vec(keys[0])
        else:
            tmp = []
            for i in range(len(keys)):
                tmp.append(self.model.word_vec(keys[i].strip(',')))
            return np.mean(tmp, axis=0)

    def query_expansion(self, query, topk=5):
        result = self.model.similar_by_vector(query, topn=topk)
        tmp = []
        for r in result:
            tmp.append(self.model.word_vec(r[0]))
        return np.mean(tmp, axis=0)

    def query_vec(self, query):
        keys = query.lower().split()
        if len(keys) == 1:
            return self.model.word_vec(keys[0])
        else:
            tmp = []
            for i in range(len(keys)):
                tmp.append(self.model.word_vec(keys[i].strip(',')))
            return np.mean(tmp, axis=0)

def matching_score(query, preds, probs, topk=5):
    '''matching score between a query and a video
    query: embedding of the query
    preds: embedding of classes (matrix)
    probs: confidence of the class predictions (vector)
    topk: top k classes to select
    '''
    idx = np.argsort(probs)

    tmp = 0
    for i in idx[:topk]:
        tmp += similarity(query, preds[i, :]) * probs[i]

    return tmp


if __name__ == "__main__":
    translation = get_eng2dutch(root='Translations')
    emb = Embedding('fastText/cc.nl.300.vec', translation)
    tmp = emb.word_vec('imagenet', 'n01484850')
