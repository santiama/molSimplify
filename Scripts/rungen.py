# Written by Tim Ioannidis for HJK Group
# Dpt of Chemical Engineering, MIT

##########################################################
##########  Top level script that coordinates  ###########
##########    generation of structues, input   ###########
##########         files, jobscripts           ###########
##########################################################

from structgen import *
from io import *
#from tcgen import *
from gamgen import *
from sgejobgen import *
from slurmjobgen import *
import argparse, sys, os, shutil, itertools
from collections import Counter
from tcgen import *
import pybel

#######################################
### unconstrained random generation ###
#######################################
def randomgen(installdir,rundir,args,globs):
    emsg = False
    print 'Random generation started..\n\n'
    # load global variables
    licores = readdict(installdir+'/Ligands/ligands.dict')
    # remove empty ligand
    licores.pop("x", None)
    # get all combinations of ligands
    combos = []
    for i in range(1,8):
        for combs in itertools.combinations(range(0,len(licores)),i):
            combos.append(combs)
    # get a sample of these combinations
    samps = random.sample(range(0,len(combos)),int(args.rgen[0]))
    # loop over samples
    for c in samps:
        combo = combos[c]
        args.lig = []
        args.ligocc = []
        args.totocc = 0 
        combol = list(combo)
        random.shuffle(combol)
        for cj in combol:
            rocc = random.randint(1,7-args.totocc+1)
            trocc = rocc*int(len(licores[licores.keys()[cj]][1:]))
            if args.totocc+trocc <= 7:
                args.lig.append(licores.keys()[cj])
                args.ligocc.append(rocc)
                args.totocc += trocc
        if len(args.lig) > 0 :
                emsg = rungen(installdir,rundir,args,False,globs) # run structure generation
    return args, emsg

#######################################
### get subset between list1, list2 ###
#######################################
def counterSubset(list1, list2):
        c1, c2 = Counter(list1), Counter(list2)
        for k, n in c1.items():
            if n > c2[k]:
                return False
        return True

###############################################
### get sample aggreeing to the constraints ###
###############################################
def getconstsample(no_rgen,args,licores,coord):
    samp = []
    # 4 types of constraints: ligand, ligocc, coord, lignum
    # get ligand and ligocc
    get = False
    occup=[]
    combos = []
    generated = 0 
    # generate all combinations of ligands
    for i in range(1,coord+1):
        combos += (list(itertools.combinations_with_replacement(range(0,len(licores)),i)))
        random.shuffle(combos)
    for combo in combos:
        # get total denticity
        totdent = 0
        dents =[]
        for l in combo:
            totdent += int(len(licores[licores.keys()[l]][2:]))
            dents.append(int(len(licores[licores.keys()[l]][2:])))
        # check for multiple multidentate ligands
        dsorted = sorted(dents)
        if not coord or (coord and totdent == coord):
            if len(dsorted) > 1 and (dsorted[-1]+dsorted[-2] > totdent):
                generated = generated
            else:
                if (args.lignum and len(set(combo))==int(args.lignum)):
                    # reorder with high denticity atoms in the beginning
                    keysl = sorted(range(len(dents)), key=lambda k: dents[k])
                    ncombo = [combo[i] for i in keysl]
                    # add combo
                    samp.append(ncombo)
                    generated += 1
                elif not args.lignum:
                    # reorder with high denticity atoms in the beginning
                    keysl = sorted(range(len(dents)), key=lambda k: dents[k])
                    ncombo = [combo[i] for i in keysl]
                    # add combo
                    samp.append(ncombo)
                    generated += 1
            if (generated >= no_rgen):
                break
    return samp

