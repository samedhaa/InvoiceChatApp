from flask import Flask, render_template, request, url_for, jsonify, redirect
from flask_weasyprint import HTML, render_pdf
import urllib.request
import json
import datetime



chatApp = Flask(__name__)

Messages = ['Hi im a bot']


# a list has the steps of the invoice
InvoicingProccess = ['CreateInvoice', 'SenderName', 'RecieverName', 'Address', 'Date', 'InvoiceNumber', 'Description','Notes','ShowInvoice']

# this dicionary works as a follower to which step are we if the step is 0 then we didn't come to that step yet
InvoiceProccess = {InvoicingProccess[0] : 0, InvoicingProccess[1] : 0, InvoicingProccess[2] : 0, InvoicingProccess[3] : 0, InvoicingProccess[4] : 0, InvoicingProccess[5] : 0,InvoicingProccess[6] : 0,InvoicingProccess[7] : 0, InvoicingProccess[8] : 0}

# this dicionary will have all the invoice information
INVOICE = {}

# If luis.ai didn't understand if you want to make invoice or not we do it manually using this variable
wouldYouMakeInvoice = False

# Those variables are for entering the items 
itemsInserted = 0
ItemNumber  = 1
stage6Entered = False



# A function that route to /invoice where the last invoice is exist
@chatApp.route('/invoice', methods = ['POST','GET'])
def InvoiceReport():
    return render_template("invoice.html", result=INVOICE)

# This url have the pdf of the invoice.
@chatApp.route('/hello.pdf')
def hello_pdf():
    # Make a PDF from another view
    return render_pdf(url_for('InvoiceReport'))

# A function where have all the messages as a json file
@chatApp.route('/chat/GetMessages', methods = ['POST','GET'])
def getallMessages():
    return jsonify(results = Messages)

# A function that gets the message from chat.html
def getMessage():
    Message = str(request.form.get('Message'))
    return Message


# THE FUNCTION WHERE THE CHAT PROCCESS BEEN HANDLED BY IT. 
@chatApp.route('/chat', methods = ['POST','GET'])
def chatBox():
    Message = getMessage()
    global wouldYouMakeInvoice
    global ItemNumber
    global itemsInserted
    global stage6Entered
    if Message != 'None':
        GetIntent = LuisMagic(Message)
        Messages.append(Message)
        getallMessages()
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
            elif InvoiceProccess[InvoicingProccess[4]] == 0:
                INVOICE['Date'] = Message
                GetInvoiceNumber()
            elif InvoiceProccess[InvoicingProccess[5]] == 0:
                INVOICE['InvoiceNumber'] = Message
                GetItems()
            elif InvoiceProccess[InvoicingProccess[6]] == 0:
                if stage6Entered == False:
                    INVOICE['NumOfItems'] = int(Message)
                    print("Invoice : ")
                    print(INVOICE['NumOfItems'])
                    if INVOICE['NumOfItems'] > 0:
                        Messages.append("Please add the name of the item press enter")
                        Messages.append("and then add the quantity and press enter")
                        Messages.append("and then add the price and press enter")
                        stage6Entered = True
                else:
                    if ItemNumber == 1:
                        INVOICE.setdefault('Item', []).append(Message)
                        ItemNumber+=1
                    elif ItemNumber == 2:
                        INVOICE.setdefault('Quantity', []).append(Message)
                        ItemNumber+=1
                    else:
                        INVOICE.setdefault('Price', []).append(Message)
                        ItemNumber=1
                        itemsInserted+=1

                if itemsInserted == int(INVOICE['NumOfItems']):
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

    return render_template("chat.html", string=Messages)

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
    luis = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/3ca01edc-15d6-4ee6-b481-b2840cd6b476?subscription-key=11f1b249304d47bc852d57eb73f036fc&timezoneOffset=-360&q=" + KEYWORD

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
        Messages.append("Please enter the date of this invoice ")
        InvoiceProccess[InvoicingProccess[3]] = 1
    else:
        return

def GetInvoiceNumber():
    if InvoiceProccess[InvoicingProccess[4]] == 0:
        Messages.append("Please enter the InvoiceNumber : ")
        InvoiceProccess[InvoicingProccess[4]] = 1
    else:
        return
def GetItems():
    if InvoiceProccess[InvoicingProccess[5]] == 0:
        Messages.append("How Many items would you like to add ? ")
        InvoiceProccess[InvoicingProccess[5]] = 1
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
        hello_pdf()

    else:
        Messages.append("Would you like to make an invoice")

def wouldYouMakeNote():
    Messages.append("Do you want to make a note ? ")


if __name__ == "__main__":
    chatApp.run(debug=True)
