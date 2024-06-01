# Demo Hypermedia-Driven Multi-Page Application

## Contact.app

### Stack

|                    |        |
|--------------------|--------|
|Programming Language| Python |
|Web Framework       | Flask  |
|Templating Language | Jinja  |


### Installation (Windows):

- [ ] Install virtual environment: `py -3 -m venv .venv`
- [ ] Activate `.venv\Scripts\activate`
- [ ] Install dependencies `pip install -r requirements.txt`
- [ ] Start server `flask --app contact_app.py run`


## What is the simplest thing that could possibly work?

This document provides an overview of web hypermedia systems, focusing on the
RESTful network architecture where the server and client communicate using
hypermedia.

- Powerful, interactive, and simple aproach.
- Tolerant of content and API changes.
- Leverages web browser features.
- Server-side application value
- Flexible server-side logic, poly-linguistic and multi-framework
- Universal web language
- API versioning not necessary

**Hypermedia On Whatever you'd Like (HOWL)**
EXAMPLES: Python, Lisp, OCaml, Haskell, Julia, Nim, Ruby, JavaScript

## Definitions

### Hypermedia System

A system that adheres to RESTful network architecture. Made up of:

- a hypermedia, e.g. HTML
- a network protocol, e.g. HTTPS
- a server providing a hypermedia API responding to HTTP requests with HTTP responses,
- a client that processes hypermedia responses, e.g. a web browser, and takes advantage of the uniform interface.

See: Roy Fielding, Architectural Styles and the Design of Network-Based Software Architectures.

### Hypermedia

Hypermedia is a dynamic, non-linear, branching structure that enables
communication between points within the media with embedded hypermedia controls.

**Example:** Hypertext Markup Language (HTML)

### Hypermedia Control

A hypermedia control is a self-contained element within a hypermedia system
that encodes and manages interactions by directly incorporating all the
necessary information required for the interaction within its own structure,
without relying on external resources.

This allows the hypermedia control to govern and facilitate communication
between the user and the system, often involving exchanges with a remote server.

The self-contained nature of the hypermedia control ensures that the interaction
can be initiated and completed solely based on the information contained within
the control itself.

**Example:** HTML anchor (`<a>`) and form (`<form>`) tags.

### Uniform Resource Locator (URL)

A string referencing a network location from where a resource can be retrieved,
and how it can be retrieved.


```text
[scheme]://[userinfo]@[host]:[port][path]?[query]#[fragment]
```

### Representational State Transfer (REST)

a network architecture, a technique to architect a distributed system
associated with HTML and Hypermedia

Constraints on the behvaior of a RESTful system

- [ ] Is it a client-server architecture?
- [ ] Is it stateless? Does every request encapsulate all information necessary to respond to the request, with no side state or context stored on neither the client nor the server?
- [ ] Does it allow for cahcing with explicit information on the cachability of responses for future requests of the same resource?
- [ ] Does it have a *uniform interface* (Identification of resources, manipulation of resources through representations, self-descriptive messages, and hypermedia as the engine of application state)?
- [ ] Is it a layered system?
- [ ] *OPTIONAL* Does it allow for Code-On-Demand, i.e., scripting?

a browser and Apache Web Server communicating through a network connection.
Session cookies violate the stateless constraint.
HTTP caching
URL as ID.
Response has all information necessary to display and operate on the data being represented.

```html
<html lang="en">
<!-- ... -->
<body>
    <h1> Response </h1>
    <div>
        <div> Email: contact1@email.com </div>
    </div>
    <div>
        <p>
            <a href="/contacts/1/archive"> Archive </a>
        </p>
    </div>
</body>

</html>

```


## Navigating Between Server Resources

To navigate between server resources, an HTTP GET request is sent with metadata
to the URL specified in the `href` attribute. The page content and navigation
bar are updated with the URL and HTML from the HTTP response.


**Example:**
```html
<a href="#">hyperlink</a>
```

## Updating a Server Resource State

To update a server resource state, an HTML form is used. When the form is
submitted, it sends an HTTP POST request to the specified `action` URL, with
the data encoded in the form fields.

**Example:**
```html
<form action="/create" method="POST">
    <select name="choice">
        <option value="first">First Value</option>
        <option value="second" selected>Second Value</option>
        <option value="third">Third Value</option>
    </select>
    <button>create</button>
</form>
```

## htmx-powerd button

```html
<div id="contact-ui"></div>
<button hx-get="/contacts/1" hx-target="#contact-ui"> Fetch </button>
```

HTTP response
```html
<details>
    <h2>Contact 1</h2>
    <div>
        <a href="mailto:contact@email.com"> E-mail </a>
    </div>
</details>
```

## References

1. C. Gross, A. Stepinski, D. Akşimşek, and W. Talcott, *Hypermedia Systems*. Independently published, 2023.
2. Vannevar Bush, *As We May Think*. 1945. Available: <https://archive.org/details/as-we-may-think>
3. https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
4. https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm#sec_5_1_6
5. https://html.spec.whatwg.org/multipage/
