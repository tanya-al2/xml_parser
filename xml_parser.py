# coding: utf-8

from shutil import copyfile
import codecs
import operator
import os
import re
import subprocess
import sys
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from lxml import etree
from re import *


class Trey(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(u'Настройки')
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # работа с треем
        close_action = QAction(u'Закрыть', self)
        close_action.triggered.connect(self.close_from_menu)
        activate_action = QAction(u'Развернуть', self)
        activate_action.triggered.connect(self.activate_window)
        tray_menu = QMenu(u'...')
        tray_menu.addAction(close_action)
        tray_menu.addAction(activate_action)
        self.close_action_from_menu = False

        self.tray_icon = QSystemTrayIcon(QIcon(u'xmlParser.ico'), self)
        self.tray_icon.show()
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.activate_window)

        # окно настроек
        # Добавляем виджеты
        # Сами виджеты
        self.mainWindows_layout = QFormLayout()
        # добавляем в окно вкладки из конфигурационных файлов
        self.configVariables = {}
        for variable in self.searchPattern('(.*)=(.*)', self.readfile(u'utility.conf'), u'параметры'):  # найти в конфигах
            self.configVariables[variable[0]] = None

        for key in self.configVariables:
            self.configVariables[key] = QComboBox()
            self.configVariables[key].setMinimumContentsLength(15)
            self.configVariables[key].addItems(
                self.searchPattern('({0}=)(.*)'.format(key), self.readfile(u'utility.conf'), key, True, 2).split())
            self.mainWindows_layout.addRow(key, self.configVariables[key])

        # Добавляю кнопку для установки параметров в утилите автоподписи
        self.setupConfig = QPushButton(u'Установить параметры в утилите')
        self.mainWindows_layout.addRow(self.setupConfig)
        self.setupConfig.clicked.connect(self.readAndPastConfigfile, True)

        # окно с которого все началось
        # self.checkboxeslayout = QGroupBox()
        # Добавляю чек-боксы к окну
        self.putChangedXml_checkBox = QCheckBox(u'загрузить xml')
        self.changeTextInTag_checkBox = QCheckBox(u'поменять текст')
        self.changeBySymbol_checkbox = QCheckBox(u'добавить по одному символу')
        # Создаю layout с чекбоксами
        self.layoutWithCheckBoxes_boxLayout = QVBoxLayout()
        self.layoutWithCheckBoxes_boxLayout.addWidget(self.putChangedXml_checkBox)
        self.layoutWithCheckBoxes_boxLayout.addWidget(self.changeTextInTag_checkBox)
        self.layoutWithCheckBoxes_boxLayout.addWidget(self.changeBySymbol_checkbox)

        # Создаю таблицу для приема символов и тагов
        self.changeTagContent_table = QTableWidget(0, 2, self)
        self.changeTagContent_table.setHorizontalHeaderLabels([u'текст/символы', 'tags'])
        for columnumber, width in enumerate((300, 250)):
            self.changeTagContent_table.horizontalHeader().resizeSection(columnumber, width)
        # Добавляю кнопки для управления таблицей
        self.addRow_changeXml_button = QPushButton(u'добавить строку')
        self.removeRow_changeXml_button = QPushButton(u'удалить строку')
        self.addRow_changeXml_button.clicked.connect(
            lambda: self.changeTagContent_table.insertRow(self.changeTagContent_table.rowCount()))
        self.removeRow_changeXml_button.clicked.connect(
            lambda: self.changeTagContent_table.removeRow(self.changeTagContent_table.currentRow()))

        # Кнопка!
        self.startChangeXml_button = QPushButton(u'жми!')
        self.startChangeXml_button.clicked.connect(self.changeTagContant)  # start_Threading

        # Создаю layout кнопками для таблицы
        self.buttons_changeXml_boxLayout = QHBoxLayout()
        self.buttons_changeXml_boxLayout.addWidget(self.startChangeXml_button)
        self.buttons_changeXml_boxLayout.addWidget(self.addRow_changeXml_button)
        self.buttons_changeXml_boxLayout.addWidget(self.removeRow_changeXml_button)

        # | self.changeTagContent_table.rowCount()-1

        # Создаю layout с таблицей для приема символов и тагов
        self.table_changeXml_boxLayout = QVBoxLayout()
        self.table_changeXml_boxLayout.addWidget(self.changeTagContent_table)

        # Создаю layout с таблицей, чекерами и кнопками
        self.total_changeXml_boxLayout = QHBoxLayout()
        self.total_changeXml_boxLayout.addLayout(self.layoutWithCheckBoxes_boxLayout)
        self.total_changeXml_boxLayout.addLayout(self.buttons_changeXml_boxLayout)
        self.table_changeXml_boxLayout.addLayout(self.total_changeXml_boxLayout)

        # Добавляю все в главное окно
        # Создаю виджет с вкладкой для установки конфигов в утилите автоподписи
        self.config_wiget = QWidget()
        self.config_wiget.setLayout(self.mainWindows_layout)

        # Создаю виджет с вкладкой для заметы содержания вкладок
        self.changeXml_wiget = QWidget()
        self.changeXml_wiget.setLayout(self.table_changeXml_boxLayout)

        # главное окно
        main_widget = QTabWidget(self)
        # добавляем вкладки
        main_widget.addTab(self.config_wiget, u'Установка настроеек для утилиты автоподписи')
        main_widget.addTab(self.changeXml_wiget, u'Окно для замены текста в тагах')

    def setConfigVariables(self):
        self.configVariables.clear()

    def singAndPutXmlToServer(self):

        if not self.isHidden():
            self.show()

        for path in [os.path.dirname(self.configVariables['pathToSingmessage'].currentText()),
                     os.path.dirname(self.configVariables['pathToSingmessage'].currentText())]:
            for fileitem in os.listdir(path):
                print(path)
                print(fileitem)
                os.remove(fileitem)

        for fileitem in os.listdir('./out'):
            print(fileitem)
            copyfile(fileitem, os.path.join(self.configVariables['pathToSingmessage'].currentText(), 'in', fileitem))
            #subprocess.Popen(os.path.join(self.configVariables['pathToSingmessage'].currentText(),
       #                                   'run.sh')).wait()  # .communicate()

        for fileitem in os.listdir(os.path.join(self.configVariables['pathToSingmessage'].currentText(), 'out')):
            print(fileitem)
            copyfile(fileitem,
                     os.path.join(os.path.join(self.configVariables['pathToPutmessage'].currentText(), 'resources'),
                                  fileitem))
        #subprocess.Popen(
      #      os.path.join(self.configVariables['pathToPutmessage'].currentText(), 'run.sh')).wait()  # .communicate()
        self.hide()
        self.tray_icon.showMessage(u'файл отправлен', u'файлы отправлены')

    def readAndPastConfigfile(self, pastconfig=False):
        path_to_config = os.path.join(self.configVariables['pathToPutmessage'].currentText(), 'conf.properties')
        configs = self.readfile(path_to_config)

        if pastconfig:
            for key in self.configVariables:
                configs = configs.replace(self.searchPattern('{0}=.*'.format(key), configs, key, True, 0),
                                          '{0}='.format(key) + self.configVariables[key].currentText(), key)
            self.whriteFile(path_to_config, configs)
            self.tray_icon.showMessage(u'Значения установлены', u'значения установлены')

    def getTextFromTable(self, row, column):
        return self.changeTagContent_table.item(row, column).text()

    def changeTagContant(self):
        past_text = False
        past_text_by_symbol = False
        put_file = False
        if self.changeTextInTag_checkBox.isChecked():
            past_text = True
        if self.changeBySymbol_checkbox.isChecked():
            past_text_by_symbol = True
        if self.putChangedXml_checkBox.isChecked():
            put_file = True
        list_of_files_for_change = os.listdir('./in')
        tag_or_text = {'tag': 1, 'text': 0}

        self.tray_icon.showMessage(u'будут подменены следующие сообщения', ''.join(list_of_files_for_change))
        # Считываю xml-файл
        for xml in list_of_files_for_change:
            xml_text = self.readfile(os.path.join('./in', xml))
            # цикл по всем строкам в таблице
            row_count = self.changeTagContent_table.rowCount()
            for row in range(0, row_count):
                # Получаю текст, который будет подставлен в xml
                if past_text:
                    text_list = [self.getTextFromTable(row, tag_or_text['text'])]
                else:
                    text_list = self.getTextFromTable(row, tag_or_text['text'])

                # Цикл по всем тэгам из строки с тэгами
                tags_from_table = str(self.getTextFromTable(row, tag_or_text['tag'])).split()
                for tag in tags_from_table:
                    # Ищу в xml теги, указанные в таблице и возвращаю текст внути тагов
                    tag_content = self.searchPattern(':{0}.*>(.*)<\/.*:{0}>'.format(tag),
                                                     self.readfile(os.path.join('./in', xml)), tag)
                    if len(tag_content) > 1:
                        tag_content, ok = QInputDialog().getItem(self, u'Было найдено более одного тега',
                                                                 u'Было найдено более одного тега\s{0}\sвыберите один\s'.format(tag),
                                                                 tag_content)
                        if not ok:
                            return
                    else:
                        tag_content = str(tag_content)[2:-2]

                    current_text = self.searchPattern('(:{0}.*>{1}<\/.*{0}>)'.format(tag, tag_content),
                                                      self.readfile(os.path.join('./in', xml)), tag, True)
                    for item in text_list:
                        new_xml = xml_text.replace(current_text,
                                                   current_text.replace(str(tag_content), item))

                        if past_text_by_symbol:
                            if put_file:
                                self.whriteFile(os.path.join('./in', xml), new_xml)
                                self.singAndPutXmlToServer()
                                if not self.showQuestionMessage():
                                    return

                        elif past_text:
                            xml_text = xml_text.replace(current_text,
                                                        current_text.replace(str(tag_content), item))
                            # Записываю все в папку
                            if past_text and not put_file:
                                self.tray_icon.showMessage(u'запись файла', u'помещаю перезаписанный файл в output')
                            self.whriteFile(os.path.join('./out', xml), xml_text)
                            # Если отмечен флаг - закидывать, то отправляю все, что позаменяла
                            if put_file and not past_text_by_symbol:
                                self.singAndPutXmlToServer()
                            if not self.showQuestionMessage():
                                return

    def showQuestionMessage(self):
        if not self.isHidden():
            self.show()
            self.raise_()
        return True if QMessageBox.question(self, 'Message', u'Продолжить подмену текста и отправку файла на сервер?',
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.No) == QMessageBox.Yes else False

    def searchPattern(self, pattern, file, serchparametr, search_particular=False, gr=0):
        self.tray_icon.showMessage('поиск значения', 'поиск значения в файле' + str(file))
        try:
            if search_particular:
                return search(pattern, file).group(gr)
            else:
                temp = findall(pattern, file)
                return findall(pattern, file)
        except TypeError:
            self.tray_icon.showMessage('TypeError', u'невозможно найти ' + serchparametr)
        except AttributeError:
            self.tray_icon.showMessage('AttributeError', u'невозможно найти ' + serchparametr)

    @staticmethod
    def whriteFile(path_to_config, text):
        with open(path_to_config, 'w') as f:
            f.write(text)

    def readfile(self, path_to_config='utility.conf'):
        with open(path_to_config, 'r') as f:
            output = f.read()
        return output

    # Функции для работы с треем
    def close_from_menu(self):
        self.close_action_from_menu = True
        self.close()

    def closeEvent(self, event):
        if self.close_action_from_menu:
            event.accept()
        else:
            event.ignore()
            self.hide()

    def activate_window(self):
        self.show()

def checkFolderExist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def prepareToStart():
    checkFolderExist("./in")
    checkFolderExist("./out")

    if not os.path.exists('./utility.conf'):
        Trey.whriteFile('./utility.conf', 'pathToSingmessage=\npathToPutmessage=\n')


if __name__ == "__main__":
    prepareToStart()
    app = QApplication(sys.argv)
    window = Trey()
    #app.show()
    # window.readFile('Store','IpStore')
    sys.exit(app.exec_())
