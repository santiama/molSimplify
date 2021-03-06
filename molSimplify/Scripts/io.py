# Written by Tim Ioannidis for HJK Group
# modified by JP Janet
# Dpt of Chemical Engineering, MIT

##########################################################
########## This script handles input/output  #############
##########################################################

# import std modules
import pybel, glob, os,shutil, re, argparse, sys, random
from molSimplify.Classes.mol3D import *
from molSimplify.Classes.globalvars import *
from pkg_resources import resource_filename, Requirement

##############################################
### function to print available geometries ###
##############################################
def printgeoms():
    globs = globalvars()
    if globs.custom_path:
        f = globs.custom_path + "/Data/coordinations.dict"
    else:
        f = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Data/coordinations.dict")
    f = open(f,'r')
    s = f.read().splitlines()
    s = filter(None,s)
    f.close()
    geomnames = []
    geomshorts = []
    coords = []
    for line in s:
        if (line[0]!='#'):
            vals = filter(None,re.split(',| |:',line))
            coords.append(vals[0])
            geomnames.append(vals[1])
            geomshorts.append(vals[2])
    geomgroups = list([] for a in set(coords))
    for i,g in enumerate(coords):
        geomgroups[int(g)-1].append(geomshorts[i])
    for i,g in enumerate(geomnames):
        print "Coordination: %s, geometry: %s,\t short name: %s " %(coords[i],g,geomshorts[i])
    print ''
    
##############################################
### function to get available geometries ###
##############################################
def getgeoms():
    globs = globalvars()
#   f = open(globs.installdir+'/Data/coordinations.dict','r')
    if globs.custom_path:
        f = globs.custom_path + "/Data/coordinations.dict"
    else:
        f = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Data/coordinations.dict")
    f = open(f,'r')
    s = f.read().splitlines()
    s = filter(None,s)
    f.close()
    geomnames = []
    geomshorts = []
    coords = []
    for line in s:
        if (line[0]!='#'):
            vals = filter(None,re.split(',| |:',line))
            coords.append(vals[0]) # get coordination
            geomnames.append(vals[1]) # get name of geometry
            geomshorts.append(vals[2]) # get short names
    geomgroups = list([] for a in set(coords)) # get unique coordinations
    count = 0
    geomgroups[count].append(geomshorts[0])
    for i in range(1,len(coords)):
        if coords[i-1]!=coords[i]:
            count += 1
        geomgroups[count].append(geomshorts[i])
    return coords,geomnames,geomshorts,geomgroups

###################################
### function to read dictionary ###
###################################
def readdict(fname):
    d = dict()
    f = open(fname,'r')
    txt = f.read()
    lines = filter(None,txt.splitlines())
    f.close()
    for line in lines:
        if (line[0]!='#'):
            key = filter(None,line.split(':')[0])
            val = filter(None,line.split(':')[1])
            vals = filter(None,re.split(',',val))
            vv = []
            for i,val in enumerate(vals):
                vvs = (filter(None,val.split(' ')))
                if len(vvs) > 1 or i > 2:
                    vv.append(vvs)
                else:
                    vv += vvs
            d[key] = vv
    return d 

##############################
### get ligands dictionary ###
##############################
def getligs():
    licores = getlicores()
    a=[]
    for key in licores:
        a.append(key)
    a = sorted(a)
    a = ' '.join(a)
    return a
##############################
### get ligands cores      ###
##############################
def getlicores():
    ## this form of the functionn
    ## is used extensively in the GUI
    ## so it got it's own call. This
    ## is basically the same as getligs but
    ## returns the full dictionary
    globs = globalvars()
    if globs.custom_path: # test if a custom path is used:
         licores = str(globs.custom_path).rstrip('/') + "/Ligands/ligands.dict"
    else:
        licores = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Ligands/ligands.dict")
    licores = readdict(licores)
    return licores
##############################
### get simple ligands dict###
##############################
def getsimpleligs():
    slicores = getslicores()
    for key in slicores:
        a.append(key)
    a = sorted(a)
    a = ' '.join(a)
    return a
