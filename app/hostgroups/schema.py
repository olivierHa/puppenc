from app.puppenc import ma
from app.hostgroups.models import Hostgroup

class HostgroupSchema(ma.ModelSchema):
    class Meta:
        model = Hostgroup
        # Fields to expose
        fields = ('id', 'name', 'insert_date', 'update_date', 'class_id')
