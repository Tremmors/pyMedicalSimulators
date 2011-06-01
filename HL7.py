"""
An HL7 Device Simulator.

Classes:
	Line -- An HL7 Line containing data
	Message -- An HL7 Message containging one or more lines
	Connection -- A socket connection that can directly send Messages
	
"""

import datetime
import socket

SOH 	= chr( 0x01 )	# Start of Heading
STX 	= chr( 0x02 )	# Start of Text
ETX 	= chr( 0x03 )	# End of Text
EOT 	= chr( 0x04 )	# End of Transmission
ENQ 	= chr( 0x05 )	# Enquiry
ACK 	= chr( 0x06 )	# Acknowledgement
BEL  	= chr( 0x07 )	# Bell
BS 	= chr( 0x08 )	# Backspace
TAB	= chr( 0x09 )	# Horizontal Tab
LF 	= chr( 0x0A )	# Line Feed
VT	= chr( 0x0B )	# Vertical Tab
FF	= chr( 0x0C )	# Form Feed
CR 	= chr( 0x0D )	# Carriage Return
SO	= chr( 0x0E )	# Shift Out
SI	= chr( 0x0F )	# Shift In
DLE	= chr( 0x10 )	# Data Link Escape
DC1	= chr( 0x11 )	# Device Control 1
DC2	= chr( 0x12 )	# Device Control 2
DC3	= chr( 0x13 )	# Device Control 3
DC4 	= chr( 0x14 )	# Device Control 4
NAK	= chr( 0x15 )	# Negative Acknowledgement
DLE	= chr( 0x16 )	# Data Link Exchange
ETB 	= chr( 0x17 )	# End Transmission Block
CAN 	= chr( 0x18 )	# Cancel
EM 	= chr( 0x19 )	# End of Medium
SUB 	= chr( 0x1A )	# Substitute
ESC 	= chr( 0x1B )	# Escape
FS 	= chr( 0x1C )	# File Separator
GS 	= chr( 0x1D )	# Group Separator
RS 	= chr( 0x1E )	# Record Separator
US 	= chr( 0x1F )	# Unit Separator

def RandomDateInThePastXDays( Days ):
	""" 
	Return a random DateTime in the past X Days formatted in HL7 DateTime format. 
	
	Not strictly needed for HL7, but a good helper function to have to generate fake messages
	
	Arguments:
	Days -- The number of days to look back when generating the random DateTime
	
	"""
	MaxSeconds = Days * 24 * 60 * 60
	Seconds = random.randint( 1, MaxSeconds )
	Delta = datetime.timedelta( seconds = Seconds )
	return FormatDate( datetime.datetime.now() - Delta )

def CurrentDate():
	""" 
	Return the current DateTime formatted in the HL7 DateTime format. 
	
	"""
	return FormatDate( datetime.datetime.now() )

def FormatDate( DateTime ):
	""" 
	Return a HL7 formatted DateTime (YYYYMMDDHHmmss). 
	
	Arguments:
	DateTime -- The datetime.datetime object to format
	
	"""
	return DateTime.strftime( '%Y%m%d%H%M%S' )
	
class Line:
	""" 
	An individual HL7 Line. 
	
	This is a very simplistic container element.  It does not do all the segment, component addressing
	that you would expect from a true HL7 Line element.  That would be entirely too much work, this 
	is just a quick and dirty simulator.
	
	"""
	def __init__(  self, data='' ):
		""" 
		Create a new HL7 Line object.  
		
		Arguments:
		data -- Whatever text this line will contain (including all segment and component separators)
		
		Example:
		Line("MSH|^&\|SendingApp|SendingFac|ReceivingApp|ReceivingFac|"+CurrentDate()+"||ADT^A01|995476|P|2.2|995476||AL|||||||2.5")
		"""
		self.Data = data
	def Render( self ):
		""" 
		Render this Line including all content and framing characters. 
		
		"""
		return self.Data + CR

class Message:
	""" 
	An HL7 Message object, which contains one or more Lines. 
	
	"""
	def __init__( self ):
		""" 
		Create a new HL7 Message object.
		
		"""
		self.Lines  = []
	def AddLine( self, content ):
		""" 
		Add a new HL7 Line with the given data in it. 
		
		Arguments:
		content -- Whatever text this line will contain (including all segment and component separators)

		Example:
		AddLine("MSH|^&\|SendingApp|SendingFac|ReceivingApp|ReceivingFac|"+CurrentDate()+"||ADT^A01|995476|P|2.2|995476||AL|||||||2.5")

		"""
		self.Lines.append( Line( content ) )
	def Render( self ):
		""" 
		Render all lines in this message including line level and message level framing characters. 
		
		"""
		output = ''
		for thisLine in self.Lines:
			output += thisLine.Render()
		return VT + output + FS+CR

class Connection:
	""" 
	A Connection object, manages the socket connection and allows you to send an HL7 Message directly. 
	
	"""
	def __init__( self, host, port ):
		""" 
		Create a new connection object.
		
		Arguments:
		host -- The IP or HostName to connect to
		port -- The TCP Port to connect to
		
		"""
		self.HOST = host;
		self.PORT = port;
		
	def Open( self ):
		""" 
		Attempt to open the connection to the server.
		
		"""
		self.Socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.Socket.connect( ( self.HOST, self.PORT ) )

	def Send( self, msg ):
		"""
		Send a specific HL7.Message to the server and wait for at least one packet in response.
		
		"""
		self.Socket.send( msg.Render().encode( "windows-1252" ) )
		data = self.Socket.recv( 1024 )

	def Close( self ):
		"""
		Close the connection to the server.
		
		"""
		self.Socket.close()