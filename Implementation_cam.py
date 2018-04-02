# -*- coding: utf-8 -*-
import os

def board(card_txt):
    card = open(card_txt, 'r')  
    fh = card.readlines()
##('size:', '39 40', 'portals:', '20 3', '20 38', 'asteroids:', '10 14 12 1', '5 21 12 2') 
    card.close()  
    
    ## Creation de la structure de données du plateau 
    board = []
    size = fh[1].split(' ')
    lines = int(size[0])
    columns = int(size[1])
    
    for e in range(lines):
        board += []
        for i in range(columns): 
            board += []
    ## Ajout des portails 
    gate_A = {}
    gate_B = {}     
    for i in range(3, 5):
        portals = fh[i].split(' ') 
        lines = int(portals[0])
        columns = int(portals[1])
        board [lines:columns] += 'p'
        if i == 3: 
            gate_A['Position'] = (lines, columns)  
            gate_A['Ore'] = 4
            gate_A['Life'] = 100
        if i == 4:
            gate_B['Position'] = (lines, columns)  
            gate_B['Ore'] = 4
            gate_B['Life'] = 100
        
    ## Ajout des astéroides 
    lengh = len(fh)
    asteroides = {}
    for i in range(6, lengh):
        asteroids = fh[i].split(' ') 
        lines = int(asteroids[0])
        columns = int(asteroids[1])
        board [lines:columns] += '*'
        ore = int(asteroids[2])
        possibility= int(asteroids[3])
        asteroides[(lines, columns)] = {'Ore': ore, 'Possiblility': possibility} 
    
    return board
    

print(board('game.txt'))
