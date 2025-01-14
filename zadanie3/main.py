from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)
SPECIES_INT_KEYS = {0 : "Iris-setosa", 1 : "Iris-versicolor", 2 : "Iris-virginica"}
SPECIES_STR_KEYS = {"Iris-setosa": 0, "Iris-versicolor": 1 , "Iris-virginica" : 2}


class IrisModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    sepal_length_cm = db.Column(db.Float, nullable=False)
    sepal_width_cm = db.Column(db.Float, nullable=False)
    petal_length_cm = db.Column(db.Float, nullable=False)
    petal_width_cm = db.Column(db.Float, nullable=False)
    species = db.Column(db.Integer, nullable=False)
    
    def getValues(self):
        return float(self.sepal_length_cm), float(self.sepal_width_cm), float(self.petal_length_cm), float(self.petal_width_cm)
    
iris_args = reqparse.RequestParser()
iris_args.add_argument('sepal_length_cm', type=float, required=True)
iris_args.add_argument('sepal_width_cm', type=float, required=True)
iris_args.add_argument('petal_length_cm', type=float, required=True)
iris_args.add_argument('petal_width_cm', type=float, required=True)
iris_args.add_argument('species', type=int, choices = (0,1,2), required=True)

class Iris(Resource):
    def get(self):
        iris_data = IrisModel.query.all()
        result = []
        for iris in iris_data:
            result.append({
                'id': iris.id,
                'sepal_length_cm': iris.sepal_length_cm,
                'sepal_width_cm': iris.sepal_width_cm,
                'petal_length_cm': iris.petal_length_cm,
                'petal_width_cm': iris.petal_width_cm,
                'species': iris.species
            })
        return result
    def delete(self, id):
        iris = IrisModel.query.get(id)
        if not iris:
            abort(404, message="Iris with id {} not found".format(id))
        db.session.delete(iris)
        db.session.commit()
        return {'primary key': iris.id}, 200
    def post(self): 
        args = iris_args.parse_args()
        if args["species"] in SPECIES_INT_KEYS.keys():
            new_iris = IrisModel(
            sepal_length_cm=args['sepal_length_cm'],
            sepal_width_cm=args['sepal_width_cm'],
            petal_length_cm=args['petal_length_cm'],
            petal_width_cm=args['petal_width_cm'],
            species=args['species']
            )
            db.session.add(new_iris)
            db.session.commit()
            return {"primary key:" : new_iris.id}, 201
        else:  
            return 'invalid data', 400

       
api.add_resource(Iris, '/api/data', '/api/data/<int:id>')

@app.route('/')
def home():
    iris_data = IrisModel.query.all()
    for i, iris in enumerate(iris_data):
        iris.species = SPECIES_INT_KEYS.get(iris.species)
        iris.number = i + 1
    return render_template('index.html', data=iris_data)

@app.route('/add', methods=['GET', 'POST'])
def add_iris():
    if request.method == 'POST':
        try:
            iris = IrisModel(
                sepal_length_cm=float(request.form['sepal_length_cm']),
                sepal_width_cm=float(request.form['sepal_width_cm']),
                petal_length_cm=float(request.form['petal_length_cm']),
                petal_width_cm=float(request.form['petal_width_cm']),
                species=SPECIES_STR_KEYS.get(request.form['species'])
            )
            for value in iris.getValues():
                if value <= 0:
                    return abort(400)

            db.session.add(iris)
            db.session.commit()
            iris.species = SPECIES_INT_KEYS.get(iris.species)
            return render_template('success.html', iris=iris)
        except Exception as e:
            return f"An error occurred: {e}", 400
    return render_template('form.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_iris(id):
    try:
        iris = Iris()
        iris.delete(id)
        return render_template('form.html')
    except Exception as e:
        return f"An error occurred: {e}", 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