##############################
### get simple ligands core###
##############################
def getslicores():
    globs = globalvars()
    if globs.custom_path: # test if a custom path is used:
         slicores = str(globs.custom_path).rstrip('/') + "/Ligands/simple_ligands.dict"
    else:
        slicores = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Ligands/simple_ligands.dict")
    slicores = readdict(slicores)
    return slicores
#########################
### get ligand groups ###
#########################
def getligroups(licores):
    groups = []
    for entry in licores:
        groups += licores[entry][3]
    groups = sorted(list(set(groups)))
    a = ' '.join(groups)
    return a
    
###################################
### put [] on metals for SMILES ###
###################################
def checkTMsmiles(smi):
    g = globalvars()
    for m in g.metals():
        if m in smi:
            smi = smi.replace(m,'['+m+']')
    return smi

##############################
### get bind dictionary ###
##############################
def getbinds():
    bindcores = getbcores() 
    a=[]
    for key in bindcores:
        a.append(key)
    a = sorted(a)
    a = ' '.join(a)
    return a
#############################
### get bind cores      ###
##############################
def getbcores():
    ## this form of the functionn
    ## is used extensively in the GUI
    ## so it got it's own call. This
    ## is basically the same as getbinds() but
    ## returns the full dictionary
    globs = globalvars()
    if globs.custom_path: # test if a custom path is used:
        bcores = str(globs.custom_path).rstrip('/') + "/Bind/bind.dict"
    else:
        bcores = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Bind/bind.dict")
    bcores = readdict(bcores)
    return bcores
############################
### get cores dictionary ###
############################
def getcores():
    mcores = getmcores()
    a=[]
    for key in mcores:
        a.append(key)
    a = sorted(a)
    a = ' '.join(a)
    return a
#############################
### get mcores            ###
##############################
def getmcores():
    ## this form of the functionn
    ## is used extensively in the GUI
    ## so it got it's own call. This
    ## is basically the same as getcores() but
    ## returns the full dictionary
    globs = globalvars()
    if globs.custom_path: # test if a custom path is used:
         mcores = str(globs.custom_path).rstrip('/') + "/Cores/cores.dict"
    else:
        mcores = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Cores/cores.dict")
    mcores = readdict(mcores)
    return mcores
#######################
### load bonds data ###
#######################
def loaddata(path):
    globs = globalvars()
        # loads ML data from ML.dat file and
        # store to dictionary
    if globs.custom_path: # test if a custom path is used:
        fname = str(globs.custom_path).rstrip('/')  + path
    else:
        fname = resource_filename(Requirement.parse("molSimplify"),"molSimplify"+path)
    d = dict()

    f = open(fname)
    txt = f.read()
    lines = filter(None,txt.splitlines())
    for line in lines[1:]:
        if '#'!=line[0]: # skip comments
            l = filter(None,line.split(None))
            d[(l[0],l[1],l[2],l[3],l[4])] = l[5] # read dictionary
    f.close()
    return d

###########################
###    load backbone    ###
###########################
def loadcoord(coord):
    globs = globalvars()
#    f = open(installdir+'Data/'+coord+'.dat')
    if globs.custom_path:
        f = globs.custom_path + "/Data/" +coord + ".dat"
    else:
        f = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Data/" +coord + ".dat")
    f = open(f)

    txt = filter(None,f.read().splitlines())
    f.close()
    b = []
    for line in txt:
        l = filter(None,line.split(None))
        b.append([float(l[0]),float(l[1]),float(l[2])])
    return b
    
    
