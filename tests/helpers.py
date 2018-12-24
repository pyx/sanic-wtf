


# NOTE
# taking shortcut here, assuming there will be only one "string" (the token)
# ever longer than 40.
csrf_token_pattern = '''value="([0-9a-f#]{40,})"'''

def render_form(form, multipart=False):
    if multipart is True:
        multipart = ' enctype="multipart/form-data"'
    return """
    <form action="" method="POST"{}>
    {}
    </form>""".format(multipart, ''.join(str(field) for field in form))
