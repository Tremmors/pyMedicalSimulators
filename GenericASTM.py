"""
        Simulates a generic ASTM device.  Requires the ASTM1394 library.

"""
import ASTM1394
import random
import datetime
import time
	
def GetXResults( Count ):
	MSG = ASTM1394.Message()
	MSG.AddLine( 'H|\^&|||^^11223344|||||IDMS||P|1|' + ASTM1394.CurrentDate() )
	for i in range( 0, Count ):
		MSG.AddLine( 'P|1||555' )
		MSG.AddLine( 'O|1||171|^^^|||' + ASTM1394.RandomDateInThePastXDays(7) + '|||' )
		MSG.AddLine( 'R|1|^^^tHb^M|' + str(random.uniform(2,30)) + '|g/dL||||R' )
		MSG.AddLine( 'R|2|^^^O2Hb^M|' + str(random.uniform(75,125)) + '|%||||R' )
		MSG.AddLine( 'R|3|^^^COHb^M|' + str(random.uniform(0,2)) + '|%||||R' )
		MSG.AddLine( 'R|4|^^^MetHb^M|' + str(random.uniform(2,7)) + '|%||||R' )
		MSG.AddLine( 'R|5|^^^O2Ct^C|' + str(random.uniform(20,35)) + '|mL/dL||||R' )
		MSG.AddLine( 'R|6|^^^O2Cap^C|' + str(random.uniform(20,35)) + '|mL/dL||||R' )
		MSG.AddLine( 'R|7|^^^sO2^C|' + str(random.uniform(50,100)) + '|%||||R' )
	MSG.AddLine( 'L|1|N' )
	return MSG

Conn = ASTM1394.Device( '127.0.0.1', 4000 )
Conn.Open()

ASTM1394.Config_LineNumbering = 1 # include line numbers
ASTM1394.Config_CheckSum_IncludeSTX = 0 # don't include the <2> in the checksum calculation

Conn.Send(GetXResults(1))

Conn.Close()
