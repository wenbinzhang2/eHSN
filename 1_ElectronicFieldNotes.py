from ElectronicFieldNotesGUI import *
from TitleHeaderManager import *
from GenInfoManager import *
from DischargeMeasurementsManager import *
from StageMeasurementsManager import *
from EnvironmentConditionsManager import *
from MeasurementResultsManager import *
from InstrumentDeploymentInfoManager import *
from PartyInfoManager import *
from WaterLevelRunManager import *
# from AnnualLevellingManager import *
from FRChecklistManager import *
from MovingBoatMeasurementsManager import *
from MidSectionMeasurementsManager import *

from RatingCurveViewerToolManager import *

# from UserConfigManager import *
from AquariusMiscUploadDialogs import *
import VersionCheck
import XMLManager
import AquariusUploadManager

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.dom import minidom

from xhtml2pdf import pisa             # import python module
from lxml import etree

import os
from os import chdir
from os import environ
from os.path import join
from os.path import dirname
import sys
import thread
import suds

import datetime
import sys

# import atexit

##mode = "DEBUG"
mode = "PRODUCTION"
EHSN_VERSION = "v1.2.3"
# SERVER_EHSN = r"\\Ncr.int.ec.gc.ca\shares\H\HYDSTOR\Hydrometric Data Systems\Bin\Release"
# files = os.listdir(SERVER_EHSN)


# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)



class ElectronicHydrometricSurveyNotes:
    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.headerTitle = "Hydrometric Survey Notes " + EHSN_VERSION

        # Label variables
        self.exportAQTitle = "Uploading Field Visit to AQUARIUS"
        self.exportAQLoginMessage = "Logging into AQUARIUS..."
        self.exportAQLocMessage = "Checking location..."
        self.exportAQNoLoc = "Location does not exist. Please enter valid location number."
        self.exportAQFVMessage = "Checking if a Field Visit exists for selected date..."
        self.exportAQNoFV = "Could not find Field Visits for location:"
        self.exportAQNewFV = "Creating new Field Visit in AQUARIUS..."
        # self.exportAQAppendFV = "It appears that a Field Visit exists for this date. The data in this Hydrometric Survey note will be appended to the Field Visit. Continue?"
        self.exportAQAppendFV = "It appears that a Field Visit exists for this date.  Press OK to append the HSN to this field visit."
        self.exportAQWarning = "Upload Warning!"
        self.exportAQCancel = "Upload cancelled"
        self.exportAQFVUpdate = "Updating Field Visit in AQUARIUS"
        self.saveXMLErrorDesc = "Failed on saving to XML"
        self.saveXMLErrorTitle = "Failed on saving to XML"
        self.lockWarningTitle = "Are you sure?"
        self.lockWarningMessage = "If unlocked, it means that the user has made a decision to view or modify the uploaded xml file because any changes in the xml may not be reflected in AQUARIUS unless the file is uploaded again or modified manually in AQUARIUS."

        self.InitUI()


    def InitUI(self):
        if mode == "DEBUG":
            print "EHSN"
        app = wx.App()
        self.uploadRecord = None
        self.gui = EHSNGui(mode, EHSN_VERSION, None, title=self.headerTitle, size=(810, 790))
        self.SetupManagers()
        self.stageMeasManager.AddEntry()
        self.waterLevelRunManager.AddRun()
        # 6 Entries
        for i in range(9):
            self.movingBoatMeasurementsManager.AddEntry()
        self.BindAutoSave()
        self.BindCorrectedMGH()
        self.gui.LoadDefaultConfig()

        self.gui.titleHeader.enteredInHWSCB.Bind(wx.EVT_CHECKBOX, self.LockEvent)


        # try:
        #     self.gui.OpenStationFile('stations.csv')
        # except:
        #     pass
        # try:
        #     self.gui.OpenLevelFile('levels.csv')
        # except:
        #     pass
        # try:
        #     self.gui.OpenMeterFile('meters.csv')
        # except:
        #     pass

        self.DT_FORMAT = "%Y/%m/%d"
        ############################################
        #Version checking
        # latest = self.find(files)
        # if latest is not None:
        #   if not self.compare(EHSN_VERSION, self.find(files)):
        #       self.CreateDialog('System out of update, please download the newest version from the server.')

        ############################################

