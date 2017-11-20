from collections import namedtuple
from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import IntegerField, RadioField, SubmitField
from wtforms.validators import Required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'gallao'
bootstrap = Bootstrap(app)


# Classes

Pertinence = namedtuple('Pertinence', ['weakFactor',
                                       'softFactor',
                                       'strongFactor'])

Pertinences = namedtuple('Pertinences', ['cola', 'rum', 'ice'])

Palate = tuple()

Palates = namedtuple('Palates', ['weak', 'soft', 'strong'])


class CubaForm(Form):
    qtdSoda = IntegerField('Quantidade de refrigerante:', validators=[
                                                            Required()])
    typeSoda = RadioField(label='Tipo de refrigerante:',
                          choices=[
                              ('coke', 'Coca-Cola'),
                              ('pepsi', 'Pepsi')],
                          validators=[Required()])
    qtdRum = IntegerField('Quantidade de rum:', validators=[Required()])
    qtdIce = IntegerField('Quantidade de gelo:', validators=[Required()])
    submit = SubmitField('Calcular')


class Drink(object):

    def __init__(self, qtdSoda, typeSoda, qtdRum, qtdIce):
        self.qtdSoda = qtdSoda
        self.typeSoda = typeSoda
        self.qtdRum = qtdRum
        self.qtdIce = qtdIce

    def __str__(self):
        return "qtdSoda: {}, typeSoda: {}, qtdRum: {}, qtdIce: {}".format(
                    self.qtdSoda, self.typeSoda, self.qtdRum, self.qtdIce)


# Routes


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        form = CubaForm()
        if form.validate_on_submit():
            drink = Drink(form.qtdSoda.data,
                          form.typeSoda.data,
                          form.qtdRum.data,
                          form.qtdIce.data)
            pertinences = calculatePertinences(drink)
            drink_valid = validate_drink_data(drink)

            if(drink_valid):
                palates = calculatePalates(pertinences)
                maximum = (max(palates.weak),
                           max(palates.soft),
                           max(palates.strong))
                result = max(maximum)

                category = get_category(maximum)
                price = get_price(category)

                return render_template('result.html',
                                       pertinences=pertinences,
                                       palates=palates,
                                       maximum=maximum,
                                       result=result,
                                       category=category,
                                       price=price)
        return render_template('index.html', form=form)
    except Exception as error:
        return redirect(url_for('error_handler'))


@app.route('/error', methods=['GET'])
def error_handler(error_messages=list()):
    return render_template('error.html', error_messages=error_messages)


# Private Functions


def calculatePertinences(drink: Drink) -> tuple:
    if(drink.typeSoda == 'coke'):
        colaPertinence = calculateCokePertinence(drink.qtdSoda)
    else:
        colaPertinence = calculatePepsiPertinence(drink.qtdSoda)
    rumPertinence = calculateRumPertinence(drink.qtdRum)
    icePertinence = calculateIcePertinence(drink.qtdIce)
    return Pertinences(colaPertinence, rumPertinence, icePertinence)


def calculateCokePertinence(qtdSoda: int) -> Pertinence:
    try:
        # Cálculo pertinência fraca
        if qtdSoda < 56 or qtdSoda > 60:
            weakFactor = 0
        elif 56 <= qtdSoda <= 58:
            weakFactor = increasingLinear(qtdSoda, 56, 58)
        elif 58 <= qtdSoda <= 60:
            weakFactor = 1
        else:
            raise ValueError

        # Cálculo pertinência suave
        if qtdSoda < 52 or qtdSoda > 58:
            softFactor = 0
        elif 52 <= qtdSoda <= 54:
            softFactor = increasingLinear(qtdSoda, 52, 54)
        elif 54 <= qtdSoda <= 56:
            softFactor = 1
        elif 56 <= qtdSoda <= 58:
            softFactor = decreasingLinear(qtdSoda, 56, 58)
        else:
            raise ValueError

        # Cálculo pertinência forte
        if qtdSoda < 50 or qtdSoda > 54:
            strongFactor = 0
        elif 50 <= qtdSoda <= 52:
            strongFactor = 1
        elif 52 <= qtdSoda <= 54:
            strongFactor = decreasingLinear(qtdSoda, 52, 54)
        else:
            raise ValueError

        return Pertinence(weakFactor, softFactor, strongFactor)

    except ValueError as error:
        raise


