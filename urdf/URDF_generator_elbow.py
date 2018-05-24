import sys
import re
import xml.etree.ElementTree as ET
import xacro
import xml.dom.minidom

from read_yaml import read_yaml

import tf  

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


def main():    

  ET.register_namespace('xacro', "http://ros.org/wiki/xacro")

  #obtaining tree from base file
  urdf_tree = ET.parse('ModularBot_new.urdf.xacro')

  root = urdf_tree.getroot()

  i=0
  Joints=[]
  origin, xaxis, yaxis, zaxis = (0, 0, 0.4), (1, 0, 0), (0, 1, 0), (0, 0, 1)
  
  T = tf.transformations.translation_matrix(origin)
  R = tf.transformations.identity_matrix()
  H0 = tf.transformations.concatenate_matrices(T, R)

  variable = ''
  variable = raw_input('Input the name of the module to load (END to stop): ')

  while(variable!='END'):  
    #add the module to the joints list
    Joints.append(read_yaml(variable))

    if(i==0):
      Joints[i].get_rototranslation(H0, Joints[i].Proximal_tf)
    else:
      Joints[i].get_rototranslation(Joints[i-1].Distal_tf, Joints[i].Proximal_tf)

    p=str(Joints[i].kinematics.joint.distal.p_dl)
    n=str(Joints[i].kinematics.joint.distal.n_dl)

    #adding 3 links to the tree
    ET.SubElement(root, "{http://ros.org/wiki/xacro}add_link_elbow", suffix = str(i+1), p = p, n= n, x = Joints[i].x, y= Joints[i].y, z= Joints[i].z, roll= Joints[i].roll, pitch= Joints[i].pitch, yaw= Joints[i].yaw)

    #update the urdf file, adding the new module 
    write_urdf(sys.argv[1], urdf_tree)

    i+=1

    variable = raw_input('Input the name of the module to load (END to stop): ')
          
  ###########################################################

  # J2 = read_yaml("module_elbow.yaml")
  # count+=1

  # J2.get_rototranslation(J1.Distal_tf, J2.Proximal_tf)

  # p=str(J2.kinematics.joint.distal.p_dl)
  # n=str(J2.kinematics.joint.distal.n_dl)

  # b = ET.SubElement(root, "{http://ros.org/wiki/xacro}add_link_elbow", suffix = str(count), p = p, n= n, x = J2.x, y= J2.y, z= J2.z, roll= J2.roll, pitch=J2.pitch, yaw=J2.yaw)
  
  # ###########################################################
  
  # J3 = read_yaml("module_elbow.yaml")
  # count+=1

  # J3.get_rototranslation(J2.Distal_tf, J3.Proximal_tf)

  # p=str(J3.kinematics.joint.distal.p_dl)
  # n=str(J3.kinematics.joint.distal.n_dl)
  
  # c = ET.SubElement(root, "{http://ros.org/wiki/xacro}add_link_elbow", suffix = str(count), p = p, n= n, x = J3.x, y= J3.y, z= J3.z, roll= J3.roll, pitch=J3.pitch, yaw=J3.yaw)

  # ###########################################################

  # #writing .xacro file
  # tree.write(sys.argv[1], xml_declaration=True, encoding='utf-8')

  # #converting from .xacro to .urdf
  # xacro.main()

if __name__ == '__main__':
  main()