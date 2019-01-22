import tqdm
import pandas as pd
from cfuzzyset import cFuzzySet as FuzzySet
from wordfreq import word_frequency
import os
import string
import sys


def load_dictionary():
    print("loading dutch dictionary...")
    opentaal_dict_file = "data/Dutch.dic"
    fasttext_vocab_file = "data/dutch_vocabulary.txt"
    words = FuzzySet()

    for counter, line in tqdm.tqdm(enumerate(open(opentaal_dict_file))):
        if counter == 0:
            continue
    words.add(line.split("/")[0].strip())

    for counter, line in tqdm.tqdm(enumerate(open(fasttext_vocab_file))):
        if counter ==0:
            continue
        words.add(line.strip())
    return words

dutch_vocabulary = load_dictionary()


def get_clean_word(x):

    if len(x)<1:
        return None
    if ' ' in x:
        candidate = dutch_vocabulary.get(x)[0]
        words_score = []
        _words = x.split()
        for w in _words:
            words_score.append(dutch_vocabulary.get(w)[0])
        probability_sum = sum([x[0]*word_frequency(x[1], "nl") for x in words_score])/len(words_score)
        full_word_probability = word_frequency(candidate[1], "nl") * candidate[0]
        if probability_sum > full_word_probability:
            return " ".join([x[1] for x in words_score])
        else:
            return candidate[1]
    candidate = dutch_vocabulary.get(x)[0]
    if candidate[0]< 0.6:
        return None
    return candidate[1]

def main():
    bad_chars =  string.punctuation+"'„”‘…»—“‘‚"
    translator = str.maketrans(bad_chars, ' '*len(bad_chars))
    home_folder = sys.argv[1]
    print(home_folder)
    outfolder = "data/processed_ocr/{}/".format(home_folder.split("/")[-1])
    try:
        os.mkdir(outfolder)
    except Exception as e:
        print(e)
        pass
    for counter, f in enumerate(tqdm.tqdm(os.listdir(home_folder))):
        df = pd.read_csv(os.path.join(home_folder, f), sep="\t", doublequote=False, quotechar="'")
        df = df[(-df.text.isna()) & (df.conf>10) & (df.height>20)]
        df.text = df.text.apply(lambda x: x.translate(translator).strip())
        df['actual_word'] = df.text.apply(get_clean_word)
        df = df[-df.actual_word.isna()]
        df.to_csv(outfolder+f, sep="\t")


if __name__=="__main__":
    main()
