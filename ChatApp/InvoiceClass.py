# Implementing 2 classes that have all data needed for invoicing.
class InvoiceData: 

	# Initialize the data.
	def __init__(self, SenderName, RecieverName, Address, Date, InvoiceNumber, Notes):

		self.SenderName = SenderName
		self.RecieverName = RecieverName
		self.Address = Address
		self.Date = Date
		self.InvoiceNumber = InvoiceNumber
		self.Items = []
		self.Notes = Notes
	# Add a new items

	def insertItem(self, Name, Quantity, Price, Currency):

		# Having an object of ItemsData.
		item = ItemsData(Name, Quantity, Price, Currency)

		# Insert this object to a list.
		self.Items.append(item)

	# Return the list that have all the items objects.
	def getItems(self):
		return self.Items

	# Returning the data.
	def getData(self):
		# This list will have the data for this Invoice.
		DATA = [self.SenderName, self.RecieverName, self.Address, self.Date, self.InvoiceNumber, self.Notes]
		
		return DATA

	


# This class will have the items that will be added to the invoice
class ItemsData:
	# Initialize the data.
	def __init__(self, itemName, itemQuantity, itemPrice, itemCurrency): 
		self.itemName = itemName
		self.itemQuantity = itemQuantity
		self.itemPrice = itemPrice
		self.itemCurrency = itemCurrency

	def ItemsGet(self):
		return [self.itemName, self.itemQuantity, self.itemPrice, self.itemCurrency]


# TEST.
'''
obj = InvoiceData("samed","sam","add","date","num","mote")
#print(obj) 
obj.insertItem("ja","1","2","1")
print obj.getItems()[0].ItemsGet()

'''