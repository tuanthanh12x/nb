from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter

def export_to_pdf(data):
    html = "<h2>User List</h2><table border='1' cellspacing='0'><tr><th>ID</th><th>Username</th></tr>"
    for row in data:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>"
    html += "</table>"

    doc = QTextDocument()
    doc.setHtml(html)

    printer = QPrinter()
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName("exported_users.pdf")

    doc.print_(printer)
    print("PDF exported.")
