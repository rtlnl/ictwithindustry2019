import tqdm
import pandas as pd
from cfuzzyset import cFuzzySet as FuzzySet
import pickle
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

dutch_vocabulary = pickle.load(open("fuzzy_dict.pickle", 'rb'))


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
        return -1
    return candidate[1]

def main():
    bad_chars =  string.punctuation+"'„”‘…»—“‘‚"
    translator = str.maketrans(bad_chars, ' '*len(bad_chars))
    if len(sys.argv) > 2 and sys.argv[1] == "line":
        home_folder = sys.argv[2]
        print(home_folder)
        outfolder = "data/processed_ocr/{}/".format(home_folder.split("/")[-1])
        try:
            os.mkdir(outfolder)
        except Exception as e:
            print(e)
            pass
        for counter, f in enumerate(tqdm.tqdm(os.listdir(home_folder))):
            list_of_dicts = []
            for line_number, line in enumerate(open(os.path.join(home_folder, f))):
                line_dict = {}
                if line_number == 0:
                    header = line[:-1].split("\t")
                    continue
                l = line[:-1].split("\t")
                if len(l) != 12:
                    continue
                text = l[-1].strip()
                #empty string, low confidence, small font
                if len(text.strip()) == 0 or int(l[-2]) <10 or int(l[8])<20:
                    continue
                line_dict = {k:v for k, v in zip(header, l)}
                #remove punctuation marks
                text = text.strip().translate(translator).strip()
                #empty?
                if len(text)<1:
                    continue
                #get words from dictionary
                clean_text = " ".join([get_clean_word(x) for x in text.split() if get_clean_word(x)!=-1])
                line_dict["clean_text"] = clean_text
                list_of_dicts.append(line_dict.copy())
            if len(list_of_dicts) == 0:
                continue
            final_df = pd.DataFrame(list_of_dicts)
            final_df.to_csv(outfolder+f, sep="\t")
        return
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
