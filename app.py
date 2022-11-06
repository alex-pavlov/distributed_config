#----------------------------------------------------------------------------#
# This is Distributed config project developed by Alexander Pavlov, 
# as a test assignment for the sbercloud.ru GoCloudCamp.
#
# https://github.com/gocloudcamp/test-assignment
# 06.11.2022
# pavlov.crimea@mail.ru
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import datetime
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
import unittest
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apps_configs.db'
app.config['SECRET_KEY'] = 'A2X2bpCSlu6W7x9'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Parent table
class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    serviceJSONconf = db.Column(db.String(1000), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    service = db.Column(db.String(1000), nullable=False, unique=True)
    children = db.relationship('Child', back_populates='parent', lazy=True)
    def __repr__(self):
        return f'<ID: {self.id}, serviceJSONconf: {self.serviceJSONconf}, enabled: {self.enabled}, service: {self.service}>'

# Child table
class Child(db.Model):
    __tablename__ = 'child'
    id = db.Column(db.Integer, primary_key=True)
    serviceJSONconf = db.Column(db.String(1000), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    parent = db.relationship('Parent', back_populates='children')
    def __repr__(self):
        return f'<ID: {self.id}, serviceJSONconf: {self.serviceJSONconf}>'

with app.app_context():
    db.create_all()

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/config', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def distributed_config():

    if request.method == 'GET':

        service_name = request.args.get('service')

        if service_name:
            query_result = Parent.query.filter(Parent.service == service_name).all()
            if len(query_result) == 0:
                abort(404)
            elif len(query_result) == 1 and len(query_result[0].children) == 0:
                return query_result[0].serviceJSONconf
            elif len(query_result) == 1 and len(query_result[0].children) > 0:
                configs = {}
                configs[0] = query_result[0].serviceJSONconf
                for version in range(1, len(query_result[0].children) + 1):
                    configs[version] = query_result[0].children[version - 1].serviceJSONconf 
                return jsonify(configs)
            else:
                abort(500)
                print(sys.exc_info())
        else:
            print('You should specify a service name like this: http://localhost:5000/config?service=managed-k8s')
            abort(422)


    elif request.method == 'POST':

        try:
            service_name = request.args.get('service')
            body = request.get_json()

            if not service_name:
                print('You should specify a service name like this: http://localhost:5000/config?service=managed-k8s')
                abort(422)
            if 'service' not in body:
                print('You should add the "service" key into the JSON you post!')
                abort(422)
            if  len(Parent.query.filter(Parent.service == service_name).all()) > 0:
                print('It looks like ' + service_name + ' already is in the database:')
                print(Parent.query.filter(Parent.service == service_name).all())
                abort(422)
               
            new_config = Parent(serviceJSONconf=json.dumps(body), service=body['service'])
            db.session.add(new_config)
            db.session.commit()

            return jsonify(
                        {
                            'success': True,
                            'ID': Parent.query.order_by(-Parent.id).first().id,
                            'serviceJSONconf': Parent.query.order_by(-Parent.id).first().serviceJSONconf,
                            'enabled': Parent.query.order_by(-Parent.id).first().enabled,
                            'service': Parent.query.order_by(-Parent.id).first().service,
                            'total_configs': len(Parent.query.all()),
                        }
            )

        except:
            abort(422)
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

    elif request.method == 'PATCH':

        try:
            service_name = request.args.get('service')
            body = request.get_json()

            if not service_name:
                print('You should specify a service name like this: http://localhost:5000/config?service=managed-k8s')
                abort(422)

            if 'service' not in body:
                print('You should add the "service" key into the JSON you patch!')
                abort(422)

            if  len(Parent.query.filter(Parent.service == service_name).all()) == 0:
                print('There is no ' + service_name + ' in the database:')
                print(Parent.query.filter(Parent.service == service_name).all())
                abort(422)
            
            parent = Parent.query.filter(Parent.service == service_name).first()
            child = Child(serviceJSONconf=json.dumps(body))
            child.parent = parent
 
            print(parent.children)

            db.session.add(child)
            db.session.commit()
            
            return jsonify(
                {
                    "success": True,
                }
            )

        except:
                abort(422)
                db.session.rollback()
                print(sys.exc_info())
        finally:
                db.session.close()
    
    elif request.method == 'DELETE':
        try:
            service_name = request.args.get('service')

            if not service_name:
                print('You should specify a service name like this: http://localhost:5000/config?service=managed-k8s')
                abort(422)

            if  len(Parent.query.filter(Parent.service == service_name).all()) == 0:
                print('There is no ' + service_name + ' in the database:')
                print(Parent.query.filter(Parent.service == service_name).all())
                abort(404)

            service_is_in_use = Parent.query.filter(Parent.service == service_name).first().enabled

            print(service_is_in_use)
            
            if service_is_in_use:
                return jsonify(
                    {
                        "success": False,
                        "reason": "Parent.query.filter(Parent.service == service_name).first().enabled == True",
                    }
                )
            else:
                try:
                    Parent.query.filter(Parent.service == service_name).first().delete()
                    db.session.commit()
                except:
                    db.session.rollback()
                    abort(500)
                    print(sys.exc_info())
                finally:
                    db.session.close()
                
        except:
                abort(422)
                db.session.rollback()
                print(sys.exc_info())
        finally:
                db.session.close()
    else:
        abort(400)
    
@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )

@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "unprocessable"}),
        422,
    )

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"success": False, "error": 500, "message": "internal server error"}), 500

#----------------------------------------------------------------------------#
# Test.
#----------------------------------------------------------------------------#
class Distributed_configCase(unittest.TestCase):
    """This class represents the Distributed config test case"""

    def setUp(self):
        """Executed before each test. Define test variables and initialize app."""
        self.app = app
        self.client = app.test_client
        self.managed_k8s_v1 = {"service": "managed-k8s", "data": [{"key1": "value1"}, {"key2": "value2"}]}
        self.managed_k8s_v2 = {"service": "managed-k8s", "data": [{"key1": "value1"}, {"key2": "value2"}, {"key3": "value3"}, {"key4": "value4"}]}
        self.managed_k8s_v3 = {"service": "managed-k8s", "data": [{"key1": "value1"}, {"key2": "value2"}, {"key3": "value3"}, {"key4": "value4"}, {"key5": "value5"}]}
        self.nginx_v1 = {"service": "nginx", "data": [{"key1": "value1"}, {"key2": "value2"}]}
        self.nginx_v2 = {"service": "nginx", "data": [{"key1": "value1"}, {"key2": "value2"}, {"key3": "value3"}, {"key4": "value4"}]}
        self.nginx_v3 = {"service": "nginx", "data": [{"key1": "value1"}, {"key2": "value2"}, {"key3": "value3"}, {"key4": "value4"}, {"key5": "value5"}]}
        pass

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_create_behavior(self):
        """ Test create operations  """
        res = self.client().post("/config?service=managed-k8s", json=self.managed_k8s_v1)
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
        self.assertEqual(data["service"], "managed-k8s")
        self.assertEqual(data["ID"], 1)
        pass

    def test_read_behavior(self):
        """Test read operations """
        res = self.client().get('/config?service=managed-k8s')
        data = json.loads(res.data)

        self.assertEqual(data["service"], "managed-k8s")
        self.assertEqual(data["data"], [{"key1": "value1"}, {"key2": "value2"}])
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:

if __name__ == '__main__':
    app.run(debug=True)


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
