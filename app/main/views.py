from .import main
from ..auth.forms import LoginForm
from ..models import *
from ..tools.database import db




@main.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@main.route('/<path:path>', methods=['GET', 'POST'])
def pages(path):
    """
    Catch all requests, but without other's registred routes
    """

    auth_form = None
    if not current_user.is_authenticated:
      auth_form = LoginForm()

    return render_template(
        page_tmpl, auth_form=auth_form
    )

