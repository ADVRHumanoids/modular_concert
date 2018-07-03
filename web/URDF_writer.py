import sys
sys.path.append('/home/edoardo/catkin_ws/src') #Add folder where "modular" package is to the $PYTHONPATH

import os
import re
import xml.etree.ElementTree as ET
import xacro
import xml.dom.minidom

from modular.urdf.read_yaml import read_yaml

import modular

import tf  

ET.register_namespace('xacro', "http://ros.org/wiki/xacro")

#obtaining tree from base file
path_name = os.path.dirname(modular.__file__)
basefile_name=path_name + '/urdf/ModularBot_new.urdf.xacro'
urdf_tree = ET.parse(basefile_name)

root = urdf_tree.getroot()

i=0
Joints=[]
origin, xaxis, yaxis, zaxis = (0, 0, 0.4), (1, 0, 0), (0, 1, 0), (0, 0, 1)

T = tf.transformations.translation_matrix(origin)
R = tf.transformations.identity_matrix()
H0 = tf.transformations.concatenate_matrices(T, R)

def main(filename):
  global i
  module_name = path_name + '/web/static/yaml/' + filename
  

  Joints.append(read_yaml(module_name))

  if(i==0):
    Joints[i].get_rototranslation(H0, Joints[i].Proximal_tf)
  else:
    Joints[i].get_rototranslation(Joints[i-1].Distal_tf, Joints[i].Proximal_tf)

  p=str(Joints[i].kinematics.joint.distal.p_dl)
  n=str(Joints[i].kinematics.joint.distal.n_dl)

  #adding 3 links to the tree
  ET.SubElement(root, "{http://ros.org/wiki/xacro}add_link_elbow", suffix = str(i+1), p = p, n= n, x = Joints[i].x, y= Joints[i].y, z= Joints[i].z, roll= Joints[i].roll, pitch= Joints[i].pitch, yaw= Joints[i].yaw)

  #update the urdf file, adding the new module 
  write_urdf(path_name + '/urdf/ModularBot_test.urdf', urdf_tree)

  i=i+1

  data = {'result': module_name}
  # data = jsonify(data)

  return data
  

#Function writin the urdf file after converting from .xacro (See xacro/__init__.py for reference)
def write_urdf(urdf_filename, tree):
  
  out=xacro.open_output(urdf_filename)

  urdf_xacro_filename = urdf_filename + '.xacro'

  #writing .xacro file
  # tree.write(urdf_xacro_filename, xml_declaration=True, encoding='utf-8')
  xmlstr = xml.dom.minidom.parseString(ET.tostring(tree.getroot())).toprettyxml(indent="   ")
  with open(urdf_xacro_filename, "w") as f:
    f.write(xmlstr)
  

  #parse the document into a xml.dom tree
  doc = xacro.parse(None, urdf_xacro_filename)
  #perform macro replacement
  xacro.process_doc(doc)

  # add xacro auto-generated banner
  banner = [xml.dom.minidom.Comment(c) for c in
            [" %s " % ('=' * 83),
              " |    This document was autogenerated by xacro from %-30s | " % urdf_xacro_filename,
              " |    EDITING THIS FILE BY HAND IS NOT RECOMMENDED  %-30s | " % "",
              " %s " % ('=' * 83)]]
  first = doc.firstChild
  for comment in banner:
    doc.insertBefore(comment, first)

  out.write(doc.toprettyxml(indent='  '))
