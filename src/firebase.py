from os import path

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import config

###############################################
#                Connection                   #
###############################################


def conn():
    # dir_path = path.dirname(path.realpath(__file__))

    # cred = credentials.Certificate(dir_path + '/cred/certificate.json')
    firebase_admin.initialize_app()

    return firestore.client()


###############################################
#                   Users                     #
###############################################


def setUser(db, user, username):
    doc_ref = db.collection('users').document(username)

    doc_ref.set(user)


def getUsers(db, w=None):

    users = {}
    ref = db.collection('users')
    if w == 1:
        docs = ref.where("retweeter", "==", True).get()
    elif w == 2:
        docs = ref.where("retweeted", "==", True).get()
    else:
        docs = ref.get()
    for doc in docs:
        users[doc.id] = doc.to_dict()
    return users


def getUser(db, username):
    user = {}
    ref = db.collection('users').document(username)
    doc = ref.get()
    user[doc.id] = doc.to_dict()

    return user


def deleteUser(db, username):
    db.collection("users").document(username).delete()


###############################################
#                 Retweeteds                  #
###############################################
def setRetweeted(db, retweeted, username):
    doc_ref = db.collection('retweeteds').document(username)

    doc_ref.set(retweeted)


def getRetweeteds(db, w=None):
    retweeteds = {}
    ref = db.collection('retweeteds')
    if w == 1:
        docs = ref.where("retweeted", "==", True).get()
    else:
        docs = ref.get()
    for doc in docs:
        retweeteds[doc.id] = doc.to_dict()
    return retweeteds


def getRetweeted(db, username):
    retweeted = {}
    ref = db.collection('retweeteds').document(username)
    doc = ref.get()
    retweeted[doc.id] = doc.to_dict()

    return retweeted


def deleteRetweeted(db, username):
    db.collection("retweeteds").document(username).delete()


###############################################
#                 Retweets                    #
###############################################


def setRetweet(db, retweet, id):
    doc_ref = db.collection('retweets').document(id)

    doc_ref.set(retweet)

    # print("Retweet para se remov adicionado.")


def getRetweets(db):
    retweets = {}
    ref = db.collection('retweets')
    docs = ref.get()
    for doc in docs:
        retweets[doc.id] = doc.to_dict()
    return retweets


def deleteRetweet(db, id):
    db.collection("retweets").document(id).delete()

    # print("Retweeted deletado com sucesso.")


if __name__ == "__main__":
    db = conn()
    # setUser(db, None)
    # setRetweet(db, "1384687631590739973")
    #users = getUsers(db)
    # deleteRetweet(db,"1384687631590739973")
    retweeteds = getRetweeteds(db)
    #retweets = getRetweets(db)
    # deleteRetweeted(db, "Marcos_10111")
    #  print(json.dumps(retweets, sort_keys=True, indent=4))
    # print(retweets)
    #print(getUser(db, "conta23test"))
    print(retweeteds)
