
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Experiment3 import *  #the .ui file (converted to .py) containing all interface information

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QApplication(sys.argv)

window = QMainWindow()

ui = Ui_CentalWindow()
ui.setupUi(window)
window.show()
ui.stackedWidget.setCurrentIndex(0)

#all variables used across functions are set below
window.Page2Checkboxes = [ui.check1, ui.check2, ui.check3, ui.check4, ui.check5, ui.check6, ui.check7, ui.check8]

window.Page2Labels = [ui.lbl2, ui.lbl3, ui.lbl4, ui.lbl5, ui.lbl6, ui.lbl7, ui.lbl8, ui.lbl9]

#if a new page is added, a new title needs to be added as well!
window.pageTitles = ["Information Page", "Consent Page", "Demographics Page", "Instructions Page", "Disclaimer Page"]

window.checked = False  # used on demographics page
window.name = ""  # used on demographics page
window.age = ""  # used on demographics page
window.gender = ""  # used on demographics page
window.education = ""  # used on demographics page

ui.lblErrorName.hide()
ui.lblErrorAge.hide()
ui.lblErrorGender.hide()
ui.lblErrorEdu.hide()
ui.lblError.hide()  # first error label, on demographics page

# checks if all consent checkboxes are checked.
# runs when the "Submit" button on the consent page is clicked.
# only function in the program to start with a capital letter because it was the first function I wrote. So sue me.
def CheckedConsent():
    allChecked = []  # creates empty local list when function is run, will contain booleans for each checkbox
    # function still works when more boxes are added to the window.Page2Checkboxes list (Variables.py file)
    for i in range(len(window.Page2Checkboxes)):
        # links window.Page2Labels list and window.Page2Checkboxes list together
        checkbox = window.Page2Checkboxes[i]
        label = window.Page2Labels[i]
        labelPallette = label.palette()  # gets current colour of label
        if not checkbox.isChecked():  # makes label belonging to the checkbox red if box isn't ticked.
            colour = "red"
            allChecked.append(False)
        else:  # sets colour of label belong to the checkbox to black if the checkbox is ticked
            colour = "black"
            allChecked.append(True)
        labelPallette.setColor(QPalette.WindowText, QColor(colour))
        label.setPalette(labelPallette)  # sets colour of label depending on state
    # the following checks if list contains a False boolean. If so, an error is shown. Otherwise, the exp. continues
    if False not in allChecked:  # runs when allChecked only contains True
        nextPage()
    else:
        ui.lblError.show()  # error message is displayed (label is hidden by default, see Variables.py file)
        ui.lblError.setText("Please read and check all boxes.")


 # checks if all demographics have been entered.
# runs when the Submit button on the demographics page is clicked.
# all if-statements could have been reversed, but that didn't make as much sense to me
def checkDemog():
    demogEntered = []  # local empty list, will contain bools, just like the local list in the CheckedConsent function
    if ui.txtname.text() == '':  # runs if name field is empty
        ui.lblErrorName.show()  # shows error label belonging to name field
        ui.lblErrorName.setText("Please enter your name")
        demogEntered.append(False)  # same principle as CheckedConsent function
    else:  # runs if name fields is not empty
        ui.lblErrorName.hide()  # hidden by default -> Variables.py
    if ui.boxAge.value() == 0:  # runs if age is set to 0. Because who lets a baby use a computer?!
        ui.lblErrorAge.show()
        ui.lblErrorAge.setText("Please enter your age")
        demogEntered.append(False)
    else:  # runs if age field is not empty
        ui.lblErrorAge.hide()
    # runs if neither gender option is checked
    if not ui.rbGender.isChecked() and not ui.rbGender_2.isChecked() and not ui.rbGender_3.isChecked():
        ui.lblErrorGender.show()
        ui.lblErrorGender.setText("Please enter your gender")
        demogEntered.append(False)
    else:  # runs if a gender option is checked
        ui.lblErrorGender.hide()
    if not ui.dropEducation.currentIndex() >= 1:  # runs if the education field is at its default index ( = 0)
        ui.lblErrorEdu.show()
        ui.lblErrorEdu.setText("Please select your education")
        demogEntered.append(False)
    else:  # runs if the education field is not at default
        ui.lblErrorEdu.hide()
    if False not in demogEntered:  # runs when demogEntered only contains True
        getDemographics()
        write()
        nextPage()
    else:
        None  # nothing happens until all demographics have been entered and demogEntered contains no more False
        # else statement intentionally left blank


# this function gets the entered demographics from the demographics page and readies them for writing to output file.
# it is called by the checkDemog function.
# also see write function
def getDemographics():
    window.name = ui.txtname.text()  # get name from name field
    window.age = str(ui.boxAge.value())  # gets age from age field and converts it to a string
    for item in [ui.rbGender, ui.rbGender_2, ui.rbGender_3]:  # finds which gender item is checked
        if item.isChecked():
            window.gender = item.text()
    # converts gender to a string containing a number
    if window.gender == "Male":
        window.gender = "1"
    elif window.gender == "Female":
        window.gender = "2"
    else:
        window.gender = "3"
    window.education = ui.dropEducation.currentText()  # gets education from education field


# this function moves to the next page in the stacked widget.
# quite possibly the most complex function in the program.
# carefully crafted so it still works if another page + page title is added somewhere in the middle.
# works with all three experiment conditions.
# works with all two marble outcomes.
# called by many, many functions.
# this function makes more sense when you look at the layout of the stacked widget in Designer.
def nextPage():
    index = ui.stackedWidget.currentIndex()
    title = window.pageTitles[index + 1]  # gets the titles belonging to the next page
    window.setWindowTitle(title)  # changing the window title when the page changes
    # runs when the expCondition is the 10 marbles condition and the current page is the demographics page
    # or the current page is the instruction page for the 10 marbles condition
    ui.stackedWidget.setCurrentIndex(index + 1)  # go to the next page

def write():
    window.newFileAppend = open("participants/ParticipantData.csv", "a")
    window.newFileRead = open("participants/ParticipantData.csv", "r")
    window.allLines = window.newFileRead.readlines()
    labelInfo = ["name", "age", "gender (1 = male 2 = female 3 = other)", "education"]
    window.labels = ",".join(labelInfo)
    if len(window.allLines) == 0:  # only writes labels to top of file when file is new/empty
        window.newFileAppend.write(window.labels)  # writes labels to the file that is opened as append
    else:
        pass
        # intentionally left empty
    allInfo = [window.name, window.age, window.gender, window.education]
    toFile = ",".join(allInfo) + "\n"
    window.newFileAppend.write(toFile)  # writes to the file that is opened as append
    window.newFileAppend.close()
    window.newFileRead.close()  # closes read file (could've been closed earlier as well)

ui.btnNext.clicked.connect(nextPage)  # does what it says
ui.btnContinue.clicked.connect(CheckedConsent)  # checks if all checkboxes are checked

#demographics page
ui.btnSubmit.clicked.connect(checkDemog)

#iinstructions page
ui.btnUnderstand.clicked.connect(nextPage)

sys.exit(app.exec_())