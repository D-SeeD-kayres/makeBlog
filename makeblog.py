import os
import openai
import sys
import uuid
import getmac
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

import threading
import time
import clipboard

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import re
import hashlib
from datetime import datetime


# open ai에서 발급받은 api key를 등록합니다
cred = credentials.Certificate("makeblog_firebase.json")
# firebase_admin.initialize_app(cred)
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://makeblog-8f685-default-rtdb.asia-southeast1.firebasedatabase.app/'
    #'databaseURL' : '데이터 베이스 url'
})

form_class = uic.loadUiType("1.ui")[0]
form_login = uic.loadUiType("login.ui")[0]
form_signup = uic.loadUiType("signup.ui")[0]

class SignupClass(QMainWindow, form_signup):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label_mac.setText(getmac.get_mac_address())
        self.btnOk.clicked.connect(self.checkId)

    def checkId(self):
        strId = self.textId.text()
        strPass = self.textPass.text()
        strCheckPass = self.textPassCheck.text()

        if len(strId) < 10 or len(strId) > 11:
            self.show_popup("Error", "휴대폰 번호는 10-11 글자 사이로 작성되어야 합니다.")
        elif strId[0:3] != "010" and strId[0:3] != "011" and strId[0:3] != "016" and strId[0:3] != "017" and strId[0:3] != "018":
            print(strId[0:3])
            self.show_popup("Error", "휴대폰 번호가 아닙니다.")
        elif not strId.isdigit():
            self.show_popup("Error", "숫자만 입력 가능합니다.")
        elif len(strPass) < 8:
            self.show_popup("Error", "비밀번호는 8자 이상이어야 합니다.")
        elif strPass != strCheckPass:
            self.show_popup("Error", "입력된 비밀번호가 다릅니다.")
        else:
            self.show_signpopup("MakeBlog", strId+" 으로 가입하시겠습니까?\n가입한 디바이스에서만 사용 가능합니다.", strId, strPass)
    def show_signpopup(self, title: str, content: str, userId: str, userPass: str):

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setWindowTitle(title)
        self.msg.setText(content)
        self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        result = self.msg.exec_()
        if result == QMessageBox.Ok:
            print("ok")
            ref = db.reference('users/'+userId)  # db 위치 지정, 기본 가장 상단을 가르킴
            print(ref.get())
            if ref.get() == None:
                now = datetime.now()
                date = now.strftime('%Y-%m-%d %H:%M:%S')
                result = hashlib.md5(userPass.encode()).hexdigest()
                profile = {'pass':result,'signdate':date, 'mac': self.label_mac.text()}
                ref.update(profile)
                self.main = WindowClass()
                self.close()
                self.main.show()
            else:
                self.show_popup("Error", "이미 가입된 번호가 있습니다.")
            # ref.update(lux1)  # 해당 변수가 없으면 생성한다.
        elif result == QMessageBox.Cancel:
            print("cancel")
    def show_popup(self, title: str, content: str):

        self.msg = QMessageBox()
        self.msg.setWindowTitle(title)
        self.msg.setText(content)
        self.msg.setStandardButtons(QMessageBox.Ok)


        result = self.msg.exec_()
