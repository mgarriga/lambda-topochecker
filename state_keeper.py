from flask import Flask, request, jsonify
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)

# space_state = {"W237957579":[3015, 6665] , "N1415627440":[6810], "N2575941579":[1389]}

space_state ={}


class SpaceState(Resource):
    def get(self):
        return space_state

@app.route('/update', methods = ['POST'])
def api_message():
	global space_state
	print 'Currently tracking',len(space_state),'positions.'
	for key, value in request.get_json().items():
		space_state[key] = value
	return jsonify(new_space_state=space_state) 

api.add_resource(SpaceState, '/space')

if __name__ == '__main__':
    
    app.run(host='0.0.0.0',port=5001)

    # curl -H "Content-type: application/json" -X POST http://127.0.0.1:5001/update -d '{"taxi2":"here2"}'
