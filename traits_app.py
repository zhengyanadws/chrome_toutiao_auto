
#-*- coding: utf-8 -*-
#!/usr/bin/env python

import wx

from traits_frame import MainFrame

class TraitsApp(wx.App):
    main_frame = None

    def OnInit(self):
        main_frame = MainFrame()

        main_frame.Show(True)

        return True


