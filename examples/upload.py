from pathlib import Path
from sanic import Sanic, response
from sanic_wtf import FileAllowed, FileRequired, SanicForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import Length


app = Sanic(__name__)
app.config['SECRET_KEY'] = 'top secret !!!'
app.config['UPLOAD_DIR'] = './uploaded.tmp'


# NOTE
# session should be setup somewhere, SanicWTF expects request.ctx.session is a
# dict like session object.
# For demonstration purpose, we use a mock-up globally-shared session object.
session = {}


@app.middleware('request')
async def add_session(request):
    request.ctx.session = session


class UploadForm(SanicForm):
    image = FileField('Image', validators=[
        FileRequired(), FileAllowed('bmp gif jpg jpeg png'.split())])
    description = StringField('Description', validators=[Length(max=20)])
    submit = SubmitField('Upload')


app.static('/img', app.config.UPLOAD_DIR)


@app.listener('after_server_start')
async def make_upload_dir(app, loop):
    Path(app.config.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
async def index(request):
    form = UploadForm(request)
    if form.validate_on_submit():
        image = form.image.data
        # NOTE: trusting user submitted file names here, the name should be
        # sanitized in production.
        uploaded_file = Path(request.app.config.UPLOAD_DIR) / image.name
        uploaded_file.write_bytes(image.body)
        description = form.description.data or 'no description'
        session.setdefault('files', []).append((image.name, description))
        return response.redirect('/')
    img = '<section><img src="/img/{}"><p>{}</p><hr></section>'
    images = ''.join(img.format(i, d) for i, d in session.get('files', []))
    content = f"""
    <h1>Sanic-WTF file field validators example</h1>
    {images}
    <form action="" method="POST" enctype="multipart/form-data">
      {'<br>'.join(form.csrf_token.errors)}
      {form.csrf_token}
      {'<br>'.join(form.image.errors)}
      {'<br>'.join(form.description.errors)}
      <br> {form.image.label}
      <br> {form.image}
      <br> {form.description.label}
      <br> {form.description(size=20, placeholder="description")}
      <br> {form.submit}
    </form>
    """
    return response.html(content)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
