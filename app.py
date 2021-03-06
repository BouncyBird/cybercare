from flask import Flask, render_template, request, redirect, url_for, flash, session, Markup
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, IntegerField, DecimalField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms.fields.core import Field
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user, LoginManager
from flask_mail import Message, Mail
from flask_mobility import Mobility
from flask_ckeditor import CKEditor, CKEditorField
import ast
import requests
import json
from better_profanity import profanity
import html2text
#from pyzbar.pyzbar import decode
#from PIL import Image

disease_links = {
    'Influenza': 'https://www.cdc.gov/flu/treatment/takingcare.htm',
    'Ebola': 'https://www.cdc.gov/vhf/ebola/index.html',
    'Common Cold': 'https://www.cdc.gov/features/rhinoviruses/index.html',
    'Covid-19': 'https://www.cdc.gov/coronavirus/2019-ncov/if-you-are-sick/steps-when-sick.html',
    'Malaria': 'https://www.cdc.gov/parasites/malaria/index.html',
    'Cholera': 'https://www.cdc.gov/cholera/treatment/index.html',
    'Measles': 'https://www.cdc.gov/measles/symptoms/signs-symptoms.html',
    'Heart Attack': 'https://www.cdc.gov/heartdisease/heart_attack.htm',
    'Allergic Reaction': ''
}

disease_pages = {
    'Influenza': 'https://www.cdc.gov/flu/',
    'Ebola': 'https://www.cdc.gov/vhf/ebola/index.html',
    'Common Cold': 'https://www.cdc.gov/features/rhinoviruses/index.html',
    'Covid-19': 'https://www.coronavirus.gov/',
    'Malaria': 'https://www.cdc.gov/parasites/malaria/index.html',
    'Cholera': 'https://www.cdc.gov/cholera/index.html',
    'Measles': 'https://www.cdc.gov/measles/index.html',
    'Heart Attack': 'https://www.cdc.gov/heartdisease/heart_attack.htm',
    'Allergic Reaction': ''
}

disease_extra = {
    'Influenza': '',
    'Ebola': 'Ebola can be extremely deadly. <a href="https://www.cdc.gov/vhf/ebola/symptoms/index.html">Symptoms of Ebola</a>. If you think you have Ebola, see a doctor immediately.',
    'Common Cold': '',
    'Covid-19': '',
    'Malaria': '',
    'Cholera': '',
    'Measles': '',
    'Heart Attack': '',
    'Allergic Reaction': ''
}

app = Flask(__name__)

app.config['SECRET_KEY'] = '1a0303f517b1a1c15d4637c83be89ebc'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lc46NEaAAAAACT9wezgGCyNFGxld_lLC6y8Zko1'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lc46NEaAAAAABA089xpPhOB2e-MZB-EsoOyXXLO'
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'getcybercare@gmail.com'
app.config['MAIL_PASSWORD'] = "asdfghjkl;'!@#$%^&*()"
Mobility(app)
ckeditor = CKEditor()
mail = Mail()
ckeditor.init_app(app)
mail.init_app(app)


def no_dispose(form, field):
    if requests.get(f'https://disposable.debounce.io/?email={field.data}').json()['disposable'] == 'true':
        raise ValidationError('Disposable Emails are not allowed')


def no_profane(form, field):
    if profanity.contains_profanity(html2text.html2text(field.data)):
        raise ValidationError('We strictly prohibit profane messages')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(
        min=2, max=20)], render_kw={"placeholder": "Jane Doe"})
    email = StringField('Email', validators=[DataRequired(), Email(
    ), no_dispose], render_kw={"placeholder": "example@company.com"})
    content = CKEditorField('Your Message', validators=[
                            DataRequired(), no_profane])
    recaptcha = RecaptchaField()
    submit = SubmitField('Message')


