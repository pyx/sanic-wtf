from datetime import datetime
from sanic import Sanic, response
from sanic_wtf import SanicForm
from wtforms import SubmitField, TextField
from wtforms.validators import DataRequired, Length


app = Sanic(__name__)
app.config['SECRET_KEY'] = 'top secret !!!'


# NOTE
# session should be setup somewhere, SanicWTF expects request['session'] is a
# dict like session object.
# For demonstration purpose, we use a mock-up session object by providing our
# own get_csrf_context
session = {}
@app.middleware('request')
async def add_session(request):
    request['session'] = session


class FeedbackForm(SanicForm):
    note = TextField('Note', validators=[DataRequired(), Length(max=40)])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
async def index(request):
    form = FeedbackForm(request)
    if request.method == 'POST' and form.validate():
        note = form.note.data
        msg = '{} - {}'.format(datetime.now(), note)
        session.setdefault('fb', []).append(msg)
        return response.redirect('/')
    # NOTE: trusting user input here, never do that in production
    feedback = ''.join('<p>{}</p>'.format(m) for m in session.get('fb', []))
    # Ah, f string, so, python 3.6, what do you expect from someone brave
    # enough to use sanic... :)
    content = f"""
    <h1>Form with CSRF Validation</h1>
    <p>Try <a href="/fail">form</a> that fails CSRF validation</p>
    {feedback}
    <form action="" method="POST">
      {'<br>'.join(form.hidden_tag.errors)}
      {form.hidden_tag()}
      {'<br>'.join(form.note.errors)}
      <br>
      {form.note(size=40, placeholder="say something..")}
      {form.submit}
    </form>
    """
    return response.html(content)


@app.route('/fail', methods=['GET', 'POST'])
async def fail(request):
    form = FeedbackForm(request)
    if request.method == 'POST' and form.validate():
        note = form.note.data
        msg = '{} - {}'.format(datetime.now(), note)
        session.setdefault('fb', []).append(msg)
        return response.redirect('/fail')
    feedback = ''.join('<p>{}</p>'.format(m) for m in session.get('fb', []))
    content = f"""
    <h1>Form which fails CSRF Validation</h1>
    <p>This is the same as this <a href="/">form</a> except that CSRF
    validation always fail because we did not render the hidden csrf token</p>
    {feedback}
    <form action="" method="POST">
      {'<br>'.join(form.hidden_tag.errors)}
      {'<br>'.join(form.note.errors)}
      <br>
      {form.note(size=40, placeholder="say something..")}
      {form.submit}
    </form>
    """
    return response.html(content)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
