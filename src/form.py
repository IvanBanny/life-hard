from flask import session, request, redirect

from .app import app

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        session['form_data'] = {
            'country': request.form['country'],
            'dates': request.form['dates'],
        }
        return redirect('/')
    return app.send_static_file("form.html")
