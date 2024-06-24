from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Project, Resource, ProjectResource


def init_routes(app):
    @app.route('/')
    def index():
        projects = Project.query.all()
        resources = Resource.query.all()
        return render_template('index.html', projects=projects, resources=resources)

    @app.route('/create_project', methods=['GET', 'POST'])
    def create_project():
        if request.method == 'POST':
            project_name = request.form['name']
            existing_project = Project.query.filter_by(name=project_name).first()
            if existing_project:
                error = 'Project name already exists. Please choose a different name.'
                return render_template('create_project.html', error=error)
            project = Project(name=project_name)
            db.session.add(project)
            db.session.commit()
            return redirect(url_for('add_resources_to_project', project_id=project.id))
        return render_template('create_project.html')

    @app.route('/add_resources_to_project/<int:project_id>', methods=['GET', 'POST'])
    def add_resources_to_project(project_id):
        project = Project.query.get_or_404(project_id)
        if request.method == 'POST':
            if 'add_resource' in request.form:
                resource_name = request.form['resource_name']
                quantity = request.form.get('quantity', 1)

                resource = Resource.query.filter_by(name=resource_name).first()
                if not resource:
                    resource = Resource(name=resource_name)
                    db.session.add(resource)
                    db.session.commit()

                project_resource = ProjectResource(project_id=project.id, resource_id=resource.id,
                                                   quantity_needed=quantity)
                db.session.add(project_resource)
                db.session.commit()
            elif 'remove_resource' in request.form:
                project_resource_id = request.form['project_resource_id']
                project_resource = ProjectResource.query.get(project_resource_id)
                resource_id = project_resource.resource_id
                db.session.delete(project_resource)
                db.session.commit()

                # Check if the resource is used by any other project
                if ProjectResource.query.filter_by(resource_id=resource_id).count() == 0:
                    resource = Resource.query.get(resource_id)
                    db.session.delete(resource)
                    db.session.commit()

        resources = Resource.query.all()
        return render_template('add_resources_to_project.html', project=project, resources=resources)

    @app.route('/projects', methods=['GET', 'POST'])
    def list_projects():
        if request.method == 'POST':
            if 'delete' in request.form:
                project_id = request.form['project_id']
                project = Project.query.get_or_404(project_id)
                db.session.delete(project)
                db.session.commit()
            elif 'update' in request.form:
                project_id = request.form['project_id']
                project = Project.query.get_or_404(project_id)
                project.name = request.form['name']
                db.session.commit()
        projects = Project.query.all()
        return render_template('list_projects.html', projects=projects)

    @app.route('/create_resource', methods=['GET', 'POST'])
    def create_resource():
        if request.method == 'POST':
            resource_name = request.form['name']
            resource_quantity = request.form.get('quantity', 0)  # Default to 0 if not provided
            resource = Resource(name=resource_name, quantity_available=resource_quantity)
            db.session.add(resource)
            db.session.commit()
            return redirect(url_for('list_resources'))
        return render_template('create_resource.html')

    @app.route('/resources', methods=['GET', 'POST'])
    def list_resources():
        if request.method == 'POST':
            if 'delete' in request.form:
                resource_id = request.form['resource_id']
                resource = Resource.query.get_or_404(resource_id)
                db.session.delete(resource)
                db.session.commit()
            elif 'update' in request.form:
                resource_id = request.form['resource_id']
                resource = Resource.query.get_or_404(resource_id)
                resource.name = request.form['name']
                resource.quantity_available = request.form.get('quantity', 0)  # Default to 0 if not provided
                db.session.commit()
        resources = Resource.query.all()
        return render_template('list_resources.html', resources=resources)

    @app.route('/resource/<int:resource_id>', methods=['GET', 'POST'])
    def resource_detail(resource_id):
        resource = Resource.query.get_or_404(resource_id)
        if request.method == 'POST':
            if 'delete' in request.form:
                db.session.delete(resource)
                db.session.commit()
                return redirect(url_for('list_resources'))
            elif 'update' in request.form:
                resource.name = request.form['name']
                resource.quantity_available = request.form.get('quantity', 0)  # Default to 0 if not provided
                db.session.commit()
                return redirect(url_for('resource_detail', resource_id=resource.id))
        return render_template('resource_detail.html', resource=resource)

    @app.route('/add_resource_to_project', methods=['POST'])
    def add_resource_to_project():
        project_id = request.form['project_id']
        resource_name = request.form['resource_name']
        quantity = request.form.get('quantity', 1)

        resource = Resource.query.filter_by(name=resource_name).first()
        if not resource:
            resource = Resource(name=resource_name, quantity_available=0)
            db.session.add(resource)
            db.session.commit()

        project_resource = ProjectResource(project_id=project_id, resource_id=resource.id, quantity_needed=quantity)
        db.session.add(project_resource)
        db.session.commit()
        return redirect(url_for('add_resources_to_project', project_id=project_id))

    @app.route('/remove_resource_from_project', methods=['POST'])
    def remove_resource_from_project():
        project_resource_id = request.form['project_resource_id']
        project_resource = ProjectResource.query.get(project_resource_id)
        project_id = project_resource.project_id
        resource_id = project_resource.resource_id
        db.session.delete(project_resource)
        db.session.commit()

        # Check if the resource is used by any other project
        if ProjectResource.query.filter_by(resource_id=resource_id).count() == 0:
            resource = Resource.query.get(resource_id)
            db.session.delete(resource)
            db.session.commit()

        return redirect(url_for('add_resources_to_project', project_id=project_id))

    @app.route('/update_resource_quantity', methods=['POST'])
    def update_resource_quantity():
        project_resource_id = request.form['project_resource_id']
        new_quantity = request.form['quantity']
        project_resource = ProjectResource.query.get(project_resource_id)
        project_resource.quantity_needed = new_quantity
        db.session.commit()
        return redirect(url_for('add_resources_to_project', project_id=project_resource.project_id))
