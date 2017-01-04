import os
import re

import jinja2
import webapp2

import hmac
import hashlib
import random
from string import letters

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        self.write("Hello world!")

class RestaurantPage(Handler):
    def get(self):
        restaurants = Restaurant.all()
        self.render("restaurants.html", restaurants = restaurants)


class SignUpPage(Handler):
    def get(self):
        self.render("index.html", 
            username = "",
            password = "",
            verify = "",
            email = "",
            error_username = "",
            error_password = "",
            error_verify = "")

    def post(self):
        username = self.request.get("username", "")
        password = self.request.get("password", "")
        verify = self.request.get("verify", "")
        email = self.request.get("email", "")

        error_username = ""
        error_password = "" 
        error_verify = ""
        error_email = ""

        valid_username = self.verify_username(username)
        valid_password = self.verify_password(password)
        valid_verify = self.verify_verify(password, verify)
        valid_email = self.verify_email(email)

        if not valid_username:
            error_username = "That's not a username."

        if not valid_password:
            error_password = "That's not a password"
            password = ""
            verify = ""

        if not valid_verify:
            error_verify = "That's not a match"
            password = ""
            verify = ""

        if not valid_email:
            error_email = "That's not a email"

        if valid_username and valid_password and valid_verify and valid_email:

            if User.by_name(username):
                error_username = "User already exist"
                self.render("index.html",
                    username = username,
                    password = password,
                    verify = verify,
                    email = email,
                    error_username = error_username,
                    error_password = error_password,
                    error_verify = error_verify,
                    error_email = error_email)
            else:
                # Write to DB
                user = User.sign_up(username, password, email)
                user.put()

                # Add cookie
                self.set_cookie("user_id", user.key().id())

                # Redirect
                self.redirect("/welcome")
        else:
            self.render("index.html",
                username = username,
                password = password,
                verify = verify,
                email = email,
                error_username = error_username,
                error_password = error_password,
                error_verify = error_verify,
                error_email = error_email)


class newPage(Handler):
    def render_page(self, error = ""):
        self.render("new.html", error = error)

    def get(self):
        self.render_page()

    def post(self):
        name = self.request.get("name")

        if name:
            r = Restaurant(name = name)
            r.put()

            self.redirect("/restaurants")
        else:
            error = "Invalid input"
            self.render_page(error)


class EditPage(Handler):
    def render_page(self, name = "", error = ""):

        self.render("edit.html", name = name, error = error)

    def get(self, rid):

        if rid:
            rid = int(rid)
            r = Restaurant.get_by_id(rid)
            self.render_page(r.name, "")
        else:
            self.redirect("/restaurants")

    def post(self, rid):

        newName = self.request.get("newName")

        if newName and rid:
            r = Restaurant.get_by_id(int(rid))
            r.name = newName
            r.put()

            self.redirect("/restaurants")
        else:
            error = "Invalid input"
            self.render_page("", error)


class DeletePage(Handler):
    def get(self, rid):
        if rid:
            rid = int(rid)
            r = Restaurant.get_by_id(rid)
            self.render("delete.html", name = r.name)

    def post(self, rid):
        if rid:
            r = Restaurant.get_by_id(int(rid))
            r.delete()

            self.redirect("/restaurants")


class Restaurant(db.Model):
    name = db.StringProperty(required = True)

    @classmethod
    def restaurant_key(cls, group = 'default'):
        return db.Key.from_path('restaurant', group)

    @classmethod
    def by_id(cls, rid):
        return Restaurant.get_by_id(rid, parent = Restaurant.restaurant_key())

    @classmethod
    def by_name(cls, name):
        r = Restaurant.all().filter('name =', name).get()
        return r



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/restaurants', RestaurantPage),
    ('/new', newPage),
    (r'/(\d+)/edit', EditPage),
    (r'/(\d+)/delete', DeletePage)
    ], debug=True)
