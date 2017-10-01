from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Department, Employee

engine = create_engine('sqlite:///depts_and_employees.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Respond to a GET Request"""
        try:
            if (self.path.startswith('/departments') and self.path.endswith('/edit')):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                mID = self.path.split('/')[2]
                
                department_name = session.query(Department).filter_by(id = mID).one().name                

                output=""
                output+="<html><body>"
                output+="<h1>%s</h1>" % department_name
                output+="<form method='POST' enctype='multipart/form-data' action='/departments/%s/edit'>" % mID
                output+='<input name="updatedDepartmentName" type="text" placeholder="%s" >' % department_name
                output+='<input type="submit" value="Rename"> </form>'
                output+="</body></html>"

                self.wfile.write(output)
                return
            elif (self.path.startswith('/departments') and self.path.endswith('/delete')):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                mID = self.path.split('/')[2]

                department_name = session.query(Department).filter_by(id = mID).one().name

                output=""
                output+="<html><body>"
                output+="<h1>Are you sure you want to delete %s </h1>" % department_name
                output+="<form method='POST' enctype='multipart/form-data' action='/departments/%s/delete'>" % mID
                output+="<input name='deleteDepartment' type='submit' value='Delete'></form>"
                output+="</body></html>"

                self.wfile.write(output)
                return
            elif self.path.endswith('/departments'):                
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                #after headers we are fetching all the departments in a list
                departments = fetch_departments()

                #check the departments received from the database
                print departments

                output = ""
                output+="<html><body>"
                output+='<a href="/departments/new"><h3>Create a new department</h3></a>'
                output+= generate_output(departments)
                output+="</body></html>"
                self.wfile.write(output)

                #check the html code of the page
                #print output

                return
            elif self.path.endswith('/departments/new'):                
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                

                output = ""
                output+="<html><body>"
                output+="<h1>Make a New Department</h1>"
                output+='''<form method='POST' enctype='multipart/form-data' action='/departments/new'><input name="newDepartmentName" type="text" placeholder="New Department Name" ><input type="submit" value="Create"> </form>'''
                output+="</body></html>"

                self.wfile.write(output)
                return
            

        except IOError:
            self.send_error(404,'File Not Found %s' % self.path)

    def do_POST(self):
        '''Handling POST requests'''
        try:
            if self.path.endswith("/departments/new"):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)                
                    messagecontent = fields.get('newDepartmentName')
                
                    add_department_to_db(messagecontent[0])
                    #department added to db 

                # self.send_response(301)
                # self.send_header('Location','/departments')
                # self.end_headers()                        
            elif (self.path.startswith("/departments") and self.path.endswith('/edit')):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)
                    posted_content = fields.get('updatedDepartmentName')                                    
                    update_department_name_to_db(self.path.split('/')[2],posted_content[0])
                    print "out of update"
            elif (self.path.startswith('/departments') and self.path.endswith('/delete')):            
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                print ctype
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)
                    delete_department(self.path.split('/')[2])
                    print "department deleted"
            self.send_response(301)
            self.send_header('Location','/departments')
            self.end_headers()

            return

        except:
            pass

def fetch_departments():
    #make request to db to give all departments
    departments = session.query(Department).all()
    # department_list = []
    # for department in departments:
    #     department_list.append(department.name)
    # return department_list
    return departments

def add_department_to_db(department):
    #add a new department to the db
    department1 = Department(name=department)
    session.add(department1)
    session.commit()    
    return

def update_department_name_to_db(mID,new_name):
    department = session.query(Department).filter_by(id = mID).one()
    department.name = new_name
    session.add(department)
    session.commit()
    return

def delete_department(mID):    
    department = session.query(Department).filter(Department.id == mID).first()        
    session.delete(department)
    session.commit()
    return

def generate_output(departments):
    output=""
    for department in departments:
        output+="<div><p>%s" % department.name
        output+="<br>"
        output+="<a href='/departments/%s/edit'>Edit</a>" % department.id
        output+="<br>"
        output+="<a href='/departments/%s/delete'>Delete</a></p></div>" % department.id

    return output   

def main():
    try:
        port = 8080
        server = HTTPServer(('',port),webserverHandler)
        print 'Server running at port %s' % port
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C entered, stopping web server...'
        server.socket.close()
    
if __name__ == '__main__':
    main()