def calculatePepsiPertinence(qtdSoda: int) -> Pertinence:
    try:
        # Cálculo pertinência fraca
        if qtdSoda < 66 or qtdSoda > 70:
            weakFactor = 0
        elif 66 <= qtdSoda <= 68:
            weakFactor = increasingLinear(qtdSoda, 66, 68)
        elif 68 <= qtdSoda <= 70:
            weakFactor = 1
        else:
            raise ValueError

        # Cálculo pertinência suave
        if qtdSoda < 62 or qtdSoda > 68:
            softFactor = 0
        elif 62 <= qtdSoda <= 64:
            softFactor = increasingLinear(qtdSoda, 62, 64)
        elif 64 <= qtdSoda <= 66:
            softFactor = 1
        elif 66 <= qtdSoda <= 68:
            softFactor = decreasingLinear(qtdSoda, 66, 68)
        else:
            raise ValueError

        # Cálculo pertinência forte
        if qtdSoda < 60 or qtdSoda > 64:
            strongFactor = 0
        elif 60 <= qtdSoda <= 62:
            strongFactor = 1
        elif 62 <= qtdSoda <= 64:
            strongFactor = decreasingLinear(qtdSoda, 62, 64)

        return Pertinence(weakFactor, softFactor, strongFactor)

    except ValueError as error:
        raise


def calculateRumPertinence(qtdRum: int):
    try:
        # Cálculo pertinência fraca
        if qtdRum < 10 or qtdRum > 20:
            weakFactor = 0
        elif 10 <= qtdRum <= 15:
            weakFactor = 1
        elif 15 <= qtdRum <= 20:
            weakFactor = decreasingLinear(qtdRum, 15, 20)
        else:
            raise ValueError

        # Cálculo pertinência suave
        if qtdRum < 15 or qtdRum > 27:
            softFactor = 0
        elif 15 <= qtdRum <= 20:
            softFactor = increasingLinear(qtdRum, 15, 20)
        elif 20 <= qtdRum <= 25:
            softFactor = 1
        elif 25 <= qtdRum <= 27:
            softFactor = decreasingLinear(qtdRum, 25, 27)
        else:
            raise ValueError

        # Cálculo pertinência forte
        if qtdRum < 23 or qtdRum > 30:
            strongFactor = 0
        elif 23 <= qtdRum <= 28:
            strongFactor = increasingLinear(qtdRum, 23, 28)
        elif 28 <= qtdRum <= 30:
            strongFactor = 1
        else:
            raise ValueError

        return Pertinence(weakFactor, softFactor, strongFactor)

    except ValueError as error:
        raise


def calculateIcePertinence(qtdIce):
    try:
        if qtdIce == 20:
            return 1,
        else:
            return 0,
    except ValueError as error:
        raise


def calculatePalates(pertinences):
    weakPalate = (
        min(pertinences.cola.weakFactor, pertinences.rum.weakFactor,
            pertinences.ice[0]),
        min(pertinences.cola.weakFactor, pertinences.rum.softFactor,
            pertinences.ice[0]),
        min(pertinences.cola.softFactor, pertinences.rum.weakFactor,
            pertinences.ice[0])
    )

    softPalate = (
            min(pertinences.cola.strongFactor, pertinences.rum.weakFactor,
                pertinences.ice[0]),
            min(pertinences.cola.softFactor, pertinences.rum.softFactor,
                pertinences.ice[0]),
            min(pertinences.cola.weakFactor, pertinences.rum.strongFactor,
                pertinences.ice[0])
    )

    strongPalate = (
            min(pertinences.cola.strongFactor, pertinences.rum.softFactor,
                pertinences.ice[0]),
            min(pertinences.cola.strongFactor, pertinences.rum.strongFactor,
                pertinences.ice[0]),
            min(pertinences.cola.softFactor, pertinences.rum.strongFactor,
                pertinences.ice[0])
    )

    return Palates(weakPalate, softPalate, strongPalate)


def get_category(maximum: tuple):
    categories = ("fraco", "suave", "forte")
    return categories[len(maximum) - 1 - maximum[::-1].index(max(maximum))]


def get_price(category: str):
    prices = {'fraco': 15.0, 'suave': 20.0, 'forte': 25.0}
    return prices.get(category)


def increasingLinear(factor: float, lowerBound: float, upperBound: float):
    return (factor - lowerBound) / (upperBound - lowerBound)


def decreasingLinear(factor: float, lowerBound: float, upperBound: float):
    return (upperBound - factor) / (upperBound - lowerBound)


def validate_drink_data(drink: Drink):
    try:
        status = True
        if drink.typeSoda == 'coke' and (drink.qtdSoda < 50
                                         or drink.qtdSoda > 60):
            status = False
            flash("Drinks com Coca-cola devem ter quantidades "
                  + "entre 50ml e 60ml.")
        if drink.typeSoda == 'pepsi' and (drink.qtdSoda < 60
                                          or drink.qtdSoda > 70):
            status = False
            flash("Drinks com Pepsi devem ter quantidades "
                  + "entre 60ml e 70ml.")
        if drink.qtdRum < 10 or drink.qtdRum > 30:
            status = False
            flash("Cuba Livre deve ter quantidades de rum "
                  + "entre 10ml e 30ml.")
        if drink.qtdIce != 20:
            status = False
            flash("Cuba Livre deve ter quantidades de gelo "
                  + "entre 20ml.")
        return status
    except Exception as error:
        raise


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
