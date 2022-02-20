from requests_oauthlib import OAuth1Session
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import re
from firebase import setUser, getUsers, getUser,deleteUser,setRetweeted, getRetweeted,getRetweeteds, deleteRetweeted
from stream import db, allRetweeteds, create_headers, get_rules, delete_all_rules, set_rules
from actions import follow

# Carrega a variaveis de ambiente
load_dotenv()

# Connecção com firebase.
# db = conn()


#####################USERS#######################
def authorization(consumer_key, consumer_secret):
    
    request_token_url = "https://api.twitter.com/oauth/request_token"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)

    print("Entre nesse link para autoriza a aplicação: %s" % authorization_url)
    verifier = input("Cole o PIN aqui ou digite sair para cancela a autorização: ")
    
    if not(re.match("\\d{7}", verifier)):
        print("Autorização cancelada.")
        return 0

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )

    user = oauth.fetch_access_token(access_token_url)


    username = user["screen_name"]
    
    user.pop('screen_name')

    date_now = datetime.utcnow()

    user["standby"] = date_now

    qRetweeted = input("Deve ser retuitado? digite 1 para sim: ")

    if qRetweeted == 1:
        retweeted = True
    else:
        retweeted = False

    user["retweeted"] = retweeted    
    user["retweeter"] = True
    setUser(db, user, username)

    print("Authorização concluida.")
    print(f"@{username} autorizado.")

def showUsers():
    users = getUsers(db)

    print("\nUsername".ljust(21)+"|".ljust(10)+"Retuitar".ljust(15)+"|".ljust(10)+"Deve ser retuitada  ".ljust(15)+"|".ljust(10)+"pausa de retuite")
    for username in users:
        retweeted = "Sim" if users[username]["retweeted"] else "Não"
        retweeter = "Sim" if users[username]["retweeter"] else "Não"
        standby = users[username]["standby"].strftime("%d-%m-%YT%H:%M:%S")
        print(username.ljust(20)+"|".ljust(10)+"retweeter".ljust(15)+ "|".ljust(15)+"retweeted".ljust(15)+"|".ljust(8)+standby)

    # input("\nAperte ENTER para continua.")


def selectUser():
    username = input("\nDigite o @ da conta autorizada: ") 

    user = getUser(db, username) if username != "" else {username:None}
    if user[username]:
        print("\nUsername    |  Retuitar   |   Deve ser retuitada  | pausa de retuite")
        retweeted = "Sim" if user[username]["retweeted"] else "Não"
        retweeter = "Sim" if user[username]["retweeter"] else "Não"
        standby = user[username]["standby"].strftime("%d-%m-%YT%H:%M:%S")
        print(f"{username} |   {retweeter}      |          {retweeted}          |  {standby}")

        retweeter = "Desativar" if user[username]["retweeter"] else "Ativar" 
        retweeted = "Desativar" if user[username]["retweeted"] else "Ativar" 

        print(f"\n   @{username} autorizada.")
        print("digite   |             ação")
        print(f"  1      | {retweeter} retuitar.")
        print(f"  2      | {retweeted} para ser retuitada.")
        print("  3      | Remover pausa de retuite.")
        print("  4      | Deleta conta.")
        print("  0      | INICIO.")
        cod  = input("Digite o número da ação: ")

        if cod == "1":
            user[username]["retweeter"] = False if user[username]["retweeter"] else True
            setUser(db, user[username], username)
            print(f"Conta alterada com sucesso.")

        elif cod == "2":
            user[username]["retweeted"] = False if user[username]["retweeted"] else True
            setUser(db, user[username], username)
            print(f"Conta alterada com sucesso.")

        elif cod == "3":
            user[username]["standby"] = datetime.now()
            setUser(db, user[username], username)
            print(f"Conta alterada com sucesso.")

        elif cod == "4":
            deleteUser(db, username)
            print("Conta autorizada deletad com sucesso.")
        else:
            return 0

    else:
        print(f"Conta @{username} não foi autorizado.")
        return 0
