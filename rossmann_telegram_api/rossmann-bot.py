import os
import pandas as pd
import json
import requests
from flask import Flask, request, Response


config_file = open('variables.cfg')

config_vars = json.load(config_file)

# Inserindo Telegram toke:
token = config_file["API_TOKEN"]
tunnel_url = config_file["TUNNEL_URL"]
rossmann_api_url = config_file["ROSSMANN_API_URL"]
host = config_file["HOST_URL"]

# Informação sobre o Bot (Método Get)
# Colocar o token personalizado
#https://api.telegram.org/bot<token>/getMe

# Get updates
#https://api.telegram.org/bot<token>/getUpdates

# Send message (número do chat_id vem do update)
#https://api.telegram.org/bot<token>/sendMessage?5662646943chat_id=&text=Hi Bot

#webhook (endpoint máquina local)
#https://https://api.telegram.org/bot<token>/setWebhook?url=<tunnel_url>
#localhost.run(copiar e colar no terminal)

def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot{}/'.format( token )
    url = url + 'sendMessage?chat_id={}'.format( chat_id )

    r = requests.post( url, json={'text': text } )
    print( 'Status Code {}'.format( r.status_code ) )

    return None


def load_dataset(store_id):
    # Carregando o dataset test.csv
    df10 = pd.read_csv('test.csv' )
    df_store_raw = pd.read_csv( 'store.csv' )

    # Merge dos datasets test + store
    df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )

    # Escolha da loja para fazer a predição
    df_test = df_test[df_test['Store'] == store_id ]

    if not df_test.empty:
        df_test = df_test[df_test['Open'] != 0]       #remove os dias que a loja está fechada
        df_test = df_test[~df_test['Open'].isnull()]  #seleciona as linhas que não tem o Open vazio (sem impacto na loja 22..)
        df_test = df_test.drop( 'Id', axis=1 )        #drop id

    # Convertendo o Dataframe em json
        data = json.dumps( df_test.to_dict( orient='records' ) )

    else:
        data = 'error'

    return data

def predict (data):

    # API CALL
    #url = 'https://rossmann-store-prediction.herokuapp.com/rossmann/predict' #ulr heroku + endpoint rossman/predict
    url = f'{rossmann_api_url}/rossmann/predict'
    header = {'Content-type':'application/json'}
    data = data
 
    # enviar dados
    r = requests.post( url, data=data, headers=header )
    print( 'Status Code {}'.format( r.status_code ) )

    # converter novamente para um dataframe a partir do json retornado
    # D1 é o dataframe que possui a coluna de predição
    d1 = pd.DataFrame( r.json(), columns=r.json()[0].keys() )

    return d1

def parse_message( message ): # para receber apenas o Id da loja/separar o resultado por loja, vem de dentro do json

    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']

    store_id = store_id.replace( '/','' )

    try:
        store_id = int( store_id )

    except ValueError:
        store_id = 'error'

    return chat_id, store_id


# Inicializando a API 
app = Flask( __name__ )


@app.route('/', methods=['GET','POST'] ) #endpoint
def index(): # roda toda vez que o rout for acionado
    if request.method == 'POST':
        message = request.get_json()
        
        chat_id, store_id = parse_message( message )
        
        print(chat_id, store_id)
        
        if store_id != 'error':
            # carregando os dados
            data = load_dataset( store_id )

            print(data)

            if data != 'error':
                
                # previsões
                d1 = predict (data)

                # soma de predição por loja
                d2 = d1[['store','prediction']].groupby( 'store' ).sum().reset_index()

                # envio da mensagem
                msg = 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format(
                    d2['store'].values[0],
                    d2['prediction'].values[0] )

                send_message( chat_id, msg )
                return Response( 'Ok', status=200 )

            else:
                send_message( chat_id, 'Store Not Available!' )
                return Response( 'Ok', status=200 )
        else:
            send_message( chat_id, 'Store ID is Wrong!' )
            return Response( 'Ok', status=200 )

    else:
        return '<h1> Rossmann Telegram BOT </h1>'


if __name__ == '__main__':
    port = os.environ.get( 'PORT', 8080 )
    app.run( host=host, port=port )