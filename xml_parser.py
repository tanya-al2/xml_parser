# coding: utf-8

from shutil import copyfile
import os, sys, subprocess
from PyQt5.QtCore import QFile, QXmlStreamReader
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
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
        activate_action.triggered.connect(self.show)
        tray_menu = QMenu(u'...')
        tray_menu.addAction(close_action)
        tray_menu.addAction(activate_action)
        self.close_action_from_menu = False
        self.tray_icon = QSystemTrayIcon(QIcon(u'xml_parser.ico'), self)
        self.tray_icon.show()
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.activate_window)
        # self.tray_icon.showMessage(u'ошибочка', u'просто говорю, что')
        # Создаем виджет с вкладкой для заметы содержания вкладок
        # главное окно
        self.main_tab_layout = QVBoxLayout(self)
        self.main_tab_widget = QTabWidget(self)

        # добавляем вкладки
        self.main_tab_widget.addTab(ChangeXmlTab(self), u'Окно для замены текста в тагах')
        self.main_tab_widget.addTab(SettingTab(self), u'Установка настроеек для утилиты автоподписи')

        self.main_tab_layout.addWidget(self.main_tab_widget)
        self.setLayout(self.main_tab_layout)

    def search_pattern(self, pattern, file, search_parameters, search_particular=False, gr=0):
        try:
            if search_particular:
                return search(pattern, file).group(gr)
            else:
                return findall(pattern, file)
        except TypeError:
            self.tray_icon.showMessage('TypeError', u'невозможно найти ' + search_parameters)
        except AttributeError:
            self.tray_icon.showMessage('AttributeError', u'невозможно найти ' + search_parameters)

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


# окно в котором считываются настройки для указанной в кофигах утилиты
class SettingTab(Trey):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        # Добавляю виджеты
        # Сами виджеты
        self._parent = parent
        self.main_windows_layout = QFormLayout()
        # Добавляю кнопку для установки параметров в утилите автоподписи
        self.setup_config = QPushButton(u'Установить параметры в утилите')
        self.main_windows_layout.addRow(self.setup_config)
        self.update_config = QPushButton(u'Установить')
        self.main_windows_layout.addRow(self.update_config)
        self.setup_config.clicked.connect(self.read_and_past_configfile, True)
        self.update_config.clicked.connect(self.utility_config_updater)
        # Считываю из конфиг-файла поля и добавляю комбобоксы в окно для установки конфигов другой утилиты
        self.to_change_parameters_config_reader()
        self.setLayout(self.main_windows_layout)

    def to_change_parameters_config_reader(self):
        config_variables = {}

        for variable in self._parent.search_pattern('(.*)=(.*)',
                                            read_file(os.path.join(os.curdir, 'xml_parser.conf')),
                                            u'параметры'):  # найти в конфигах
            key = variable[0]
            config_variables[key] = QComboBox()
            config_variables[key].setMinimumContentsLength(15)
            config_variables[key].addItems(variable[1].split())
            self.main_windows_layout.addRow(key, config_variables[key])

    def utility_config_updater(self):
        for i in range(self.main_windows_layout.rowCount(), 2, -1):
            self.main_windows_layout.removeRow(i)
        self.to_change_parameters_config_reader()
        self.update()

    # , 'pathToSignMessage', self.config_variables['pathToSignMessage']
    def read_and_past_configfile(self, pastconfig=False):
        path_to_config = os.path.join(self.config_variables['pathToPutMessage'].currentText(), 'conf.properties')
        configs = read_file(path_to_config)

        if pastconfig:
            for key in self.config_variables:
                configs = configs.replace(self._parent.search_pattern('{0}=.*'.format(key), configs, key, True, 0),
                                          '{0}='.format(key) + self.config_variables[key].currentText(), key)
            write_file(path_to_config, configs)