##        self.gui.Centre()

        self.gui.Show()
        # Muluken! if the new midsection is giving you problems, uncomment the below line!!
        #self.gui.form4.Disable()

        # atexit.register(self.OnExit())
        try:
            app.MainLoop()
        except:
            if self.gui.fullname == '':
                self.ExportAsXML(str(os.getcwd()) + '\\' + self.genInfoManager.stnNumCmbo + "_CrashLog.xml", None)
            self.ExportAsXML(self.gui.fullname, None)

        # VersionCheck.Check(EHSN_VERSION, self, False)
    def GetLayout(self):
        return self.gui.layout


    # def OnExit(self):
    #     # if self.gui.fullname == '':
    #     #         self.ExportAsXML(str(os.getcwd()) + '\\' + self.genInfoManager.stnNumCmbo + "_CrashLog.xml")
    #     # self.ExportAsXML(self.gui.fullname)
    #     print "You are now leaving the eHSN, Have a nie day"


    # Instantiates all Managers and gives their respective GUIs
    def SetupManagers(self):
        self.gui.manager = self
        self.titleHeaderManager = TitleHeaderManager(mode, self.gui.titleHeader, self)
        self.genInfoManager = GenInfoManager(mode, self.gui.genInfo, self)
        self.disMeasManager = DischargeMeasurementsManager(mode, self.gui.disMeas, self)
        self.stageMeasManager = StageMeasurementsManager(mode, self.gui.stageMeas, self)
        self.envCondManager = EnvironmentConditionsManager(mode, self.gui.envCond, self)
        self.measResultsManager = MeasurementResultsManager(mode, self.gui.measResults, self)
        self.instrDepManager = InstrumentDeploymentInfoManager(mode, self.gui.instrDep, self)
        self.partyInfoManager = PartyInfoManager(mode, self.gui.partyInfo, self)
        self.waterLevelRunManager = WaterLevelRunManager(mode, self.gui.waterLevelRun, self)
        # self.annualLevelNotesManager = AnnualLevellingManager(mode, self.gui.annualLevelNotes, self)
        self.frChecklistManager = FRChecklistManager(mode, self.gui.frChecklist, self)
        self.movingBoatMeasurementsManager = MovingBoatMeasurementsManager(mode, self.gui.movingBoatMeasurements, self)
        self.midsecMeasurementsManager = MidSectionMeasurementsManager(mode, self.gui.midsecMeasurements, self)
        # self.ratingCurveExtractionToolmanager = RatingCurveExtractionToolManager()
        # self.ratingCurveViewerToolManager = RatingCurveViewerToolManager(mode, self.gui.midsecMeasurements, self)


        # self.userConfigManager = UserConfigManager(mode, self.gui.userConfig, self)











    # Update the Field Review Checklist with the value of depType
    def DeploymentUpdate(self, depType):
        self.frChecklistManager.changeDepType(depType)


    def FieldReviewChecklistUpdate(self, val):
        self.frChecklistManager.onInstrumentType(val)

    def ExportAsPDFWithoutOpen(self, filePath, xslPath):
        if mode == "DEBUG":
            print "Saving PDF"

##        pisa.showLogging()


        xml = self.EHSNToXML()
        print xslPath
        # transform = etree.XSLT(etree.parse(xslPath))
        transform = etree.XSLT(etree.parse(xslPath))
        result = transform(etree.fromstring(xml))

        # result = str(result).replace("%5C", "\\")
        result = str(result).replace("logo_path", self.gui.logo_path)
        result = result.replace("qr_path", self.gui.qr_path)

        # open output file for writing (truncated binary)
        resultFile = open(filePath, "w+b")

        # convert HTML to PDF
        pisa.CreatePDF(
                src=result,                # the HTML to convert
                dest=resultFile,           # file handle to receive result
                encoding="UTF-8")
        resultFile.close()




    # Call EHSNToXML() to create xml tree
    # transform xml tree into html format (based on xsl)
    # create PDF based on html
    def ExportAsPDF(self, filePath, xslPath):

        self.ExportAsPDFWithoutOpen(filePath, xslPath)
        #Open the pdf

        if sys.platform == 'linux2':
            subprocess.call(["xdg-open", filePath])
        else:
            os.startfile(filePath)

    #create pdf from a given xml file without open
    def ExportAsPDFFromXML(self, filePath, xslPath, xml):
        if mode == "DEBUG":
            print "Saving PDF"

