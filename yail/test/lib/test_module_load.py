from importlib.util import module_from_spec
import os
import sys


__abs_file__ = os.path.abspath(__file__)
lib_dir = os.path.dirname(__abs_file__)
test_dir = os.path.dirname(lib_dir)
code_dir = os.path.dirname(test_dir)
sys.path.append(code_dir)


import importlib
import pkgutil

# import sys

import www.handlers.index as modules



def find_abs_modules(module):
    path_list = []
    spec_list = []
    print("type(module)",type(module))
    for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
        import_path = f"{module.__name__}.{modname}"
        print(importer, modname, ispkg,import_path)
        if ispkg:
            spec = pkgutil._get_spec(importer, modname)
            importlib._bootstrap._load(spec)
            spec_list.append(spec)
            print(importer, modname,spec,spec_list)
        else:
            path_list.append(import_path)
    for spec in spec_list:
        del sys.modules[spec.name]
    return path_list


# import os
# import re



def check_module(module_name):
    """
    Checks if module can be imported without actually
    importing it
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        print("Module: {} not found".format(module_name))
        return None
    else:
        print("Module: {} can be imported".format(module_name))
        return module_spec

def import_module_from_spec(module_spec):
    """
    Import the module via the passed in module specification
    Returns the newly imported module
    """
    module = importlib.util.module_from_spec(module_spec)
    
    module_spec.loader.exec_module(module)
    return module

def find_abs_modules_of_pkg(package):
    modules = []
    for path in package.__path__:
        for root,dirname,filename in os.walk(path):
            # print(root,dirname,filename)
        
            for fn in filename:
                if fn == "__init__.py" or fn == "__init__.pyc":
                    continue

                if not fn.split('.')[1] == "py":
                    # 不是py文件，跳过
                    continue

                name = fn.split('.')[0]

                root_name = root.split(path)[1]
                # print("root_name:",root_name)
                if root_name != '':
                    root_name = '.'.join(root_name.split(os.path.sep))
                    # print("root_name:",root_name)
                    # print("package.__name__:",package.__name__)
                    modname = package.__name__ + root_name + "." + name
                else:
                    modname = package.__name__ + "." + name
                
                # print("modname:",modname)
                spec = check_module(modname)
                module = import_module_from_spec(spec)
                modules.append(module)
    
    return modules      



def load_all_of_packages(package_or_module):
    '''package: 包或者名字'''
    if type(package_or_module) == str:
        module_spec = check_module(package_or_module)
        package_or_module = import_module_from_spec(module_spec)

    # print(package_or_module)
    path = getattr(package_or_module, '__path__', None)
    # print(package_or_module.__name__)
    if path is not None:
        # pkg
        # print(path)
        modules = find_abs_modules_of_pkg(package_or_module)

        return modules

    return [package_or_module]






if __name__ == "__main__":
    # print(sys.modules)
    # print(find_abs_modules(modules))
    # print(sys.modules)

    # find_abs_modules_by_dir('D:\project\linbirg\ww\ww\precord\yail\www\handlers')
    modules = load_all_of_packages('www.handlers')

    for m in modules:
        print(m)
    
    