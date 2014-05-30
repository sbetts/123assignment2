from network import Listener, Handler, poll


handlers = {} # map client handler to user name
names = {} # map name to handler
subs = {} # map tag to handlers

def broadcast(msg):
    for h in handlers.keys():
        h.do_send(msg)


class MyHandler(Handler):
    
    def on_open(self):
        handlers[self] = None
        
    def on_close(self):
        name = handlers[self]
        del handlers[self]
        broadcast({'leave': name, 'users': handlers.values()})
        
    def on_msg(self, msg):
        if 'join' in msg:
            name = msg['join']
            handlers[self] = name
            broadcast({'join': name, 'users': handlers.values()})
        elif 'speak' in msg:
            name, txt = msg['speak'], msg['txt']
            itercount = 0
            plusindex = 0
            plusset = False
            plusstring = ""
            minusindex = 0
            minusset = False
            minusstring = ""
            atindex = 0
            atset = False
            atstring = ""
            finalmessage = ""
            hashindex = 0
            hashset = False
            hashstring = ""
            setofhashes = set()
            setofrecipients = set()
            for x in txt:
                if x == "+":
                    plusindex = itercount
                    plusset = True
                    itercount += 1
                elif x == "#":
                    finalmessage += txt[itercount]
                    hashindex = itercount
                    hashset = True
                    itercount += 1
                elif x == "-":
                    minusindex = itercount
                    minusset = True
                    itercount += 1
                elif x == "@":
                    finalmessage += txt[itercount]
                    atindex = itercount
                    atset = True
                    itercount += 1
                else:
                    if plusset == True:
                        if x == " ":
                            finalmessage += txt[itercount]
                            ##Subscribe using plusstring
                            if plusstring in subs:
                                subs[plusstring].add(name)
                            else:
                                subs[plusstring] = set()
                                subs[plusstring].add(name)
                            ##print(plusstring)
                            plusset = False
                            plusindex = 0
                            itercount += 1
                            plusstring = ""
                        else:
                            plusstring += txt[itercount]
                            itercount += 1
                    elif hashset == True:
                        if x == " ":
                            finalmessage += txt[itercount]
                            setofhashes.add(hashstring)
                            hashset = False
                            hashindex = 0
                            itercount += 1
                            hashstring = ""
                        else:
                            finalmessage += txt[itercount]
                            hashstring += txt[itercount]
                            itercount += 1
                    elif minusset == True:
                        if x == " ":
                            finalmessage += txt[itercount]
                            ##Unsubscribe using minusstring
                            if minusstring in subs:
                                subs[minusstring].remove(name)
                            minusset = False
                            minusindex = 0
                            itercount += 1
                            minusstring = ""
                        else:
                            minusstring += txt[itercount]
                            itercount += 1
                    elif atset == True:
                        if x == " ":
                            finalmessage += txt[itercount]
                            ##Add to recipients
                            for h in handlers.keys():
                                if handlers[h] == atstring:
                                    setofrecipients.add(h)
                            atset = False
                            atindex = 0
                            itercount += 1
                            atstring = ""
                        else:
                            finalmessage += txt[itercount]
                            atstring += txt[itercount]
                            itercount += 1
                    else:
                       finalmessage += txt[itercount]
                       itercount += 1
            if plusset == True:
                ##Subscribe using plusstring
                if plusstring in subs:
                    subs[plusstring].add(name)
                else:
                    subs[plusstring] = set()
                    subs[plusstring].add(name)
                ##print(plusstring)
                plusset = False
                plusindex = 0
                plusstring = ""
            if hashset == True:
                setofhashes.add(hashstring)
                hashset = False
                hashindex = 0
                hashstring = ""
            if minusset == True:
                ## Unsubscribe using minusset
                if minusstring in subs:
                    subs[minusstring].remove(name)
                minusset = False
                minusindex = 0
                minusstring = ""
            if atset == True:
                ##Add to recipients
                for h in handlers.keys():
                    if handlers[h] == atstring:
                        setofrecipients.add(h)
                atset = False
                atindex = 0
                atstring = ""

            ##broadcast({'speak': name, 'txt': finalmessage})
            if len(setofhashes) > 0:
                
                for x in setofhashes:
                    for h in handlers.keys():
                        if x in subs:
                            if handlers[h] in subs[x]:
                                setofrecipients.add(h)
            if len(setofrecipients) > 0:                    
                for h in handlers.keys():
                    if h in setofrecipients:
                        h.do_send({'speak': name, 'txt': finalmessage})
            else:
                broadcast({'speak': name, 'txt': finalmessage})


Listener(8888, MyHandler)
while 1:
    poll(0.05)