###########################
###    load core and    ###
### convert to molecule ###
###########################
def core_load(usercore,mcores):
    globs = globalvars()
    if '~' in usercore:
        homedir = os.path.expanduser("~")
        usercore = usercore.replace('~',homedir)
    emsg = False
    core = mol3D() # initialize core molecule
    ### check if core exists in dictionary
    if usercore.lower() in mcores.keys():
        dbentry = mcores[usercore.lower()]
        # load core mol file (with hydrogens
        if globs.custom_path:
            fcore = globs.custom_path + "/Cores/" +dbentry[0]
        else:
            fcore = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Cores/" +dbentry[0])

        # check if core xyz/mol file exists
        if not glob.glob(fcore):
            emsg ="We can't find the core structure file %s right now! Something is amiss. Exiting..\n" % fcore
            print emsg
            return False,emsg
        if ('.xyz' in fcore):
            core.OBmol = core.getOBmol(fcore,'xyzf')
        elif ('.mol' in fcore):
            core.OBmol = core.getOBmol(fcore,'molf')
        elif ('.smi' in fcore):
            core.OBmol = core.getOBmol(fcore,'smif')
            core.OBmol.make3D('mmff94',0) # generate 3D coords
        core.cat = [int(l) for l in filter(None,dbentry[1])]
        core.denticity = dbentry[2]
        core.ident = usercore
    ### load from file
    elif ('.mol' in usercore or '.xyz' in usercore or '.smi' in usercore):
        if glob.glob(usercore):
            ftype = usercore.split('.')[-1]
            # try and catch error if conversion doesn't work
            try:
                core.OBmol = core.getOBmol(usercore,ftype+'f') # convert from file
                if 'smi' in usercore:
                    core.OBmol.make3D('mmff94',0)
            except IOError:
                emsg = 'Failed converting file ' +usercore+' to molecule..Check your file.\n'
                print emsg
                return False,emsg
            core.ident = usercore.split('.')[0]
            core.ident = core.ident.rsplit('/')[-1]
        else:
            emsg = 'Core file '+usercore+' does not exist. Exiting..\n'
            print emsg
            return False,emsg
    ### if not, try converting from SMILES
    else:
        # check for transition metals
        usercore = checkTMsmiles(usercore)
        # try and catch error if conversion doesn't work
        try:
            core.OBmol = core.getOBmol(usercore,'smi') # convert from smiles
            core.OBmol.make3D('mmff94',0) # add hydrogens and coordinates
        except IOError:
            emsg = "We tried converting the string '%s' to a molecule but it wasn't a valid SMILES string.\n" % usercore
            emsg += "Furthermore, we couldn't find the core structure: '%s' in the cores dictionary. Try again!\n" % usercore
            emsg += "\nAvailable cores are: %s\n" % getcores()
            print emsg
            return False,emsg
        core.cat = [0]
        core.denticity = 1
        core.ident = 'core'
    return core,emsg
    
