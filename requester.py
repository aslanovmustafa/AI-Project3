import requests
import http.client
import ast

userId = "1065"
api_key = "0a9d191bd9285e868611"
teamId = "1264" #Gaintelligence
board_size = '12'
target = '6'

def create_game(opponent_team: int): #returns game ID
    payload = (
        "teamId1="
        + teamId
        + "&teamId2="
        + str(opponent_team)
        + "&type=game&gameType=TTT"
        + "&boardSize="
        + board_size
        + "&target="
        + target
    )
    headers = {
        'x-api-key': api_key,
        'userId': userId,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    conn = http.client.HTTPSConnection('www.notexponential.com')

    conn.request("POST", '/aip2pgaming/api/index.php', payload, headers)
    response = conn.getresponse()
    reply = response.read()

    return ast.literal_eval(reply.decode('utf-8'))["gameId"]

def get_board_map(gameId: int): #prints board map
    url = (
        "/aip2pgaming/api/index.php?type=boardMap&gameId="
        + str(gameId)
    )
    payload = {}
    headers = {
        "x-api-key": api_key, 
        "userId": userId
    }

    conn = http.client.HTTPSConnection('www.notexponential.com')
    conn.request("GET", url, payload, headers)
    response = conn.getresponse()
    reply = response.read()
    reply = reply.decode('utf-8')
    try:
      reply.index('null')
    except Exception as e:
      return ast.literal_eval(reply) 
    else:
      return None

def get_moves(gameId: int, count: int = 1): #Get list of recent moves based on count number
    
    url = (
        "/aip2pgaming/api/index.php?type=moves&gameId="
        + str(gameId)
        + "&count="
        + str(count)
    )
    payload = {}
    headers = {
        "x-api-key": api_key,
        "userId": userId,
    }

    conn = http.client.HTTPSConnection('www.notexponential.com')
    conn.request("GET", url, payload, headers)
    response = conn.getresponse()
    reply = response.read()
    # print(reply)
    # print(ast.literal_eval(reply.decode('utf-8')))
    return ast.literal_eval(reply.decode('utf-8'))

def make_a_move(gameId: int, move: tuple): #makes a move
    x, y = move
    payload = (
        "teamId="
        + teamId
        + "&move="
        + str(x)
        + "%2C"
        + str(y)
        + "%20&type=move&gameId="
        + str(gameId)
    )

    headers = {
        "x-api-key": api_key,
        "userId": userId,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    conn = http.client.HTTPSConnection('www.notexponential.com')
    conn.request("POST", '/aip2pgaming/api/index.php', payload, headers)
    response = conn.getresponse()
    reply = response.read()
    print(ast.literal_eval(reply.decode('utf-8')))