class DiseaseForm(FlaskForm):
    gender = SelectField('Gender', choices=[
                         ('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    diarreah_vomit = BooleanField('Diarreah and Vomit')
    body_aches = BooleanField('Body Aches')
    runny_nose = BooleanField('Runny Nose')
    fever = BooleanField('Fever')
    fatigue = BooleanField('Fatigue')
    hemorrhage = BooleanField('Hemorrhage')
    coughing = BooleanField('Coughing')
    shortness_of_breath = BooleanField('Shortness of Breath')
    swollen_lymph_nodes = BooleanField('Swollen Lymph')
    headaches = BooleanField('Headaches')
    red_eyes = BooleanField('Red Eyes')
    rapid_heart_rate = BooleanField('Rapid Heart Rate')
    submit = SubmitField('Check Disease')


class NutriSearchForm(FlaskForm):
    query = StringField('Search Term or UPC', validators=[
                        DataRequired()], render_kw={"placeholder": "Apple"})
    alcohol_free = BooleanField('Alcohol Free')
    celery_free = BooleanField('Celery Free')
    crustacean_free = BooleanField('Crustacean Free')
    dairy_free = BooleanField('Dairy Free')
    egg_free = BooleanField('Egg Free')
    fish_free = BooleanField('Fish Free')
    fodmap_free = BooleanField('FODMAP Free')
    gluten_free = BooleanField('Gluten Free')
    kosher = BooleanField('Kosher')
    lupine_free = BooleanField('Lupine Free')
    mustard_free = BooleanField('Mustard Free')
    No_oil_added = BooleanField('No Oil Added')
    low_sugar = BooleanField('Low Sugar')
    paleo = BooleanField('Paleo')
    peanut_free = BooleanField('Peanut Free')
    pecatarian = BooleanField('Pescatarian')
    pork_free = BooleanField('Pork Free')
    red_meat_free = BooleanField('Red Meat Free')
    sesame_free = BooleanField('Sesame Free')
    shellfish_free = BooleanField('Shellfish Free')
    soy_free = BooleanField('Soy Free')
    tree_nut_free = BooleanField('Tree Nut Free')
    vegan = BooleanField('Vegan')
    vegetarian = BooleanField('Vegetarian')
    wheat_free = BooleanField('Wheat Free')
    calorie_filter1 = IntegerField(
        'Minimum Calories', validators=[Optional()])
    calorie_filter2 = IntegerField(
        'Maximum Calories', validators=[Optional()])
    category = SelectField('Category', choices=[('both', 'Both'), ('generic-foods', 'Generic Foods'), ('generic-meals',
                           'Generic Meals'), ('packaged-foods', 'Packaged Foods'), ('fast-foods', 'Fast Foods')])
    submit = SubmitField('Search')


class ReciSearchForm(FlaskForm):
    query = StringField('Search Term', validators=[
                        DataRequired()], render_kw={"placeholder": "Chicken"})
    alcohol_free = BooleanField('Alcohol Free')
    celery_free = BooleanField('Celery Free')
    crustacean_free = BooleanField('Crustacean Free')
    dairy_free = BooleanField('Dairy Free')
    egg_free = BooleanField('Egg Free')
    fish_free = BooleanField('Fish Free')
    fodmap_free = BooleanField('FODMAP Free')
    gluten_free = BooleanField('Gluten Free')
    kosher = BooleanField('Kosher')
    lupine_free = BooleanField('Lupine Free')
    mustard_free = BooleanField('Mustard Free')
    No_oil_added = BooleanField('No Oil Added')
    low_sugar = BooleanField('Low Sugar')
    paleo = BooleanField('Paleo')
    peanut_free = BooleanField('Peanut Free')
    pecatarian = BooleanField('Pescatarian')
    pork_free = BooleanField('Pork Free')
    red_meat_free = BooleanField('Red Meat Free')
    sesame_free = BooleanField('Sesame Free')
    shellfish_free = BooleanField('Shellfish Free')
    soy_free = BooleanField('Soy Free')
    tree_nut_free = BooleanField('Tree Nut Free')
    vegan = BooleanField('Vegan')
    vegetarian = BooleanField('Vegetarian')
    wheat_free = BooleanField('Wheat Free')
    calorie_filter1 = IntegerField(
        'Minimum Calories(Per serving)', validators=[Optional()])
    calorie_filter2 = IntegerField(
        'Maximum Calories(Per serving)', validators=[Optional()])
    time_filter1 = IntegerField(
        'Minimum Minutes(Prep and Cooking)', validators=[Optional()])
    time_filter2 = IntegerField(
        'Maximum Minutes(Prep and Cooking)', validators=[Optional()])
    max_ingredients = IntegerField(
        'Maximum Ingredients', validators=[Optional()])
    submit = SubmitField('Search')


class BMIForm(FlaskForm):
    age = DecimalField(
        'Age(Years)', places=2, validators=[Optional()])
    weight = DecimalField(
        'Weight(Pounds)', places=2, validators=[Optional()])
    height = DecimalField(
        'Height(Inches)', places=2, validators=[Optional()])
    submit = SubmitField('Calculate')


class IdealWeightForm(FlaskForm):
    gender = SelectField('Gender', choices=[
                         ('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    height = DecimalField(
        'Height(Inches)', places=2, validators=[Optional()])
    submit = SubmitField('Calculate')


"""class NutriScanForm(FlaskForm):
    image = FileField('Image of Barcode', validators=[FileRequired()])
    submit = SubmitField('Search')"""


def get_prediction(data={"Diarreah & Vomit": "No", "Body Aches": "Yes", "Runny nose": "No", "Fever": "Yes", "Fatigue": "Yes", "Hemorrhage": "No", "Coughing": "No", "Shortness of Breath": "No", "Swollen Lymph Nodes": "No", "Headaches": "Yes", "Red yes": "No", "Rapid Heart Rate": "No", "Gender": "Male"}):
    url = 'https://yyuen2447j.execute-api.us-east-1.amazonaws.com/Predict/05a0f3ef-0b87-4eec-bff5-e5addcd8ec61'
    r = requests.post(url, data=json.dumps(data))
    print(r.text)
    response = eval(eval(
        getattr(r, '_content').decode("utf-8"))['body'])
    return response


@app.route('/')
def home():
    return render_template("home.html", route='home')


@app.route('/about')
def about():
    return render_template("about.html", title="About", route='about')


@app.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        tlen = len(form.name.data) + len(form.email.data) + 3
        msg = Message(f'New Message from {form.name.data} - {form.email.data}', sender=form.email.data, recipients=[
                      'djonimuresan@gmail.com', 'eshan.nalajala@gmail.com', 'aarnavkumta09@gmail.com', 'matthewcharlotteyang@gmail.com'])
        msg.html = f'<h4>{form.name.data} - {form.email.data}<br>{"=" * tlen}<br></h4>' + \
            form.content.data
        mail.send(msg)
        flash('Message Sent!', 'success')
        return redirect(url_for('home'))
    return render_template("contact.html", title="Contact Us", form=form, route='contact')


def conv(item):
    if item == True:
        val = 'Yes'
    elif item == False:
        val = 'No'

    return val


@app.route('/disease_check', methods=["GET", "POST"])
def disease_check():
    form = DiseaseForm()
    if form.validate_on_submit():
        dd = {"Diarreah & Vomit": conv(form.diarreah_vomit.data), "Body Aches": conv(form.body_aches.data), "Runny nose": conv(form.runny_nose.data), "Fever": conv(form.fever.data), "Fatigue": conv(form.fatigue.data), "Hemorrhage": conv(form.hemorrhage.data), "Coughing": conv(
            form.coughing.data), "Shortness of Breath": conv(form.shortness_of_breath.data), "Swollen Lymph Nodes": conv(form.swollen_lymph_nodes.data), "Headaches": conv(form.headaches.data), "Red yes": conv(form.red_eyes.data), "Rapid Heart Rate": conv(form.rapid_heart_rate.data), "Gender": form.gender.data}
        print(dd)
        result = get_prediction(data=dd)
        if result['predicted_label'] == "You're all good":
            flash(result['predicted_label'], 'success')
        elif result['predicted_label'] == 'Youre dead':
            flash(result['predicted_label'], 'danger')
        elif result['predicted_label'] == 'Ebola':
            flash(Markup(
                f'You might have <a href="{disease_pages[result["predicted_label"]]}"><b>{result["predicted_label"]}</b></a>. {disease_extra[result["predicted_label"]]} <a href="{disease_links[result["predicted_label"]]}">Next Steps and More Info</a>'), 'danger')
        else:
            flash(Markup(
                f'You might have <a href="{disease_pages[result["predicted_label"]]}"><b>{result["predicted_label"]}</b></a>. {disease_extra[result["predicted_label"]]} <a href="{disease_links[result["predicted_label"]]}">Next Steps and More Info</a>'), 'info')
    return render_template("disease.html", title="Disease Checker", form=form, route='disease_check')


@app.route('/clinics')
def clinics():
    url = 'https://raw.githubusercontent.com/BouncyBird/hhoster/main/2021-05-08%20(7).png'
    return render_template("clinics.html", url=url, route='clinics')


@app.route('/routines')
def routines():
    return render_template("routines.html", title='Routines', route='routines')


@app.route('/routines/stretching')
def stretching():
    return render_template("stretching.html", title='Stretching Routines', route='stretching')


@app.route('/routines/skincare')
def skincare():
    return render_template("skincare.html", title='Skincare Routines', route='skincare')


@app.route('/routines/simple_exercises')
def simple_exercises():
    return render_template("exercises.html", title='Simple Exercises', route='exercises')


def convn(item, protocol):
    if item == True:
        val = f'&health={protocol}'
    elif item == False:
        val = ''
    return val


@app.route('/nutrisearch', methods=["GET", "POST"])
def nutrisearch():
    form = NutriSearchForm()
    if form.validate_on_submit():
        if form.calorie_filter1.data != None and form.calorie_filter2.data != None:
            calfilt = f'&calories={form.calorie_filter1.data}-{form.calorie_filter2.data}'
        elif form.calorie_filter1.data != None and form.calorie_filter2.data == None:
            calfilt = f'&calories={form.calorie_filter1.data}%2B'
        elif form.calorie_filter1.data == None and form.calorie_filter2.data != None:
            calfilt = f'&calories=0-{form.calorie_filter2.data}'
        elif form.calorie_filter1.data == None and form.calorie_filter2.data == None:
            calfilt = ''
        if form.category.data == 'both':
            catfilt = ''
        elif form.category.data != 'both':
            catfilt = f'&category={form.category.data}'
        if form.query.data.isnumeric():
            r = requests.get(f"https://api.edamam.com/api/food-database/v2/parser?app_id=104d2abe&app_key=621914ce184adee2580e7970b7ca5148&upc={form.query.data}{convn(form.alcohol_free.data, 'alcohol-free')}{convn(form.celery_free.data, 'celery-free')}{convn(form.crustacean_free.data, 'crustacean-free')}{convn(form.dairy_free.data, 'dairy-free')}{convn(form.egg_free.data, 'egg-free')}{convn(form.fish_free.data, 'fish-free')}{convn(form.fodmap_free.data, 'fodmap-free')}{convn(form.gluten_free.data, 'gluten-free')}{convn(form.kosher.data, 'kosher')}{convn(form.lupine_free.data, 'lupine-free')}{convn(form.mustard_free.data, 'mustard-free')}{convn(form.No_oil_added.data, 'No-oil-added')}{convn(form.low_sugar.data, 'low-sugar')}{convn(form.paleo.data, 'paleo')}{convn(form.peanut_free.data, 'peanut-free')}{convn(form.pecatarian.data, 'pecatarian')}{convn(form.pork_free.data, 'pork-free')}{convn(form.red_meat_free.data, 'red-meat-free')}{convn(form.sesame_free.data, 'sesame-free')}{convn(form.shellfish_free.data, 'shellfish-free')}{convn(form.soy_free.data, 'soy-free')}{convn(form.tree_nut_free.data, 'tree-nut-free')}{convn(form.vegan.data, 'vegan')}{convn(form.vegetarian.data, 'vegetarian')}{convn(form.wheat_free.data, 'wheat-free')}{calfilt}{catfilt}")
        else:
            r = requests.get(f"https://api.edamam.com/api/food-database/v2/parser?app_id=104d2abe&app_key=621914ce184adee2580e7970b7ca5148&ingr={form.query.data}{convn(form.alcohol_free.data, 'alcohol-free')}{convn(form.celery_free.data, 'celery-free')}{convn(form.crustacean_free.data, 'crustacean-free')}{convn(form.dairy_free.data, 'dairy-free')}{convn(form.egg_free.data, 'egg-free')}{convn(form.fish_free.data, 'fish-free')}{convn(form.fodmap_free.data, 'fodmap-free')}{convn(form.gluten_free.data, 'gluten-free')}{convn(form.kosher.data, 'kosher')}{convn(form.lupine_free.data, 'lupine-free')}{convn(form.mustard_free.data, 'mustard-free')}{convn(form.No_oil_added.data, 'No-oil-added')}{convn(form.low_sugar.data, 'low-sugar')}{convn(form.paleo.data, 'paleo')}{convn(form.peanut_free.data, 'peanut-free')}{convn(form.pecatarian.data, 'pecatarian')}{convn(form.pork_free.data, 'pork-free')}{convn(form.red_meat_free.data, 'red-meat-free')}{convn(form.sesame_free.data, 'sesame-free')}{convn(form.shellfish_free.data, 'shellfish-free')}{convn(form.soy_free.data, 'soy-free')}{convn(form.tree_nut_free.data, 'tree-nut-free')}{convn(form.vegan.data, 'vegan')}{convn(form.vegetarian.data, 'vegetarian')}{convn(form.wheat_free.data, 'wheat-free')}{calfilt}{catfilt}")
        res = r.json()
        return render_template('nutrisearch.html', r=res, form=form, title='NutriSearch', route='nutrisearch')
    return render_template('nutrisearch.html', r=[], form=form, title='NutriSearch', route='nutrisearch')


@app.route('/recisearch', methods=["GET", "POST"])
def recisearch():
    form = ReciSearchForm()
    if form.validate_on_submit():
        if form.calorie_filter1.data != None and form.calorie_filter2.data != None:
            calfilt = f'&calories={form.calorie_filter1.data}-{form.calorie_filter2.data}'
        elif form.calorie_filter1.data != None and form.calorie_filter2.data == None:
            calfilt = f'&calories={form.calorie_filter1.data}%2B'
        elif form.calorie_filter1.data == None and form.calorie_filter2.data != None:
            calfilt = f'&calories=0-{form.calorie_filter2.data}'
        elif form.calorie_filter1.data == None and form.calorie_filter2.data == None:
            calfilt = ''
        if form.time_filter1.data != None and form.time_filter2.data != None:
            timefilt = f'&time={form.time_filter1.data}-{form.time_filter2.data}'
        elif form.time_filter1.data != None and form.time_filter2.data == None:
            timefilt = f'&time={form.time_filter1.data}%2B'
        elif form.time_filter1.data == None and form.time_filter2.data != None:
            timefilt = f'&time=0-{form.time_filter2.data}'
        elif form.time_filter1.data == None and form.time_filter2.data == None:
            timefilt = ''
        if form.max_ingredients.data != None:
            mifilt = f'&ingr={form.max_ingredients.data}'
        else:
            mifilt = ''
        r = requests.get(f"https://api.edamam.com/search?app_id=ffb22013&app_key=0253bf93b7dd1e87cffc7c480c42242f&q={form.query.data}{convn(form.alcohol_free.data, 'alcohol-free')}{convn(form.celery_free.data, 'celery-free')}{convn(form.crustacean_free.data, 'crustacean-free')}{convn(form.dairy_free.data, 'dairy-free')}{convn(form.egg_free.data, 'egg-free')}{convn(form.fish_free.data, 'fish-free')}{convn(form.fodmap_free.data, 'fodmap-free')}{convn(form.gluten_free.data, 'gluten-free')}{convn(form.kosher.data, 'kosher')}{convn(form.lupine_free.data, 'lupine-free')}{convn(form.mustard_free.data, 'mustard-free')}{convn(form.No_oil_added.data, 'No-oil-added')}{convn(form.low_sugar.data, 'low-sugar')}{convn(form.paleo.data, 'paleo')}{convn(form.peanut_free.data, 'peanut-free')}{convn(form.pecatarian.data, 'pecatarian')}{convn(form.pork_free.data, 'pork-free')}{convn(form.red_meat_free.data, 'red-meat-free')}{convn(form.sesame_free.data, 'sesame-free')}{convn(form.shellfish_free.data, 'shellfish-free')}{convn(form.soy_free.data, 'soy-free')}{convn(form.tree_nut_free.data, 'tree-nut-free')}{convn(form.vegan.data, 'vegan')}{convn(form.vegetarian.data, 'vegetarian')}{convn(form.wheat_free.data, 'wheat-free')}{calfilt}{timefilt}{mifilt}")
        res = r.json()
        return render_template('recisearch.html', r=res, form=form, title='ReciSearch', route='recisearch')
    return render_template('recisearch.html', r=[], form=form, title='ReciSearch', route='recisearch')


"""@app.route('/nutriscan', methods=["GET", "POST"])
def nutriscan():
    form = NutriScanForm()
    if form.validate_on_submit():
        d = decode(Image.open(form.image.data))
        if d == []:
            flash('ERROR! Image may be corrupted, blank, or not a barcode')
            return redirect(url_for('nutriscan'))
        d = d[0][0].decode("utf-8")
        r = requests.get(f'https://api.edamam.com/api/food-database/v2/parser?app_id=104d2abe&app_key=621914ce184adee2580e7970b7ca5148&upc={d}')
        res = r.json()
        return render_template('nutriscan.html', r=res, form=form, title='NutriScan', route='nutriscan')
    return render_template('nutriscan.html', r=[], form=form, title='NutriScan', route='nutriscan')"""


@app.route('/mentalhealth')
def mental_health():
    return render_template('mental_health.html', title='Mental Health', route='mental_health')


@app.route('/mentalhealth/anxiety')
def anxiety():
    return render_template('anxiety.html', title='Anxiety - Mental Health', route='mental_health')


@app.route('/mentalhealth/asmr')
def asmr():
    return render_template('asmr.html', title='ASMR - Mental Health', route='mental_health')


@app.route('/mentalhealth/depression')
def depression():
    return render_template('depression.html', title='Depression - Mental Health', route='mental_health')


@app.route('/mentalhealth/anger-management')
def anger():
    return render_template('anger.html', title="Anger Management - Mental Health", route='mental_health')


@app.route('/weighttools/bmi', methods=["GET", "POST"])
def bmi():
    form = BMIForm()
    if form.validate_on_submit():
        height = float(form.height.data) * 2.54
        weight = float(form.weight.data) / 2.205
        url = "https://fitness-calculator.p.rapidapi.com/bmi"

        querystring = {"age": str(form.age.data),
                       "weight": str(weight), "height": str(height)}

        headers = {
            'x-rapidapi-key': "4768364f52mshf6f95184e114982p1c9548jsn9fff5ab8c3b1",
            'x-rapidapi-host': "fitness-calculator.p.rapidapi.com"
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        return render_template('bmi.html', title='BMI Calculator', route='weighttools', form=form, res=response.json())
    return render_template('bmi.html', title='BMI Calculator', route='weighttools', form=form, res='')


@app.route('/weighttools/idealweight', methods=["GET", "POST"])
def idealweight():
    form = IdealWeightForm()
    if form.validate_on_submit():
        height = float(form.height.data) * 2.54
        url = "https://fitness-calculator.p.rapidapi.com/idealweight"

        querystring = {"gender": form.gender.data,
                       "weight": "0", "height": height}

        headers = {
            'x-rapidapi-key': "4768364f52mshf6f95184e114982p1c9548jsn9fff5ab8c3b1",
            'x-rapidapi-host': "fitness-calculator.p.rapidapi.com"
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        fres = response.json()
        try:
            nd = round(float(fres["Devine"]) * 2.205, 2)
            nh = round(float(fres["Hamwi"]) * 2.205, 2)
            nm = round(float(fres["Miller"]) * 2.205, 2)
            nr = round(float(fres["Robinson"]) * 2.205, 2)
        except:
            flash('Height is too low', 'warning')
            return redirect(url_for('idealweight'))
        fres["Devine"] = nd
        fres["Hamwi"] = nh
        fres["Miller"] = nm
        fres["Robinson"] = nr
        return render_template('idealweight.html', res=fres, title='Ideal Weight Calculator', route='weighttools', form=form)
    return render_template('idealweight.html', title='Ideal Weight Calculator', route='weighttools', form=form, res='')


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
