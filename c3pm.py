import json
import shutil
import os
from os import walk
from os.path import basename
import zipfile
from datetime import datetime

defaultC3ProjectRoot =  'temp/c3Project'
folders = {'c3Pack' : {'source' : '', 'root' : 'temp/c3Pack'}, 'c3Project' : {'source' : defaultC3ProjectRoot, 'root' : 'temp/c3Project'}, 'backup' : 'backups'}

def zipDir(dirPath, zipPath):
    zipf = zipfile.ZipFile(zipPath , mode='w')
    lenDirPath = len(dirPath)
    for root, _ , files in os.walk(dirPath):
        for file in files:
            filePath = os.path.join(root, file)
            zipf.write(filePath , filePath[lenDirPath :] )
    zipf.close()    

fileTypeList = {
    'eventSheets' : {'folderName' : 'eventSheets', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true' },
    'families' : {'folderName' : 'families', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'objectTypes' : {'folderName' : 'objectTypes', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'layouts' : {'folderName' : 'layouts', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'timelines' : {'folderName' : 'timelines', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'true'},
    'ease' : {'folderName' : 'timelines//transitions', 'copyFiles' : 'true', 'metaData' : 'false', 'c3File' : 'true'},
    'images' : {'folderName' : 'images', 'copyFiles' : 'true', 'metaData' : 'false', 'c3File' : 'false'},
    'script' : {'folderName' : 'scripts', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'sound' : {'folderName' : 'sounds', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'music' : {'folderName' : 'music', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'video' : {'folderName' : 'videos', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'font' : {'folderName' : 'fonts', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'},
    'general' : {'folderName' : 'files', 'copyFiles' : 'true', 'metaData' : 'true', 'c3File' : 'false'}
}

def importPack_extractFiles(overwriteRepeatedFiles):
   
    
    #copy project files
    for fileTypeKey, fileTypeValue in fileTypeList.items():
        
        source = folders['c3Pack']['root'] + "/" + fileTypeValue['folderName']
        dest = folders['c3Project']['root'] + "/"  + fileTypeValue['folderName']

        if(os.path.exists(source)):
            fileTypeValue['copyFiles'] = 'true'
            if(not os.path.exists(dest)):
                os.mkdir(dest)

            src_files = os.listdir(source)
            for file_name in src_files:
                full_file_name = os.path.join(source, file_name)
                
                if os.path.isfile(full_file_name):
                    if(not os.path.exists(folders['c3Project']['root'] + "/" + fileTypeValue['folderName'] + "/" + file_name) or (overwriteRepeatedFiles)):
                        shutil.copy(full_file_name, dest)
                    else:
                        raise ValueError("File already exists in the targeted project: " + file_name)
        else:
            fileTypeValue['copyFiles'] = 'false'

def importPack_updateMetaData():
    c3Proj = {'c3Pack' : {}, 'c3Project' : {}}

    #load project.c3proj
    for project in ['c3Pack', 'c3Project']:
        c3Proj[project] = ""
        with open(folders[project]['root'] + "/project.c3proj") as json_file:
            c3Proj[project] = json.load(json_file)

        



    # update used addons
    c3Proj['c3Project']['usedAddons'] += c3Proj['c3Pack']['usedAddons']

    # update containers data
    c3Proj['c3Project']['containers'] += c3Proj['c3Pack']['containers']

    packageName = c3Proj['c3Pack']['name']
    # update c3 meta data

    for fileTypeKey, fileTypeValue in fileTypeList.items():

            if fileTypeValue['metaData'] == 'true' and fileTypeValue['copyFiles'] == 'true':

                # get source project file data

                c3pmFolder = {'items':[], 'subfolders' : [], 'name' : 'c3Packs'}
                
                keyRootPath = {}
                
                if fileTypeValue['c3File'] == 'true':
                    keyRootPath['c3Pack'] = c3Proj['c3Pack'][fileTypeKey]
                    keyRootPath['c3Project'] = c3Proj['c3Project'][fileTypeKey]
                else:    
                    keyRootPath['c3Pack'] = c3Proj['c3Pack']['rootFileFolders'][fileTypeKey]
                    keyRootPath['c3Project'] = c3Proj['c3Project']['rootFileFolders'][fileTypeKey]
                
                # set target project file data
                
                folderIndex = 0
                createC3packFolder = True
                
                for fileFolder in keyRootPath['c3Project']['subfolders']:
    
                    if 'name' in fileFolder:
                        if fileFolder['name'] == 'c3Packs':
                            createC3packFolder = False
                            break
        
                    folderIndex = folderIndex + 1    
                
                

                if createC3packFolder:
                    keyRootPath['c3Project']['subfolders'].append(c3pmFolder)
                    folderIndex = len(keyRootPath['c3Project']['subfolders']) -1
                else:
                    pass
                
                c3packFolder = keyRootPath['c3Project']['subfolders'][folderIndex]['subfolders']

                createThisPackFolder = True
                packFolderIndex = 0

                for packFolder in c3packFolder:
                    if 'name' in packFolder:
                        if packFolder['name'] == packageName:
                            createThisPackFolder = False
                            break
                    packFolderIndex += 1

                fileData = {'items':[], 'subfolders' : [], 'name' : packageName}
                if createThisPackFolder:
                    c3packFolder.append(fileData)
                    packFolderIndex = len(c3packFolder) -1
                
                c3packFolder[packFolderIndex]['items'] = keyRootPath['c3Pack']['items']
                c3packFolder[packFolderIndex]['subfolders'] = keyRootPath['c3Pack']['subfolders']
                
                #fileData['items'] = keyRootPath['c3Pack']['items']
                #fileData['subfolders'] = keyRootPath['c3Pack']['subfolders']

                #c3packFolder.append(fileData)
                            
    with open(folders['c3Project']['root'] + '/' + '/project.c3proj', 'w') as outfile:
        json.dump(c3Proj['c3Project'], outfile, indent=4)

def importPack_createBackup(fileData):

    projectName = fileData['c3Project']['c3proj']['name']

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y(%H-%M-%S)")
    
    backupPath = folders['backup'] + "/" + projectName + "_" + timestampStr + ".c3p"
    print('path: ' + backupPath)

    if (not os.path.exists(folders['backup'])):
                os.makedirs(folders['backup'])

    zipDir(folders['c3Project']['root'], backupPath)

def importPack(packPath, projectPath, writeOverOriginalFiles, overwriteRepeatedFiles):
    

    try:
        #remove old temp files
        if (os.path.exists('temp')):
            shutil.rmtree('temp')
        
        folders['c3Project']['root'] = defaultC3ProjectRoot
        folders['c3Pack']['source'] = packPath
        folders['c3Project']['source'] = projectPath
        
        fileData = {'c3Pack' : {'fileDir' : '', 'fileName' : '', 'fileExtension' : '', 'c3proj' : ''}, 'c3Project' : {}}

        projectIsC3p = True

        # check pack and project files
        for projectType in ['c3Pack', 'c3Project']:

            fileData[projectType]['fileDir'] = os.path.dirname(folders[projectType]['source'])
            fileData[projectType]['fileName'] = os.path.basename(folders[projectType]['source']).split('.')[0]
            fileData[projectType]['fileExtension'] = os.path.basename(folders[projectType]['source']).split('.')[1]
            print ("Checking " + projectType + " file")
            print('file path: ' + fileData[projectType]['fileDir'])
            print('file name: ' + fileData[projectType]['fileName'])
            print('file ext: ' + fileData[projectType]['fileExtension'])
            
            if projectType == 'c3Project':
                if fileData[projectType]['fileExtension'] == 'c3p':
                    pass
                elif fileData[projectType]['fileExtension'] == 'c3proj':
                    projectIsC3p = False
                    folders['c3Project']['root'] = fileData[projectType]['fileDir']
                else:
                    raise NameError("The file extension < " + fileData[projectType]['fileExtension'] +  " > for a c3 project")
            elif projectType == 'c3Pack':
                if fileData[projectType]['fileExtension'] == 'c3p' or fileData[projectType]['fileExtension'] == 'c3pack':
                    pass
                else:
                    raise NameError("The file extension < " + fileData[projectType]['fileExtension'] +  " > for a c3 pack")
        
        

        # place project folder files in temp folder
        if projectIsC3p:
            if (not os.path.exists(folders['c3Project']['root'])):
                os.makedirs(folders['c3Project']['root'])
            
            with zipfile.ZipFile(folders['c3Project']['source'], 'r') as zip_ref:
                    zip_ref.extractall(folders['c3Project']['root'])
        else:  
            #shutil.copytree(os.path.dirname(folders['c3Project']['source']), folders['c3Project']['root'])
            pass

        # unzip c3p pack files on temp folders
        if (not os.path.exists(folders['c3Pack']['root'])):
            os.makedirs(folders['c3Pack']['root'])
        
        with zipfile.ZipFile(folders['c3Pack']['source'], 'r') as zip_ref:
                zip_ref.extractall(folders['c3Pack']['root'])
  
        #load c3proj json data        
        for projectType in ['c3Pack', 'c3Project']:
            with open(folders[projectType]['root'] + "/project.c3proj") as json_file:
                fileData[projectType]['c3proj'] = json.load(json_file)

        #c3pm magic
        
        print("Creating backups")
        importPack_createBackup(fileData)
        
        
        print("Importing files")
        importPack_extractFiles(overwriteRepeatedFiles)
    
        print("Updating meta data")
        importPack_updateMetaData()

        
        # export packed project
        
        zipPath = ""
        if projectIsC3p:
            if(writeOverOriginalFiles):
                zipPath = folders['c3Project']['source']
            else:
                zipPath = folders['c3Project']['source'].split('.')[0] + "_c3packed.c3p"
            
            zipDir(folders['c3Project']['root'], zipPath)
        
        return {'status':'sucess', 'projectName' : zipPath}

    except Exception as e:
        #raise
        return {'status':'fail', 'error':e}

def runTests():

    # set test enviroment
    filesPath = 'test/files'
    copyPath = 'test/copy'
    if os.path.exists(copyPath):
        shutil.rmtree(copyPath)
    
    if os.path.exists(filesPath):
        shutil.copytree(filesPath, copyPath)

    # 1 pack test
    if True:
        print("------------")
        print("Test: Importing 1 pack into project")
        importPack("test/copy/packs/[c3pack] Color Blink r_18902.c3pack", "test/copy/projects/project_1pack.c3p", True, True)
    
    # Update pack test
    if True:
        print("------------")
        print("Test: Importing the same packs into project 2 times")
        importPack("test/copy/packs/[c3pack] Color Blink r_18902.c3pack", "test/copy/projects/project_1pack_update.c3p", True, True)
        importPack("test/copy/packs/[c3pack] Color Blink r_18902.c3pack", "test/copy/projects/project_1pack_update.c3p", True, True)
    
    # folder project test
    if True:
        print("------------")
        print("Test: Importing 1 pack into a folder project")
        importPack("test/copy/packs/[c3pack] Color Blink r_18902.c3pack", "test/copy/projects/project_folder/project.c3proj", True, True)
    
    # 2 packs test
    if True:
        print("------------")
        print("Test: Importing 2 diferent packs into project")
        importPack("test/copy/packs/[c3pack] Color Blink r_18902.c3pack", "test/copy/projects/project_2packs.c3p", True, True)
        importPack("test/copy/packs/[C3pack] Shadow Trail r_18902.c3pack", "test/copy/projects/project_2packs.c3p", True, True)

def main():
    runTests()
    
    
if __name__== "__main__":
    main()