###########################
###   load ligand and   ###
### convert to molecule ###
###########################
def lig_load(userligand,licores):
    
    globs = globalvars()
    ### get groups ###
    groups = []
    for entry in licores:
        groups += licores[entry][3]
    groups = sorted(list(set(groups)))
    # check if user requested group
    if userligand.lower() in groups:
        subligs = [key for key in licores if userligand.lower() in licores[key][3]]
        # randomly select ligand
        userligand = random.choice(subligs)
    if '~' in userligand:
        homedir = os.path.expanduser("~")
        userligand = userligand.replace('~',homedir)
    emsg = False
    lig = mol3D() # initialize ligand molecule
    ### check if ligand exists in dictionary
    if userligand in licores.keys():
        dbentry = licores[userligand]
        # load lig mol file (with hydrogens)
        if globs.custom_path:
            flig = globs.custom_path + "/Ligands/" + dbentry[0]
        else:
            flig = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Ligands/" +dbentry[0])
        # check if ligand xyz/mol file exists
        if not glob.glob(flig):
            emsg = "We can't find the ligand structure file %s right now! Something is amiss. Exiting..\n" % flig
            print emsg
            return False, emsg
        
        if ('.xyz' in flig):
            lig.OBmol = lig.getOBmol(flig,'xyzf')
            
        elif ('.mol' in flig):
            lig.OBmol = lig.getOBmol(flig,'molf')
            
        elif ('.smi' in flig):
            lig.OBmol = lig.getOBmol(flig,'smif')
            # generate coordinates if not existing
            lig.OBmol.make3D('mmff94',0) # add hydrogens and coordinates
        ### modified the check for length,
        ### as it parsing string length instead of
        ### list length!
        if isinstance(dbentry[2], (str, unicode)):
           lig.denticity = 1
        else:
           lig.denticity = len(dbentry[2])
        lig.ident = dbentry[1]
        lig.charge = lig.OBmol.charge
        if 'pi' in dbentry[2]:
            lig.cat = [int(l) for l in dbentry[2][:-1]]
            lig.cat.append('pi')
        else:
            if lig.denticity == 1:
                lig.cat = [int(dbentry[2])]
            else:
                lig.cat = [int(l) for l in dbentry[2]]
        if lig.denticity > 1:
            lig.grps = dbentry[3]
        else:
            lig.grps = []
        if len(dbentry) > 3:
            lig.ffopt = dbentry[4][0]
        ### load from file
        #print('dent is ' + str(lig.denticity))
    elif ('.mol' in userligand or '.xyz' in userligand or '.smi' in userligand or '.sdf' in userligand):
        if glob.glob(userligand):
            ftype = userligand.split('.')[-1]
            # try and catch error if conversion doesn't work
            try:
                lig.OBmol = lig.getOBmol(userligand,ftype+'f') # convert from smiles
                # generate coordinates if not existing
                if lig.OBmol.dim==0:
                    lig.OBmol.make3D('mmff94',0) # add hydrogens and coordinates
                lig.charge = lig.OBmol.charge
            except IOError:
                emsg = 'Failed converting file ' +userligand+' to molecule..Check your file.\n'
                return False,emsg
            lig.ident = userligand.rsplit('/')[-1]
            lig.ident = lig.ident.split('.'+ftype)[0]
        else:
            emsg = 'Ligand file '+userligand+' does not exist. Exiting..\n'
            print emsg
            return False,emsg
    ### if not, try converting from SMILES
    else:
        # check for transition metals
        #userligand = checkTMsmiles(userligand)
        # try and catch error if conversion doesn't work
        try:
            if globs.debug:
                print userligand
            lig.OBmol = lig.getOBmol(userligand,'smi') # convert from smiles
            lig.OBmol.make3D('mmff94',0) # add hydrogens and coordinates
            #lig.OBmol.write(format='mol', filename='smilig.mol', overwrite=True)
            #lig.OBmol = lig.getOBmol('smilig.mol','molf')
            #os.remove('smilig.mol')
            lig.charge = lig.OBmol.charge
        except IOError:
            emsg = "We tried converting the string '%s' to a molecule but it wasn't a valid SMILES string.\n" % userligand
            emsg += "Furthermore, we couldn't find the ligand structure: '%s' in the ligands dictionary. Try again!\n" % userligand
            emsg += "\nAvailable ligands are: %s\n" % getligs()
            emsg += "\nAnd available groups are: %s\n" % getligroups(licores)
            print emsg
            return False,emsg
        lig.ident = 'smi'
    lig.name = userligand
    return lig,emsg

####################################
###   load binding species and   ###
#####   convert to molecule    #####
####################################
def bind_load(userbind,bindcores):
    globs = globalvars()
    if '~' in userbind:
        homedir = os.path.expanduser("~")
        userbind = userbind.replace('~',homedir)
    emsg = False
    bind = mol3D() # initialize binding molecule
    bsmi = False # flag for smiles
    ### check if binding molecule exists in dictionary
    if userbind in bindcores.keys():
        # load bind mol file (with hydrogens)