class LoginClass(QMainWindow, form_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.etPass.setEchoMode(QLineEdit.Password)
        self.btnLogin.clicked.connect(self.loginFunction)
        self.btnSignup.clicked.connect(self.signupFunction)
        a = getmac.get_mac_address()
        print(a)


    def signupFunction(self):
        self.signup = SignupClass()
        self.close()
        self.signup.show()
    def loginFunction(self) :
        # self.main = WindowClass()
        # self.close()
        # self.main.show()
        userId = self.etId.text()
        if len(userId) == 0:
            self.show_popup("ERROR", "아이디를 입력하세요")
        elif not userId.isdigit():
            self.show_popup("ERROR", "아이디는 숫자만 가능합니다..")
        else:
            print(self.etPass.text())
            userId = self.etId.text()
            mdPass = hashlib.md5(self.etPass.text().encode()).hexdigest()
            ref = db.reference('users/'+userId)  # db 위치 지정, 기본 가장 상단을 가르킴
            result = ref.get()
            print(type(result))
            if result == None:
                self.show_popup("ERROR", "등록된 아이디가 없습니다.")
            elif mdPass != result['pass']:
                self.show_popup("ERROR", "아이디 혹은 비밀번호가 일치하지 않습니다.")
            else:
                if result['mac'] == getmac.get_mac_address():
                    now = datetime.now()
                    date = now.strftime('%Y-%m-%d %H:%M:%S')
                    ref.update({'logindate':date})
                    self.main = WindowClass()

                    self.close()
                    self.main.show()
                else:
                    self.show_popup("ERROR", "사용하던 PC가 아닙니다.")

    def is_email_valid(email):
        REGEX_EMAIL = '([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        if not re.fullmatch(REGEX_EMAIL, email):
            return False
        else:
            return True
    def show_popup(self, title: str, content: str):

        self.msg = QMessageBox()
        self.msg.setWindowTitle("test")
        self.msg.setText(content)
        self.msg.setStandardButtons(QMessageBox.Ok)
        # bar = QProgressBar(self)
        # bar.setGeometry(0, 0, 200, 30)
        # bar.setValue(0)
        # bar.setMaximum(0)
        # lay = self.msg.layout()
        # lay.addWidget(bar)

        # bar.show()
        result = self.msg.exec_()

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        OPENAI_YOUR_KEY = "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"
        openai.api_key = OPENAI_YOUR_KEY
        self.setupUi(self)
        self.btn.clicked.connect(self.button1Function)
        self.copybtn.clicked.connect(self.buttonCopyAction)
        self.pBar.hide()


    def buttonCopyAction(self):
        clipboard.copy(self.list.toPlainText())

    def show_popup_ok(self, title: str, content: str):

        self.msg = QMessageBox()
        self.msg.setWindowTitle("test")
        self.msg.setText(content)
        self.msg.setStandardButtons(QMessageBox.Ok)
        bar = QProgressBar(self)
        bar.setGeometry(0, 0, 200, 30)
        bar.setValue(0)
        bar.setMaximum(0)
        lay = self.msg.layout()
        lay.addWidget(bar)

        # bar.show()
        result = self.msg.exec_()
    def button1Function(self):

        inputText = self.inputText.toPlainText()
        self.label
        if len(inputText) > 0:
            if len(self.list.toPlainText()) > 0:
                self.show_popup("MakeBlog", "작성된 내용이 있습니다.\n재 검색 하시겠습니까?", inputText)
            else:
                self.worker = Worker(inputText)
                self.worker.start()
                self.worker.timeout.connect(self.timeout)
                self.pBar.show()

    def show_popup(self, title: str, content: str, inputText: str):

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setWindowTitle(title)
        self.msg.setText(content)
        self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        result = self.msg.exec_()
        if result == QMessageBox.Ok:
            self.list.setPlainText("")
            self.worker = Worker(inputText)
            self.worker.start()
            self.worker.timeout.connect(self.timeout)
            self.pBar.show()
        elif result == QMessageBox.Cancel:
            print("cancel")


    @pyqtSlot(str)
    def timeout(self, num):
        self.list.setPlainText(num)
        self.label.setText(str(len(num)))
        self.pBar.hide()
        # self.edit.setText(str(num))
class Worker(QThread):
    timeout = pyqtSignal(str)
    def __init__(self, arg1):
        super().__init__()
        self.running = True
        self.result = None
        self.arg1 = arg1
    def run(self):
        while self.running:
            print(self.arg1)
            qq = self.arg1 + ("의 내용으로 블로그 포스팅할 내용의 목차 작성해줘.")
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": qq}
                ])
            self.indexResult = completion.choices[0].message.content

            self.arrResult = self.indexResult.splitlines()
            self.result = ""
            # self.result = self.indexResult
            for i in self.arrResult:
                print(i)
                for_input = self.arg1 + i + ("을 전문가 의견으로 작성해서 네이버 블로그 스타일로 소개문구는 빼고 써줘.")
                completion1 = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": for_input}
                    ])
                self.result = self.result + i + "\n" + completion1.choices[0].message.content + "\n\n"

            # self.result1 = self.result + (" 이 내용을 네이버 블로그 스타일로 바꿔줘")
            # completion2 = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "user", "content": self.result1}
            #     ])
            # self.reslut2 = completion2.choices[0].message.content
            #
            # print(self.result2)
            self.timeout.emit(self.result)     # 방출

            break
    def get_result(self):
        return self.result

    def resume(self):
        self.running = True

    def pause(self):
        self.running = False
class indexThread(threading.Thread):
    def __init__(self, arg1):
        super().__init__()
        self.arg1 = arg1
        self.result = None

    def run(self):
        print(self.arg1)
        time.sleep(0.1)
        qq = self.arg1 + ("의 내용으로 블로그 포스팅할 내용의 목차 작성해줘. 각 목차는 /로 구분해줘")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": qq}
            ])
        self.indexResult = completion.choices[0].message.content

        self.arrResult = self.indexResult.splitlines()
        self.result = ""
        for i in self.arrResult:
            for_input = self.arg1 + i +("을 전문가 의견으로 작성해줘")
            completion1 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": for_input}
                ])
            self.result = self.result+ i + "\n" + completion1.choices[0].message.content +"\n\n"

    def get_result(self):
        return self.result

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    loginWindow = LoginClass()
    #프로그램 화면을 보여주는 코드
    # myWindow.show()
    loginWindow.show()
    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()


# print("키워드를 입력해 주세요")
# question = input()

