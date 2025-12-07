from flask import Flask, render_template, make_response
import pdfkit

app = Flask(__name__)

@app.route('/report')
def report():
    html = render_template('report.html')
    options = {
        'page-size': 'A4',
        'orientation': 'portrait'
    }
    pdf = pdfkit.from_string(html, False, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=report.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
