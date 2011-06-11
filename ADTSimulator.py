"""
    Generates some common ADT (Admit, Discharge, Transfer) HL7 messages for testing purposes.
    Open a connection, send a custom message or use one fo the predefined ones.
"""

import HL7

def GetAdmitMessage( PrimaryID, VisitID,Facility='Main', Location='Admin', PatientClass='I' ):
    """
        Create an Admit (A01) message admitting a Patient.

        Parameters:
            PrimaryID - The Primary Patient ID that stays with that patient forever
            VisitID - The Patient ID that is specific to this visit, and changes next time the patient is admitted
            Facility - The name of the facility this patient is being admitted to
            Location - The name of the workstation the patient is being admitted to
            PatientClass - The Class of patient.  Defined in HL7 (see spec for complete list)
                I = Inpatient
                O = Outpatient
        
    """
    MSG = HL7.Message()    
    MSG.AddLine( 'MSH|^~\&|Hospital|H|HL7|HL7|' + HL7.CurrentDate() + '||ADT^A01|35745881|P|2.2|35745881||AL|||||||2.5' )
    MSG.AddLine( 'PID|1|^^^^^|' + PrimaryID + '^^^H^MR^||Doe^Jane^""^""|||F||7|^^^^^^^||||^^^^^|M|NO|' + VisitID + '^^^H^^||||||N|||N|||N' )
    MSG.AddLine( 'PV1|1|' + PatientClass + '|' + Location + '^^^' + Facility + '|3|||^^^""^^^^||""|^^|||N|1|||^^^""^^^^|||K|' + VisitID + '|||||||||||||||11|||H||2|||||||||||' )
    return MSG

def GetMergeMessage( SrcPrimaryID, SrcVisitID, DstPrimaryID, DstVisitID,Facility='Main',Location='Admin',PatientClass='I' ):
    """
        Create a merge message (A18) which combining all records from 2 patient (or visits) into one

        Parameters:
            SrcPrimaryID - The old patient's Primary Patient ID that stays with that patient forever
            SrcVisitID - The old patient's Visit specific ID that will change the next time the patient is admitted
            DstPrimaryID - The new patient's Primary Patient ID that stays with that patient forever
            DstVisitID - The new patient's Visit specific ID that will change the next time the patient is admitted
            Facility - The name of the facility the new Visit is at
            Location - The name of the workstation the new Visit is at
            PatientClass - The Class of patient.  Defined in HL7 (see spec for complete list)
                I = Inpatient
                O = Outpatient
        
    """
    MSG = HL7.Message()
    MSG.AddLine( 'MSH|^~\&|Hospital|H|HL7|HL7|' + HL7.CurrentDate() + '||ADT^A18|35745881|P|2.2|35745881||AL|||||||2.5' )
    MSG.AddLine( 'PID|1|^^^^^|' + DstPrimaryID + '^^^H^MR^||Doe^Jane^""^""|||F||7|^^^^^^^||||^^^^^|M|NO|' + DstVisitID + '^^^H^^||||||N|||N|||N' )
    MSG.AddLine( 'PV1|1|' + PatientClass + '|' + Location + '^^^' + Facility + '|3|||^^^""^^^^||""|^^|||N|1|||^^^""^^^^|||K|' + DstVisitID + '|||||||||||||||11|||H||2|||||||||||' )
    MSG.AddLine( 'MRG|' + SrcPrimaryID + '||||' + SrcVisitID + '|' )
    return MSG


def GetBedSwapMessage( PrimaryID1, VisitID1, PrimaryID2, VisitID2 ):
    """
        Create a bedswap message (A17) which switches the location of 2 patients.

        Parameters:
            PrimaryID1 - The first patient's Primary Patient ID that stays with the patient forever
            VisitID1 - The first patient's Visit specific ID that will change the next time the patient is admitted.
            PrimaryID2 - The second patient's Primary Patient Id that stays with the patient forever
            VisitID2 - The second patient's Visit specific ID that will change the next time the patient is admitted.
            
    """
    MSG = HL7.Message()
    MSG.AddLine( 'MSH|^~\&|Hospital|H|HL7|HL7|' + HL7.CurrentDate() + '||ADT^A17|35745881|P|2.2|35745881||AL|||||||2.5' )
    MSG.AddLine( 'PID|1|^^^^^|' + PrimaryID1 + '^^^H^MR^||Doe^Jane^""^""|||F||7|^^^^^^^||||^^^^^|M|NO|' + VisitID1 + '^^^H^^||||||N|||N|||N' )
    MSG.AddLine( 'PV1|1|I|^^^|3|||^^^""^^^^||""|^^|||N|1|||^^^""^^^^|||K|' + VisitID1 + '|||||||||||||||11|||H||2|||||||||||' )
    MSG.AddLine( 'PID|1|^^^^^|' + PrimaryID2 + '^^^H^MR^||Doe^Jane^""^""|||F||7|^^^^^^^||||^^^^^|M|NO|' + VisitID2 + '^^^H^^||||||N|||N|||N' )
    MSG.AddLine( 'PV1|1|I|^^^|3|||^^^""^^^^||""|^^|||N|1|||^^^""^^^^|||K|' + VisitID2 + '|||||||||||||||11|||H||2|||||||||||' )
    return MSG


Conn = HL7.Connection( '127.0.0.1', 8000 )
Conn.Open()

Conn.Send( GetAdmitMessage( '11223344', '0000001' ) )

Conn.Close()

