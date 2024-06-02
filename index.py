
from flask import (
    Flask, abort, redirect, render_template, request, flash, jsonify, send_file
)
from werkzeug.wrappers import Response
from contacts import Contact, Archiver


# ========================================================
# Flask App
# ========================================================

app = Flask(import_name=__name__)

app.secret_key = b'hypermedia rocks'


@app.route(rule="/")
def index() -> Response:
    return redirect(location="/contacts")


@app.route(rule="/contacts")
def contacts() -> str:
    try:
        search: str | None = request.args.get(key="q")
        _: int | str = request.args.get(key="page", default=0)
        if search is not None:
            contacts_set: list[Contact] = Contact.search(text=search)
            if request.headers.get(key='HX-Trigger') == 'search':
                return render_template(template_name_or_list="rows.html", contacts=contacts_set)
        else:
            contacts_set = Contact.all()
        return render_template(template_name_or_list="index.html", contacts=contacts_set, archiver=Archiver.get())
    except Exception as e:
        app.logger.error(msg=f"Exception occurred: {str(object=e)}")
        abort(code=500, description="An internal server error occurred.")


@app.route(rule="/contacts/archive", methods=["POST"])
def start_archive() -> str:
    archiver: Archiver = Archiver.get()
    archiver.run()
    return render_template(template_name_or_list="archive_ui.html", archiver=archiver)


@app.route(rule="/contacts/archive", methods=["GET"])
def archive_status() -> str:
    archiver: Archiver = Archiver.get()
    return render_template(template_name_or_list="archive_ui.html", archiver=archiver)


@app.route(rule="/contacts/archive/file", methods=["GET"])
def archive_content() -> Response:
    archiver: Archiver = Archiver.get()
    return send_file(path_or_file=archiver.archive_file(), mimetype="archive.json", as_attachment=True)


@app.route(rule="/contacts/archive", methods=["DELETE"])
def reset_archive() -> str:
    archiver: Archiver = Archiver.get()
    archiver.reset()
    return render_template(template_name_or_list="archive_ui.html", archiver=archiver)


@app.route(rule="/contacts/count")
def contacts_count() -> str:
    count: int = Contact.count()
    return "(" + str(object=count) + " total Contacts)"


@app.route(rule="/contacts/new", methods=['GET'])
def contacts_new_get() -> str:
    return render_template(template_name_or_list="new.html", contact=Contact())


@app.route(rule="/contacts/new", methods=['POST'])
def contacts_new() -> Response | str:
    c = Contact(id_=None,
                first=request.form['first_name'],
                last=request.form['last_name'],
                phone=request.form['phone'],
                email=request.form['email'])
    if c.save():
        flash(message="Created New Contact!")
        return redirect(location="/contacts")
    
    return render_template(template_name_or_list="new.html", contact=c)


@app.route(rule="/contacts/<int:contact_id>")
def contacts_view(contact_id: int = -1) -> str:
    contact: Contact | None = Contact.find(id_=contact_id)
    return render_template(template_name_or_list="show.html", contact=contact)


@app.route(rule="/contacts/<int:contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id: int = -1) -> str:
    contact: Contact | None = Contact.find(id_=contact_id)
    return render_template(template_name_or_list="edit.html", contact=contact)


@app.route(rule="/contacts/<int:contact_id>/edit", methods=["POST"])
def contacts_edit_post(contact_id: int = -1) -> Response | str:
    c: Contact | None = Contact.find(id_=contact_id)
    if c:
        c.update(first=request.form['first_name'],
                 last=request.form['last_name'],
                 phone=request.form['phone'],
                 email=request.form['email'])
        if c.save():
            flash(message="Updated Contact!")
            return redirect(location=f"/contacts/{contact_id}")
        return render_template(template_name_or_list="edit.html", contact=c)
    return redirect(location="/contacts")


@app.route(rule="/contacts/<int:contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id: int = -1) -> str:
    c: Contact | None = Contact.find(id_=contact_id)
    if c:
        c.email = request.args.get(key='email', default='')
        _: bool = c.validate()
        return c.errors.get('email', '')
 
    return ''


@app.route(rule="/contacts/<int:contact_id>", methods=["DELETE"])
def contacts_delete(contact_id: int = -1) -> Response | str:
    contact: Contact | None = Contact.find(id_=contact_id)
    if contact:
        contact.delete()
        if request.headers.get(key='HX-Trigger') == 'delete-btn':
            flash(message="Deleted Contact!")
            return redirect(location="/contacts", code=302)
        return ""
    return ""


@app.route(rule="/contacts/", methods=["DELETE"])
def contacts_delete_all() -> str:
    contact_ids = list(map(int, request.form.getlist(key="selected_contact_ids")))
    for contact_id in contact_ids:
        contact: Contact | None = Contact.find(id_=contact_id)
        if contact:
            contact.delete()
    flash(message="Deleted Contacts!")
    contacts_set: list[Contact] = Contact.all(page=0)
    archiver: Archiver = Archiver.get()
    return render_template(template_name_or_list="index.html", contacts=contacts_set, archiver=archiver)


# ===========================================================
# JSON Data API
# ===========================================================

@app.route(rule="/api/v0/contacts", methods=["GET"])
def json_contacts() -> Response:
    contacts_set: list[Contact] = Contact.all()
    return jsonify({"contacts": [c.__dict__ for c in contacts_set]})



@app.route(rule="/api/v0/contacts", methods=["POST"])
def json_contacts_new() -> tuple[Response, int] | Response:
    c = Contact(id_=None, first=request.form.get(key='first_name'), last=request.form.get('last_name'), phone=request.form.get(key='phone'),
                email=request.form.get(key='email'))
    if c.save():
        return jsonify(c.__dict__)
    
    return jsonify({"errors": c.errors}), 399


@app.route(rule="/api/v0/contacts/<int:contact_id>", methods=["GET"])
def json_contacts_view(contact_id: int = -1) -> tuple[Response, int] | Response:
    contact: Contact | None = Contact.find(contact_id)
    if contact:
        return jsonify(contact.__dict__)
    
    return jsonify({}), 404


@app.route(rule="/api/v0/contacts/<int:contact_id>", methods=["PUT"])
def json_contacts_edit(contact_id: int) -> tuple[Response, int] | Response:
    c: Contact | None = Contact.find(id_=contact_id)
    if c:
        c.update(first=request.form['first_name'], last=request.form['last_name'], phone=request.form['phone'], email=request.form['email'])
        if c.save():
            return jsonify(c.__dict__)
        
        return jsonify({"errors": c.errors}), 399
    
    return jsonify({}), 404


@app.route(rule="/api/v0/contacts/<int:contact_id>", methods=["DELETE"])
def json_contacts_delete(contact_id: int = -1) -> tuple[Response, int] | Response:
    contact: Contact | None = Contact.find(contact_id)
    if contact:
        contact.delete()
        return jsonify({"success": True})
    
    return jsonify({"success": False}), 404


if __name__ == "__main__":
    app.run()
