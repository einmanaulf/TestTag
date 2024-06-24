from datetime import datetime
from app import db

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    quantity_available = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Resource {self.name}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    resources = db.relationship('ProjectResource', back_populates='project')

    def __repr__(self):
        return f'<Project {self.name}>'

class ProjectResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    quantity_needed = db.Column(db.Integer, default=1)
    project = db.relationship('Project', back_populates='resources')
    resource = db.relationship('Resource')

    def __repr__(self):
        return f'<ProjectResource project_id={self.project_id} resource_id={self.resource_id} quantity_needed={self.quantity_needed}>'
