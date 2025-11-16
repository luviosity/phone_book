from controller import ContactBookController
from model import ContactBookModel
from view import ContactBookView

if __name__ == '__main__':
    model = ContactBookModel('data.json')
    view = ContactBookView()
    controller = ContactBookController(model, view)
    controller.run()