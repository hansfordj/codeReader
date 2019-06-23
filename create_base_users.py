#!/usr/bin/env python
"""Create a initial admin user"""
from getpass import getpass
from codeReader import db, app
from codeReader.models import User, UserRoles, Role, Code
import sys

def create_roles():
    try:
        admin = Role(name="ADMIN")
        manager = Role(name="MANAGER")
        tech = Role(name="TECH")

        role_list = (admin, manager, tech)
        for role in role_list:
            db.session.add(role)
          
            db.session.commit()
        return True
    except:
        print("Failure: Roles not created.")
        return False


def add_Role(user, role):
    try:
        user_role = UserRoles(user_id=user.id, role_id=role)
        return user_role
    except:
        return False

def add_AdminRole(user):
    print("Adding Admin Role")
    try:
        admin = add_Role(user, 1)
        db.session.add(admin)
        db.session.commit()
        
        return True
    except:
        print("Role Fail")
        return False

def add_ManagerRole(user):
    print("Adding Manager Role")
    try:
        manager = add_Role(user, 2)
        db.session.add(manager)
        db.session.commit()
        
        return True
    except:
        print("Role Fail")
        return False

def add_TechRole(user):
    try:
        tech = add_Role(user, 3)
        db.session.add(tech)
        db.session.commit()
        
        return True
    except:
        print("Role Fail")
        return False


def create_user(username, email, password):
    print("creating user...")
    '''
    if User.query.all():
        create = input('A user already exists! Create another? (y/n):')
        if create == 'n':
            print("Goodbye!")
            return
    '''
    if not username:
        username = input("EnterUsername:")
        email = input("Enter  Email Address:")
        password = getpass()
        assert password == getpass('Password (again):')
        user.set_password(password)
    username = username
    email = email
    password = password 
    
    #Try to create the user
    try:
        user = User(username=username, email=email)
        db.session.add(user)
        user.set_password(password)
        db.session.commit()
        print("User Created")
        return user
    

#try to assign a role
   #try:
   #     addRole()
 
    except:
        print("Failure: User not created.")
        return False

def create_admin(username, email, password):
    try:
        user = create_user(username, email, password)
     
        add_AdminRole(user)
        print("Role Pass")
        return True

    except:
        print("Failure: Admin creation failed.")
        return False
def create_manager(username, email, password):
    try:
        user = create_user(username, email, password)
     
        add_ManagerRole(user)
        print("Role Pass")
        return True
    except:
        return False

def create_technician(username, email, password):
    try:
        print("Creating Technician")
        user = create_user(username, email, password)
    
        add_TechRole(user)
        print("PASS: Role Technician Added to {user.username}")
        return True
    except:
        return False

def create_initial_selection(codeType, codeData, description):

    try:

        code = Code(codeType=codeType, codeData=codeData, description=description, selected=True)
        db.session.add(item)
        db.session.commit()
 
        
        return True
    except:

        return False


def main():
    with app.app_context():
        db.metadata.create_all(db.engine)
        create_roles()
        
        #Try to create Base Users
        try:
            
            create_admin("admin", "admin@junkteam.ca", "password")
            print("Admin Created")
            create_manager("manager", "manager@junkteam.ca", "password")
            print("Manager Created")
            create_technician("technician", "technician@junkteam.ca", "password")
            print("Technician Created")
            print("PASS: BASE USERS CREATED")
            print("Creating Initial Code...")
            create_initial_selection("QCODE", "initial_selection", "")

            print("Created Initialization Code")
            

        except:
            print("Epic Fail")
            sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
