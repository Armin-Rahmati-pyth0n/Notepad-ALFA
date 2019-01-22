

import sys, os
import configparser as parser

from PyQt5.QtWidgets import QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QDesktopWidget, QMainWindow, QAction, QMenu, qApp, QTextEdit, QLabel, QVBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("UTF-8"))
CONFIG_FILE_PATH = "notepad.ini"

class Notepad(QtWidgets.QMainWindow):
    def __init__(self):
        self.judgeConfigFile()

        self.clipboard = QtWidgets.QApplication.clipboard()

        self.lastSearchText = ""

        self.lastReplaceSearchText = ""

        self.reset = False

        self.config = parser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH)

        QtWidgets.QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Notepad-ALFA")
        self.setWindowIcon(QtGui.QIcon(" notepad.png"))

        self.initEditText()

        self.createActions()
        self.createStatusBar()
        self.createMenubars()
        self.createToolBars()

        self.readSettings()

        self.text.document().contentsChanged.connect(self.documentWasModified)

        self.resize(600,600)
        self.center()
        self.setCurrentFile('')
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        
    def initEditText(self):
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.customContextMenu)
        self.setCentralWidget(self.text)

    def customContextMenu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.undoAction)
        menu.addSeparator()
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addAction(self.deleteAction)
        menu.addSeparator()
        menu.addAction(self.selectAllAction)
        menu.exec_(QtGui.QCursor.pos())

        return menu

    def documentWasModified(self):
        self.setWindowModified(self.text.document().isModified())
        if "" != self.text.toPlainText():
            self.findAction.setEnabled(True)
            self.findNextAction.setEnabled(True)
        else:
            self.findAction.setEnabled(False)
            self.findNextAction.setEnabled(False)

    def readSettings(self):
        width = getConfig(self.config, "Display", "width", "1000")
        height = getConfig(self.config, "Display", "height", "600")
        size = QtCore.QSize(int(width), int(height))

        screen = QtWidgets.QDesktopWidget().screenGeometry()
        pos_x = getConfig(self.config, "Display", "x", (screen.width() - 1000) // 2)
        pos_y = getConfig(self.config, "Display", "y", (screen.height() - 600) // 2)
        pos = QtCore.QPoint(int(pos_x), int(pos_y))

        toolbar = getConfig(self.config, "Display", "toolbar", "True")

        wrapMode = getConfig(self.config, "TextEdit", "wrapmode", "True")

        fontFamile = getConfig(self.config, "TextEdit", "font", "Consolas")
        fontSize = getConfig(self.config, "TextEdit", "size", 14)
        fonts = QtGui.QFont(fontFamile, int(fontSize))

        if "True" == wrapMode:
            pass

        if "True" == toolbar:
            self.toolBar.show()
            self.toolBarAction.setIcon(QtGui.QIcon(" check.png"))
        else:
            self.toolBar.hide()
            self.toolBarAction.setIcon(QtGui.QIcon(" check_no.png"))

        self.resize(size)
        self.move(pos)

        self.text.setFont(fonts)

    def resetSettings(self):
        writeConfig(self.config, "Display", "width", "1000")
        writeConfig(self.config, "Display", "height", "600")
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        writeConfig(self.config, "Display", "x", str((screen.width() - 1000) // 2))
        writeConfig(self.config, "Display", "y", str((screen.height() - 600) // 2))
        writeConfig(self.config, "Display", "toolbar", "True")
        writeConfig(self.config, "TextEdit", "wrapmode", "True")
        writeConfig(self.config, "TextEdit", "font", "Consolas")
        writeConfig(self.config, "TextEdit", "size", "14")

        self.config.write(open(CONFIG_FILE_PATH, "w"))

        self.reset = True
        self.close()

    def writeSettings(self):
        writeConfig(self.config, "Display", "height", str(self.size().height()))
        writeConfig(self.config, "Display", "width", str(self.size().width()))
        writeConfig(self.config, "Display", "x", str(self.pos().x()))
        writeConfig(self.config, "Display", "y", str(self.pos().y()))
        writeConfig(self.config, "Display", "toolbar", str(not self.toolBar.isHidden()))
        writeConfig(self.config, "TextEdit", "wrapmode",
                    str(self.text.lineWrapMode() == QtWidgets.QPlainTextEdit.WidgetWidth))
        writeConfig(self.config, "TextEdit", "font", self.text.font().family())
        writeConfig(self.config, "TextEdit", "size", str(self.text.font().pointSize()))

        self.config.write(open(CONFIG_FILE_PATH, "w"))

    def judgeConfigFile(self):
        if not os.path.exists(CONFIG_FILE_PATH):
            f = open(CONFIG_FILE_PATH, mode="w", encoding="UTF-8")
            f.close()

    def createActions(self):
        self.newAction = QtWidgets.QAction(QtGui.QIcon('new.png'), "جديد", self,
                                           shortcut=QtGui.QKeySequence.New, statusTip="صفحه جديد",
                                           triggered=self.newFile)

        self.openAction = QtWidgets.QAction(QtGui.QIcon('open.png'), "باز کردن",
                                            self, shortcut=QtGui.QKeySequence.Open,
                                            statusTip="باز کردن فايل ", triggered=self.openFileEvent)

        self.saveAction = QtWidgets.QAction(QtGui.QIcon('save.png'), "ذخيره", self,
                                            shortcut=QtGui.QKeySequence.Save,
                                            statusTip="ذخيره فايل", triggered=self.save)

        self.saveAsAction = QtWidgets.QAction(QtGui.QIcon('save.png'), "ذخيره به", self,
                                              shortcut=QtGui.QKeySequence.SaveAs,
                                              statusTip="... ذخيره به عنوان",
                                              triggered=self.saveAs)

        self.printAction = QtWidgets.QAction(QtGui.QIcon('print.ico'), "چاپ", self,
                                             shortcut=QtGui.QKeySequence.Print,
                                             statusTip="چاپ فايل",
                                             triggered=self.printText)

        self.exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), "خارج", self, shortcut="Ctrl+Q",
                                            statusTip="... بيرون رفتن", triggered=self.close)

        self.undoAction = QtWidgets.QAction(QtGui.QIcon('undo.png'), "لغو", self,
                                            shortcut=QtGui.QKeySequence.Undo,
                                            statusTip="لغو کردن",
                                            triggered=self.text.undo)

        self.cutAction = QtWidgets.QAction(QtGui.QIcon('cut.png'), "برش", self,
                                           shortcut=QtGui.QKeySequence.Cut,
                                           statusTip="برش متن",
                                           triggered=self.text.cut)

        self.copyAction = QtWidgets.QAction(QtGui.QIcon('copy.png'), "کپي", self,
                                            shortcut=QtGui.QKeySequence.Copy,
                                            statusTip="کپي کردن",
                                            triggered=self.text.copy)

        self.pasteAction = QtWidgets.QAction(QtGui.QIcon('paste.png'), "چسباندن", self,
                                             shortcut=QtGui.QKeySequence.Paste,
                                             statusTip="چسباندن متن",
                                             triggered=self.text.paste)

        self.clearAction = QtWidgets.QAction(QtGui.QIcon('clear.ico'), "پاک کردن", self,
                                             statusTip="پاک کردن حافظه کپي",
                                             triggered=self.clearClipboard)

        self.deleteAction = QtWidgets.QAction(QtGui.QIcon("delete.png"), "حذف", self,
                                              statusTip="حذف موارد انتخاب شده",
                                              triggered=self.delete)

        self.findAction = QtWidgets.QAction(QtGui.QIcon("find.png"), "يافتن", self,
                                            statusTip="جست و جو براي يافتن", triggered=self.findText, shortcut=QtGui.QKeySequence.Find)

        self.findNextAction = QtWidgets.QAction(QtGui.QIcon("find.png"), "بعدی را پیدا کنید", self,
                                                statusTip="متن را پیدا کنید", triggered=self.findNextText,
                                                shortcut=QtGui.QKeySequence.FindNext)

        self.replaceAction = QtWidgets.QAction(QtGui.QIcon("replace.png"), "جاي گزيني", self,
                                               statusTip="... جايگزين کردن", triggered=self.replaceText,
                                               shortcut=QtGui.QKeySequence.Replace)

        self.selectAllAction = QtWidgets.QAction(QtGui.QIcon('selectAll.png'), "انتخاب همه", self,
                                                 shortcut=QtGui.QKeySequence.SelectAll,
                                                 statusTip="انتخاب همه متن",
                                                 triggered=self.text.selectAll)

        self.dateAction = QtWidgets.QAction(QtGui.QIcon("date.png"), "تاريخ :-)", self, shortcut="F5",
                                            statusTip="... چاپ تاريخ",
                                            triggered=self.dateEvent)

        self.fontAction = QtWidgets.QAction(QtGui.QIcon("font.png"), "فونت", self,
                                            statusTip="انتخاب فونت و سايز", triggered=self.setFont_)

        self.toolBarAction = QtWidgets.QAction(QtGui.QIcon("check.png"), "جعبه ابزار", self,
                                               statusTip="جعبه ابزار",
                                               triggered=self.toggleToolBar)

        self.aboutAction = QtWidgets.QAction(QtGui.QIcon("about.png"), "درباره", self, triggered=self.about)

        self.aboutQtAction = QtWidgets.QAction(QtGui.QIcon("qt.png"), "درباره qt", self,
                                               triggered=QtWidgets.QApplication.instance().aboutQt)

        self.undoAction.setEnabled(False)
        self.cutAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.deleteAction.setEnabled(False)
        if "" == self.clipboard.text():
            self.pasteAction.setEnabled(False)
            self.clearAction.setEnabled(False)
        if "" == self.text.toPlainText():
            self.findAction.setEnabled(False)
            self.findNextAction.setEnabled(False)

        self.text.undoAvailable.connect(self.undoAction.setEnabled)
        self.text.copyAvailable.connect(self.cutAction.setEnabled)
        self.text.copyAvailable.connect(self.copyAction.setEnabled)
        self.text.copyAvailable.connect(self.deleteAction.setEnabled)

        self.clipboard.dataChanged.connect(self.enabledSomeActionByClipboard)

    def enabledSomeActionByClipboard(self):
        if ("" != self.clipboard.text()):
            self.pasteAction.setEnabled(True)
            self.clearAction.setEnabled(True)

    def clearClipboard(self):
        self.clipboard.clear()
        self.pasteAction.setEnabled(False)
        self.clearAction.setEnabled(False)

    def createStatusBar(self):
        self.statusBar().showMessage("آماده است")

    def createMenubars(self):
        file = self.menuBar().addMenu("پرونده")
        file.addAction(self.newAction)
        file.addAction(self.openAction)
        file.addAction(self.saveAction)
        file.addAction(self.saveAsAction)
        file.addSeparator()
        file.addAction(self.printAction)
        file.addSeparator()
        file.addAction(self.exitAction)

        edit = self.menuBar().addMenu("ويرايش")
        edit.addAction(self.undoAction)
        edit.addSeparator()
        edit.addAction(self.cutAction)
        edit.addAction(self.copyAction)
        edit.addAction(self.pasteAction)
        edit.addAction(self.clearAction)
        edit.addAction(self.deleteAction)
        edit.addSeparator()
        edit.addAction(self.findAction)
        edit.addAction(self.findNextAction)
        edit.addAction(self.replaceAction)
        edit.addSeparator()
        edit.addAction(self.selectAllAction)
        edit.addAction(self.dateAction)

        style = self.menuBar().addMenu("فونت")

        style.addAction(self.fontAction)

        view = self.menuBar().addMenu("مشاهده")
        view.addAction(self.toolBarAction)


        help = self.menuBar().addMenu("راهنما")
        help.addAction(self.aboutAction)
        help.addAction(self.aboutQtAction)

    def createToolBars(self):
        self.toolBar = self.addToolBar("")
        self.toolBar.addAction(self.newAction)
        self.toolBar.addAction(self.openAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.cutAction)
        self.toolBar.addAction(self.copyAction)
        self.toolBar.addAction(self.pasteAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.clearAction)

    def newFile(self):
        if self.maybeSave():
            self.text.clear()

    def maybeSave(self):
        if self.text.document().isModified():
            ret = self.tip()

            if 0 == ret:
                return self.save()

            if 2 == ret:
                return False

        return True

    def openFileEvent(self):
        if self.maybeSave():
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self)
            file = QtCore.QFile(fileName)
            if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                QtWidgets.QMessageBox.warning(self, "دفترچه یادداشت",
                                              "فايل%sقابل خواندن نيست!:\n%s." % (fileName, file.errorString()))
                return

            inf = QtCore.QTextStream(file)
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.text.setPlainText(inf.readAll())
            QtWidgets.QApplication.restoreOverrideCursor()

            self.setCurrentFile(fileName)
            self.statusBar().showMessage("فایل با موفقیت خوانده شده", 2000)

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.text.document().setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'Notepad'

        self.setWindowTitle("%s[*] - ALFA" % shownName)

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)
        else:
            return self.saveAs()

    def saveAs(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)

        return False

    def saveFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self, "دفترچه یادداشت",
                                          "پرونده %s را نمیتوان نوشت!\n%s" % (fileName, file.errorString()))
            return False

        outf = QtCore.QTextStream(file)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outf << self.text.toPlainText()
        QtWidgets.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("به صورت فایل ضمیمه شده", 2000)
        return True

    def closeEvent(self, event):
        if not self.maybeSave():
            event.ignore()
        else:
            if not self.reset:
                self.writeSettings()
            event.accept()

    def tip(self, title="دفترچه یادداشت", content="پرونده اصلاح شده است，آیا ذخیره شود؟"):
        alertBox = QtWidgets.QMessageBox(self)
        saveButton = alertBox.addButton("ذخیره شود", QtWidgets.QMessageBox.ActionRole)
        unSaveButton = alertBox.addButton("ذخیره نشود", QtWidgets.QMessageBox.ActionRole)
        cancelButton = alertBox.addButton("لغو", QtWidgets.QMessageBox.ActionRole)

        alertBox.setWindowTitle(title)
        alertBox.setText(content)
        alertBox.exec_()
        button = alertBox.clickedButton()

        if saveButton == button:
            return 0
        elif unSaveButton == button:
            return 1
        elif cancelButton == button:
            return 2
        else:
            return -1;

    def dateEvent(self):
        current = QtCore.QDateTime.currentDateTime();
        current = current.toString("yyyy-MM-dd hh:mm");
        self.text.insertPlainText(current)

    def printText(self):
        document = self.text.document()
        printer = QPrinter()

        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return

        document.print_(printer)

        self.statusBar().showMessage("打印成功", 2000)

    def delete(self):
        cursor = self.text.textCursor()
        if not cursor.isNull():
            cursor.removeSelectedText()
            self.statusBar().showMessage("حذف شد با موفقیت", 2000)

    def findText(self):
        self.displayFindDialog()

    def findNextText(self):
        if "" == self.lastSearchText:
            self.displayFindDialog()
        else:
            self.searchText()

    def displayFindDialog(self):
        self.findDialog = QtWidgets.QDialog(self)

        label = QtWidgets.QLabel("محتوا را پیدا کنید:")
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText(self.lastSearchText)
        label.setBuddy(self.lineEdit)

        self.findButton = QtWidgets.QPushButton("بعدی را پیدا کنید")
        self.findButton.setDefault(True)
        self.findButton.clicked.connect(self.searchText)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(self.findButton, QtWidgets.QDialogButtonBox.ActionRole)

        topLeftLayout = QtWidgets.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.lineEdit)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        mainLayout.setRowStretch(2, 1)
        self.findDialog.setLayout(mainLayout)

        self.findDialog.setWindowTitle("پیدا کردن")
        self.findDialog.show()

    def searchText(self):
        cursor = self.text.textCursor()
        findIndex = cursor.anchor()
        text = self.lineEdit.text()
        content = self.text.toPlainText()
        length = len(text)

        self.lastSearchText = text
        index = content.find(text, findIndex)

        if -1 == index:
            errorDialog = QtWidgets.QMessageBox(self)
            errorDialog.addButton("لغو", QtWidgets.QMessageBox.ActionRole)

            errorDialog.setWindowTitle("دفترچه یادداشت")
            errorDialog.setText("نمی توان پیدا کرد\"%s\"." % text)
            errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
            errorDialog.exec_()
        else:
            start = index

            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + length)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, length)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceText(self):
        replaceDialog = QtWidgets.QDialog(self)

        replaceLabel = QtWidgets.QLabel("محتوای جایگزین:")
        self.replaceText = QtWidgets.QLineEdit()
        self.replaceText.setText(self.lastReplaceSearchText)
        replaceLabel.setBuddy(self.replaceText)

        replaceToLabel = QtWidgets.QLabel("با جایگزین کردن  :")
        self.replaceToText = QtWidgets.QLineEdit()
        replaceToLabel.setBuddy(self.replaceToText)

        findNextButton = QtWidgets.QPushButton("بعدی را پیدا کنید")
        findNextButton.setDefault(True)
        replaceButton = QtWidgets.QPushButton("جایگزین کنید")
        replaceAllButton = QtWidgets.QPushButton("همه را جایگزین کنید")
        cancelAllButton = QtWidgets.QPushButton("لغو")

        findNextButton.clicked.connect(lambda: self.replaceOrSearch(False))
        cancelAllButton.clicked.connect(replaceDialog.close)
        replaceButton.clicked.connect(lambda: self.replaceOrSearch(True))
        replaceAllButton.clicked.connect(self.replaceAllText)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(findNextButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(replaceButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(replaceAllButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelAllButton, QtWidgets.QDialogButtonBox.ActionRole)

        topLeftLayout = QtWidgets.QHBoxLayout()

        topLeftLayout.addWidget(replaceLabel)
        topLeftLayout.addWidget(self.replaceText)

        topLeftLayout2 = QtWidgets.QHBoxLayout()
        topLeftLayout2.addWidget(replaceToLabel)
        topLeftLayout2.addWidget(self.replaceToText)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addLayout(topLeftLayout2)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        mainLayout.setRowStretch(2, 1)
        replaceDialog.setLayout(mainLayout)

        replaceDialog.setWindowTitle("جایگزین کنید")
        replaceDialog.show()

    def replaceOrSearch(self, isReplace):

        cursor = self.text.textCursor()
        findIndex = cursor.anchor()
        text = self.replaceText.text()
        content = self.text.toPlainText()
        length = len(text)
        index = content.find(text, findIndex)
        self.lastReplaceSearchText = text
        if -1 == index:
            errorDialog = QtWidgets.QMessageBox(self)
            errorDialog.addButton("لغو", QtWidgets.QMessageBox.ActionRole)

            errorDialog.setWindowTitle("دفترچه یادداشت")
            errorDialog.setText("نمی توان پیدا کرد\"%s\"." % text)
            errorDialog.setIcon(QtWidgets.QMessageBox.Critical)
            errorDialog.exec_()
        else:
            start = index
            if isReplace:
                toReplaceText = self.replaceToText.text()
                prefix = content[0:start]
                postfix = content[start + length:]
                newText = prefix + toReplaceText + postfix
                self.text.setPlainText(newText)
                length = len(toReplaceText)
                self.text.document().setModified(True)

            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + length)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, length)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceAllText(self):
        text = self.replaceText.text()
        content = self.text.toPlainText()
        toReplaceText = self.replaceToText.text()
        content = content.replace(text, toReplaceText)
        self.text.setPlainText(content)
        self.text.document().setModified(True)


    def toggleToolBar(self):
        if self.toolBar.isHidden():
            self.toolBar.show()
            self.toolBarAction.setIcon(QtGui.QIcon(" check.png"))
        else:
            self.toolBar.hide()
            self.toolBarAction.setIcon(QtGui.QIcon(" check_no.png"))

    def setFont_(self):
        font, ok = QtWidgets.QFontDialog.getFont(QtGui.QFont(self.text.toPlainText()), self)
        if ok:
            self.text.setFont(font)

    def about(self):
        QtWidgets.QMessageBox.about(self, "درباره دفترچه یادداشت",
                                    "آلفا نوت پد، یک نوت پد نیمه حرفه است که در سال 2019 توسط آرمین رحمتی طراحی و تولید شده است\n"
                                    "نیرو گرفته از زبان قدرتمند پایتون و کتابخانه PyQt_5.4.1\n"
                                    "\n************************************"
                                    "\nطراح و برنامه نویس : آرمین رحمتی\n"
                                    "سال تولید : 2019"
                                    "\nتماس با من : a.arminrahmati@gmail.com or mr.arminrahmati@gmail.com"
                                    "\n************************************\n"
                                    "")


def getConfig(config, selection, option, default=""):
    if config is None:
        return default
    else:
        try:
            return config.get(selection, option)
        except:
            return default


def writeConfig(config, selection, option, value):
    if not config.has_section(selection):
        config.add_section(selection)

    config.set(selection, option, value)

app = QtWidgets.QApplication(sys.argv)
notepad = Notepad()
notepad.show()
app.exec_()
