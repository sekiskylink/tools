#!/usr/bin/env
import os
import sys
import psycopg2
import getopt
dbname = 'etopup'
user = 'postgres'
passwd = 'postgres'

fstring = ""
def generate_inser_function(table_name, column_list):
        if not column_list:
                return ""
        arg_list=""; param_list=""; args=""
        for i in column_list:
                if i == ',' or i == 'id,bigint': continue
                param_list += "x%s %s,"%(i.split(',')[0],i.split(',')[1])
                arg_list += "%s,"%(i.split(',')[0])
                args +="x%s,"%(i.split(',')[0])
        arg_list = arg_list[:len(arg_list)-1]
        param_list = param_list[:len(param_list)-1]
        args = args[:len(args)-1]
        res = "CREATE OR REPLACE FUNCTION add_%s(%s)\n"%(table_name,param_list)
        res +="\tRETURNS BOOLEAN AS $$\n"
        res +="\tBEGIN\n"
        res +="\t\tINSERT INTO %s (%s) \n"%(table_name,arg_list)
        res +="\t\tVALUES(%s);\n"%args
        res +="\t\tRETURN TRUE;\n"
        res +="\tEND;\n"
        res +="$$ LANGUAGE 'plpgsql' SECURITY DEFINER;\n\n"
        return res

def generate_update_function(table_name, column_list):
        if not column_list:
                return ""
        arg_list=""; param_list="xid bigint,"; args=""
        for i in column_list[1:]:
                if i == ',' or i == 'id,bigint': continue
                param_list += "x%s %s,"%(i.split(',')[0],i.split(',')[1])
                #arg_list += "%s,"%i
                args +=" %s = x%s ,"%(i.split(',')[0],i.split(',')[0])
        #arg_list = arg_list[:len(arg_list)-1]
        param_list = param_list[:len(param_list)-1]
        args = args[:len(args)-1]
        res = "CREATE OR REPLACE FUNCTION update_%s(%s)\n"%(table_name,param_list)
        res +="\tRETURNS BOOLEAN AS $$\n"
        res +="\tBEGIN\n"
        res +="\t\tUPDATE %s SET %s WHERE id = xid;\n"%(table_name,args)
        res +="\t\tRETURN TRUE;\n"
        res +="\tEND;\n"
        res +="$$ LANGUAGE 'plpgsql' SECURITY DEFINER;\n\n"
        return res



cmd = """psql -d %s -P border=0 -t -U %s -c "\dt " | awk '{print $2}' | grep -v "^$" """%(dbname,user)
s = os.popen(cmd)
table_list = [i.strip() for i in s.readlines()]
#print table_list
for t in table_list:
    cmd2 = """psql -d %s -P border=0 -t -U %s -c "\d %s " | awk '{print $1","$2}' | grep -v "^$" """%(dbname, user, t)
    x = os.popen(cmd2)
    clist = [i.strip() for i in x]
    #print t,"==>",clist
    fstring += generate_inser_function(t,clist)
    fstring += generate_update_function(t,clist)
print fstring
