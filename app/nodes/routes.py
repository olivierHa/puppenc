from flask_restful import Resource
from flask import jsonify, request

from app.puppenc import api, db
from app.decorators import *

from app.nodes.models import Node
from app.nodes.schema import NodeSchema

class Nodes(Resource):
    def __init__(self):
        self.node_schema = NodeSchema()
        self.nodes_schema = NodeSchema(many=True)

    def get(self, page=1, id=None):
        """
        @api {get} /nodes Get all nodes
        @apiVersion 1.0.0
        @apiName get_nodes
        @apiGroup Nodes
        @apiSuccess {Number}    id              The node's id.
        @apiSuccess {String}    name            The node's name.
        @apiSuccess {Datetime}  insert_date     The node's inserted date
        @apiSuccess {Datetime}  update_date     The node's updated date
        @apiSuccess {Datetime}  delete_date     The node's deleted date
        """

        """
        @api {get} /nodes/<id> Get a single node
        @apiVersion 1.0.0
        @apiName get_node
        @apiGroup Nodes
        @apiParam   {Number}    id              The node's id.
        @apiSuccess {Number}    id              The node's id.
        @apiSuccess {String}    name            The node's name.
        @apiSuccess {Datetime}  insert_date     The node's inserted date
        @apiSuccess {Datetime}  update_date     The node's updated date
        @apiSuccess {Datetime}  delete_date     The node's deleted date
        """
        if not id:
            obj = Node.query.paginate(page, 20).items
            return self.nodes_schema.jsonify(obj)
        else:
            obj = Node.query.filter_by(id=id).first()
            if not obj:
                return { "success": False, "message": "Node not found" }, 404
            return self.node_schema.jsonify(obj)


    @body_is_valid
    def post(self, id=None):
        """
        @api {post} /nodes Add a new node
        @apiVersion 1.0.0
        @apiName add_node
        @apiGroup Nodes
        @apiParam   {String}    name            The node's name.
        @apiSuccess {Number}    id              The node's id.
        @apiExample {curl} Example usage :
            curl -X POST -H "Content-Type: application/json" \
            -d '{ "name": "my_server", "environment_id":1 }' \
            http://127.0.0.1:5000/api/v1/nodes
        """
        content = request.get_json(silent=True)
        name    = content['name']

        # Check if the node already exists
        exists = db.session.query(db.exists().where(Node.name == name)).scalar()
        if exists:
            return { "success": False, "message": "Node already exists" }, 200

        if not 'hostgroup_id' in content:
            hostgroup_id = None
        else:
            hostgroup_id = content['hostgroup_id']

        if not 'environment_id' in content:
            return { "success": False, "message": "No environment_id given" }, 500
        else:
            environment_id = content['environment_id']

        obj = Node(name, environment_id, hostgroup_id)
        db.session.add(obj)
        db.session.commit()

        return jsonify({obj.id: {
            'name': obj.name,
        }})

    def put(self, id):
        """
        @api {put} /nodes/<id> Edit a node
        @apiVersion 1.0.0
        @apiName put_node
        @apiGroup Nodes
        @apiParam {Number}    id              The node's id.
        @apiParam {String}    name            The node's name.
        @apiParam {Number}    environment_id  The node's environment_id.
        @apiParam {Number}    hostgroup_id    The node's hostgroup_id.
        @apiSuccess {Boolean}   success         Success (True if ok).
        @apiSuccess {String}    message         A success or error message.
        @apiExample {curl} Example usage :
            curl -X PUT -H "Content-Type: application/json" \
            -d '{ "name": "my_new_server" }' \
            http://127.0.0.1:5000/api/v1/nodes/1
        """
        node = Node.query.filter_by(id=id).first()
        if not node:
            return { "success": False, "message": "Node not found" }, 304
        else:
            Node.query.filter_by(id=id).update({ "update_date": db.func.current_timestamp() }, synchronize_session=False)

            content = request.get_json(silent=True)
            if 'name' in content:
                Node.query.filter_by(id=id).update({ "name": content['name'] }, synchronize_session=False)

            if 'environment_id' in content:
                Node.query.filter_by(id=id).update({ "environment_id": content['environment_id'] }, synchronize_session=False)

            if 'hostgroup_id' in content:
                Node.query.filter_by(id=id).update({ "hostgroup_id": content['hostgroup_id'] }, synchronize_session=False)


            db.session.commit()
            return { "success": True, "message": "Node successfully modified" }, 200


    def delete(self, id):
        """
        @api {delete} /nodes/<id> Delete a single node
        @apiVersion 1.0.0
        @apiDescription Delete will not delete the node from the database
            The flag active is set to 0, and delete_date is set to NOW()
        @apiName rm_node
        @apiGroup Nodes
        @apiParam   {Number}    id              The node's id.
        @apiSuccess {Boolean}   success         Success (True if ok).
        @apiSuccess {String}    message         A success or error message.
        @apiExample {curl} Example usage :
            curl -X DELETE http://127.0.0.1:5000/api/v1/nodes/<id>
        """
        node = Node.query.filter_by(id=id).first()
        if not node:
            return { "success": False, "message": "Node not found" }, 304
        else:
            Node.query.filter_by(id=id).update({ "active": 0, "delete_date": db.func.current_timestamp() }, synchronize_session=False)
            db.session.commit()
            return { "success": True }, 200