#####################################
### constrained random generation ###
#####################################
def constrgen(installdir,rundir,args,globs):
    emsg = False
    # load global variables
    licores = readdict(installdir+'/Ligands/ligands.dict')
    # remove empty ligand
    licores.pop("x", None)
    print 'Random generation started..\n\n'
    # if ligand constraint apply it now
    ligs0 = []
    ligocc0 = []
    coord = False if not args.coord else int(args.coord)
    if args.gui:
        args.gui.iWtxt.setText('\n----------------------------------------------------------------------------------\n'+
                                'Random generation started\nGenerating ligand combinations.\n\n'+args.gui.iWtxt.toPlainText())
        args.gui.app.processEvents()
    if args.lig:
        for i,l in enumerate(args.lig):
            ligs0.append(l)
            ligentry,emsg = lig_load(installdir,l,licores) # check ligand
            if emsg:
                return False,emsg
            if args.ligocc:
                if len(args.ligocc) < i and len(args.lig)==1:
                    args.ligocc.append(coord)
                elif len(args.ligocc) < i:
                    args.ligocc.append(1)
            else:
                args.ligocc = []
                if len(args.lig)==1:
                    args.ligocc.append(coord)
                else:
                    args.ligocc.append(1)
            ligocc0.append(args.ligocc[i])
            if args.lignum:
                args.lignum = str(int(args.lignum) - 1)
            if coord:
                coord -= int(args.ligocc[i])*len(licores[l][2:])
            licores.pop(l, None) # remove from dictionary
    # get a sample of these combinations
    samps = getconstsample(int(args.rgen[0]),args,licores,coord)
    if len(samps)==0:
        if coord==0:
            args.lig = [a for a in ligs0]
            args.ligocc = [a for a in ligocc0]
            emsg = rungen(installdir,rundir,args,False,globs) # run structure generation
        else:
            if args.gui:
                from Classes.qBox import qBoxError
                qqb = qBoxError(args.gui.mainWindow,'Error','No suitable ligand sets were found for random generation. Exiting...')
            else:
                emsg = 'No suitable ligand sets were found for random generation. Exiting...'
                print 'No suitable ligand sets were found for random generation. Exiting...\n\n'
            return args,emsg
    # loop over samples
    for combo in samps:
        args.lig = [a for a in ligs0]
        args.ligocc = [a for a in ligocc0]
        for cj in set(combo):
            lcount = Counter(combo)
            rocc = lcount[cj]
            args.lig.append(licores.keys()[cj])
            args.ligocc.append(rocc)
        emsg = rungen(installdir,rundir,args,False,globs) # run structure generation
    return args, emsg

################################################################
### generates multiple runs for different ox and spin states ###
################################################################
def multigenruns(installdir,rundir,args,globs):
    emsg = False
    args.jid = 0 # initilize global name identifier
    multch = False
    multsp = False
    charges = args.charge
    spins = args.spin
    # check if multiple charges specified
    if args.charge and len(args.charge) > 1:
        multch = True
    # check if multiple spin states specified
    if (args.spin and len(args.spin) > 1):
        multsp = True
    # iterate over all
    fname = False
    if (multch and multsp):
        for ch in charges:
            for sp in spins:
                args.charge = ch
                args.spin = sp
                if ch[0]=='-':
                    fname='N'+ch[1:]+'S'+sp
                else:
                    fname='P'+ch+'S'+sp
                emsg = rungen(installdir,rundir,args,fname,globs)
                if emsg:
                    return emsg
    elif (multch):
        for ch in charges:
            args.charge = ch
            if (args.spin):
                args.spin = args.spin[0]
            if ch[0]=='-':
                fname='N'+ch[1:]
            else:
                fname='P'+ch[1:]
            emsg = rungen(installdir,rundir,args,fname,globs)
            if emsg:
                return emsg
    elif (multsp):
        if args.charge:
            args.charge = args.charge[0]
        for sp in spins:
            args.spin = sp
            fname = 'S'+sp
            emsg = rungen(installdir,rundir,args,fname,globs)
            if emsg:
                return emsg
    else:
        if args.charge:
            args.charge = args.charge[0]
        if args.spin:
            args.spin = args.spin[0]
        emsg = rungen(installdir,rundir,args,fname,globs) # default
    return emsg