##        pisa.showLogging()


        transform = etree.XSLT(etree.parse(xslPath))
        result = transform(etree.fromstring(xml))

        result = str(result).replace("logo_path", self.gui.logo_path)
        result = result.replace("qr_path", self.gui.qr_path)

        # open output file for writing (truncated binary)
        resultFile = open(filePath, "w+b")

        # convert HTML to PDF
        pisa.CreatePDF(
                src=result,                # the HTML to convert
                dest=resultFile,           # file handle to receive result
                encoding="UTF-8")
        resultFile.close()

    #After generating the pdf from xml, open the pdf
    def ExportAsPDFFromXMLOpen(self, filePath, xslPath, xml):

        self.ExportAsPDFFromXML(filePath, xslPath, xml)
        #Open the pdf

        if sys.platform == 'linux2':
            subprocess.call(["xdg-open", filePath])
        else:
            os.startfile(filePath)


    #validate the mandatory value before uploading to AQ
    def CheckFVVals(self):

        AquariusUploadManager.CheckFVVals(mode, self)



    # Check if the values in the eHSN will cause an error during upload to AQ
    # Log in to AQ
    # Check Location (based on StationNumber)
    # Check if Field Visit exists for given date
    # If it exists, prompt user for append of info
    # If it doesn't exist, create new FV
    def ExportToAquarius(self, server, username, password, fvDate, discharge, levelNote):



        # Aquarius Login
        self.gui.createProgressDialog(self.exportAQTitle, self.exportAQLoginMessage)
        exists, value = AquariusUploadManager.AquariusLogin(mode, server, username, password)

        if exists:
            aq = value

            #See if location exists
            self.gui.updateProgressDialog(self.exportAQLocMessage)
            exists, locid = AquariusUploadManager.AquariusCheckLocInfo(mode, aq, self.genInfoManager.stnNumCmbo)

            if not exists:
                self.gui.deleteProgressDialog()
                return self.exportAQNoLoc

            # See if Field Visit Exists in Aquarius
            self.gui.updateProgressDialog(self.exportAQFVMessage)
            fv, val = AquariusUploadManager.AquariusFieldVisitExistsByDate(mode, aq, locid, fvDate)

            if val is None:
                self.gui.deleteProgressDialog()
                return self.exportAQNoFV + " %d" % locid


            if fv or len(val) > 0:
                self.gui.deleteProgressDialog()
                warning = wx.MessageDialog(None,
                                           self.exportAQAppendFV,
                                           self.exportAQWarning, wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
                cont = warning.ShowModal()
                if cont == wx.ID_CANCEL:
                    return self.exportAQCancel

                self.gui.createProgressDialog(self.exportAQTitle, self.exportAQFVUpdate)


            if len(val) >= 1:
                # make popup

                displayLis = []
                for dis in val:
                    disTime = dis.MeasurementTime
                    startDate = datetime.datetime.strptime(str(self.genInfoManager.datePicker), "%Y/%m/%d")
                    startDate = startDate.replace(hour=disTime.hour, minute=disTime.minute, second=disTime.second)

                    disName = startDate.strftime("%Y/%m/%d") + " discharge activity started at " + startDate.strftime("%H:%M:%S")
                    displayLis.append(disName)

                self.gui.deleteProgressDialog()
                if discharge:
                    AMDUD = AquariusMultDisUploadDialog("DEBUG", None, displayLis, None, title="Upload Field Visit to Aquarius")
                    AMDUD.Show()

                    re = AMDUD.ShowModal()


                    if re == wx.ID_YES:
                        if AMDUD.MergeRBIsSelected():
                            selectedDis = AMDUD.GetSelectedDisMeas()
                            index = displayLis.index(selectedDis)



                            val = [val[index]]
                        else:
                            val = []
                    else:
                        print "Cancel"
                        return "Cancelled out of field visit" + " %d" % locid

                    AMDUD.Destroy()
                self.gui.createProgressDialog(self.exportAQTitle, self.exportAQFVMessage)

            #There is no Field Visit for this day

            if len(val) == 0:
                self.gui.updateProgressDialog(self.exportAQNewFV)

                try:
                    emptyList = []

                    export = AquariusUploadManager.ExportToAquarius(mode, EHSN_VERSION, self, aq, fv, locid, discharge, levelNote, emptyList, None, server)

                    self.gui.deleteProgressDialog()

                    return export
                except suds.WebFault, e:
                    self.gui.deleteProgressDialog()

                    print e
                    return str(e)
                except ValueError, e:
                    self.gui.deleteProgressDialog()

                    return str(e)
            else:
                if mode == "DEBUG":
                    print "Field Visit for selected date"
                    print val

                paraList = AquariusUploadManager.GetParaIDByFV(val[0])
                export = AquariusUploadManager.ExportToAquarius(mode, EHSN_VERSION, self, aq, fv, locid, discharge, levelNote, paraList, val[0], server)
                self.gui.deleteProgressDialog()
                return export
        else:
            self.gui.deleteProgressDialog()
            return value

    # Checks the "Entered in HWS" checkbox at top of front page
    def ExportToAquariusSuccess(self):
        self.titleHeaderManager.enteredInHWSCB = True
        self.Lock()

    # Locks all the pages except the title header.
    def LockEvent(self, e):
        if self.gui.titleHeader.enteredInHWSCB.GetValue():
            self.Lock()
        elif e is not None:
            dlg = wx.MessageDialog(None, self.lockWarningMessage, self.lockWarningTitle, wx.YES_NO)
            res = dlg.ShowModal()
            if res==wx.ID_YES:
                for widget in self.gui.form.GetChildren():
                    widget.Enable()
                self.gui.form2.Enable()
                self.gui.form3.Enable()
                self.gui.form4.Enable()
                self.gui.form5.Enable()
            else:
                self.gui.titleHeader.enteredInHWSCB.SetValue(True)
        else:
            for widget in self.gui.form.GetChildren():
                widget.Enable()
            self.gui.form2.Enable()
            self.gui.form3.Enable()
            self.gui.form4.Enable()
            self.gui.form5.Enable()

    def Lock(self):
        for widget in self.gui.form.GetChildren():
            widget.Disable()
        self.gui.titleHeader.Enable()
        self.gui.form2.Disable()
        self.gui.form3.Disable()
        self.gui.form4.Disable()
        self.gui.form5.Disable()

    # Generates xml from all info from eHSN
    # Writes to file based on filePath
    def ExportAsXML(self, filePath, msg):
        if mode == "DEBUG":
            print "Saving File"
        # try:
        #     # raise Exception('*****Error Raised for Testing Only!*****') # don't, if you catch, likely to hide bugs.
        #     pretty_xml = self.EHSNToXML() # Collects all info and puts into eTree

        #     if mode == "DEBUG":
        #         print pretty_xml
        #         print filePath

        #     output = open(filePath, 'w')
        #     output.write( pretty_xml.encode('utf-8') )
        #     output.close()
        #     return pretty_xml
        # except:
        #     if msg != None:
        #         desc = self.saveXMLErrorDesc + "\n " + msg + " may contain an invalid character"
        #     else:
        #         desc = self.saveXMLErrorDesc
        #     dlg = wx.MessageDialog(self.gui, desc, self.saveXMLErrorTitle, wx.OK | wx.ICON_QUESTION)

        #     res = dlg.ShowModal()
        #     if res == wx.ID_OK:
        #         dlg.Destroy()
        #     else:
        #         dlg.Destroy()

        #########################for testing without catching exceptions###################################
        pretty_xml = self.EHSNToXML() # Collects all info and puts into eTree

        if mode == "DEBUG":
            print pretty_xml
            print filePath

        output = open(filePath, 'w')
        output.write( pretty_xml.encode('utf-8') )
        output.close()
        return pretty_xml
        ##################################################################################################


    # Creates xml tree based on eHSN values
    # Puts in human readable format
    def EHSNToXML(self):
        if mode == "DEBUG":
            print "To XML"

        #Page 1
        #Create XML Tree structure
        EHSN = Element('EHSN', version=EHSN_VERSION)

        # if hasattr(sys, '_MEIPASS'):
            # DirInfo = SubElement(EHSN, 'dirInfo')
            # DirInfo.text = (join(sys._MEIPASS, "icon_transparent.png"))

        #Title Header Branch
        TitleHeader = SubElement(EHSN, 'TitleHeader')
        self.TitleHeaderAsXMLTree(TitleHeader)

        #General Info Branch
        GenInfo = SubElement(EHSN, 'GenInfo')
        self.GenInfoAsXMLTree(GenInfo)



        #Stage Measurements Branch
        StageMeas = SubElement(EHSN, 'StageMeas')
        self.StageMeasAsXMLTree(StageMeas)

        #Discharge Measurements Branch
        DisMeas = SubElement(EHSN, 'DisMeas')
        self.DischMeasAsXMLTree(DisMeas)

        #Environment Conditions Branch
        EnvCond = SubElement(EHSN, 'EnvCond')
        self.EnvCondAsXMLTree(EnvCond)

        #Measurement Results Branch
        MeasResults = SubElement(EHSN, 'MeasResults', empty = 'False')
        self.MeasResultsAsXMLTree(MeasResults)

        #Instrument Deployment Branch
        InstrumentDeployment = SubElement(EHSN, 'InstrumentDeployment')
        self.InstrumentDepAsXMLTree(InstrumentDeployment)

        #Party Information Branch
        PartyInfo = SubElement(EHSN, 'PartyInfo')
        self.PartyInfoAsXMLTree(PartyInfo)


        #Page 2
        #LevelNotes
        LevelNotes = SubElement(EHSN, 'LevelNotes')

        #Level Checks
        LevelChecks = SubElement(LevelNotes, 'LevelChecks')
        self.LevelChecksAsXMLTree(LevelChecks)

        # #Annual Levels
        # AnnualLevels = SubElement(LevelNotes, 'AnnualLevels')
        # self.AnnualLevelsAsXMLTree(AnnualLevels)


        #Page 3
        #Checklist
        FieldReview = SubElement(EHSN, "FieldReview")
        self.FieldReviewAsXMLTree(FieldReview)


        #Page 4
        #ADCP Measurements
        MovingBoatMeas = SubElement(EHSN, "MovingBoatMeas", empty="False")
        self.MovingBoatMeasAsXMLTree(MovingBoatMeas)

        #Page 5
        #Midsection Measurements
        MidsecMeas = SubElement(EHSN, "MidsecMeas", empty="False")
        self.MidsecMeasAsXMLTree(MidsecMeas)

        #save current upload record
        if self.uploadRecord is not None:
            UploadRecord = SubElement(EHSN, "AQ_Upload_Record")
            for row in self.uploadRecord.findall('record'):
                details = []
                for col in row.getchildren():
                    details.append(col.text)
                self.UploadInfoAsXMLTree(UploadRecord, details)

            # EHSN.append(self.uploadRecord)


        doc_string = ElementTree.tostring(EHSN)
        reparsed = minidom.parseString(doc_string)
        style = reparsed.createProcessingInstruction('xml-stylesheet',
                                                     'type="text/xsl" href="WSC_EHSN.xsml"')
        root = reparsed.firstChild
        reparsed.insertBefore(style, root)
        pretty_xml = reparsed.toprettyxml(indent="\t")

        return pretty_xml




    #Read from external xml files for moving boat
    def OpenMovingBoatMmt(self, filePath):
        if mode == "DEBUG":
            print "Opening Moving Boat XML"

        winRiver = ElementTree.parse(filePath).getroot()
        # siteInformation = winRiver.find('Project').find('Site_Information')
        # dischargeSummary = winRiver.find('Project').find('Site_Discharge').find('Discharge_Summary')
        self.MovingBoatTransectFromMmt(winRiver)





    #Read xml file and place each val into text fields in eHSN
    def OpenFile(self, filePath):
        if mode == "DEBUG":
            print "Opening File"


        EHSN = ElementTree.parse(filePath).getroot()

        #First Page
        TitleHeader = EHSN.find('TitleHeader')
        self.TitleHeaderFromXML(TitleHeader)

        GenInfo = EHSN.find('GenInfo')
        self.GenInfoFromXML(GenInfo)



        StageMeas = EHSN.find('StageMeas')
        self.StageMeasFromXML(StageMeas)

        DisMeas = EHSN.find('DisMeas')
        self.DischMeasFromXML(DisMeas)

        EnvCond = EHSN.find('EnvCond')
        self.EnvCondFromXML(EnvCond)

        MeasResults = EHSN.find('MeasResults')
        self.MeasResultsFromXML(MeasResults)

        InstrumentDeployment = EHSN.find('InstrumentDeployment')
        self.InstrumentDepFromXML(InstrumentDeployment)



        PartyInfo = EHSN.find('PartyInfo')
        self.PartyInfoFromXML(PartyInfo)

        #Second Page
        LevelNotes = EHSN.find('LevelNotes')
        LevelChecks = LevelNotes.find('LevelChecks')
        self.LevelChecksFromXML(LevelChecks)

        # AnnualLevels = LevelNotes.find('AnnualLevels')
        # self.AnnualLevelsFromXML(AnnualLevels)

        #Third Page
        FieldReview = EHSN.find('FieldReview')
        self.FieldReviewFromXML(FieldReview)

        #Fourth Page
        MovingBoatMeas = EHSN.find('MovingBoatMeas')
        MovingBoatMeas = EHSN.find('ADCPMeas') if MovingBoatMeas is None else MovingBoatMeas
        self.MovingMeasFromXML(MovingBoatMeas)

        #Fifth Page
        MidsecMeas = EHSN.find('MidsecMeas')
        self.MidsecMeasFromXML(MidsecMeas)

        #Upload Record

        self.uploadRecord = EHSN.find('AQ_Upload_Record')



    def TitleHeaderAsXMLTree(self, TitleHeader):
        XMLManager.TitleHeaderAsXMLTree(TitleHeader, self.titleHeaderManager)

    def TitleHeaderFromXML(self, TitleHeader):
        XMLManager.TitleHeaderFromXML(TitleHeader, self.titleHeaderManager)


    def GenInfoAsXMLTree(self, GenInfo):
        XMLManager.GenInfoAsXMLTree(GenInfo, self.genInfoManager)

    def GenInfoFromXML(self, GenInfo):
        XMLManager.GenInfoFromXML(GenInfo, self.genInfoManager)





    def StageMeasAsXMLTree(self, StageMeas):
        XMLManager.StageMeasAsXMLTree(StageMeas, self.stageMeasManager)

    def StageMeasFromXML(self, StageMeas):
        XMLManager.StageMeasFromXML(StageMeas, self.stageMeasManager)

    def DischMeasAsXMLTree(self, DisMeas):
        XMLManager.DischMeasAsXMLTree(DisMeas, self.disMeasManager)

    def DischMeasFromXML(self, DisMeas):
        XMLManager.DischMeasFromXML(DisMeas, self.disMeasManager)


    def EnvCondAsXMLTree(self, EnvCond):
        XMLManager.EnvCondAsXMLTree(EnvCond, self.envCondManager)

    def EnvCondFromXML(self, EnvCond):
        XMLManager.EnvCondFromXML(EnvCond, self.envCondManager)


    def MeasResultsAsXMLTree(self, MeasResults):
        XMLManager.MeasResultsAsXMLTree(MeasResults, self.measResultsManager)

    def MeasResultsFromXML(self, MeasResults):
        XMLManager.MeasResultsFromXML(MeasResults, self.measResultsManager)



    def InstrumentDepAsXMLTree(self, InstrumentDeployment):
        XMLManager.InstrumentDepAsXMLTree(InstrumentDeployment, self.instrDepManager)

    def InstrumentDepFromXML(self, InstrumentDeployment):
        XMLManager.InstrumentDepFromXML(InstrumentDeployment, self.instrDepManager)


    def PartyInfoAsXMLTree(self, PartyInfo):
        XMLManager.PartyInfoAsXMLTree(PartyInfo, self.partyInfoManager)

    def PartyInfoFromXML(self, PartyInfo):
        XMLManager.PartyInfoFromXML(PartyInfo, self.partyInfoManager)


    def LevelChecksAsXMLTree(self, LevelChecks):
        XMLManager.LevelChecksAsXMLTree(LevelChecks, self.waterLevelRunManager)

    def LevelChecksFromXML(self, LevelChecks):
        XMLManager.LevelChecksFromXML(LevelChecks, self.waterLevelRunManager)
        # self.gui.LoadDefaultConfig()


    # def AnnualLevelsAsXMLTree(self, AnnualLevels):
    #     XMLManager.AnnualLevelsAsXMLTree(AnnualLevels, self.annualLevelNotesManager)

    # def AnnualLevelsFromXML(self, AnnualLevels):
    #     XMLManager.AnnualLevelsFromXML(AnnualLevels, self.annualLevelNotesManager)


    def FieldReviewAsXMLTree(self, FieldReview):
        XMLManager.FieldReviewAsXMLTree(FieldReview, self.frChecklistManager)

    def FieldReviewFromXML(self, FieldReview):
        XMLManager.FieldReviewFromXML(FieldReview, self.frChecklistManager)


    def MovingBoatMeasAsXMLTree(self, MovingBoatMeas):
        XMLManager.MovingBoatMeasAsXMLTree(MovingBoatMeas, self.movingBoatMeasurementsManager)

    def MovingMeasFromXML(self, MovingBoatMeas):
        XMLManager.MovingBoatMeasFromXML(MovingBoatMeas, self.movingBoatMeasurementsManager)


    def MidsecMeasAsXMLTree(self, MidsecMeas):
        XMLManager.MidsecMeasAsXMLTree(MidsecMeas, self.midsecMeasurementsManager)

    def MidsecMeasFromXML(self, MidsecMeas):
        XMLManager.MidsecMeasFromXML(MidsecMeas, self.midsecMeasurementsManager)

    def UploadInfoAsXMLTree(self, UploadInfo, uploadInfo):
        XMLManager.UploadInfoAsXMLTree(UploadInfo, uploadInfo)



    def MovingBoatTransectFromMmt(self, winRiver):
        date = self.genInfoManager.datePicker.split('/')
        convertedDate = date[1] + '/' + date[2] + '/' + date[0]
        XMLManager.OnImportMmt(winRiver, self.movingBoatMeasurementsManager, self.genInfoManager.stnNumCmbo, convertedDate, self.gui)


    def newEHSN(self):
        thread.start_new_thread(self.startNewEHSN(), ("new-thread", ))
    def startNewEHSN(self):
        app = wx.App()
        ElectronicHydrometricSurveyNotes()
        app.MainLoop()


    def CreateDialog(self, message):
        info = wx.MessageDialog(None, message, "Out of Update",
                                wx.OK | wx.ICON_EXCLAMATION)
        info.ShowModal()


    #return the name of the latest version of eHSN
    def find(self, names):
        for e in names:
            m = re.match("^.*_v\d+", e)
            if m:
                return e



    #compare current version to latest version of eHSN on the server
    #return false if need to be updated
    def compare(self, str1, str2):
        ver = str1.split('.')
        latest = str2.split('_')

        if int(ver[0][1:]) > int(latest[2][1:]):
            return True
        elif int(ver[0][1:]) == int(latest[2][1:]) and int(ver[1]) > int(latest[3]):
            return True
        elif int(ver[0][1:]) == int(latest[2][1:]) and int(ver[1]) == int(latest[3]) and int(ver[2]) >= int(latest[4]):
            return True
        else:
            return False

    @property
    def FlatNoteBook(self):
        return self.gui.GetFlatNoteBook()

    def GetGuiDir(self):
        return self.gui.dir


    #Bind the auto save event to each field from each model
    def BindAutoSave(self):
        #genInfor
        self.genInfoManager.GetStnNumCmboCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.genInfoManager.GetStnNameCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        #disMeas
        self.disMeasManager.GetStartTimeCtrl().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetEndTimeCtrl().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetStartTimeCtrl().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetEndTimeCtrl().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetAirTempCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetWaterTempCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetWidthCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetAreaCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetMeanVelCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetMghCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetDischCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetShiftCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetDiffCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.disMeasManager.GetCurveCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        #stageMeasManager
        self.stageMeasManager.GetHgCkbox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetHg2Ckbox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetWlr1Ckbox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetWlr2Ckbox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.stageMeasManager.GetStageLabelCtrl1().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetStageLabelCtrl2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetBmLeft().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetBmRight().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.stageMeasManager.GetMGHHG().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetMGHHG2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetMGHWLRefL().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetMGHWLRefR().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.stageMeasManager.GetSRCHG().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetSRCHG2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.stageMeasManager.GetGCHG().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetGCHG2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetGCWLRefL().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetGCWLRefR().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.stageMeasManager.GetCMGHHG().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetCMGHHG2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetCMGHWLRefL().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.stageMeasManager.GetCMGHWLRefR().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.stageMeasManager.GetMghMethodCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #envCondManager
        self.envCondManager.GetLevelsCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetCloudCoverCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetPrecipCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetWindMagCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetWindmagCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetBatteryCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetGasSysCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetFeedCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetBpmrotCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetBpmrotCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetIntakeTimeCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetOrificeTimeCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetIntakeCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetOrificeCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetProgramCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetDataCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetDataPeriodFromPicker().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.envCondManager.GetDataPeriodToPicker().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #measResultsManager
        self.measResultsManager.GetTimeCtrlPanel1().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel1().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel2().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel2().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel3().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel3().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel4().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel4().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorRefEntry1().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetObservedVal1().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorVal1().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorRefEntry2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetObservedVal2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorVal2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorRefEntry3().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetObservedVal3().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorVal3().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorRefEntry4().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetObservedVal4().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetSensorVal4().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        self.measResultsManager.GetCol1Combo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetCol2Combo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetReset1Combo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetReset2Combo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel7().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel7().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel8().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel8().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel9().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel9().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel10().GetHourCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.measResultsManager.GetTimeCtrlPanel10().GetMinuteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #instrDepManager

        self.instrDepManager.GetDeploymentCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetPositionMethodCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetGaugeCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetLengthRadButBox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetPosRadButBox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetGauge1RadButBox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetGauge2RadButBox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetGaugeOtherTxt().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetSerialCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetInstrumentCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetManufactureCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetModelCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetFrequencyCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetFirmwareCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetSoftwareCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetNumOfPanelsScroll().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetFlowAngleCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetCoEffCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetMethodCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetMetresCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetWeightCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetWeightRadButBox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetWeightRadBut2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetWeightRadBut1().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetConfigCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetConfigCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetAdcpSetToClockCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetDiagTestCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetAdcpDepthCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetMagnDeclCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetControlConditionCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetDischRemarksCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetStageRemarksCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetStationHealthRemarksCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.instrDepManager.GetPicturedCkbox().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #partyInfoManager
        self.partyInfoManager.GetPartyCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.partyInfoManager.GetCompleteCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.partyInfoManager.GetReviewedCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #waterLevelRunManager
        self.waterLevelRunManager.GetRb1().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.waterLevelRunManager.GetRb2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.waterLevelRunManager.GetHgText().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.waterLevelRunManager.GetHgText2().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.waterLevelRunManager.GetCommentsCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #movingBoatMeasurementsManager
        self.movingBoatMeasurementsManager.GetBedMatCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetMbCB().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetMbCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetTrackRefCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetCompositeTrackCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetLeftBankCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetLeftBankOtherCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetRightBankCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetRightBankOtherCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetEdgeDistMmntCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetDepthRefCmbo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetVelocityTopCombo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetVelocityBottomCombo().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetVelocityExponentCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetDifferenceCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetMmntStartTimeCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetRawDischMeanCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetCorrMeanGHCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetStandDevMeanDischCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetMmntEndTimeCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetMbCorrAppCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetBaseCurveGHCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetCalcShiftBaseCurveCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetMmntMeanTimeCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetFinalDischCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetBaseCurveDischCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetDischDiffBaseCurveCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)
        self.movingBoatMeasurementsManager.GetCommentsCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)

        #frChecklistManager
        self.frChecklistManager.GetSiteNotesCtrl().Bind(wx.EVT_KILL_FOCUS, self.gui.OnAutoSave)


    def BindCorrectedMGH(self):
        self.disMeasManager.GetStartTimeCtrl().GetHourCtrl().Bind(wx.EVT_COMBOBOX, self.stageMeasManager.gui.CalculateAllMGH)
        self.disMeasManager.GetStartTimeCtrl().GetMinuteCtrl().Bind(wx.EVT_COMBOBOX, self.stageMeasManager.gui.CalculateAllMGH)
        self.disMeasManager.GetStartTimeCtrl().GetHourCtrl().Bind(wx.EVT_KEY_DOWN, self.stageMeasManager.gui.CalculateAllMGH)
        self.disMeasManager.GetStartTimeCtrl().GetMinuteCtrl().Bind(wx.EVT_KEY_DOWN, self.stageMeasManager.gui.CalculateAllMGH)

        self.disMeasManager.GetEndTimeCtrl().GetHourCtrl().Bind(wx.EVT_COMBOBOX, self.stageMeasManager.gui.CalculateAllMGH)
        self.disMeasManager.GetEndTimeCtrl().GetMinuteCtrl().Bind(wx.EVT_COMBOBOX, self.stageMeasManager.gui.CalculateAllMGH)
        self.disMeasManager.GetEndTimeCtrl().GetHourCtrl().Bind(wx.EVT_KEY_DOWN, self.stageMeasManager.gui.CalculateAllMGH)
        self.disMeasManager.GetEndTimeCtrl().GetMinuteCtrl().Bind(wx.EVT_KEY_DOWN, self.stageMeasManager.gui.CalculateAllMGH)




# This is for the icon
filename = 'myfilesname.type'
if hasattr(sys, '_MEIPASS'):
    # PyInstaller >= 1.6
    chdir(sys._MEIPASS)
    filename = join(sys._MEIPASS, filename)
elif '_MEIPASS2' in environ:
    # PyInstaller < 1.6 (tested on 1.5 only)
    chdir(environ['_MEIPASS2'])
    filename = join(environ['_MEIPASS2'], filename)
else:
    chdir(dirname(sys.argv[0]))
    filename = join(dirname(sys.argv[0]), filename)


def main():

        app = wx.App()
        ElectronicHydrometricSurveyNotes()
        app.MainLoop()


if __name__=='__main__':
    main()
