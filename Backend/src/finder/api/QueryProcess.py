import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import gensim
from nltk.tokenize import word_tokenize
import regex as re


def NLP_processor(documents, type):

    """
    function to make new corpus for a certain set of documents
    :param documents: list of lists of strings
    :param type: type of repository
    :return: Corpus of the documents, list of lists of pairs (token_id, token_frequency)
    """

    if type == 'BSF':
        dir = 'C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_BSF'

    if type == 'ISF':
        dir = 'C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_ISF'

    if type == 'MST':
        dir = 'C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_MST'

    if type == 'INNOVATION':
        dir = 'C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_INNOVATION'

    if type == 'Technion':
        dir = 'C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_Technion'

    if type == 'EU':
        dir = 'C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_Eu'


    tokens = [process_document(doc) for doc in documents ]

    try:

        dictionary = reload_dictionary(dir)
        # print("reloading")
    except:
        dictionary = make_dictionary([])
        # print("Making dictionary")
        dictionary.save(dir)

    dictionary.add_documents(tokens)
    dictionary.save(dir)
    # for k, v in dictionary.token2id.items():
    #     print(k, v)
    # print(dictionary.token2id)
    return build_corpus(dictionary, tokens)


def process_document(document):

    """
    function to process a certain document by 1- tokenizing it 2- remove stop words 3- making lower cas of tokens
    4- stemming each token
    :param document: string
    :return: list of tokens
    """

    ps = PorterStemmer()
    # nltk.download('stopwords')  # for the first run only
    # nltk.download('punkt')   # for the first run only

    try:
        stop_words = (stopwords.words('english'))

    except Exception as e:
        print("ERR", e)

    try:

        tokens_list = [ps.stem(word.lower()) for word in word_tokenize(document) if
                not word in stop_words]  # tokenizing and normalize tokens

        # remove punctuation characters from the token list
        for token in tokens_list:
            if len(token) <= 1:
                tokens_list.remove(token)

    except Exception as e:
        print("ERR", e)

    return tokens_list


def make_dictionary(tokens):

    """
    function to build new dictionary with a certain tokens
    :param tokens: list of lists of tokens
    :return: Dictionary object
    """

    dictionary = gensim.corpora.Dictionary(tokens)
    # print("This is the dictionary",dictionary.token2id)
    return dictionary  # mapping termId : term


def build_corpus(dictionary, tokens):

    """
    function to build a corpus, which is mapping each token id to its frequency
    :param dictionary: inner dictionary object for mapping token -> token id
    :param tokens: list of lists of tokens
    :return: list of lists of tuples (id, frequency)
    """

    # for each doc map termId : term frequency
    corpus = [dictionary.doc2bow(lst) for lst in tokens]
    #print("Corpus: ", res)
    return corpus


def process_query_result(result):

    """
    function to process similarity result, it will map each document similarity percentage with the document id
    :param result: list of lists of percentages
    :return: pair of (doc id, doc similarity percentage)
    """

    if len(result) == 0:
        return []
    result = result[0]
    pairs = []
    for idx, sim_perc in enumerate(result):

        if sim_perc != 0:
            pairs.append((idx, sim_perc))
    return pairs


def add_document_to_curr_index(index, documents,org_type):

    """
    function to add new documents to existent index
    :param index: current index
    :param documents: list of lists of strings
    :param org_type: string to know which repository
    :return: updated index
    """

    corpus = NLP_processor(documents,org_type)
    index.num_features += len(corpus) * 1000
    for doc in corpus:
        index.num_features += (len(doc) * 2)
    index.add_documents(corpus)
    index.save()
    return index


def reload_index(path):

    """
    function to load index from a specific directory on disk
    :param path: path to directory
    :return: Similarity Object
    """

    return gensim.similarities.Similarity.load(path)


def reload_dictionary(path):

    """
    function to load dictionary from a specific directory on disk
    :param path: path to directory
    :return: Dictionary object
    """

    return gensim.corpora.Dictionary.load(path)


def make_index(path, type):

    """
    build an empty index in disk and save it on a specific directory
    :param path: path of the directory
    :param type: string to know what index b2match or eu
    :return: Similarity object "index"
    """

    corpus = NLP_processor([], type)
    tfidf = gensim.models.TfidfModel(corpus)

    return gensim.similarities.Similarity(path, tfidf[corpus], num_features=10000)


def get_document_from_bsf_call(info, area):

    """
    function to get the description and tags from bsf call
    :param info: call information
    :param area: tags
    :return: document
    """

    doc = info + " " + area

    return doc


def get_document_from_isf_call(info, orgName):

    """
    function to get the description and tags from isf call
    :param orgName:
    :param info: call information
    :return: document
    """

    doc = orgName + " " + info

    return doc


def get_document_from_innovation_call(orgName, info, area):

    """
    function to get the description and tags from innovation call
    :param orgName: Organization name
    :param info: call information
    :param area: tags
    :return: document
    """

    doc = orgName + " " + info + " " + area

    return doc


def get_document_from_mst_call(topic, info):

    """
    function to get the description and tags from innovation call
    :param info: call information
    :param topic: call topic
    :return: document
    """

    doc = topic + " " + info

    return doc


def get_document_from_technion_call(topic, field, info):

    """
    function to get the description and tags from Technion call
    :param topic: call title
    :param field: call field
    :param info: call information
    :return: document
    """
    doc = topic + " " + field + " " + info

    return doc

def get_document_from_eu_call(orgName, title, tags):

    """
    function to get the description and tags from EU call
    :param orgName: organization name
    :param title: call title
    :param tags: call tags
    :return: document
    """
    orgName = re.sub(r'[^A-Za-z0-9]+', ' ', orgName)
    doc = orgName + " " + tags + " " + title
    return doc