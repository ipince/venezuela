#!/usr/bin/python

# sudo pip install mysql-python
import MySQLdb as mdb
# TODO(ipince): comment

class DB(object):
  def __init__(self, username, password, dbname):
    self.conn = mdb.connect('localhost', username, password, dbname)
    self.cursor = self.conn.cursor()

  def get_version(self):
    self.cursor.execute('SELECT VERSION()')
    return self.cursor.fetchone()

  def create_tables(self):
    self.cursor.execute('''
      create table if not exists
      sources(
        id int not null,
        name varchar(20) not null,
        primary key (id)
      ) Engine=InnoDB;
      ''')
    self.cursor.execute('''
      create table if not exists
      centers(
        id int not null auto_increment,
        rep_code int not null,
        primary key (id)
      ) Engine=InnoDB;
    ''')
    self.cursor.execute('''
      create table if not exists
      people(
        cedula int not null,
        full_name varchar(200),
        first_name varchar(50),
        second_name varchar(50),
        first_surname varchar(50),
        second_surname varchar(50),
        birthday int unsigned,
        primary key (cedula),
        index (first_name),
        index (first_surname)
      );
      ''')

  def save_person(self, cedula, full_name = None,
                  first_name = None, second_name = None,
                  first_surname = None, second_surname = None, birthday = None):
    self.cursor.execute('''
      insert into people(cedula, full_name, first_name, second_name, first_surname, second_surname) values (%s, %s, %s, %s, %s, %s)''',
      (cedula, full_name, first_name, second_name, first_surname, second_surname))
    self.conn.commit()

  def select_person(self, cedula):
    self.cursor.execute('''
      select cedula, first_name, second_name, first_surname, second_surname from people where cedula = %s''', cedula)
    return self.cursor.fetchall()
