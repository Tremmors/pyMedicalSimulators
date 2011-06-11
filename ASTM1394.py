"""
An ASTM1394 Device Simulator.

Classes:
	Frame -- A single frame that contains data (this may or may not be a single line)
	Message -- A Message which contains one or more frames.
	Device -- A socket connection that can directly send Messages

"""

import datetime
import random
import socket
import time

SOH 	= chr( 0x01 )	# Start of Heading
STX 	= chr( 0x02 )	# Start of Text
ETX 	= chr( 0x03 )	# End of Text
EOT 	= chr( 0x04 )	# End of Transmission
ENQ 	= chr( 0x05 )	# Enquiry
ACK 	= chr( 0x06 )	# Acknowledgement
BEL  	= chr( 0x07 )	# Bell
BS 	= chr( 0x08 )	# Backspace
TAB	= chr( 0x09 )	# Horizontal Tab
LF 	= chr( 0x0A ) 	# Line Feed
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

Config_CheckSum_IncludeSTX = 1
Config_LineNumbering = 1
Config_FrameSize = 0


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

def ReformatForLog( data ):
	"""
	Change all non printable characters into something human readable.  
	
	Arguments:
	data -- The raw data that may contain unprintable characters
	
	Example: 0x0D will show up as <D>
	
	"""
	output = ''
	for char in data:
		o = ord( char )
		if( o < 32 ):	# Unprintable control character
			output += '<' + '%X'  % o + '>'
		else:	
			output += char
	return output
	
def CheckSum( data ):
	"""
	Calculate an ASTM checksum for the supplied data
	
	Arguments:
	data -- whatever you want to calculate a checksum for.
	
	If manually calculating checksums, you need to be mindful of whether or not you want to include
	the <2> (STX) that begins the frame.  Sometimes this is expected, sometimes not.
	
	"""
	
	Output = ''
	Counter = 0
	for char in data:
		Counter += ord( char )		# Sum up all the bytes in the data
	CheckValue = Counter % 256		# Checksum = Sum mod 256
	Output = '%X' % CheckValue
	if len( Output ) == 1:
		Output = '0' + Output
	return Output	

class Frame:
	""" 
	An ASTM frame, which may or may not represent a single line.
	
	Depending on the specific interpretation of the spec, this may refer to a 
	size limited portion of the message (after 240bytes for example) or may
	refer to a single logical field (line).
	Also; if this message will contain mutiple frames, this may represent either 
	an intermediate frame or a final frame
	
	"""
	Value = ''
	IsFinalFrame = 1			# Assume a final frame unless otherwise specified.
	
	def __init__( self, FrameContents, FinalFrame ):
		"""
		Create a new ASTM Frame object.
		
		Arguments:
		FrameContents -- What content to put into this frame
		FinalFrame -- 1 = FinalFrame, 0 = Intermediate Frame
		
		"""
		self.Value = FrameContents
		self.IsFinalFrame = FinalFrame
		
	def Add( self, content ):
		""" 
		Append some content to this Frame 
		
		"""
		self.Value += content
		
	def AddLine( self, content ):
		"""
		Add a line to this frame
		
		"""
		self.Value += content + CR
		
	def Output( self, Counter ):
		"""
		Render this entire Frame including all content and framing characters
		
		Arguments:
		Counter -- Numeric frame counter (used by the Message when rendering each frame)
		
		"""
		output = ''
		if Config_CheckSum_IncludeSTX == 1:	# the leading <2> STX is to be included in the checksum
			output += STX
		if Config_LineNumbering == 1:		# include Frame Numbering
			output +=  str( Counter )
		output += self.Value 
		if self.IsFinalFrame == 1:			# Final Frame
			output +=  CR + ETX
		else:
			output += ETB				# Intermediate Frame
			
		output += CheckSum( output )		# Calculate Checksum
		output += CR + LF
		
		if Config_CheckSum_IncludeSTX != 1:
			output= STX + output
		return output

	def Log( self, Counter ):
		"""
		Render this entire Frame but reformat all non-printable characters as human readable
		
		"""
		return ReformatForLog( self.Output( Counter ) )

class Message:
	"""
		An ASTM 1394 message
		Output() should return a fully formatted ASTM message including all framing characters.
		
	"""
	LineBuffer = []
	Frames = []
	def __init__( self ):
		self.LineBuffer = []
		self.Frames = []
	def AddLine( self, content ):
		if Config_FrameSize < 1:
			self.AddFinalFrame( content )
		else:
			self.LineBuffer.append( content + CR )
	def AddIntermediateFrame( self, content ):
		output = Frame( content, 0 )
		self.Frames.append( output )
		return output
	def AddFinalFrame( self, content ):
		output = Frame( content, 1 )
		self.Frames.append( output )
		return output
	def Output( self ):
		if Config_FrameSize > 0:
			self.Frames = []
			TotalMessage = ''.join( self.LineBuffer )
			Buffer = ''
			for thisChar in TotalMessage:
				if len( Buffer ) < Config_FrameSize:
					Buffer += thisChar
				else:
					self.Frames.append( Frame( Buffer , 0 ) )
					Buffer = ''
			if len(Buffer) > 0:
				self.Frames.append( Frame( Buffer, 1 ) )
		output = ''
		Counter = 1
		#print self.Frames
		for thisFrame in self.Frames:
			output += thisFrame.Output( Counter )
			Counter = Counter + 1
			if Counter > 7:
				Counter = 0
		return EOT + ENQ + output + EOT
	def Log( self ):
		return ReformatForLog( self.Output() )
		
class Device:
	"""
		A device object capable of connecting out to an IP/Port and sending an ASTM1394.Message
		
	"""
	def __init__( self, host = '127.0.0.1', port = 8000 ):
		self.HOST = host;
		self.PORT = port;
	def Open( self ):
		self.Socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.Socket.connect( ( self.HOST, self.PORT ) )
	def Send( self, msg ):
		self.Socket.send( msg.Output().encode( "windows-1252" ) )
		data = self.Socket.recv( 1024 )
		return data
	def Close( self ):
		self.Socket.close()