#        fbind = installdir+'Bind/'+bindcores[userbind][0]
        if globs.custom_path:
            fbind = globs.custom_path + "/Bind/" + bindcores[userbind][0]
        else:
            fbind = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Bind/" +bindcores[userbind][0])
        # check if bind xyz/mol file exists
        if not glob.glob(fbind):
            emsg = "We can't find the binding species structure file %s right now! Something is amiss. Exiting..\n" % fbind
            print emsg
            return False,False,emsg
        if ('.xyz' in fbind):
            bind.OBmol = bind.getOBmol(fbind,'xyzf')
        elif ('.mol' in fbind):
            bind.OBmol = bind.getOBmol(fbind,'molf')
        elif ('.smi' in fbind):
            bind.OBmol = bind.getOBmol(fbind,'smif')
        bind.charge = bind.OBmol.charge
    ### load from file
    elif ('.mol' in userbind or '.xyz' in userbind or '.smi' in userbind):
        if glob.glob(userbind):
            ftype = userbind.split('.')[-1]
            # try and catch error if conversion doesn't work
            try:
                bind.OBmol = bind.getOBmol(userbind,ftype+'f') # convert from file
                if bind.OBmol.dim==0:
                    bind.OBmol.make3D('mmff94',0) # add hydrogens and coordinates
                bind.charge = bind.OBmol.charge
            except IOError:
                emsg = 'Failed converting file ' +userbind+' to molecule..Check your file.\n'
                return False,emsg
            bind.ident = userbind.rsplit('/')[-1]
            bind.ident = bind.ident.split('.'+ftype)[0]
        else:
            emsg = 'Binding species file '+userbind+' does not exist. Exiting..\n'
            return False,emsg
    ### if not, try converting from SMILES
    else:
        # check for transition metals
        userbind = checkTMsmiles(userbind)
        # try and catch error if conversion doesn't work
        try:
            bind.OBmol = bind.getOBmol(userbind,'smi') # convert from smiles
            bind.OBmol.make3D('mmff94',0) # add hydrogens and coordinates
            bind.charge = bind.OBmol.charge
            bsmi = True
            bind.ident = 'smi'
        except IOError:
            emsg = "We tried converting the string '%s' to a molecule but it wasn't a valid SMILES string.\n" % userbind
            emsg += "Furthermore, we couldn't find the binding species structure: '%s' in the binding species dictionary. Try again!\n" % userbind
            print emsg
            return False,False,emsg
    return bind, bsmi, emsg


# write input file
def getinputargs(args,fname):
    # list with arguments
    # write input args
    f = open(fname+'.molinp','w')
    f.write("# Input file generated from molSimplify at "+time.strftime('%m/%d/%Y %H:%M')+'\n')
    for arg in vars(args):
        if 'nbind' not in arg and 'rgen' not in arg and 'i'!=arg:
            if getattr(args,arg):
                f.write('-'+arg+' ')
                if isinstance(getattr(args, arg),list):
                    for ii,iar in enumerate(getattr(args, arg)):
                        if isinstance(iar,list):
                            if ii < len(getattr(args, arg))-1:
                                f.write('/')
                            for jj,iiar in enumerate(iar):
                                f.write(str(iiar))
                                if jj < len(iar)-1:
                                    f.write(',')
                        else:
                            f.write(str(iar))
                            if ii < len(getattr(args, arg))-1:
                                f.write(',')
                else:
                    f.write(str(getattr(args, arg)))
                f.write('\n')
    f.close()
#####################################
###    load plugin definitions    ###
#####################################
def plugin_defs():
    globs = globalvars()
    plugin_path = resource_filename(Requirement.parse("molSimplify"),"molSimplify/plugindefines_reference.txt")
    return plugin_path

#####################################
###   file/folder name control   ###
####################################
def get_name(args,rootdir,core,ligname,bind = False,bsmi = False):
    ### DEPRECIATED, USE NAME_COMPLEX instead
    # reads in argument namespace
    # and chooses an appropriate name
    # bind_ident is used to pass binding
    # species information 
    print('the root directory for this calc is '+ (rootdir))
    # check if smiles string in binding species
    if args.bind:
        if bsmi:
            if args.nambsmi: # if name specified use it in file
                fname = rootdir+'/'+core.ident[0:3]+ligname+args.nambsmi[0:2]
                if args.name:
                    fname = rootdir+'/'+args.name+args.nambsmi[0:2]
            else: # else use default
                fname = rootdir+'/'+core.ident[0:3]+ligname+'bsm' 
                if args.name:
                   fname = rootdir+'/'+args.name+'bsm'
        else: # else use name from binding in dictionary
            fname = rootdir+'/'+core.ident[0:3]+ligname+bind.ident[0:2]
            if args.name:
                fname = rootdir+'/'+args.name + bind.ident[0:2]
    else:
        if globs.debug:
            print('the root calculation directory is' + str(rootdir))
        fname = rootdir+'/'+core.ident[0:3]+ligname
        if args.name:
            fname = rootdir+'/'+args.name

    return fname



