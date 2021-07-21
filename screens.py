from helpers import onFail, getPath
import platform
import wx
import os
import socket
import ssl
import sys


class setup(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Cyber Essentials at Home Setup")
        self.drawWindow()
        self.initUI()

    def drawWindow(self):
        self.panel = wx.Panel(self)
        self.Show(True)

    def initUI(self):
        vert = wx.BoxSizer(wx.VERTICAL)
        label = " Please enter your unique code that was sent to you in the email with the download link: \n"
        error_label = "Error: Invalid code! Check that this is right and if so, please try again later."
        mac_label = " Make sure to click the notification in the top right and toggle 'Allow notifications' when prompted to complete the setup. "
        vert.Add(wx.StaticText(self.panel, label=label), 0, wx.ALIGN_CENTER, 0)
        self.answerBox = wx.TextCtrl(self.panel)
        vert.Add(self.answerBox, 0, wx.ALIGN_CENTER, 0)
        vert.Add(wx.StaticText(self.panel, label=""), 0, wx.ALIGN_CENTER, 0)
        self.submitButton = wx.Button(self.panel, -1, "Submit")
        vert.Add(self.submitButton, 0, wx.ALIGN_CENTER, 0)
        self.Bind(wx.EVT_BUTTON, self.onSubmit, id=self.submitButton.GetId())
        self.error = wx.StaticText(self.panel, label=error_label)
        if platform.system() == "Darwin":
            self.error.SetLabel(mac_label)
        vert.Add(self.error, 0, wx.ALIGN_CENTER, 0)
        self.panel.SetSizer(vert)
        vert.Fit(self)
        if platform.system() != "Darwin":
            self.error.SetLabel("")

    def onSubmit(self, e):
        unique = self.answerBox.GetValue()
        if validate(unique):

            if platform.system() == "Darwin":
                import asyncio
                asyncio.run(testNotif())

            self.error.SetLabel("")
            os.mkdir(getPath("DO_NOT_DELETE"))
            f = open(getPath("DO_NOT_DELETE/id.txt"), 'w')
            f.write(unique)
            f.close()
            self.Close()
        else:
            self.error.SetForegroundColour(wx.Colour(255, 0, 0))
            self.error.SetLabel("Error: Invalid code! Check that this is right and if so, please try again later.")


async def testNotif():
    from desktop_notifier import DesktopNotifier
    notif = DesktopNotifier()
    if not await notif.has_authorisation():
        await notif.request_authorisation()


def validate(unique):
    if len(unique) != 7:
        return False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    s.connect((socket.gethostbyname("app.markturner.uk"), 1701))
    s = context.wrap_socket(s, server_hostname="app.markturner.uk")
    s.send(str("SYN " + unique).encode())
    valid = s.recv(4096).decode() == "ACK " + unique
    s.close()
    return valid


def wxFirstRun():
    try:
        print("Showing dialog...", end='\t')
        app = wx.App()
        setup()
        app.MainLoop()
        sys.exit(0)
    except Exception as e:
        onFail(e, critical=True)
