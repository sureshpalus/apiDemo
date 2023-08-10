# import dependencies
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# configure the app
def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/apiDemo1'
    db = SQLAlchemy(app)
    migrate = Migrate(app, db) 

    # table model
    class Employee(db.Model):
        __tablename__ = 'employees'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(), nullable=False)
        role = db.Column(db.String(), nullable=True)
        team = db.Column(db.String(), nullable=True)

        def format(self):
            return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'team': self.team
            }

    # Create the database tables
    with app.app_context():
        db.create_all()

    # create an endpoint to check status
    @app.route('/status')
    @app.route('/')
    def app_health():
        return jsonify({'message': 'Hello! Flask app is up and running.'})
        # return "hello"

    # endpoint to get and create employees
    @app.route('/employees', methods=['GET', 'POST'])
    def employees():
        if request.method == 'GET':
            employees = Employee.query.order_by(Employee.id).all()
            employees = [employee.format() for employee in employees]
            return jsonify(employees)
        if request.method == 'POST':
            request_name = request.json.get('name', None)
            request_role = request.json.get('role', None)
            request_team = request.json.get('team', None)
            new_employee = Employee(
            name = request_name,
            role = request_role,
            team = request_team
            )
            db.session.add(new_employee)
            db.session.commit()
            return jsonify(new_employee.format())
    
    # endpoint to get , update and delete employees item
    @app.route('/employees/<employee_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
    def employees_item(employee_id):
        try:
         employee = Employee.query.filter(Employee.id == employee_id).one_or_none()
         if employee is None:
             abort(404)
         if request.method == 'GET':
               return jsonify(employee.format())
         if request.method == 'PUT' or request.method == 'PATCH':
               request_name = request.json.get('name', None)
               request_role = request.json.get('role', None)
               request_team = request.json.get('team', None)
               if request_name:
                  employee.name = request_name
               if request_role:
                  employee.role = request_role  
               if request_team:
                  employee.team = request_team
               db.session.commit()
               return jsonify(employee.format())
         if request.method == 'DELETE':
               db.session.delete(employee)
               db.session.commit()
               return jsonify({"success": "true"})
        except Exception as e:
            abort(e.code)
    
    @app.errorhandler(404)
    def bad_request(error):
        print(error)
        return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

    return app

 # create and run app
    app = create_app()

    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=5000)