#!/usr/bin/env python
# -*- coding: UTF8 -*-
import sys, os, locale, StringIO
import wxversion
wxversion.select('2.8')
import wx, wx.lib.filebrowsebutton
import webbrowser
import ConfigParser

import vkontakte.auth
import vkontakte.friends
import vkontakte.groups
import vkontakte.graffiti

__author__= "Alexey Osipov -Lion-Simba- <simba@lerlan.ru>"
__version__= "0.7.1"

class LoginDlg(wx.Dialog):
    def __init__(self, parent, config):
        self._config = config
        # begin wxGlade: LoginDlg.__init__        
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE)
        self.sizerData_staticbox = wx.StaticBox(self, -1, u"Введите данные")
        self.label_2 = wx.StaticText(self, -1, "E-Mail:")
        self.txtEMail = wx.TextCtrl(self, -1, self._config.get('main', 'login'))
        self.label_1 = wx.StaticText(self, -1, u"Пароль:")
        self.txtPassword = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.btnOK = wx.Button(self, wx.ID_OK, u"Войти")        

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.Bind(wx.EVT_KEY_UP, self.OnEnter)        
        if len(self.txtEMail.GetValue()) == 0:
            self.txtEMail.SetFocus()
        else:
            self.txtPassword.SetFocus()
        
        self.SetEscapeId(wx.ID_CANCEL)
        
    def OnEnter(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:            
            self.EndModal(wx.ID_OK)
        elif event.GetKeyCode() == wx.WXK_NUMPAD_ENTER:
            self.EndModal(wx.ID_OK)
        elif event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
            
        event.Skip()

    def __set_properties(self):
        # begin wxGlade: LoginDlg.__set_properties
        self.SetTitle(u"Аутентификация")
        self.txtEMail.SetMinSize((187, 25))
        self.txtPassword.SetMinSize((187, 25))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: LoginDlg.__do_layout
        sizerData = wx.StaticBoxSizer(self.sizerData_staticbox, wx.VERTICAL)
        sizerPassword = wx.BoxSizer(wx.HORIZONTAL)
        sizerEMail = wx.BoxSizer(wx.HORIZONTAL)
        sizerEMail.Add(self.label_2, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizerEMail.Add(self.txtEMail, 2, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        sizerData.Add(sizerEMail, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        sizerPassword.Add(self.label_1, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizerPassword.Add(self.txtPassword, 2, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        sizerData.Add(sizerPassword, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        sizerData.Add(self.btnOK, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.SetSizer(sizerData)
        sizerData.Fit(self)
        self.Layout()
        # end wxGlade

# end of class LoginDlg

class SuccessDialog(wx.Dialog):
    def __init__(self, parent, url, sentas):
        # begin wxGlade: SuccessDialog.__init__
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE)
        if sentas == vkontakte.graffiti.SENDAS_JPEG:
            fmt = u"JPEG"
        elif sentas == vkontakte.graffiti.SENDAS_PNG:
            fmt = u"PNG"
        else:
            fmt = u"UNKNOWN"
        self.label_1 = wx.StaticText(self, -1, u"Графити загружено успешно в формате %s,\nвы можете увидеть его по ссылке:" % fmt, style=wx.ALIGN_CENTRE)
        #self.label_2 = wx.StaticText(self, -1, "http://vkontakte.ru/profile.php?id=12312412", style=wx.ALIGN_CENTRE)
        self.link_id = wx.NewId()
        self.link = wx.HyperlinkCtrl(self, self.link_id, url, url, style=wx.ALIGN_CENTRE)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        wx.EVT_HYPERLINK(self, self.link_id, self.OnLink)

    def __set_properties(self):
        # begin wxGlade: SuccessDialog.__set_properties
        self.SetTitle(u"В контакте")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SuccessDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        sizer_1.Add(self.link, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
    
    def OnLink(self, e):
        webbrowser.open(self.link.GetURL())
        self.EndModal(wx.ID_OK)

# end of class SuccessDialog

ID_EXIT = wx.NewId()
ID_ABOUT = wx.NewId()
ID_SEND = wx.NewId()
ID_LOGIN = wx.NewId()
ID_IMAGE = wx.NewId()
ID_TIMER = wx.NewId()
ID_RADIO = wx.NewId()
ID_CFG_SENDAS = wx.NewId()

class VkontakteMain(wx.Frame):
    def __init__(self, parent, id, caption, config):
        self._config = config
        # begin wxGlade: VkontakteMain.__init__        
        wx.Frame.__init__(self, parent, id, caption, style=wx.DEFAULT_FRAME_STYLE)
        self.notebook_1 = wx.Notebook(self, -1, style=0)
        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, -1)
        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, -1)
        self.sizerTarget_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"Адресат")
        self.sizerImage_staticbox = wx.StaticBox(self.notebook_1_pane_1, -1, u"Изображение")
        
        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()                
        wxglade_tmp_menu.Append(ID_LOGIN, u"Войти...", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendSeparator()        
        wxglade_tmp_menu.Append(ID_EXIT, u"Выход", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"В контакте")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(ID_ABOUT, u"О программе", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, u"Помощь")
        self.SetMenuBar(self.frame_1_menubar)
        # Menu Bar end
        self.imageBox = wx.StaticBitmap(self.notebook_1_pane_1, -1, wx.NullBitmap)
        #self.combo_box_1 = wx.ComboBox(self.notebook_1_pane_1, -1, choices=[], style=wx.CB_DROPDOWN)        
        self.browseImage = wx.lib.filebrowsebutton.FileBrowseButton(self.notebook_1_pane_1, ID_IMAGE, \
                                                                    buttonText=u"Обзор...", \
                                                                    labelText=u"Путь к файлу: ", \
                                                                    toolTip=u"Введите путь или щелкните Обзор", \
                                                                    dialogTitle=u"Выберите изображение", \
                                                                    fileMask="Изображения (*.bmp, *.jpg, *.png)|*.jpg;*.png;*.bmp;*.JPG;*.PNG;*.BMP;*.jpeg;*.JPEG|Все файлы (*.*)|*.*", \
                                                                    changeCallback=self.OnImageChanged, \
                                                                    startDirectory=self._config.get('main', 'last_path'))

        self.rbTargetType = wx.RadioBox(self.notebook_1_pane_1, ID_RADIO, u"Тип", choices=[u"Друг", u"Группа"], majorDimension=0, style=wx.RA_SPECIFY_COLS)
        self.listTarget = wx.ListBox(self.notebook_1_pane_1, -1, choices=[], style=wx.LB_SINGLE)
        self.txtImageInfo = wx.StaticText(self.notebook_1_pane_1)
        self.btnSend = wx.Button(self.notebook_1_pane_1, ID_SEND, u"Отправить")
        
        # config tab
        self.listCfgSendAs = wx.Choice(self.notebook_1_pane_2, ID_CFG_SENDAS, choices=[u"JPEG", u"PNG", u"PNG, затем JPEG"])
        self.listCfgSendAs.SetSelection(self._config.getint('graffiti', 'sendas'))
        self.txtCfgSendAs = wx.StaticText(self.notebook_1_pane_2, -1, u"Отправлять как")
        self.staticCfgGraffiti = wx.StaticBox(self.notebook_1_pane_2, -1, u"Граффити")
 
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        #resize to config
        w = self._config.getint('main', 'width');
        h = self._config.getint('main', 'height');
        if w > 0 and h > 0:
            self.SetSizeWH(w, h)

        # data fields                        
        self.imageBitmap = wx.EmptyBitmap(self.imageBox.GetMinWidth(), self.imageBox.GetMinHeight())
        self.timer = wx.Timer(self, ID_TIMER)
        self.vkontakte_auth = vkontakte.auth.VkontakteAuth()
        self.vkontakte_graffiti = vkontakte.graffiti.Graffiti(self.vkontakte_auth)
        self.vkontakte_friends = vkontakte.friends.FriendsFetcher(self.vkontakte_auth)
        self.vkontakte_groups = vkontakte.groups.GroupsFetcher(self.vkontakte_auth)
        # -------------
        
        self.DrawHelp()        
        
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_LOGIN, self.OnLogin)
        
        wx.EVT_TIMER(self, ID_TIMER, self.ReloadImage)
        
        wx.EVT_RADIOBOX(self, ID_RADIO, self.OnRadioGroupClicked)
        
        wx.EVT_CHOICE(self, ID_CFG_SENDAS, self.OnCfgSendAsChanged)
        
        wx.EVT_BUTTON(self, ID_SEND, self.OnSend)
        wx.EVT_CLOSE(self, self.OnClose)

        
        self.Show(True)
        
        self.dlgLogin = LoginDlg(self, self._config)
        if not self.DoLogin():
            self.Close()
            return
        
        self.FillList()        

    def __set_properties(self):
        # begin wxGlade: VkontakteMain.__set_properties
        self.SetTitle(u"Инструмент \"В контакте\"")
        self.imageBox.SetMinSize((vkontakte.graffiti.GRAFFITI_THUMB_SIZE_W, \
                                                  vkontakte.graffiti.GRAFFITI_THUMB_SIZE_H))
        #self.bmpImage.SetForegroundColour(wx.Colour(215, 215, 215))
        self.rbTargetType.SetSelection(0)
        self.listTarget.SetMinSize((400, 100))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: VkontakteMain.__do_layout
        
        #graffiti sizers
        sizerImage = wx.StaticBoxSizer(self.sizerImage_staticbox, wx.VERTICAL)        
        sizerImage.Add(self.imageBox, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)        
        sizerImage.Add(self.browseImage, 0, wx.EXPAND | wx.ALIGN_BOTTOM, 0)
                
        sizerTarget = wx.StaticBoxSizer(self.sizerTarget_staticbox, wx.VERTICAL)
        sizerTarget.Add(self.rbTargetType, 0, wx.EXPAND, 0)
        sizerTarget.Add(self.listTarget, 1, wx.EXPAND, 0)
        
        sizerImageInfo = wx.BoxSizer(wx.HORIZONTAL)
        sizerImageInfo.Add(self.txtImageInfo, 1, wx.ALIGN_CENTER_VERTICAL)
        sizerImageInfo.Add(self.btnSend, 0, wx.ALIGN_RIGHT)
        
        sizerGraffiti = wx.BoxSizer(wx.VERTICAL)
        sizerGraffiti.Add(sizerImage, 0, wx.EXPAND, 0)
        sizerGraffiti.Add(sizerTarget, 1, wx.EXPAND)                
        sizerGraffiti.Add(sizerImageInfo, 0, wx.EXPAND)

        #properties sizers
        sizerSendAs = wx.StaticBoxSizer(self.staticCfgGraffiti, wx.HORIZONTAL)
        sizerSendAs.Add(self.txtCfgSendAs, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        sizerSendAs.Add(self.listCfgSendAs, 1, wx.ALIGN_CENTER_VERTICAL)
                
        sizerProperties = wx.BoxSizer(wx.VERTICAL)
        sizerProperties.Add(sizerSendAs, 0, wx.EXPAND)

        #notebook setup
        self.notebook_1_pane_1.SetSizer(sizerGraffiti)
        self.notebook_1.AddPage(self.notebook_1_pane_1, u"Граффити")
        
        self.notebook_1_pane_2.SetSizer(sizerProperties)
        self.notebook_1.AddPage(self.notebook_1_pane_2, u"Настройки")

        #main sizer
        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerMain.Add(self.notebook_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizerMain)
        sizerMain.Fit(self)
        sizerMain.SetSizeHints(self)
        self.Layout()
        # end wxGlade
        
    def _size_fmt(self, num):
        for x in [u'байт',u'КиБ',u'МиБ',u'ГиБ',u'ТиБ']:
            if num < 1024.0:
                return u"%3.1f %s" % (num, x)
            num /= 1024.0

        
    def OnClose(self, event):
        (w, h) = self.GetSize()
        self._config.set('main', 'width', str(w))
        self._config.set('main', 'height', str(h))
        self.Destroy()
        
    def DrawHelp(self):
        dc = wx.MemoryDC(self.imageBitmap)
        self.backBrush = wx.Brush(self.GetBackgroundColour())
        dc.SetBackground(self.backBrush)        
        dc.Clear()
        dc.SetTextForeground(self.GetForegroundColour())
        dc.DrawLabel(u"Выберите изображение       ", \
                              wx.Rect(0, 0, self.imageBox.GetMinWidth(), self.imageBox.GetMinHeight()), \
                              wx.ALIGN_CENTER)        
        self.imageBox.SetBitmap(self.imageBitmap)
        self.imageBox.Refresh()

    def FillList(self, is_groups = False):
        self.listTarget.Clear()
        if is_groups:
            groups_list = self.vkontakte_groups.GetAcceptedGroups()
            groups_list.sort(key=lambda x: x[1].lower())
            for (gid, name) in groups_list:
                self.listTarget.Append(name, gid)
        else:
            self.listTarget.Append(u"Я сам(а)", self.vkontakte_auth.GetID())
            friends_list = self.vkontakte_friends.GetFriends()
            friends_list.sort(key=lambda x: x[1].lower())
            for (fid, name) in friends_list:
                self.listTarget.Append(name, fid)

    def OnRadioGroupClicked(self, e):
        if self.rbTargetType.GetSelection() == 0:
            self.FillList(False)
        elif self.rbTargetType.GetSelection() == 1:
            self.FillList(True)
        else:
            raise Exception("Unknown target type")
        
    def OnCfgSendAsChanged(self, e):
        oldsendas = self._config.getint('graffiti', 'sendas')
        selection = self.listCfgSendAs.GetSelection()
        if selection != oldsendas:
            self._config.set('graffiti', 'sendas', str(selection))
            self.ReloadImage(None)
        
    def OnSend(self, e):
        selection = self.listTarget.GetSelection()
        if selection == wx.NOT_FOUND:
            return
        
        if not self.vkontakte_graffiti.IsReady():
            return
        
        sel = self.rbTargetType.GetSelection()
        if sel == 0:
            target_type = 'friend'
        elif sel == 1:
            target_type = 'group'
        else:
            raise Exception("Unknown target type")
        
        target_id = self.listTarget.GetClientData(selection)
        
        try:
            (the_link, sentas) = self.vkontakte_graffiti.PostImage(target_type, target_id, self._config.getint('graffiti', 'sendas'))
        except Exception, e:
            errmsg = unicode(e)
            errstr = u"Загрузка возможно не удалась"
            if len(errmsg) > 0:
                errstr = errstr + u": " + errmsg
            else:
                errmsg = unicode(str(e))
                if len(errmsg) > 0:
                    errstr = errstr + u": " + errmsg
            dlg = wx.MessageDialog(self, errstr, u"Ошибка", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            return
        
        dlg = SuccessDialog(self, the_link, sentas)
        dlg.ShowModal()
    
    def OnImageChanged(self, e):
        dir = os.path.dirname(self.browseImage.GetValue())        
        if os.path.isdir(dir):            
            self._config.set('main', 'last_path', dir.encode(locale.getpreferredencoding()))
        self.timer.Stop()
        self.timer.Start(500, True)        

    def ReloadImage(self, e):
        if len(self.browseImage.GetValue()) == 0:
            self.DrawHelp();
            return
       
        try:
            self.vkontakte_graffiti.LoadImage(self.browseImage.GetValue())
        except vkontakte.graffiti.WrongImageTypeError, e:
            errDlg = wx.MessageDialog(self, u"Неподдерживаемый тип изображения", u"Ошибка", wx.OK | wx.ICON_ERROR)
            errDlg.ShowModal()
            return
        except Exception, e:
            errDlg = wx.MessageDialog(self, unicode(e), u"Ошибка", wx.OK | wx.ICON_ERROR)
            errDlg.ShowModal()
            return
        
        self.imageBox.SetBitmap(wx.BitmapFromImage(wx.ImageFromStream(StringIO.StringIO(self.vkontakte_graffiti.GetWallImageData()))))
        
        sendas = self._config.getint('graffiti', 'sendas')
        
        if sendas == vkontakte.graffiti.SENDAS_PNG_JPEG:
            self.txtImageInfo.SetLabel(u"Размер: PNG: %s, JPEG: %s" % (\
                                   self._size_fmt(len(self.vkontakte_graffiti.GetImageData(vkontakte.graffiti.SENDAS_PNG))), \
                                   self._size_fmt(len(self.vkontakte_graffiti.GetImageData(vkontakte.graffiti.SENDAS_JPEG))) \
                                   ))
        else:
            self.txtImageInfo.SetLabel(u"Размер: %s" % self._size_fmt(len(self.vkontakte_graffiti.GetImageData(sendas))))
        
        
    def OnLogin(self, e):
        self.DoLogin()
        
    def DoLogin(self):        
        while self.dlgLogin.ShowModal() == wx.ID_OK:
            result = self.vkontakte_auth.Login(self.dlgLogin.txtEMail.GetValue(), self.dlgLogin.txtPassword.GetValue())
            if result:                
                self._config.set('main', 'login', self.dlgLogin.txtEMail.GetValue())
                self.SetTitle(u"Инструмент \"В контакте\" - id%d" % self.vkontakte_auth.GetID())
                return True
            errDlg = wx.MessageDialog(self, u"Вход не удался", u"Ошибка", wx.OK | wx.ICON_ERROR)
            errDlg.ShowModal()
        return False
        
    
    def OnAbout(self,e):
        d= wx.MessageDialog( self, "Инструмент \"В контакте\"\n\n"
                            "Автор: Алексей Осипов <lion-simba@pridelands.ru>\n"
                            "Версия: %s\n"
                            "Лицензия: GPLv2\n\n"
                            "Посвящается моей подруге Наде. :)" % __version__,"Об инструменте", wx.OK)
        d.ShowModal() 
        d.Destroy()
        
    def OnExit(self,e):
        self.Close(True)

# end of class VkontakteMain

def main():
    #config reading
    #defaults:
    config_defaults = {'main': {'login': '', 'last_path': '', 'width': '-1', 'height': '-1'}, 'graffiti': {'sendas': '2'}}
    config_rel_path = '~/.vkontakte/config'
    config_path = os.path.expanduser(config_rel_path)
    config = ConfigParser.SafeConfigParser()
    config.read(config_path)
    
    for (section, defs) in config_defaults.items():    
        if not config.has_section(section):    
            config.add_section(section)        
        for (key, val) in defs.items():
            try:
                config.get(section, key)
            except:
                config.set(section, key, val)
            
    try:
        if not os.path.isdir(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path))
        conf_file = open(os.path.expanduser(config_rel_path), "w")
        config.write(conf_file)
        conf_file.close()
    except:
        pass
    
    app = wx.PySimpleApp()
    frame = VkontakteMain(None, wx.ID_ANY, "В контакте", config)
    app.MainLoop()
    
    #config writing
    
    try:
        conf_file = open(config_path, "w")
        config.write(conf_file)
        conf_file.close()
    except Exception, e:
        pass

if __name__ == '__main__':
    main()