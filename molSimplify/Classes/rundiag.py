# Written by JP Janet for HJK Group
# Dpt of Chemical Engineering, MIT

##########################################################
########   Defines class of run diagnoistc   #############
########   information to automated decision #############
########   making and property prediction    #############
##########################################################

# import modules
from molSimplify.Classes.atom3D import atom3D
from molSimplify.Classes.globalvars import globalvars

class run_diag:
    ################################
    ### constructor for classs  ####
    ################################
    def __init__(self):
        # INPUT
        """ Create a blank diagnostic object """
        globs = globalvars()
        self.sanity_is_set = False # flag to indicate if properties 
                            # have been written to this file
        self.ANN_is_set = False
        self.bl_is_set = False
        self.mol_is_set = False
        self.sanity  = False
        self.min_dist = False
        self.ANN_flag = False # ANN value has been set?
        self.ANN_reason = " not set" # Reason ANN not set
        self.ANN_attributes = dict() # placeholder for
                                     # predicted properties
        self.dict_bondl = False # stores the ML-dict bond dist
        self.mol = False # stores a mol3D representation of the mol.
    ########################################
    ### class methods needed to populate ###
    ########################################

    def set_sanity(self,sanity,min_distance):
        if not self.sanity_is_set:
            self.sanity_is_set = True
        self.sanity = sanity
        self.min_dist = min_distance
    def set_ANN(self,ANN_flag,ANN_reason =  False,ANN_dict = False):
        if not self.ANN_is_set:
            self.ANN_is_set = True
        self.ANN_flag = ANN_flag
        if not ANN_flag:
            self.ANN_reason = ANN_reason
        elif ANN_flag:
            self.ANN_attributes = ANN_dict
    def set_dict_bl(self,dict_bl):
        if not self.bl_is_set:
            self.bl_is_set = True
        self.dict_bondl = dict_bl
    def set_mol(self,mol):
        if not self.mol_is_set:
            self.mol_is_set = True
        self.mol = mol

    ########################################
    ### class methods needed to report  ####
    ########################################
    def write_report(self,path):
        report = []
        if (not self.sanity_is_set) and (not self.ANN_is_set) and (not self.bl_is_set):
            report.append('No diagnostic set')
        else:
            if self.sanity_is_set:
                report.append('Bad structure?, ' + str(self.sanity) )
                if not self.sanity:
                    report.append('Min_dist (A), ' + str(self.min_dist))
            if self.ANN_is_set:
                report.append('Was ANN used?, '+str(self.ANN_flag))
                if not self.ANN_flag:
                    report.append('ANN reason, ' + str(self.ANN_reason))
                else:
                    for keys in self.ANN_attributes.keys():
                        report.append(str(keys) + ', '+ str(self.ANN_attributes[keys]))
            if self.bl_is_set:
                report.append('ML-bl (database, A), ' + str(self.dict_bondl))
        with open(path,'w') as f:
            for lines in report:
                f.write(lines + '\n')

                        