#########################################################
### checks for multiple ligands specified in one file ###
#########################################################
def checkmultilig(ligs):
    mligs = []
    connatoms = []
    # loop over ligands
    for i,lig in enumerate(ligs):
        if ('.' in lig):
            lsuf = lig.split('.')[-1]
            if len(lsuf) == 3:
                # read molecule
                if glob.glob(lig):
                    moll = list(pybel.readfile(lsuf,lig))
                    mols = [m.write('smi') for m in moll]
                    f = open(lig,'r')
                    s = f.read().splitlines()
                    for ss in s:
                        sf = filter(None,ss.split(' '))
                        if len(sf) > 0:
                            connatoms.append(sf[-1])
                    f.close()
                    mligs.append(mols)
                else:
                    mligs.append([lig])
        else:
            mligs.append([lig])
    ligandslist = list(itertools.product(*mligs))
    # convert tuple to list
    llist = []
    for l0 in ligandslist:
        loclist = []
        if len(l0) > 0:
            for l1 in l0:
                loclist.append(l1)
            llist.append(loclist)
    return llist,connatoms

##############################################
### normal structure generation of complex ###
##############################################
def rungen(installdir,rundir,args,chspfname,globs):
    try:
        from Classes.qBox import qBoxFolder
        from Classes.qBox import qBoxInfo
        from Classes.qBox import qBoxError
    except ImportError:
        args.gui = False
    emsg = False
    licores = readdict(installdir+'/Ligands/ligands.dict')
    mcores = readdict(installdir+'/Cores/cores.dict')
    bindcores = readdict(installdir+'/Bind/bind.dict')
    cc, emsg = core_load(installdir,args.core,mcores)
    if emsg:
        return emsg
    mname = cc.ident
    globs.nosmiles = 0 # reset smiles ligands for each run
    # check for specified ligands/functionalization
    ligocc = []
    # check for files specified for multiple ligands
    mligs,catoms = [False],[False]
    if args.lig:
        mligs,catoms = checkmultilig(args.lig)
    # loop over ligands
    for mcount, mlig in enumerate(mligs):
        args.checkdir, skip = False, False # initialize flags
        if len(mligs) > 0 and mligs[0]:
            args.lig = mlig # get combination
            if catoms and len(catoms) > mcount:
                sscat = filter(None,catoms[mcount].split(','))
                if len(sscat) > 1:
                    args.smicat = [int(scat)-1 for scat in sscat]
        if (args.lig):
            ligands = args.lig
            if (args.ligocc):
                ligocc = args.ligocc
            else:
                if len(args.lig)==1 and args.coord:
                    ligocc.append(args.coord)
                else:
                    ligocc.append('1')
            for i in range(len(ligocc),len(ligands)):
                ligocc.append('1')
            lig = ''
            for i,l in enumerate(ligands):
                ligentry,emsg = lig_load(installdir,l,licores)
                if emsg:
                    skip = True
                    break
                if ligentry.ident == 'smi':
                    ligentry.ident += str(globs.nosmiles)
                    globs.nosmiles += 1
                    if args.sminame:
                        if len(args.sminame) > int(ligentry.ident[-1]):
                            ligentry.ident = args.sminame[globs.nosmiles-1][0:3]
                lig += ''.join("%s%s" % (ligentry.ident,ligocc[i]))
        else:
            ligands =[]
            lig = ''
            ligocc = ''
        if args.bind:
            # create folder for runs and check if it already exists
            if args.nambsmi:
                rootdir = rundir+mname[0:4]+lig+args.nambsmi[0:3]
            elif not args.bind in bindcores.keys():
                rootdir = rundir+mname[0:4]+lig+'bsmi'
            else:
                rootdir = rundir+mname[0:4]+lig+args.bind[0:4]
        else:
            rootdir = rundir+mname[0:4]+lig
        # check for charges/spin
        rootcheck = False
        if (chspfname):
            rootcheck = rootdir
            rootdir = rootdir + '/'+chspfname
        if (args.suff):
            rootdir += args.suff
        # check for top directory
        if  rootcheck and os.path.isdir(rootcheck) and not args.checkdirt and not skip:
            args.checkdirt = True
            if not args.gui:
                flagdir=raw_input('\nDirectory '+rootcheck +' already exists. Keep both (k), replace (r) or skip (s) k/r/s: ')
                if 'k' in flagdir.lower():
                    flagdir = 'keep'
                elif 's' in flagdir.lower():
                    flagdir = 'skip'
                else:
                    flagdir = 'replace'
            else:
                qqb = qBoxFolder(args.gui.mainWindow,'Folder exists','Directory '+rootcheck+' already exists. What do you want to do?')
                flagdir = qqb.getaction()
            # replace existing directory
            if (flagdir=='replace'):
                shutil.rmtree(rootcheck)
                os.mkdir(rootcheck)
            # skip existing directory
            elif flagdir=='skip':
                skip = True
            # keep both (default)
            else:
                ifold = 1
                while glob.glob(rootdir+'_'+str(ifold)):
                    ifold += 1
                rootcheck += '_'+str(ifold)
                os.mkdir(rootcheck)
        elif rootcheck and (not os.path.isdir(rootcheck) or not args.checkdirt) and not skip:
            print rootcheck
            args.checkdirt = True
            os.mkdir(rootcheck)
        # check for actual directory
        if os.path.isdir(rootdir) and not args.checkdirb and not skip:
            args.checkdirb = True
            if not args.gui:
                flagdir=raw_input('\nDirectory '+rootdir +' already exists. Keep both (k), replace (r) or skip (s) k/r/s: ')
                if 'k' in flagdir.lower():
                    flagdir = 'keep'
                elif 's' in flagdir.lower():
                    flagdir = 'skip'
                else:
                    flagdir = 'replace'
            else:
                qqb = qBoxFolder(args.gui.mainWindow,'Folder exists','Directory '+rootdir+' already exists. What do you want to do?')
                flagdir = qqb.getaction()
            # replace existing directory
            if (flagdir=='replace'):
                shutil.rmtree(rootdir)
                os.mkdir(rootdir)
            # skip existing directory
            elif flagdir=='skip':
                skip = True
            # keep both (default)
            else:
                ifold = 1
                while glob.glob(rootdir+'_'+str(ifold)):
                    ifold += 1
                rootdir += '_'+str(ifold)
                os.mkdir(rootdir)
        elif not os.path.isdir(rootdir) or not args.checkdirb and not skip:
            args.checkdirb = True
            os.mkdir(rootdir)
        ####################################
        ############ GENERATION ############
        ####################################
        if not skip:
            # generate xyz files
            strfiles,emsg = structgen(installdir,args,rootdir,ligands,ligocc,globs)
            # generate QC input files
            if args.qccode and not emsg:
                if args.charge and (isinstance(args.charge, list)):
                    args.charge = args.charge[0]
                if args.spin and (isinstance(args.spin, list)):
                    args.spin = args.spin[0]
                if args.qccode in 'terachem tc Terachem TeraChem TERACHEM TC':
                    jobdirs = multitcgen(args,strfiles)
                    print 'TeraChem input files generated!'
                elif args.qccode in 'gamess gam Gamess GAMESS':
                    jobdirs = multigamgen(args,strfiles)
                    print 'GAMESS input files generated!'
                else:
                    print 'Only TeraChem and GAMESS are supported right now.\n'
            # generate jobscripts
            if args.jsched and not emsg:
                if args.jsched in 'SBATCH SLURM slurm sbatch':
                    slurmjobgen(args,jobdirs)
                    print 'SLURM jobscripts generated!'
                elif args.jsched in 'SGE Sungrid sge':
                    sgejobgen(args,jobdirs)
                    print 'SGE jobscripts generated!'
        elif not emsg:
            if args.gui:
                qq = qBoxInfo(args.gui.mainWindow,'Folder skipped','Folder '+rootdir+' was skipped.')
            else:
                print 'Folder '+rootdir+' was skipped..\n'
    return emsg    