class ChangeXmlTab(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        # окно с которого все началось
        # Добавляю чек-боксы к окну
        self.put_check_box = QCheckBox(u'загрузить xml')
        self.tag_check_box = QCheckBox(u'поменять текст')
        self.change_by_symbol_checkbox = QCheckBox(u'добавить по одному символу')

        # Создаю main_tab_layout с чекбоксами
        self.check_boxes_box_layout = QVBoxLayout()
        self.check_boxes_box_layout.addWidget(self.put_check_box)
        self.check_boxes_box_layout.addWidget(self.tag_check_box)
        self.check_boxes_box_layout.addWidget(self.change_by_symbol_checkbox)

        # Создаю таблицу для приема символов и тагов
        self.tag_content_table = QTableWidget(0, 2, self)
        self.tag_content_table.setHorizontalHeaderLabels([u'текст/символы', 'tags'])
        for colum_number, width in enumerate((300, 250)):
            self.tag_content_table.horizontalHeader().resizeSection(colum_number, width)
        # Добавляю кнопки для управления таблицей
        self.add_row_button = QPushButton(u'добавить строку')
        self.remove_row_button = QPushButton(u'удалить строку')
        self.add_row_button.clicked.connect(
            lambda: self.tag_content_table.insertRow(self.tag_content_table.rowCount()))
        self.remove_row_button.clicked.connect(
            lambda: self.tag_content_table.removeRow(self.tag_content_table.currentRow()))

        # Кнопка!
        self.start_button = QPushButton(u'жми!')
        self.start_button.clicked.connect(self.change_tag_contant)

        # Создаю main_tab_layout кнопками для таблицы
        self.buttons_box_layout = QHBoxLayout()
        self.buttons_box_layout.addWidget(self.start_button)
        self.buttons_box_layout.addWidget(self.add_row_button)
        self.buttons_box_layout.addWidget(self.remove_row_button)

        # | self.tag_content_table.rowCount()-1

        # Создаю main_tab_layout с таблицей для приема символов и тагов
        self.table_box_layout = QVBoxLayout()
        self.table_box_layout.addWidget(self.tag_content_table)

        # self.table_box_layout.addWidget(self.tag_content_table)

        # Создаю main_tab_layout с таблицей, чекерами и кнопками
        self.all_box_layout = QHBoxLayout()
        self.all_box_layout.addLayout(self.check_boxes_box_layout)
        self.all_box_layout.addLayout(self.buttons_box_layout)
        self.table_box_layout.addLayout(self.all_box_layout)

        self.setLayout(self.table_box_layout)

    def get_text_from_table(self, row, column):
        return self.tag_content_table.item(row, column).text()

    def read_xml_file(self, xml, tag):

        try:
            xml_file = QFile(os.path.join(os.curdir, 'in', xml))
            xml_file.open(xml_file.ReadOnly | xml_file.Text)
            doc = QXmlStreamReader(xml_file)
            text_list = []
            while not doc.atEnd():
                doc.readNextStartElement()
                if doc.name() == tag:
                    temp = doc.namespaceUri()
                    text_list.append(
                        '{0}, {1}, {2}'.format(doc.namespaceUri(), doc.qualifiedName(), doc.readElementText()))
            xml_file.close()
            return text_list
        finally:
            xml_file.close()

    def rewrite_qfile(self, xml_file, pattern_old, pattern_new):
        text = read_file(os.path.join(os.curdir, 'in', xml_file))
        new_text = text.replace(pattern_old, pattern_new)
        write_file(os.path.join(os.curdir, 'out', xml_file), new_text)

    def sign_and_put_xml_to_server(self):

        if not self.isHidden():
            self.show()

        for path in [os.path.join(self.configVariables['pathToSignMessage'].currentText(), 'in'),
                     os.path.join(self.configVariables['pathToPutMessage'].currentText(), 'resources')]:
            for file_item in os.scandir(path):
                os.remove(file_item.path)

        for file_item in os.scandir(os.path.join(os.curdir, 'out')):
            copyfile(file_item.path,
                     os.path.join(self.configVariables['pathToSignMessage'].currentText(), 'in', file_item.name))
            subprocess.Popen(os.path.join(self.configVariables['pathToSignMessage'].currentText(),
                                          'run.sh')).wait()  # .communicate()

        for file_item in os.scandir(os.path.join(self.configVariables['pathToSignMessage'].currentText(), 'out')):
            copyfile(file_item.path,
                     os.path.join(self.configVariables['pathToPutMessage'].currentText(), 'resources',
                                  file_item.name))
            subprocess.Popen(
                os.path.join(self.configVariables['pathToPutMessage'].currentText(), 'run.sh')).wait()  # .communicate()

    def change_tag_contant(self):
        list_of_files_for_change = os.listdir(os.path.join(os.curdir, 'in'))
        tag_or_text = {'tag': 1, 'text': 0}

        # self.tray_icon.showMessage(u'будут подменены следующие сообщения', ''.join(list_of_files_for_change))
        # Считываю xml-файл
        for xml in list_of_files_for_change:
            # цикл по всем строкам в таблице
            row_count = self.tag_content_table.rowCount()
            for row in range(0, row_count):

                # Получаю текст, который будет подставлен в xml
                if self.tag_check_box.isChecked():
                    text_to_replace = [self.get_text_from_table(row, tag_or_text['text'])]
                else:
                    text_to_replace = self.get_text_from_table(row, tag_or_text['text'])

                # Цикл по всем тэгам из строки с тэгами
                tags_from_table = str(self.get_text_from_table(row, tag_or_text['tag'])).split()
                for tag in tags_from_table:
                    # Ищу в xml теги, указанные в таблице и возвращаю текст внути тагов
                    tag_content = self.read_xml_file(xml, tag)
                    if len(tag_content) > 1:
                        tag_content, ok = QInputDialog().getItem(self, u'Было найдено более одного тега',
                                                                 u'Было найдено более одного тега\s{0}\sвыберите один\s'.format(
                                                                     tag),
                                                                 tag_content)
                        if not ok:
                            return
                    if not tag_content: return

                    tag_content_url, tag_content_name, tag_content_text = tag_content.split(', ')
                    for item in text_to_replace:
                        if self.change_by_symbol_checkbox.isChecked():
                            if self.put_check_box.isChecked():
                                self.rewrite_qfile(xml,
                                                   '{0}</{1}'.format(tag_content_text, tag_content_name),
                                                   '{0}</{1}'.format(item, tag_content_name))
                                self.sign_and_put_xml_to_server()
                                if not self.show_question_message():
                                    return

                        elif self.tag_check_box.isChecked():
                            # Записываю все в папку
                            self.rewrite_qfile(xml,
                                               '{0}</{1}'.format(tag_content_text, tag_content_name),
                                               '{0}</{1}'.format(item, tag_content_name))
                            if self.put_check_box.isChecked() and not self.change_by_symbol_checkbox.isChecked():
                                self.sign_and_put_xml_to_server()
                            if not self.show_question_message():
                                return

    def show_question_message(self):
        if not self.isHidden():
            self.show()
            self.raise_()
        return True if QMessageBox.question(self, 'Message', u'Продолжить подмену текста и отправку файла на сервер?',
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.No) == QMessageBox.Yes else False


def check_folder_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def prepar_to_start():
    check_folder_exist(os.path.join(os.curdir, 'in'))
    check_folder_exist(os.path.join(os.curdir, 'out'))

    if not os.path.exists(os.path.join(os.curdir, 'xml_parser.conf')):
        write_file(os.path.join(os.curdir, 'xml_parser.conf'),
                   'pathToSignMessage=\npathToPutMessage=\n')


def write_file(path_to_file, text):
    with open(path_to_file, 'w') as f:
        f.write(text)


def read_file(path_to_file):
    with open(path_to_file, 'r') as f:
        output = f.read()
    return output


if __name__ == "__main__":
    prepar_to_start()
    app = QApplication(sys.argv)
    window = Trey()
    sys.exit(app.exec_())
