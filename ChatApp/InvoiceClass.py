# Implementing 2 classes that have all data needed for invoicing.
class InvoiceData: 

	# Initialize the data.
	def __init__(self, SenderName, RecieverName, Address, Date, InvoiceNumber, Notes):

		self.SenderName = SenderName
		self.RecieverName = RecieverName
		self.Address = Address
		self.Date = Date
		self.InvoiceNumber = InvoiceNumber
		self.Notes = Notes


	# Returning the data.
	def getData(self):
		# This list will have the data for this Invoice.
		DATA = [self.SenderName, self.RecieverName, self.Address, self.Date, self.InvoiceNumber, self.Notes]
		
		return DATA


# This class will have the items that will be added to the invoice
class ItemsData:
	# Initialize the data.
	def __init__(self): 
		self.itemName = []
		self.itemQuantity = []
		self.itemPrice = []
		self.itemCurrency = []

	# Add a new item.
	def insert(self, Name, Quantity, Price, Currency):
		self.itemName.append(Name)
		self.itemQuantity.append(Quantity)
		self.itemPrice.append(Price)
		self.itemCurrency.append(Currency)

	# Deleting item.
	# Will be implemented in another version.
	def Delete(self, itemNumber):
		# will have to add item id.
		pass

	# Returning the items.
	def getData(self):
		# This multiD list will have the data for the items.
		DATA = [self.itemName, self.itemQuantity, self.itemPrice, self.itemCurrency]
		
		return DATA