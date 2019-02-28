"""
This module defines the 'Module' class, used to describe any link or joint module, and some functions to instantiate
a module reading from a YAML file.
The 'Module' class is actually extended by the 'ModuleNode' class which make the
object a node of a tree, so that a robot can be represented by a tree of 'Module' objects.
"""
import yaml
import sys
import tf

import anytree


#
class Module(object):
    """
    Class describing all the properties of a module
    - Kinematics and dynamics paramters are loaded from a YAML file when instantiated
    - Methods are provided to compute frame transformations and store them as class attributes
    """
    def __init__(self, d):   
        """ Convert nested Python dictionary (obtained from the YAML file) to object

        Parameters:
        d (dict): dictionary containing all the basic attributes of the module.

        """
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Module(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, Module(b) if isinstance(b, dict) else b)

    # # Import the fields of the dictionary (obtained by reading the YAML file) as class attributes 
    # def __getattr__(self, name):
    #     value = self[name]
    #     if isinstance(value, dict):
    #         value = Module(value)
    #     return value

    # # From the name of the YAML file to be read, set the type of the module
    # def set_type(self, x):
    #     print(x)
    #     switcher = {
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_joint.yaml': "joint",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_link.yaml' : "link",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_link_500mm.yaml' : "link",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_link_700mm.yaml' : "link",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_elbow.yaml' : "elbow",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_size_adapter_B2M.yaml' : "size_adapter",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_size_adapter_B2S.yaml' : "size_adapter",
    #         '/home/edoardo/catkin_ws/src/modular/web/static/yaml/module_size_adapter_M2S.yaml' : "size_adapter"
    #     }
    #     setattr(self, 'type', switcher.get(x,"Invalid file name"))

    # 
    def set_size(self, mod):
        """Set the size of the module"""
        switcher = {
                'small': '1',
                'medium': '2',
                'big': '3',
            }
        if mod.type == "size_adapter":
            print(mod.size_in)
            setattr(self, 'size_in', switcher.get(mod.size_in, "Invalid size"))
            print(mod.size_out)
            setattr(self, 'size_out', switcher.get(mod.size_out, "Invalid size"))
        else:
            print(mod.size)
            setattr(self, 'size', switcher.get(mod.size, "Invalid size"))

    #
    # noinspection PyPep8Naming
    def get_proximal_distal_matrices(self):
        """Computes the homogeneous transformation matrices for the distal and proximal part of the joint"""
        origin, xaxis, yaxis, zaxis = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)

        proximal = self.kinematics.joint.proximal
        distal = self.kinematics.joint.distal

        H1 = tf.transformations.rotation_matrix(proximal.delta_pl, zaxis)
        H2 = tf.transformations.translation_matrix((0, 0, proximal.p_pl))
        H3 = tf.transformations.translation_matrix((proximal.a_pl, 0, 0))
        H4 = tf.transformations.rotation_matrix(proximal.alpha_pl, xaxis)
        H5 = tf.transformations.translation_matrix((0, 0, proximal.n_pl))

        P = tf.transformations.concatenate_matrices(H1, H2, H3, H4, H5)

        # Add the transformation matrix for the Proximal part as attribute of the class
        setattr(self, 'Proximal_tf', P)

        H1 = tf.transformations.translation_matrix((0, 0, distal.p_dl))
        H2 = tf.transformations.translation_matrix((distal.a_dl, 0, 0))
        H3 = tf.transformations.rotation_matrix(distal.alpha_dl, xaxis)
        H4 = tf.transformations.translation_matrix((0, 0, distal.n_dl))
        H5 = tf.transformations.rotation_matrix(distal.delta_dl, zaxis)  # 3.14

        D = tf.transformations.concatenate_matrices(H1, H2, H3, H4, H5)

        # Add the transformation matrix for the Distal part as attribute of the class
        setattr(self, 'Distal_tf', D)

        # TO BE CHECKED!!!
        # Decompose proximal transform. Translation part will be used to set the size of the joint
        scale, shear, angles, trans, persp = tf.transformations.decompose_matrix(P)

        # TO BE CHECKED!!!
        size_x = trans[0]  # 0
        size_y = trans[1]  # proximal.p_pl + distal.p_dl
        # print(size_y)
        size_z = trans[2]  # proximal.n_pl + distal.n_dl
        # print(size_z)

        # Set the joint size
        setattr(self, 'joint_size_x', str(size_x))
        setattr(self, 'joint_size_y', str(size_y))
        setattr(self, 'joint_size_z', str(size_z))
    
    # 
    # noinspection PyPep8Naming
    def get_homogeneous_matrix(self):
        """Computes the homogeneous transformation matrix for the link"""
        origin, xaxis, yaxis, zaxis = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)

        link = self.kinematics.link

        # TO BE CHECKED!!!
        H1 = tf.transformations.rotation_matrix(link.delta_l_in, zaxis)
        H2 = tf.transformations.translation_matrix((0, 0, link.p_l))
        H3 = tf.transformations.translation_matrix((link.a_l, 0, 0))
        H4 = tf.transformations.rotation_matrix(link.alpha_l, xaxis)
        H5 = tf.transformations.translation_matrix((0, 0, link.n_l))
        H6 = tf.transformations.rotation_matrix(link.delta_l_out, zaxis)

        H = tf.transformations.concatenate_matrices(H1, H2, H3, H4, H5, H6)

        # Add the transformation matrix for the Proximal part as attribute of the class
        setattr(self, 'Homogeneous_tf', H)

        size_x = 0
        size_y = link.p_l
        size_z = link.n_l

        # Set the size of the link
        setattr(self, 'link_size_x', str(size_x))
        setattr(self, 'link_size_y', str(size_y))
        setattr(self, 'link_size_z', str(size_z))
    
    #
    # noinspection PyPep8Naming
    def get_rototranslation(self, distal_previous, proximal):
        """Computes the rototranslation from the frame centered at the previous joint
        to the frame at the center of this joint module.

        Parameters:
        distal_previous: transform relative to the distal part of the previous module
        proximal: transform relative to the proximal part of the current module

        """
        F = tf.transformations.concatenate_matrices(distal_previous, proximal)

        print(F)
        scale, shear, angles, trans, persp = tf.transformations.decompose_matrix(F)

        setattr(self, 'x', str(trans[0]))
        setattr(self, 'y', str(trans[1]))
        setattr(self, 'z', str(trans[2]))
        setattr(self, 'roll', str(angles[0]))
        setattr(self, 'pitch', str(angles[1]))
        setattr(self, 'yaw', str(angles[2]))

    # 
    def get_transform(self):
        """Computes the correct transformation depending on the module type"""
        x = self.type
        print(self.type)
        return {
            'joint': self.get_proximal_distal_matrices(),
            'link': self.get_homogeneous_matrix(),
            'elbow': self.get_homogeneous_matrix(),
            'size_adapter': self.get_homogeneous_matrix()
        }.get(x, 'Invalid type')

    # def get_connector_tf(self, connector):
    #     origin, xaxis, yaxis, zaxis = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)

    #     #TO BE CHECKED!!!
    #     T = tf.transformations.translation_matrix((connector.x, connector.y, connector.z))
    #     Rx = tf.transformations.rotation_matrix(connector.roll, xaxis)
    #     Ry = tf.transformations.rotation_matrix(connector.pitch, yaxis)
    #     Rz = tf.transformations.rotation_matrix(connector.yaw, zaxis)
    #     R = tf.transformations.concatenate_matrices(Rx, Ry, Rz)
    #     H=tf.transformations.concatenate_matrices(T, R)

    #     # Add the transformation matrix for the Proximal part as attribute of the class
    #     setattr(connector, 'Homogeneous_tf', H)


