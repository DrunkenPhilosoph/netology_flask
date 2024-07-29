from flask import Flask, request, jsonify, Response
from flask.views import MethodView
from models import Session, AdwBase

app = Flask(__name__)


@app.before_request
def before_request():
    session = Session()
    request.session = session

@app.after_request
def after_request(response: Response):
    request.session.close()
    return response

class HttpError(Exception):

    def __init__(self, code: int, message: str | dict):
        self.code = code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    resp_err = jsonify({"error": error.message})
    resp_err.code = error.code
    return resp_err

def get_adw(adw_id):
    adw = request.session.get(AdwBase, adw_id)
    if adw is None:
        raise HttpError(404, f"Adw not found: {adw_id}")
    return adw

def add_adw(adw: AdwBase):
    request.session.add(adw)
    request.session.commit()
    return adw

class AdwView(MethodView):

    @property
    def session(self) -> Session:
        return request.session

    def get(self, adw_id):
        adw = get_adw(adw_id)
        return jsonify(adw.json)

    def post(self):
        json_data = request.json
        title = json_data['title']
        description = json_data['description']
        owner = json_data['owner']
        adw = AdwBase(title, description, owner)
        self.session.add(adw)
        self.session.commit()
        return jsonify(adw.json)

    def patch(self, adw_id):
        json_data = request.json
        adw = get_adw(adw_id)
        for field, value in json_data.items():
            setattr(adw, field, value)
        adw = add_adw(adw)
        return jsonify(adw.json)

    def delete(self, adw_id):
        user = get_adw(adw_id)
        self.session.delete(user)
        self.session.commit()
        return jsonify({"deleted": True})

user_view = AdwView.as_view("adw")

app.add_url_rule("/adw/", view_func=user_view, methods=["POST"])
app.add_url_rule("/adw/<int:adw_id>/", view_func=user_view, methods=["GET", "PATCH", "DELETE"])
app.run()
