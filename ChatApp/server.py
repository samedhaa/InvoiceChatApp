from flask import Flask, render_template, request, url_for, jsonify, redirect, send_from_directory
#from flask_weasyprint import HTML, render_pdf
import urllib.request
import json
from datetime import date

chatApp = Flask(__name__)

# a list has the steps of the invoice
InvoicingProccess = ['CreateInvoice', 'SenderName', 'RecieverName', 'Address', 'Date', 'InvoiceNumber', 'Description','Notes','ShowInvoice']

# this dicionary works as a follower to which step are we if the step is 0 then we didn't come to that step yet
InvoiceProccess = {InvoicingProccess[0] : 0, InvoicingProccess[1] : 0, InvoicingProccess[2] : 0, InvoicingProccess[3] : 0, InvoicingProccess[4] : 0, InvoicingProccess[5] : 0,InvoicingProccess[6] : 0,InvoicingProccess[7] : 0, InvoicingProccess[8] : 0}

# this dicionary will have all the invoice information
INVOICE = {}

# If luis.ai didn't understand if you want to make invoice or not we do it manually using this variable
wouldYouMakeInvoice = False

# Those variables are for entering the items py 
ItemStage = 1.0
stage6GetItem = False
stage6GetQuantity= False
stage6GetPrice = False
AddMoreItem = False



#initialize Messages
Messages = ['Hi im a bot']

# to serve static assets
@chatApp.route('/assets/<path:path>')
def send_asset(path):
    return send_from_directory('assets', path)

# A function that route to /invoice where the last invoice is exist
@chatApp.route('/invoice', methods = ['POST','GET'])
def InvoiceReport():
    return render_template("invoice.html", result=INVOICE)

# This url have the pdf of the invoice.

@chatApp.route('/InvoiceTo.pdf')
def MakePdfInvoice():
    # Make a PDF from another view
    return render_pdf(url_for('InvoiceReport'))

# A function where have all the messages as a json file
@chatApp.route('/chat/GetMessages', methods = ['POST','GET'])
def getallMessages():
    newMessages = Messages[::-1]
    return jsonify(results = [newMessages[0]])

# A function that gets the message from chat.html
def getMessage():
    Message = str(request.form.get('Message'))
    return Message


# THE FUNCTION WHERE THE CHAT PROCCESS BEEN HANDLED BY IT. 
@chatApp.route('/chat', methods = ['POST','GET'])
def chatBox():
    Message = getMessage()
    global wouldYouMakeInvoice
    global ItemStage
    global stage6GetItem
    global stage6GetQuantity
    global stage6GetPrice
    global AddMoreItem
    if Message != 'None':
        GetIntent = LuisMagic(Message)
        # Checking manually if the person want to make an invoice - might not be neccessary it should be the default
        # to start the invoice. the variable 'wouldYouMakeInvoice' get changed in an else statement down the function.
        if wouldYouMakeInvoice == True:
            if GetIntent == 'Agree':
                GetIntent = 'CreateInvoice'
                wouldYouMakeInvoice = False

        # Just going step by step in the invoice.
        if GetIntent == 'CreateInvoice' or InvoiceProccess[InvoicingProccess[0]] == 1:
            if InvoiceProccess[InvoicingProccess[0]] == 0:
                FromName()
            elif InvoiceProccess[InvoicingProccess[1]] == 0:
                INVOICE['FROMName'] = Message
                ToName()
            elif InvoiceProccess[InvoicingProccess[2]] == 0:
                INVOICE['TOName'] = Message
                GetAddress()
            elif InvoiceProccess[InvoicingProccess[3]] == 0:
                INVOICE['Address'] = Message
                GetDate()
            elif InvoiceProccess[InvoicingProccess[4]] == 0 or InvoiceProccess[InvoicingProccess[4]] == -1 :
                if(InvoiceProccess[InvoicingProccess[4]] == -1):
                    INVOICE['Date'] = Message
                    GetInvoiceNumber()
                elif(LuisMagic(Message) == 'Agree'):
                    INVOICE['Date'] = str(date.today())
                    GetInvoiceNumber()
                elif(InvoiceProccess[InvoicingProccess[4]] != -1):
                    Messages.append("Please enter the date for this invoice")
                    InvoiceProccess[InvoicingProccess[4]] = -1

                    
            elif InvoiceProccess[InvoicingProccess[5]] == 0 or InvoiceProccess[InvoicingProccess[6]] == 0:
                if InvoiceProccess[InvoicingProccess[5]] == 0:
                    INVOICE['InvoiceNumber'] = Message
                    InvoiceProccess[InvoicingProccess[5]] = 1
                    Messages.append("Please add the name of the item")
                else: 
                    if stage6GetItem == False:
                        INVOICE.setdefault('Item', []).append(Message)
                        stage6GetItem = True
                        ItemStage = 2.0
                        Messages.append("What is the quantity ?")

                    elif stage6GetQuantity == False:
                        INVOICE.setdefault('Quantity', []).append(Message)
                        stage6GetQuantity = True
                        ItemStage = 3.0
                        Messages.append("and how much ? ")
                    elif stage6GetPrice == False:
                        INVOICE.setdefault('Price', []).append(Message)
                        stage6GetPrice = True
                        ItemStage = 4.0
                        Messages.append("Woud you like to add a new item ? ")
                    elif AddMoreItem == False:
                        if LuisMagic(Message) == 'Agree':
                            ItemStage = 1.0
                            stage6GetPrice = False
                            stage6GetQuantity = False
                            stage6GetItem = False
                            AddMoreItem = False
                            Messages.append("Please add the name of the item")
                        else:
                            wouldYouMakeNote()
                            InvoiceProccess[InvoicingProccess[6]] = 1
            elif InvoiceProccess[InvoicingProccess[7]] == 0:
                if LuisMagic(Message) == 'Agree':
                    GetNotes()

                else:
                    Finish()
            elif InvoiceProccess[InvoicingProccess[8]] == 0:
                INVOICE['Notes'] = Message
                Finish()
            else:
                Finish()
        else:
            Messages.append("Would you like to make an invoice ? ")
            wouldYouMakeInvoice = True 

    
    getallMessages()
    return render_template("chat.html")