# 
class ModuleNode(Module, anytree.NodeMixin):
    """Class that extends the Module class to be a tree node (using anytree NodeMixin)"""
    def __init__(self, dictionary, name, parent=None):
        """When instantiated the __init__ from the inherited class is called. Name and parent attributes are updated"""
        # when calling a method of a class that has been extended super is needed
        super(ModuleNode, self).__init__(dictionary)
        self.name = name
        self.parent = parent


# 
def module_from_yaml(filename, father):
    """Function parsing YAML file describing a generic module and returning an instance of a Module class"""
    with open(filename, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    # Create an instance of a ModuleNode class from the dictionary obtained from YAML
    result = ModuleNode(data, filename, parent=father)
    # result.set_type(filename)
    result.get_transform()
    result.set_size(result)
    return result 


#
def mastercube_from_yaml(filename, father=None):
    """Function parsing YAML file describing a mastercube and returning an instance of a Module class"""
    with open(filename, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    mastercube = ModuleNode(data, filename, parent=father)
    # con1 = MasterCube.kinematics.connector_1
    # MasterCube.get_connector_tf(con1)
    # con2 = MasterCube.kinematics.connector_2
    # MasterCube.get_connector_tf(con2)
    # con3 = MasterCube.kinematics.connector_3
    # MasterCube.get_connector_tf(con3)
    # con4 = MasterCube.kinematics.connector_4
    # MasterCube.get_connector_tf(con4)

    # result.set_type(filename)
    # result.get_transform()
    # result.set_size(result)
    return mastercube


#
def slavecube_from_yaml(filename, father=None):
    """Function parsing YAML file describing a mastercube and returning an instance of a Module class"""
    with open(filename, 'r') as stream:
        try:
            data = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    # T_con = tf.transformations.translation_matrix((0, 0, 0.1))
    # T_con1 = tf.transformations.inverse_matrix(T_con)
    # data1 = {'Homogeneous_tf': T_con1, 'type': "link", 'name': name_con1, 'i': 0, 'p': 0, 'size': 3}
    # L_1a_con1 = ModuleNode(data1, name_con1, parent=father)
    slavecube = ModuleNode(data, filename, parent=father)
    # con1 = SlaveCube.kinematics.connector_1
    # SlaveCube.get_connector_tf(con1)
    # con2 = SlaveCube.kinematics.connector_2
    # SlaveCube.get_connector_tf(con2)
    # con3 = SlaveCube.kinematics.connector_3
    # SlaveCube.get_connector_tf(con3)
    # con4 = SlaveCube.kinematics.connector_4
    # SlaveCube.get_connector_tf(con4)
    
    # result.set_type(filename)
    # result.get_transform()
    # result.set_size(result)
    return slavecube

# class MasterCube(object):
    
#     def __init__(self, d):
#         for a, b in d.items():
#             if isinstance(b, (list, tuple)):
#                 setattr(self, a, [Module(x) if isinstance(x, dict) else x for x in b])
#             else:
#                 setattr(self, a, Module(b) if isinstance(b, dict) else b)

#     def get_connector_tf(self, connector):
#         origin, xaxis, yaxis, zaxis = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)

#         #TO BE CHECKED!!!
#         T = tf.transformations.translation_matrix(connector.x, connector.y, connector.z)
#         Rx = tf.transformations.rotation_matrix(connector.roll, xaxis)
#         Ry = tf.transformations.rotation_matrix(connector.pitch, yaxis)
#         Rz = tf.transformations.rotation_matrix(connector.yaw, zaxis)
#         R = tf.transformations.concatenate_matrices(Rx, Ry, Rz)
#         H=tf.transformations.concatenate_matrices(T, R)

#         # Add the transformation matrix for the Proximal part as attribute of the class
#         setattr(connector, 'Homogeneous_tf', H)


# Main function called when the script is not imported as a module but run directly
def main():
    my_dict = read_yaml(sys.argv[1])
    print(my_dict)


if __name__ == '__main__':
    main()
