import random
import string
from typing import Literal

from faker import Faker
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_file, session)
from flask.wrappers import Response
from werkzeug.wrappers import Response

from contacts import Archiver, Contact

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
    search: str | None = request.args.get(key="q")
    _: int | str = request.args.get(key="page", default=0)

    try:
        if search is not None and request.headers.get(key='HX-Trigger') == 'search':
            contacts_set: list[Contact] = Contact.search(text=search)
            return render_template(template_name_or_list="rows.html", contacts=contacts_set)

        contacts_set = Contact.all()
        return render_template(template_name_or_list="index.html", contacts=contacts_set, archiver=Archiver.get())
    except Exception as e:
        session.rollback()
        raise e


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
    return send_file(
        path_or_file=archiver.archive_file(),
        mimetype="text/csv",
        as_attachment=True,
        download_name="archive.csv"
    )


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
def contacts_view(contact_id: int = -1) -> str | Response:
    contact: Contact | None = Contact.find(id_=contact_id)
    if contact:
        return render_template(template_name_or_list="show.html", contact=contact)
    else:
        flash(message="Contact not found.")
        return redirect(location="/contacts")


@app.route(rule="/contacts/<int:contact_id>/edit", methods=["GET"])
def contacts_edit_get(contact_id: int = -1) -> str | Response:
    contact: Contact | None = Contact.find(id_=contact_id)
    if contact:
        return render_template(template_name_or_list="edit.html", contact=contact)
    else:
        flash(message="Contact not found.")
        return redirect(location="/contacts")


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
    else:
        flash(message="Contact not found.")
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
    contact: Contact | None = Contact.find(contact_id)
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


@app.route(rule="/mock")
def generate_mock_data() -> Response:
    def generate_email(first_name, last_name) -> str:
        email_domains: list[str] = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "icloud.com",
        "protonmail.com",
        "zoho.com",
        "aol.com",
        "fastmail.com",
        "yandex.com"
    ]
        formats: list[str] = [
            f"{first_name.lower()}.{last_name.lower()}",
            f"{first_name.lower()}_{last_name.lower()}",
            f"{first_name.lower()}{last_name.lower()}",
            f"{last_name.lower()}.{first_name.lower()}",
            f"{first_name.lower()}{random.randint(1, 999)}",
            f"{last_name.lower()}{random.randint(1, 999)}",
            f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}",
            f"{first_name.lower()[0]}{last_name.lower()}",
            f"{first_name.lower()}.{last_name.lower()[0]}",
            f"{''.join(random.choices(population=string.ascii_lowercase, k=8))}"
        ]

        domain: str = random.choice(seq=email_domains)
        username: str = random.choice(seq=formats)
        return f"{username}@{domain}"
    
    count = int(request.args.get('i', 10))

    fake = Faker()

    for _ in range(count):
        first_name: str = fake.first_name()
        last_name: str = fake.last_name()
        email: str = generate_email(first_name, last_name)
        phone: str = fake.phone_number()

        contact = Contact(first=first_name, last=last_name, email=email, phone=phone)
        contact.save()

    flash(message=f"Generated {count} mock contacts.")
    return redirect(location="/contacts")


# Wildcard route
@app.route(rule='/<path:path>')
def catch_all(path) -> Response:
    return redirect(location='/404')

# 404 error route
@app.route(rule='/404')
def page_not_found() -> tuple[str, Literal[404]]:
    return render_template(template_name_or_list='404.html'), 404


# ===========================================================
# JSON Data API
# ===========================================================


@app.route(rule="/api/v0/contacts", methods=["GET"])
def json_contacts() -> Response:
    contacts_set: list[Contact] = Contact.all()
    return jsonify({"contacts": [c.__dict__ for c in contacts_set]})


@app.route(rule="/api/v0/contacts", methods=["POST"])
def json_contacts_new() -> tuple[Response, int] | Response:
    c = Contact(id_=None,
                first=request.form.get(key='first_name'),
                last=request.form.get(key='last_name'),
                phone=request.form.get(key='phone'),
                email=request.form.get(key='email'))
    if c.save():
        return jsonify(c.__dict__)
    return jsonify({"errors": c.errors}), 399


@app.route(rule="/api/v0/contacts/<int:contact_id>", methods=["GET"])
def json_contacts_view(contact_id: int = -1) -> tuple[Response, int] | Response:
    contact: Contact | None = Contact.find(contact_id)
    if contact:
        return jsonify(contact.__dict__)
    else:
        return jsonify({'error': 'Contact not found'}), 404


@app.route(rule="/api/v0/contacts/<int:contact_id>", methods=["PUT"])
def json_contacts_edit(contact_id: int) -> tuple[Response, int] | Response:
    c: Contact | None = Contact.find(id_=contact_id)
    if c:
        c.update(first=request.form['first_name'],
                 last=request.form['last_name'],
                 phone=request.form['phone'],
                 email=request.form['email'])
        if c.save():
            return jsonify(c.__dict__)

        return jsonify({"errors": c.errors}), 399
    else:
        return jsonify({'error': 'Contact not found'}), 404


@app.route(rule="/api/v0/contacts/<int:contact_id>", methods=["DELETE"])
def json_contacts_delete(contact_id: int = -1) -> tuple[Response, int] | Response:
    contact: Contact | None = Contact.find(contact_id)
    if contact:
        contact.delete()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 404


# ===========================================================
# Error Handlers
# ===========================================================


@app.errorhandler(code_or_exception=404)
def handle_not_found(error) -> tuple[str, Literal[404]]:
    return render_template(template_name_or_list='404.html'), 404


@app.errorhandler(code_or_exception=500)
def handle_internal_server_error(error) -> tuple[str, Literal[500]]:
    return render_template(template_name_or_list='500.html'), 500


@app.errorhandler(code_or_exception=Exception)
def handle_exception(error) -> Response | tuple[str, Literal[500]]:
    if request.headers.get('Content-Type') == 'application/json':
        response: Response = jsonify({'error': str(object=error)})
        response.status_code = 500
        return response
    else:
        return render_template(template_name_or_list='500.html'), 500


if __name__ == "__main__":
    app.run()