# A function where all the Magic happen, e.g Abrakadabra
def LuisMagic(Message):
    # We just get rid of the spaces in the text
    KEYWORD = ''
    SPACE = '%20'
    for i in range(len(Message)):
        if Message[i] == ' ':
            KEYWORD = KEYWORD + SPACE
        else:
            KEYWORD = KEYWORD + Message[i]

    # making the last URL for where the intent of our message is.
    luis = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/3ca01edc-15d6-4ee6-b481-b2840cd6b476?subscription-key=11f1b249304d47bc852d57eb73f036fc&verbose=true&timezoneOffset=-360&q=" + KEYWORD

    # making luis understand the message and json it. 
    with urllib.request.urlopen(luis) as url:
        jsonResponse = json.loads(url.read().decode())

    # Returning the intent
    return jsonResponse['topScoringIntent']['intent']


# all the elses are for better chatting quality.
# will be modified soon.

# Those are the functions where have the basic conversations for the steps of the invoice,
# also the functions make any step that has been proccesed marked by the InvoiceProccess dictionary 
# so that we won't access it again for no reason.
def FromName():
    if InvoiceProccess[InvoicingProccess[0]] == 0:
        Messages.append("Hi! Let's start the invoice!, Who is this invoice from ? ")
        InvoiceProccess[InvoicingProccess[0]] = 1
    else:
        return

def ToName():
    if InvoiceProccess[InvoicingProccess[1]] == 0:
        Messages.append("Who is this invoice to ? ")
        InvoiceProccess[InvoicingProccess[1]] = 1
    else:
        return
def GetAddress():
    if InvoiceProccess[InvoicingProccess[2]] == 0:
        Messages.append("Please enter the address! ")
        InvoiceProccess[InvoicingProccess[2]] = 1
    else:
        return

def GetDate():
    if InvoiceProccess[InvoicingProccess[3]] == 0:
        Messages.append("Would you like the date to be today's date : " + str(date.today()) + "?")
        InvoiceProccess[InvoicingProccess[3]] = 1
    else:
        return

def GetInvoiceNumber():
    if InvoiceProccess[InvoicingProccess[4]] == 0 or InvoiceProccess[InvoicingProccess[4]] == -1 :
        Messages.append("Please enter the InvoiceNumber : ")
        InvoiceProccess[InvoicingProccess[4]] = 1
    else:
        return

def WantToAddInvoice():
    Messages.append("Would you like to add invoice ? ")


def GetNotes():
    if InvoiceProccess[InvoicingProccess[7]] == 0:
        Messages.append("Please enter Notes : ")
        InvoiceProccess[InvoicingProccess[7]] = 1

    else:
        return

def Finish():
    if InvoiceProccess[InvoicingProccess[8]] == 0:
        InvoiceProccess[InvoicingProccess[8]] = 1
        Messages.append("Done! redirecting the the invoice! FML")
        #InvoiceReport()
        # The redirecting is not ready yet.
        #return redirect(url_for('InvoiceReport'))
        MakePdfInvoice()

    else:
        Messages.append("Would you like to make an invoice")

def wouldYouMakeNote():
    Messages.append("Do you want to make a note ? ")


if __name__ == "__main__":
    chatApp.run(debug=True)
