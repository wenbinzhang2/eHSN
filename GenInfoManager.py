from GenInfoPanel import *


class GenInfoManager(object):
    def __init__(self, mode, gui, manager=None):

        self.gui = gui
        self.gui.manager = self
        self.manager = manager

        self.fieldMissingTitle = "Mandatory Field Missing"
        self.stnNameMissingMessage = "Station Name is missing"
        self.stnNumMissingMessage = "Station Number is missing"
        
        self.mode = mode
                                                            

        self.Init()

    def Init(self):
        if self.mode == "DEBUG":
            print "GenInfoControl"


    def updateNumbers(self, items):
        self.stnNumCmboPopup = ComboCtrlPopup()
        self.gui.stnNumCmbo.SetPopupControl(self.stnNumCmboPopup)
        self.stnNumCmboPopup.AddItems(items)

        self.gui.vbox.Layout()
        self.gui.Update()



    #vbox sizer
    def GetVbox(self):
        return self.gui.GetVbox()


    #Station Number Ctrl
    @property
    def stnNumCmbo(self):
        return self.gui.GetStnNumCmbo()

    @stnNumCmbo.setter
    def stnNumCmbo(self, stnNumCmbo):
        self.gui.SetStnNumCmbo(stnNumCmbo)

    #Date Ctrl
    @property
    def datePicker(self):
        return self.gui.GetDatePicker()

    @datePicker.setter
    def datePicker(self, datePicker):
        self.gui.SetDatePicker(datePicker)



    #Station Name Ctrl
    @property
    def stnName(self):
        return self.gui.GetStnName()

    @stnName.setter
    def stnName(self, stnName):
        self.gui.SetStnName(stnName)

    def GetStnNameCtrl(self):
        return self.gui.stnNameCtrl



    #Time Zone ComboBox
    @property
    def tzCmbo(self):
        return self.gui.GetTzCmbo()

    @tzCmbo.setter
    def tzCmbo(self, tzCmbo):
        self.gui.SetTzCmbo(tzCmbo)

    def mandatoryChecking(self):
        if (self.stnNumCmbo == ""):
            empty = wx.MessageDialog(None, self.stnNumMissingMessage, self.fieldMissingTitle, wx.OK)
            empty.ShowModal()
            return True
        # elif (self.stnNameCtrl == ""):
        #     empty = wx.MessageDialog(None, self.stnNameMissingMessage, self.fieldMissingTitle, wx.OK)
        #     empty.ShowModal()
        #     return True
        else:
            return False


    def GetStnNumCmboCtrl(self):
        return self.gui.GetStnNumCmboCtrl()

    def GetStnNumCmboCtrl(self):
        return self.gui.GetStnNumCmboCtrl()

    def GetStnNumCmboCtrl(self):
        return self.gui.GetStnNumCmboCtrl()

    def GetStnNumCmboCtrl(self):
        return self.gui.GetStnNumCmboCtrl()

def main():
    app = wx.App()

    frame = wx.Frame(None)
    GenInfoManager("DEBUG", GenInfoPanel("DEBUG", frame))

    frame.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()
