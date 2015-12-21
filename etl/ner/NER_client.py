"""

This is a module for communicating with a Stanford NERServer process.
You can use this module to find out if the owner of a property is a person or an organization
This module only runs under python3

Usage:
1. Download the Stanford Name Entity Recognition library from http://nlp.stanford.edu/software/CRF-NER.shtml
2. java -mx6000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -port 9191 -loadClassifier \
   classifiers/english.all.3class.distsim.crf.ser.gz -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer \
   -tokenizerOptions "tokenizeNLs=true" -outputFormat tsv  &
3. Call the perform_NER function with the name of the owner.
"""

import socket
from contextlib import contextmanager


def query_server(sock, phrase):
    phrase = phrase.strip()
    sock.send(bytes(phrase+"\n", "UTF-8"))

    answer = []
    while 1:
        data = sock.recv(1024)
        if not data:
            break
        answer.append(data.decode("utf-8"))
    answer = "".join(answer)
    return answer


def unify_entity(entities):
    """
    NER tags each word of the owner name with an entity. Sometimes there is a mismatch between entities within
    the same owner name. This function fixes some of these mismatches.
    :param entities: A list of entity strings
    :return: One entity string
    """
    # some parts of the name might be tagged with 'O' - no entity
    # we want there to be at least two non-O parts of the entity
    entities = [e for e in entities if e != 'O']
    if len(entities) < 2:
        return None

    # each part of the name is tagged as entity individually
    # if all those are the same -> have a match
    if len(set(entities)) == 1:
        return entities[0]
    # at least one is different -> be conservative and avoid making a decision
    else:
        return None

@contextmanager
def manage_socket():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 9191))
        yield client_socket
    finally:
        client_socket.close()


def perform_NER(owner):
    """
    Perform Name Entity Recognition for the given owner name
    :param owner: String containing the owner name
    :return: One of ORGANIZATION, PERSON, CINCINNATI, OHIO
    """
    with manage_socket() as sock:

        # there are a bunch of government-owned properties that do Stanford NER has trouble with
        if owner == "Cincinnati City Of":
            return "CINCINNATI"
        if owner in ["State Of Ohio The", "State Of Ohio"]:
            return "OHIO"

        answer = query_server(sock, owner)
        answer = answer.split("\n")
        answer = [a.split("\t") for a in answer if len(a) > 0]
        if (len(answer)) == 0:
            return None

        words, entities = zip(*answer)
        entity = unify_entity(entities)

        if entity not in ["ORGANIZATION", "PERSON"]:
            return None
        return entity


