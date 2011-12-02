#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    sendpkm.py is a module to send Pokémon at the fake GTS of Pokémon games.
    Tested only on ir-gts-bw 0.05 <http://code.google.com/p/ir-gts/>
    Copyright (C) 2011  Giovanni 'Roxas Shadow' Capuano

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from pokehaxlib import *
from pkmlib import encode
from boxtoparty import makeparty
from sys import argv, exit
from platform import system
from base64 import urlsafe_b64encode
import gtsvar, hashlib, os, random

def sendpkm():
    print 'Enter (or simply drag&drop) the path of the directory which contains the Pokémon:'
    path = raw_input().strip()
    if path.startswith('\'') or path.endswith('\''):
    	path = path.replace('\'', '')
    path = os.path.normpath(path)
    if system() != 'Windows':
        path = path.replace('\\', '')
    	if not path.endswith('/'):
    		path = path+'/'
    else:
    	if not path.endswith('\\'):
    		path = path+'\\'
    while True:
        dirs = [] # Just you add/remove a file from your Pokémon directory, isn't a good thing killing the software :(
        for i in os.listdir(path):
            if i.lower().endswith('.pkm'):
                dirs.append(i)
        fileName = dirs[random.randint(0, len(dirs)-1)]
        pokeyman = path + fileName
        
        # Shifting
	f = open(pokeyman, 'r')
	pkm = f.read()
	f.close()
	pkm = decode(pkm)
	if len(pkm) != 136:
	    pkm = pkm[0:136] #-- only take the top 136 bytes
	    new_pkm_file_name = self.path.GetValue()+self.filename.GetValue()+str(i)+'.pkm'
	    new_pkm_fh = open (new_pkm_file_name, 'w' )
	    new_pkm_fh.write(pkm)
	    new_pkm_fh.close()
        
        f = open(pokeyman, 'r')
        pkm = f.read()
        f.close()

        # Adding extra 100 bytes of party data
        if len(pkm) != 220 and len(pkm) != 136:
            print 'Invalid filesize: %d bytes.' % len(pkm)
            return
        if len(pkm) == 136:
            print 'PC-Boxed Pokemon! Adding party data...',
            pkm = makeparty(pkm)
            print 'done.'
            print 'Encoding!'
            bin = encode(pkm)
        else:
            print 'Filename must end in .pkm'
            return

        # Adding GTS data to end of file
        bin += '\x00' * 16
        bin += pkm[0x08:0x0a] # id
        if ord(pkm[0x40]) & 0x04: bin += '\x03' # Gender
        else: bin += chr((ord(pkm[0x40]) & 2) + 1)
        bin += pkm[0x8c] # Level
        bin += '\x01\x00\x03\x00\x00\x00\x00\x00' # Requesting bulba, either, any
        bin += '\xdb\x07\x03\x0a\x00\x00\x00\x00' # Date deposited (10 Mar 2011)
        bin += '\xdb\x07\x03\x16\x01\x30\x00\x00' # Date traded (?)
        bin += pkm[0x00:0x04] # PID
        bin += pkm[0x0c:0x0e] # OT ID
        bin += pkm[0x0e:0x10] # OT Secret ID
        bin += pkm[0x68:0x78] # OT Name
        bin += '\xDB\x02' # Country, City
        bin += '\x46\x01\x15\x02' # Sprite, Exchanged (?), Version, Lang
        bin += '\x01\x00' # Unknown

        sent = False
        response = ''
        print 'Ready to send; you can now enter the GTS...'
        while not sent:
            sock, req = getReq()
            a = req.action
            if len(req.getvars) == 1:
                sendResp(sock, gtsvar.token)
                continue
            elif a == 'info':
                response = '\x01\x00'
                print 'Connection Established.'
            elif a == 'setProfile': response = '\x00' * 8
            elif a == 'post': response = '\x0c\x00'
            elif a == 'search': response = '\x01\x00'
            elif a == 'result': response = bin
            elif a == 'delete':
                response = '\x01\x00'
                sent = True

            m = hashlib.sha1()
            m.update(gtsvar.salt + urlsafe_b64encode(response) + gtsvar.salt)
            response += m.hexdigest()
            sendResp(sock, response)

        print fileName+' sent successfully.'