def name_complex(rootdir,core,ligs,ligoc,sernum,args,bind= False,bsmi=False):
    ## new version of the above, designed to 
    ## produce more human and machine-readable formats
    romans={'I':'1','II':'2','III':'3','IV':'4','V':'5','VI':'6'}
    if args.name: # if set externerally
        name = rootdir+'/'+args.name
    else:
        try:
            center = core.getAtom(0).symbol().lower()
        except:
            center = str(core).lower()
        name = rootdir + '/' + center
        if args.oxstate:
            if args.oxstate in romans.keys():
                ox = str(romans[args.oxstate])
            else:
                ox = str(args.oxstate)
        else:
            ox = "0"
        name += "_" + str(ox)
        if args.spin:
            spin = str(args.spin)
        else:
            spin = "0"
        licores = getlicores()
        sminum = 0
        for i,lig in enumerate(ligs):
            if not lig in licores:
                lig = lig.split('\t')[0]
                sminum += 1
                name += '_smi' +str(int(sernum)+int(sminum)) + '_' + str(ligoc[i])
            else:
                name += '_' + str(lig) + '_' + str(ligoc[i])
        name += "_s_"+str(spin)
        if args.bind:
            if bsmi:
                if args.nambsmi: # if name specified use it in file
                    name += "_" + +args.nambsmi[0:2]
    return name

##############################################
### function to copy ligands, bind and     ###
### cores to user-specified path       ###
##############################################
def copy_to_custom_path():
    globs = globalvars()
    if not globs.custom_path:
        print('Error, custom path not set!')
        raise('')
    ## create folder
    if not os.path.exists(globs.custom_path):
         os.makedirs(globs.custom_path)
    ### copytree cannot overwrite, need to enusre directory does not exist already
    core_dir  = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Cores")
    li_dir = resource_filename(Requirement.parse("molSimplify"),"molSimplify/Ligands")
    bind_dir = (resource_filename(Requirement.parse("molSimplify"),"molSimplify/Bind"))
    data_dir = (resource_filename(Requirement.parse("molSimplify"),"molSimplify/Data"))
    if os.path.exists(str(globs.custom_path).rstrip("/")+"/Cores"):
        print('Note: removing old molSimplify data')
        shutil.rmtree(str(globs.custom_path).rstrip("/")+"/Cores")
    if os.path.exists(str(globs.custom_path).rstrip("/")+"/Ligands"):
        print('Note: removing old molSimplify data')
        shutil.rmtree(str(globs.custom_path).rstrip("/")+"/Ligands")
    if os.path.exists(str(globs.custom_path).rstrip("/")+"/Bind"):
        print('Note: removing old molSimplify data')
        shutil.rmtree(str(globs.custom_path).rstrip("/")+"/Bind")
    if os.path.exists(str(globs.custom_path).rstrip("/")+"/Data"):
        print('Note: removing old molSimplify data')
        shutil.rmtree(str(globs.custom_path).rstrip("/")+"/Data")

    shutil.copytree(core_dir,str(globs.custom_path).rstrip("/")+"/Cores")
    shutil.copytree(li_dir,str(globs.custom_path).rstrip("/")+"/Ligands")
    shutil.copytree(bind_dir,str(globs.custom_path).rstrip("/")+"/Bind")
    shutil.copytree(data_dir,str(globs.custom_path).rstrip("/")+"/Data")
    

