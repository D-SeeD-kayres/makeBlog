import os
import openai
import sys
import uuid
import requests
from bs4 import BeautifulSoup
import googletrans

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
translator = googletrans.Translator()


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
        self.btnBlog.clicked.connect(self.buttonBlogAction)

        self.ageCombo.addItem('타깃 연령 선택')
        self.ageCombo.addItem('전연령')
        self.ageCombo.addItem('20대')
        self.ageCombo.addItem('30대')
        self.ageCombo.addItem('40대')

        self.jobCombo.addItem('직업선택')
        self.jobCombo.addItem('전문가')
        self.jobCombo.addItem('리뷰어')
        self.jobCombo.addItem('마케터')
        self.jobCombo.addItem('블로거')

        # self.jobRadio0.clicked.connect(self.jobSelect)
        # self.jobRadio1.clicked.connect(self.jobSelect)
        # self.boxlayout1 = QBoxLayout(QBoxLayout.LeftToRight, parent=self)
        # self.boxlayout1.addWidget(self.ageRadio0)
        # self.boxlayout1.addWidget(self.ageRadio1)
        # self.boxlayout1.addWidget(self.ageRadio2)
        # self.boxlayout1.addWidget(self.ageRadio3)
        #
        # self.boxlayout2 = QBoxLayout(QBoxLayout.LeftToRight, parent=self)
        # self.boxlayout2.addWidget(self.jobRadio0)
        # self.boxlayout2.addWidget(self.jobRadio1)
        # self.boxlayout2.addWidget(self.jobRadio2)
        # self.boxlayout2.addWidget(self.jobRadio3)
        #
        # self.groupbox1 = QGroupBox(self)
        # self.groupbox1.setLayout(self.boxlayout1)
        # self.groupbox1.setGeometry(250, 0, 320, 40)
        #
        # self.groupbox2 = QGroupBox(self)
        # self.groupbox2.setLayout(self.boxlayout2)
        # self.groupbox2.setGeometry(250, 50, 320, 40)


        self.pBar.hide()

    def buttonBlogAction(self):
        textUrl = self.textLink.text()
        if len(textUrl) > 0:
            if "https://blog.naver.com" in textUrl:
                url = textUrl
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                ifra = soup.find('iframe', id='mainFrame')
                post_url = 'https://blog.naver.com' + ifra['src']
                res = requests.get(post_url)
                soup2 = BeautifulSoup(res.text, 'html.parser')
                contents = ''
                txt_contents = soup2.findAll('div', {'class': re.compile('^se-module se-module-tex.*')})
                for p_span in txt_contents:
                    for txt in p_span.find_all('span'):
                        contents += txt.get_text() + '\n'
                self.list.setPlainText(contents)
            else:
                self.show_popup_ok("ERROR", "네이버 블로그만 지원합니다.")
    def buttonCopyAction(self):
        clipboard.copy(self.list.toPlainText())

    def show_popup_ok(self, title: str, content: str):

        self.msg = QMessageBox()
        self.msg.setWindowTitle(title)
        self.msg.setText(content)
        self.msg.setStandardButtons(QMessageBox.Ok)
        # bar.show()
        result = self.msg.exec_()
    def button1Function(self):

        inputText = self.inputText.toPlainText()
        self.label
        if len(inputText) > 0:
            if len(self.list.toPlainText()) > 0:
                self.show_popup("MakeBlog", "작성된 내용이 있습니다.\n재 검색 하시겠습니까?", inputText)
            else:
                age = ''
                job = ''
                print(self.ageCombo.currentIndex())
                if self.ageCombo.currentIndex() == 0 or self.jobCombo.currentIndex() == 0:
                    self.show_popup_ok('error','필수 정보를 선택해 주세요.')
                else:
                    if self.ageCombo.currentIndex() == 1:
                        age = '전연령'
                    elif self.ageCombo.currentIndex() == 2:
                        age = '20대'
                    elif self.ageCombo.currentIndex() == 3:
                        age = '30대'
                    elif self.ageCombo.currentIndex() == 4:
                        age = '40대'

                    if self.jobCombo.currentIndex() == 1:
                        job = '전문가'
                    elif self.jobCombo.currentIndex() == 2:
                        job = '리뷰어'
                    elif self.jobCombo.currentIndex() == 3:
                        job = '마케터'
                    elif self.jobCombo.currentIndex() == 4:
                        job = '블로거'

                    self.worker = Worker(inputText,age, job)
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
            age = ''
            job = ''
            if self.ageCombo.currentIndex() == 0 or self.jobCombo.currentIndex() == 0:
                self.show_popup_ok('error','필수 정보를 선택해 주세요.')
            else:
                if self.ageCombo.currentIndex() == 1:
                    age = '전연령'
                elif self.ageCombo.currentIndex() == 2:
                    age = '20대'
                elif self.ageCombo.currentIndex() == 3:
                    age = '30대'
                elif self.ageCombo.currentIndex() == 4:
                    age = '40대'

                if self.jobCombo.currentIndex() == 1:
                    job = '전문가'
                elif self.jobCombo.currentIndex() == 2:
                    job = '리뷰어'
                elif self.jobCombo.currentIndex() == 3:
                    job = '마케터'
                elif self.jobCombo.currentIndex() == 4:
                    job = '블로거'

                self.worker = Worker(inputText, age, job)
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
    def __init__(self, arg1, age, job):
        super().__init__()
        self.running = True
        self.result = None
        self.arg1 = arg1
        self.age = age
        self.job = job
        print(job)
    def run(self):
        while self.running:

            qq = "너는 "+self.arg1+"의 "+self.job+"야."+self.arg1 + ("을(를) 주제로 네이버블로그에 포스팅건대 부제목 6개 만들어줘")
            print("111111")
            print(qq)
            # result =translator.translate(qq, src='ko', dest='en')

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
                if len(i) > 0:

                    for_input = "너를 "+self.job+"라고 가정하고, "+i + ("을 "+self.age+" 대상으로 소개하는 글을 써줘. 글 스타일은 네이버 블로그 스타일로 해주고 인사말은 빼줘. 말투는 친절하게 작성하는대 gpt를 사용한다는 글은 작성하지 말아줘.")
                    # en_input = translator.translate(for_input, src='ko', dest='en').text

                    completion1 = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": for_input}
                        ])
                    ko_result = completion1.choices[0].message.content
                    # print(ja_result)
                    # ko_result = translator.translate(ko_result, src='ja', dest='ko').text
                    self.result = self.result + i + "\n" + ko_result+ "\n\n"

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
    myWindow.show()
    # loginWindow.show()
    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()


# print("키워드를 입력해 주세요")
# question = input()

