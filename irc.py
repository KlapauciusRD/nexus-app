


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys
import threading
from functools import partial


import unicodedata

global message_queue
global p
message_queue = []

#This needs to collect new messages into a stack. Maybe a get method to allow the stack to be drawn into the main app.
class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
       with lock:
            """Write a message to the file."""
            timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
            self.file.write('%s %s\n' % (timestamp, message))
            self.file.flush()
            

    def close(self):
        self.file.close()


class KlapBot(irc.IRCClient):
    """A logging IRC bot."""
  
    #My commands.
    def send_message(self, message):
        #message = unicodedata.normalize('NFKD', message).encode('ascii','ignore')
        self.msg(self.factory.channel, message)
        self.log_message('<'+self.factory.nickname+'> '+message)
    
    def log_message(self, message):
       with lock:
            """Write a message to the file."""
            timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
            message_queue.append([timestamp, message])
            print(message)
            
        

        
        
        
    ##This is code that should get a list of users sorcery
    def names(self, channel=None):
        if not channel:
            channel = self.factory.channel
        "List the users in 'channel', usage: client.who('#testroom')"
        self.sendLine('NAMES %s' % channel)

    def irc_RPL_NAMREPLY(self, *nargs):
        "Receive NAMES reply from server"
        print 'NAMES:', nargs
        with lock:
            self.name_list = nargs[1][3]

    def irc_RPL_ENDOFNAMES(self, *nargs):
        "Called when NAMES output is complete"
        print 'NAMES COMPLETE'

    def irc_unknown(self, prefix, command, params):
        "Print all unhandled replies, for debugging."
        print 'UNKNOWN:', prefix, command, params    
    ###end user listing code sorcery
    
    
    def connectionMade(self):  
        irc.IRCClient.connectionMade(self)
        self.log_message("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))
                        

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.log_message("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))



    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.log_message("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.log_message("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: I am a log bot" % user
            self.msg(channel, msg)
            self.log_message("<%s> %s" % (self.nickname, msg))
            

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.log_message("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.log_message("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'


    #Stuff that really shouldn't be here!
    def get_message_log(self):
        with lock:
            global message_queue
            return_queue = message_queue
            message_queue = []
            return return_queue
    
    def get_names(self):
        with lock:
            return self.name_list
        
        

class KlapBotFactory(protocol.ClientFactory):
    """A factory for KlapBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, nickname, channel):
        self.channel = channel
        self.nickname= nickname

    def buildProtocol(self, addr):
        global p
        p = KlapBot()
        p.nickname = self.nickname
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

    
        
def initialise(nick, channel):
    global lock
    lock = threading.Lock()
    irc_thread = threading.Thread(target= partial(start_irc,nick,channel))
    irc_thread.daemon = True
    irc_thread.start()
    


    
def start_irc(nick, channel):
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = KlapBotFactory(nick, channel)

    # connect factory to this host and port
    reactor.connectTCP("krypton.gaijin.com", 6667, f)

    # run bot
    reactor.run()

    
    