#####################RETWEETED#######################
def addRetweeted():
    username = input("\ndigite o @ ou deixe em branco para cancelar: ")
    if re.search("\\s+|@+", username) or username == "":
        print("Adiciona para ser retuitado cancelado!")
        return 0
    retweeted = {"adicionado":datetime.utcnow(), "retweeted":True}

    setRetweeted(db, retweeted,username)
    print(f"@{username} adicionado para retweet.")

def showRetweeteds():
    retweeteds = getRetweeteds(db)
    print("\n    username".ljust(21)+"|".ljust(13)+"Retuitada")
    for username in retweeteds:
        retweeted = "Sim" if retweeteds[username]["retweeted"] else "Não"
        print(username.ljust(20) +"|".ljust(16)+retweeted)

    # input("\nAperte ENTER para continua.")

def selectRetweeted():
    username = input("\nDigite o @ da conta retuitada: ") 

    doc = getRetweeted(db, username) if username != "" else {username:None}

    if doc[username]:

        print("Username     |   Retuitada ")
        retweeted = "Sim" if doc[username]["retweeted"] else "Não"

        print(f"{username} |     {retweeted}  ")

        retweeted = "Desativar" if doc[username]["retweeted"] else "Ativar" 

        print(f"\n    @{username} retuitada.")
        print("digite   |           ação")
        print(f"  1      | {retweeted} retuitado.")
        print("  2      | Deleta conta.")
        print("  0      | INICIO.")

        cod  = input("Digite o número da ação: ")
        
        if cod == "1":
            doc[username]["retweeted"] = False if doc[username]["retweeted"] else True
            setRetweeted(db, doc[username], username)
            print(f"Conta retuitada alterada com sucesso.")

        elif cod == "2":
            deleteRetweeted(db, username)
            print(f"Conta retuitada @{username} deletado com sucesso.")
        else: 
            return 0
    else:
        print(f"Conta @{username} não foi encontrada.")
        return 0

#######################Seguir########################

def AllFollow(consumer_key, consumer_secret):
    username = input("\nDigite o @ da conta a ser seguida ou deixe em branco para cancelar:\n") 
    
    if re.search("\\s+|@+", username) or username == "":
        print("Ação seguir conta cancelada.")
        return 0
    print()
    users = getUsers(db)

    follow(users, username, consumer_key, consumer_secret)




########################MAIN#########################
def main():
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    bearer_token = os.environ.get("BEARER_TOKEN")

    while True:
        print("\n          INÍCIO")
        print("digite   |             ação")
        print("  1      | Autorizar nova conta.")
        print("  2      | Ver todas as contas autorizados.")
        print("  3      | Adiciona conta para ser retuitada.")
        print("  4      | Ver todas as contas retuitadas.")
        print("  5      | Seleciona conta autorizada.")
        print("  6      | Seleciona conta retuitada.")
        print("  7      | Seguir conta.")
        print("  8      | APLICAR MODIFICAÇÕES.")
        print("  0      | SAIR")
        
        cod  = input("Digite o número da ação: ")

        if cod == "1":
            authorization(consumer_key, consumer_secret)
        elif cod == "2":
            showUsers()
        elif cod == "3":
            addRetweeted()
        elif cod == "4":
            showRetweeteds()
        elif cod == "5":
            selectUser()
        elif cod == "6":
            selectRetweeted()
        elif cod == "7":
            AllFollow(consumer_key, consumer_secret)
        elif cod == "8":
            retweeteds = allRetweeteds()
            headers = create_headers(bearer_token)
            rules = get_rules(headers, bearer_token)
            delete_all_rules(headers, bearer_token, rules)
            res = set_rules(headers, bearer_token, retweeteds)
            print("\n"+res)
            if res != 0:
                print("Modificações foram aplicadas.")
        elif cod == "0":
            break
        else:
            print("\n!Comando não encontrado!")

if __name__=="__main__":
    main()